#!/bin/bash

sudo mn --topo=single,6 --mac --controller=remote,ip=127.0.0.1
# sudo ovs-vsctl set bridge s1 protocols=OpenFlow13
# docker run -ti -p 6633:6633 hsrnetwork/ryu bash
# ryu-manager --verbose ryu/app/simple_switch_13.py
