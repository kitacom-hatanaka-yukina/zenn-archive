# なりすましメール実験環境

記事「なりすましメールはなぜ防げるのか — SPF / DKIM / DMARC を手を動かして理解する」
（[../../articles/20260828-mail-auth.md](../../articles/20260828-mail-auth.md)）に登場するスクリプトの実行環境です。

SPF / DKIM / DMARC がなりすましをどう扱うかを、実際に送って確認します。

> [!WARNING]
> この実験は **存在しない架空ドメインから自分宛にのみ** 送るためのものです。
> 他人を騙って第三者に送る用途には絶対に使わないでください。
> ポート 25 での直接送信を禁止しているネットワーク / プロバイダも多くあります。

## 構成

| ファイル | 記事の対応セクション | 内容 |
| --- | --- | --- |
| `01_bare.py` | まるごし | SPF/DKIM/DMARC なし。エンベロープ From もヘッダ From も詐称 |
| `02_spf.py` | SPF | エンベロープ From だけを自分の管理ドメインに変えて SPF を通す |
| `03_dkim.py` | DKIM | さらに秘密鍵で DKIM 署名を付ける |
| `common.py` | — | 共通のメッセージ組み立てと設定 |
| `gen_keys.sh` | DKIM | DKIM 用の鍵ペア生成と DNS レコード表示 |

DMARC セクションはスクリプトではなく、上記の結果（アラインメント不一致）の解説です。

## セットアップ

依存の管理・実行には [uv](https://docs.astral.sh/uv/) を使います。

```bash
cd code/20260828-mail-auth

uv sync                # pyproject.toml から仮想環境を作成し dkimpy を導入
cp .env.example .env   # 自分の送信先・ドメインに書き換える
```

### 事前準備（DNS）

`02_spf.py` / `03_dkim.py` を実際に pass させるには、自分が管理するドメインに DNS レコードが必要です。

SPF レコード（送信端末のグローバル IP を登録）:

```text
mydomain.example. IN TXT "v=spf1 ip4:203.0.113.10 -all"
```

DKIM は鍵を生成して公開鍵を登録します:

```bash
./gen_keys.sh          # private.key / public.key を生成し、登録用 TXT レコードを表示
```

```text
selector1._domainkey.mydomain.example. IN TXT "v=DKIM1; k=rsa; p=<public.key の中身>"
```

## 実行

```bash
set -a; source .env; set +a      # .env を環境変数として読み込む

uv run 01_bare.py
uv run 02_spf.py
uv run 03_dkim.py
```

送信後、受信メールの原文（Gmail なら「メッセージのソースを表示」）で
`Authentication-Results` ヘッダの `spf` / `dkim` / `dmarc` の判定を確認します。
