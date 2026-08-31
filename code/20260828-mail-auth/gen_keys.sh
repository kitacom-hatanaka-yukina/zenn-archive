#!/usr/bin/env bash
# DKIM 用の鍵ペアを生成する
set -euo pipefail
cd "$(dirname "$0")"

BITS="${1:-1024}"

openssl genrsa -out private.key "$BITS"
openssl rsa -in private.key -pubout -out public.key

# ヘッダ行・改行を除いた公開鍵本体を 1 行に連結する
PUBKEY=$(grep -v -- '-----' public.key | tr -d '\n')
RECORD="v=DKIM1; k=rsa; p=${PUBKEY}"

echo
echo "DNS に登録する TXT レコード（selector1._domainkey.<自分のドメイン>）:"
echo

if [ "${#RECORD}" -le 255 ]; then
  echo "$RECORD"
else
  # 255 文字超 → 255 文字ごとに区切って複数文字列で出力する
  echo "（255 文字を超えるため複数文字列に分割。プロバイダの UI がスペース区切りの \"...\" \"...\" に対応している必要があります）"
  echo
  printf '%s' "$RECORD" | fold -w 255 | sed 's/^/"/; s/$/"/' | tr '\n' ' '
  echo
fi
