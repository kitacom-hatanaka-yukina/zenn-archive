# なりすましメール検証ラボ（コンテナ完結版）

端末内のコンテナだけで、なりすましメールの送信〜受信〜認証判定を再現します。
外部（実在のメールサーバ）へは一切送信しないので、IP がブラックリスト入りする心配がありません。

```
sender ──SMTP(25)──> mail(Postfix) ──milter──> rspamd(SPF/DKIM/DMARC 判定)
                          │                          │
                          │ LMTP + Sieve             └─ DNS lookup ─> dns(CoreDNS)
                          ▼
                    Dovecot(IMAP) <──IMAP── roundcube(Web受信箱)
```

| サービス | 役割 |
| --- | --- |
| `dns`（CoreDNS） | 3つの偽ドメインの権威 DNS。SPF/DKIM/DMARC/MX レコードを配る |
| `rspamd` | SPF/DKIM/DMARC を実判定し `Authentication-Results` を付与。Web UI もある |
| `mail`（Postfix + Dovecot） | メールを受信し、DMARC 失敗を Sieve で迷惑メール(Junk)へ振り分け、IMAP で見せる |
| `roundcube` | 被害者 `me@inbox.example` の Web 受信箱 |
| `sender` | 既存の送信スクリプト（`01_bare.py` 等）を実行する。固定 IP `172.30.0.10` |

登場するドメイン（すべて実在しない架空のもの）:

| ドメイン | 役割 | DNS レコード |
| --- | --- | --- |
| `super-ultra-mega-bank.example` | 詐称される「銀行」。ヘッダ From に使う | `_dmarc` に DMARC ポリシー |
| `mydomain.example` | 攻撃者が管理する正規ドメイン。エンベロープ From に使う | SPF・DKIM 公開鍵 |
| `inbox.example` | 被害者の受信ドメイン | MX |

## 起動

```bash
cd code/20260828-mail-auth
docker compose up -d --build
```

初回は rspamd が TLD/hyperscan をコンパイルするため、milter が待ち受けるまで 20〜30 秒ほどかかります。

受信箱を開く: <http://localhost:18080?user=me@inbox.example&pass=password>（ユーザー `me@inbox.example` / パスワード `password`）
rspamd の判定画面（おまけ）: <http://localhost:11334>

## 検証

送信スクリプトを段階的に実行します（3通ともヘッダ From は銀行を詐称）。

```bash
# SPF/DKIM/DMARC なし
docker compose exec sender python 01_bare.py
# エンベロープ From を自ドメインにして SPF を通す
docker compose exec sender python 02_spf.py
# さらに DKIM 署名を付ける
docker compose exec sender python 03_dkim.py
```

Roundcube の「迷惑メール」フォルダに 3 通届きます。各メールの「ソースを表示」で
`Authentication-Results` を見ると、判定はこう進みます。

| 送信 | spf | dkim | dmarc |
| --- | --- | --- | --- |
| `01_bare` | none | none | **fail** |
| `02_spf` | **pass** | none | **fail** |
| `03_dkim` | **pass** | **pass**（`d=mydomain.example`） | **fail** |

SPF と DKIM は自分の管理ドメインに対して pass できても、ヘッダ From
（`super-ultra-mega-bank.example`）とはドメインが一致しない＝アラインメントが
成立しないため、DMARC は最後まで fail のままです。

### DMARC を p=reject にすると配送段階で拒否される

詐称ドメインの DMARC ポリシーを `quarantine` から `reject` に変えて送り直します。

```bash
# _dmarc レコードを p=reject に書き換え
sed -i 's/p=quarantine/p=reject/' dns/zones/super-ultra-mega-bank.example.db
docker compose restart dns rspamd

# rspamd の再初期化が終わるまで待つ（重要。待たずに送ると素通り配送される）
until docker compose exec -T mail bash -c '(exec 3<>/dev/tcp/172.30.0.11/11332)' 2>/dev/null; do sleep 3; done

docker compose exec sender python 03_dkim.py
```

今度は受信箱に届く前に、SMTP の応答が `554 5.7.1 Spam message rejected` になり、
送信スクリプトが `SMTPDataError` で止まります。DMARC ポリシーが実際に配送を
止めている様子が確認できます。

元に戻すには:

```bash
sed -i 's/p=reject/p=quarantine/' dns/zones/super-ultra-mega-bank.example.db
docker compose restart dns rspamd
```

## 後片付け

```bash
docker compose down -v
```

## 仕組みのメモ

- **SPF が接続元 IP を見る**ので、送信側 `sender` は固定 IP `172.30.0.10` にし、
  その IP を `mydomain.example` の SPF レコード（`v=spf1 ip4:172.30.0.10 -all`）に登録している。
- **rspamd は既定で RFC1918 の内部ネットワークからのメールを「自分の送信＝outbound」と
  みなして受信認証をスキップする**。ラボの `172.30.0.0/24` はこれに該当するため、
  `rspamd/local.d/options.inc` で `local_addrs` を loopback だけに絞り、送信元を「外部」
  として扱わせている。
- 判定を SPF/DKIM/DMARC だけに集中させるため、外部 RBL 参照や HELO 系ヒューリスティック
  （`rbl` / `hfilter`）は無効化している。
- DMARC 失敗メールの振り分けは、Dovecot の Sieve が `Authentication-Results` の
  `dmarc=fail` を見て `Junk` に `fileinto` している（`mail/sieve/dmarc-junk.sieve`）。
- `p=reject` のときだけ SMTP 拒否させるため、rspamd の `force_actions` で
  `DMARC_POLICY_REJECT` が出たらスコアに関係なく reject アクションに固定している
  （`rspamd/local.d/force_actions.conf`）。`p=quarantine` は force しないので、
  これまで通り配送 → Sieve が Junk へ振り分ける。

> [!NOTE]
> `docker compose restart rspamd`（や `dns rspamd`）の直後は、rspamd が TLD/hyperscan を
> 再コンパイルするため 20〜30 秒ほど milter を受け付けられません。この間に送るとメールは
> スキャンされずに素通り配送されてしまいます。ポリシー変更後は少し待ってから送ってください。
> `docker compose exec mail bash -c '(exec 3<>/dev/tcp/172.30.0.11/11332)' && echo READY`
> が `READY` を返せば準備完了です。

> [!WARNING]
> このラボは学習目的で、閉じたネットワーク内でのみ動かす前提の設定になっています。
> TLS 無効・平文パスワード・認証なしの Web UI など、そのまま外部公開してはいけません。
