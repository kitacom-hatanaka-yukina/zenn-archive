# DMARC 判定に失敗したメールを迷惑メール(Junk)フォルダへ振り分ける。
# rspamd が付与する Authentication-Results ヘッダの dmarc=fail を見て判定する。
require ["fileinto", "mailbox"];

if header :contains "Authentication-Results" "dmarc=fail" {
    fileinto :create "Junk";
    stop;
}
