#!/usr/bin/env bash
# ラボの DKIM デモ鍵を作り直すスクリプト。
# 既にコミット済みの鍵があるので通常は実行不要。作り直したら、出力される TXT
# レコードを ../dns/zones/mydomain.example.db の selector1._domainkey に貼り直すこと。
set -euo pipefail
cd "$(dirname "$0")"

BITS="${1:-1024}"   # 1024bit だと TXT が 255 文字に収まる

openssl genrsa -out dkim.private "$BITS"
openssl rsa -in dkim.private -pubout -out dkim.public

PUBKEY=$(grep -v -- '-----' dkim.public | tr -d '\n')
echo "v=DKIM1; k=rsa; p=${PUBKEY}" > dkim.txt

echo
echo "selector1._domainkey.mydomain.example に登録する TXT レコード:"
echo
cat dkim.txt
