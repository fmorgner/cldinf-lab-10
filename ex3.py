from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class Exercise3(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Exercise3, self).__init__(*args, **kwargs)
        self.mac_tab = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        path = ev.msg.datapath
        pars = path.ofproto_parser

        mtch = pars.OFPMatch()
        acts = [pars.OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER,
                                     ofproto_v1_3.OFPCML_NO_BUFFER)]
        self.send_flow(path, 0, mtch, acts)

    def send_flow(self, path, prio, mtch, acts, buid=None):
        pars = path.ofproto_parser
        inst = [pars.OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS,
                                           acts)]

        if buid:
            mod = pars.OFPFlowMod(datapath=path, priority=prio, match=mtch,
                                  instructions=inst, buffer_id=buid)
        else:
            mod = pars.OFPFlowMod(datapath=path, priority=prio, match=mtch,
                                  instructions=inst)
        path.send_msg(mod)

    def get_port(self, mac, pid):
        if mac in self.mac_tab[pid]:
            return self.mac_tab[pid][mac]
        else:
            return ofproto_v1_3.OFPP_FLOOD

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        path = msg.datapath
        pars = path.ofproto_parser
        inpt = msg.match['in_port']

        pckt = packet.Packet(msg.data)
        ethe = pckt.get_protocols(ethernet.ethernet)[0]

        dest = ethe.dst
        sorc = ethe.src

        dpid = path.id

        self.mac_tab.setdefault(dpid, {})
        self.mac_tab[dpid][sorc] = inpt

        outp = self.get_port(dest, dpid)
        acts = [pars.OFPActionOutput(outp)]

        if outp != ofproto_v1_3.OFPP_FLOOD:
            mtch = pars.OFPMatch(in_port=inpt, eth_dst=dest)
            if msg.buffer_id != ofproto_v1_3.OFP_NO_BUFFER:
                self.send_flow(path, 1, mtch, acts, msg.buffer_id)
                return
            else:
                self.send_flow(path, 1, mtch, acts)

        data = None
        if msg.buffer_id == ofproto_v1_3.OFP_NO_BUFFER:
            data = msg.data

        out = pars.OFPPacketOut(datapath=path, buffer_id=msg.buffer_id,
                                in_port=inpt, actions=acts, data=data)
        path.send_msg(out)
