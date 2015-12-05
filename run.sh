#!/bin/bash

sudo mn --topo=single,6 --mac --controller=remote,ip=127.0.0.1
# sudo ovs-vsctl set bridge s1 protocols=OpenFlow13
# docker run -ti -p 6633:6633 hsrnetwork/ryu bash
# ryu-manager --verbose ryu/app/ex1.py
# ryu-manager --verbose ryu/app/ex2.py
# ryu-manager --verbose ryu/app/ex3.py
# ryu-manager --verbose ryu/app/ex4.py
