FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        postfix \
        dovecot-core dovecot-imapd dovecot-lmtpd \
        dovecot-sieve dovecot-managesieved \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 被害者メールボックス用の vmail ユーザ
RUN groupadd -g 5000 vmail \
    && useradd -g vmail -u 5000 -d /var/mail/vhosts -m vmail

COPY dovecot/dovecot.conf /etc/dovecot/dovecot.conf
COPY dovecot/users /etc/dovecot/users
COPY sieve/dmarc-junk.sieve /etc/dovecot/sieve/dmarc-junk.sieve
# グローバル Sieve を事前コンパイル（配送時に vmail が .svbin を書けないため）
RUN sievec /etc/dovecot/sieve/dmarc-junk.sieve
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 25 143
ENTRYPOINT ["/entrypoint.sh"]
