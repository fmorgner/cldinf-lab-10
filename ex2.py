from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features(self, ev):
        dpth = ev.msg.datapath
        pars = dpth.ofproto_parser
        mtch = pars.OFPMatch()
        acts = [pars.OFPActionOutput(dpth.ofproto.OFPP_FLOOD)]
        inst = [pars.OFPInstructionActions(dpth.ofproto.OFPIT_APPLY_ACTIONS,
                                           acts)]
        modi = pars.OFPFlowMod(datapath=dpth, priority=0, match=mtch,
                               instructions=inst)
        dpth.send_msg(modi)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg = ev.msg
        dpth = msg.datapath
        pars = dpth.ofproto_parser
        inpt = msg.match['in_port']

        acts = [pars.OFPActionOutput(dpth.ofproto.OFPP_FLOOD)]

        data = None
        if msg.buffer_id == dpth.ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=dpth, buffer_id=msg.buffer_id,
                                  inpt=msg.match['in_port'], actions=acts, data=data)
        dpth.send_msg(out)
