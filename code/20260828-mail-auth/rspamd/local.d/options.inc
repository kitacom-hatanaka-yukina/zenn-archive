# SPF/DKIM/DMARC のレコードを引く権威 DNS(CoreDNS)を明示する
dns {
  nameserver = ["172.30.0.53"];
}

# 重要: ラボのネットワーク 172.30.0.0/24 は RFC1918(172.16.0.0/12) に含まれるため、
# 既定では rspamd が「自分の送信網＝outbound」とみなして SPF/DKIM/DMARC 検査を
# スキップしてしまう。ローカル扱いを loopback だけに絞り、送信元を「外部」として
# 受信検査させる。
local_addrs = "127.0.0.0/8, ::1";
