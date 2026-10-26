# Postfix から milter として接続される（自分でスキャンする self-scan モード）
milter = yes;
timeout = 120s;
upstream "local" {
  default = yes;
  self_scan = yes;
}
bind_socket = "*:11332";
