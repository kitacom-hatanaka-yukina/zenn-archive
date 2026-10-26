"""
DKIM を通す
"""

import smtplib

import dkim
from common import (
    BOUNCE_ADDR,
    DKIM_PRIVATE_KEY,
    DKIM_SELECTOR,
    MY_DOMAIN,
    SMTP_HOST,
    SMTP_PORT,
    TO_ADDR,
    build_message,
)

msg = build_message()

# 秘密鍵で署名
sig = dkim.sign(
    message=msg.as_bytes(),
    selector=DKIM_SELECTOR.encode(),
    domain=MY_DOMAIN.encode(),
    privkey=open(DKIM_PRIVATE_KEY, "rb").read(),
    include_headers=[b"from", b"to", b"subject"],
)
signed = sig + msg.as_bytes()

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.set_debuglevel(1)
    smtp.sendmail(
        from_addr=BOUNCE_ADDR,  # エンベロープ From を自分の管理ドメインに
        to_addrs=[TO_ADDR],
        msg=signed,  # 署名入りのものを埋め込む
    )

print("送信しました")
