"""
ヘルパー（送信スクリプト共通）。

設定値は docker compose の environment（sender サービス）から渡される。
"""
import os
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr


# 送信先（ラボ内の被害者メールボックス）
TO_ADDR = os.environ.get("MAIL_TO", "me@inbox.example")

# ヘッダ From に詐称するドメイン（存在しない架空ドメイン）
SPOOF_FROM = os.environ.get(
    "MAIL_SPOOF_FROM",
    "スーパーウルトラメガ銀行 <info@super-ultra-mega-bank.example>",
)

# 攻撃者が管理する正規ドメイン
MY_DOMAIN = os.environ.get("MAIL_MY_DOMAIN", "mydomain.example")

# エンベロープ From に使う自分の管理ドメインのアドレス
BOUNCE_ADDR = os.environ.get("MAIL_BOUNCE_ADDR", f"bounce@{MY_DOMAIN}")

# 送信先の受信サーバ（ラボの mail コンテナ）
SMTP_HOST = os.environ.get("MAIL_SMTP_HOST", "mail")
SMTP_PORT = int(os.environ.get("MAIL_SMTP_PORT", "25"))

# DKIM 用
DKIM_SELECTOR = os.environ.get("MAIL_DKIM_SELECTOR", "selector1")
DKIM_PRIVATE_KEY = os.environ.get("MAIL_DKIM_PRIVATE_KEY", "/keys/dkim.private")


def build_message() -> EmailMessage:
    """銀行を騙るなりすましメールを組み立てる"""
    msg = EmailMessage()
    msg["From"] = SPOOF_FROM  # ヘッダ From を詐称
    msg["To"] = TO_ADDR
    msg["Subject"] = "スーパーウルトラメガ銀行からの大事なお知らせ"
    msg["Date"] = formatdate(localtime=True)
    from_domain = parseaddr(SPOOF_FROM)[1].split("@")[-1] or "localhost"
    msg["Message-ID"] = make_msgid(domain=from_domain)
    msg.set_content("1000億円を今すぐゲット！ https://www.kitacom.co.jp/")
    return msg
