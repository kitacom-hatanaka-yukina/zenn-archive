FROM python:3.12-slim
# 既存の送信スクリプトが使う dkimpy を入れる
RUN pip install --no-cache-dir "dkimpy>=1.1.0"
WORKDIR /work
# 送信スクリプトをイメージに同梱する
COPY common.py 01_bare.py 02_spf.py 03_dkim.py /work/
