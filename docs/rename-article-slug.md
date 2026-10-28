# 記事のスラッグ（ファイル名）を変更する手順

例として `00000000-git-iroiro-ignore` を `20261028-git-iroiro-ignore` に変えたときの手順。

## 変更が必要な場所

1. `articles/<slug>.md` 本体のファイル名
2. `images/<slug>/` 画像ディレクトリ名
3. `images/<slug>/<slug>_YYYYMMDD_HHMMSS.drawio.png` のような、ファイル名の頭にスラッグが付いた画像
4. 記事中の画像パス `![](/images/<slug>/...)`
5. （同期済みなら）`qiita/public/` 側の対応ファイル

## コマンド

```bash
OLD=00000000-git-iroiro-ignore
NEW=20261028-git-iroiro-ignore

# 記事本体（git 管理下なら git mv で履歴をつなぐ）
git mv articles/$OLD.md articles/$NEW.md

# 画像ディレクトリと、その中のファイル名の接頭辞
# （画像が未コミットなら mv、コミット済みなら git mv）
mv images/$OLD images/$NEW
for f in images/$NEW/$OLD*; do
  mv "$f" "images/$NEW/$(basename "$f" | sed "s/^$OLD/$NEW/")"
done

# 記事中の参照を置換
sed -i "s/$OLD/$NEW/g" articles/$NEW.md

# 取りこぼし確認（何も出なければ OK）
grep -rn "$OLD" --exclude-dir=node_modules --exclude-dir=.git .

# 画像リンク切れ確認（何も出なければ OK）
for p in $(grep -o "/images/$NEW/[^)]*" articles/$NEW.md); do test -f ".$p" || echo "MISSING $p"; done
```

最後に `npx zenn preview` で画像が表示されるか見ておく。

## 注意

スラッグは 12〜50 文字で、使えるのは `a-z0-9`、ハイフン、アンダースコアだけ。

スラッグは Zenn の記事 URL そのものなので、公開済み（`published: true` で push 済み）の記事でやると別記事扱いになり、旧 URL の記事は Zenn 上に残る。いいねやコメントも引き継がれない。リネームは公開前にやるのが無難。

Qiita に同期済みの記事も、ファイル名が変わると新規記事として投稿される可能性があるので、`qiita/public/` 側に対応ファイルがあるかを先に確認する。
