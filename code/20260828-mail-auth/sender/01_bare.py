"""
SPF も DKIM も DMARC も一切使わずに送る
"""
import smtplib

from common import SMTP_HOST, SMTP_PORT, TO_ADDR, build_message

msg = build_message()

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
    smtp.set_debuglevel(1)
    smtp.send_message(
        msg,
        from_addr="info@super-ultra-mega-bank.example",
        to_addrs=[TO_ADDR],
    )

print("送信しました")
