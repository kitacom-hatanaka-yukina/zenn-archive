"""
ヘルパー
"""
import os
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr
from pathlib import Path


def _load_dotenv() -> None:
    """
    .env を読み込む
    """
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

# 送信先
TO_ADDR = os.environ.get("MAIL_TO", "hatanaka_yukina@kita-com.com")

# ヘッダ From に詐称するドメイン（存在しない架空ドメイン）
SPOOF_FROM = os.environ.get(
    "MAIL_SPOOF_FROM",
    "スーパーウルトラメガ銀行 <info@super-ultra-mega-bank.example>",
)

# 自分が管理する正規ドメイン
MY_DOMAIN = os.environ.get("MAIL_MY_DOMAIN", "mydomain.example")

# エンベロープ From に使う自分の管理ドメインのアドレス
BOUNCE_ADDR = os.environ.get("MAIL_BOUNCE_ADDR", f"bounce@{MY_DOMAIN}")

# 送信先ドメインの受信サーバ
SMTP_HOST = os.environ.get("MAIL_SMTP_HOST", "gmail-smtp-in.l.google.com")
SMTP_PORT = int(os.environ.get("MAIL_SMTP_PORT", "25"))

# DKIM 用
DKIM_SELECTOR = os.environ.get("MAIL_DKIM_SELECTOR", "selector1")
DKIM_PRIVATE_KEY = os.environ.get("MAIL_DKIM_PRIVATE_KEY", "private.key")


def build_message() -> EmailMessage:
    """銀行を騙るなりすましメールを組み立てる"""
    msg = EmailMessage()
    msg["From"] = SPOOF_FROM # ヘッダ From を詐称
    msg["To"] = TO_ADDR
    msg["Subject"] = "スーパーウルトラメガ銀行からの大事なお知らせ"
    msg["Date"] = formatdate(localtime=True)
    from_domain = parseaddr(SPOOF_FROM)[1].split("@")[-1] or "localhost"
    msg["Message-ID"] = make_msgid(domain=from_domain)
    msg.set_content("1000億円を今すぐゲット！ https://www.kitacom.co.jp/")
    return msg
