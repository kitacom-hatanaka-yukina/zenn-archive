"""
SPF を通す
"""
import smtplib

from common import BOUNCE_ADDR, SMTP_HOST, SMTP_PORT, TO_ADDR, build_message

msg = build_message()

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.set_debuglevel(1)
    smtp.send_message(
        msg,
        from_addr=BOUNCE_ADDR,  # エンベロープ From を自分の管理ドメインに
        to_addrs=[TO_ADDR],
    )

print("送信しました")
