#!/usr/bin/env bash
# Postfix と Dovecot を最小構成で立ち上げる
set -euo pipefail

# ---- Postfix 設定（postconf で必要な項目だけ上書き）----
postconf -e "maillog_file=/dev/stdout"
postconf -e "myhostname=mail.inbox.example"
postconf -e "mydestination="
postconf -e "mynetworks=172.30.0.0/24 127.0.0.0/8"
postconf -e "inet_interfaces=all"
postconf -e "inet_protocols=ipv4"

# 受信ドメインと LMTP(Dovecot) 配送
postconf -e "virtual_mailbox_domains=inbox.example"
postconf -e "virtual_mailbox_maps=hash:/etc/postfix/vmailbox"
postconf -e "virtual_transport=lmtp:unix:private/dovecot-lmtp"

# rspamd を milter として接続（SPF/DKIM/DMARC 判定と Authentication-Results 付与）
postconf -e "smtpd_milters=inet:172.30.0.11:11332"
postconf -e "non_smtpd_milters=inet:172.30.0.11:11332"
postconf -e "milter_default_action=accept"
postconf -e "milter_protocol=6"

# ラボなので TLS/HELO/逆引き等の制限は緩める。中継は自ネットワークのみ許可。
postconf -e "smtpd_helo_required=no"
postconf -e "smtpd_relay_restrictions=permit_mynetworks,reject_unauth_destination"
postconf -e "smtpd_recipient_restrictions=permit_mynetworks,reject_unauth_destination"
postconf -e "disable_vrfy_command=yes"

echo "me@inbox.example OK" > /etc/postfix/vmailbox
postmap /etc/postfix/vmailbox

# ---- メールボックス ----
mkdir -p /var/mail/vhosts/inbox.example
chown -R vmail:vmail /var/mail/vhosts

# ---- 起動 ----
dovecot # Dovecot をデーモンとして起動
exec postfix start-fg # Postfix をフォアグラウンドで起動（PID1）
