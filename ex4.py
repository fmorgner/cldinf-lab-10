from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3 as proto
from ryu.ofproto import ofproto_v1_3_parser as parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ether_types
import re

class Exercise4(app_manager.RyuApp):
    OFP_VERSIONS = [proto.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Exercise4, self).__init__(*args, **kwargs)

        self.mac_tab = {}

        validIpAddressRegex = "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
        pattern = "^" + validIpAddressRegex + "," + validIpAddressRegex + "$"

        f = open("rules.csv", "r")
        lines = f.read().split("\n")

        self._rules = [ ]

        for line in lines:
            line = re.sub('[\s+]', '', line)
            if line != "":
                if re.match(pattern, line):
                    self._rules.append(tuple(line.split(',')))
                else:
                    print "Line: '" + line + "' is not valid"

    def send_flow(self, path, prio, mtch, acts, buid=None):
        cmd = [parser.OFPInstructionActions(proto.OFPIT_APPLY_ACTIONS, acts)]

        if buid:
            mod = parser.OFPFlowMod(datapath=path, priority=prio, match=mtch,
                                    instructions=cmd, buffer_id=buid)
        else:
            mod = parser.OFPFlowMod(datapath=path, priority=prio, match=mtch,
                                    instructions=cmd)
        path.send_msg(mod)

    def install_rule(self, path, rule):
        act = [parser.OFPActionOutput(proto.OFPP_NORMAL, 0)]

        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=1,
                                ipv4_src=rule[0], ipv4_dst=rule[1])
        self.logger.debug("installing rule: %s", match)
        self.send_flow(path, 100, match, act)

    def get_port(self, mac, pid):
        if mac in self.mac_tab[pid]:
            return self.mac_tab[pid][mac]
        else:
            return proto.OFPP_FLOOD

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def setup(self, event):
        path = event.msg.datapath
        mtch = parser.OFPMatch()
        self.send_flow(path, 0, mtch, [])

        mtch = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP)
        acts = [parser.OFPActionOutput(proto.OFPP_CONTROLLER,
                                       proto.OFPCML_NO_BUFFER)]
        self.send_flow(path, 10, mtch, acts)

        for rule in self._rules:
            self.install_rule(path, rule)
            self.install_rule(path, rule[::-1])

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, event):
        msg = event.msg
        path = msg.datapath
        inpt = msg.match['in_port']

        pckt = packet.Packet(msg.data)
        eth = pckt.get_protocols(ethernet.ethernet)[0]
        arpp = pckt.get_protocols(arp.arp)[0]

        acts = [parser.OFPActionOutput(inpt)]
        mtch = parser.OFPMatch(in_port=inpt, ipv4_dst=arpp.src_ip, ip_proto=0, eth_type=ether_types.ETH_TYPE_IP)
        self.send_flow(path, 1, mtch, acts)

        dest = eth.dst
        sorc = eth.src

        dpid = path.id
        self.mac_tab.setdefault(dpid, {})
        self.mac_tab[dpid][sorc] = inpt

        outp = self.get_port(dest, dpid)
        acts = [parser.OFPActionOutput(outp)]

        if outp != proto.OFPP_FLOOD:
            mtch = parser.OFPMatch(in_port=outp, eth_dst=dest)
            self.send_flow(path, 1, mtch, acts)

        data = None
        if msg.buffer_id == proto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=path, buffer_id=msg.buffer_id,
                                  in_port=inpt, actions=acts, data=data)
        path.send_msg(out)
