#!/bin/bash

function new_rule {
  src=$1
  dst=$2
  curl -X POST -d"{\"nw_src\": \"$1/32\", \"nw_dst\": \"$2/32\"}" http://localhost:8080/firewall/rules/0000000000000001
}

curl -X PUT http://localhost:8080/firewall/module/enable/0000000000000001
curl http://localhost:8080/firewall/module/status
curl -X DELETE -d '{"rule_id": "all"}' http://localhost:8080/firewall/rules/0000000000000001

new_rule 10.0.0.1 10.0.0.2
new_rule 10.0.0.1 10.0.0.3
new_rule 10.0.0.1 10.0.0.4

new_rule 10.0.0.2 10.0.0.1
new_rule 10.0.0.2 10.0.0.3
new_rule 10.0.0.2 10.0.0.4

new_rule 10.0.0.3 10.0.0.1
new_rule 10.0.0.3 10.0.0.2
new_rule 10.0.0.3 10.0.0.4
new_rule 10.0.0.3 10.0.0.5
new_rule 10.0.0.3 10.0.0.6

new_rule 10.0.0.4 10.0.0.1
new_rule 10.0.0.4 10.0.0.2
new_rule 10.0.0.4 10.0.0.3
new_rule 10.0.0.4 10.0.0.5
new_rule 10.0.0.4 10.0.0.6

new_rule 10.0.0.5 10.0.0.3
new_rule 10.0.0.5 10.0.0.4
new_rule 10.0.0.5 10.0.0.6

new_rule 10.0.0.6 10.0.0.3
new_rule 10.0.0.6 10.0.0.4
new_rule 10.0.0.6 10.0.0.5

curl http://localhost:8080/firewall/rules/0000000000000001
