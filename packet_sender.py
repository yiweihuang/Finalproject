import json

from webob import Response
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.topology.api import get_switch
from ryu.app.wsgi import ControllerBase, WSGIApplication, route

from helper import ofp_helper, pkt_helper

packet_sender_instance_name = 'packet_sender_api_app'


class PacketSender(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(PacketSender, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(PacketSenderController,
                      {packet_sender_instance_name: self})
        self.topology_api_app = self

    def send_syn_flood(self, amount):
        syn_pkt = pkt_helper.build_syn_packet()
        print syn_pkt
        switch_list = get_switch(self.topology_api_app, None)

        for switch in switch_list:
            datapath = switch.dp
            print datapath
            for i in range(0, amount, 1):
                ofp_helper.send_packet(datapath, syn_pkt, 1)

    def hello_app(self):
        return 'hello app'


class PacketSenderController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(PacketSenderController, self).__init__(req,
                                                     link, data, **config)
        self.packet_sender_spp = data[packet_sender_instance_name]

    @route('hello', '/hello', methods=['GET'])
    def send_hello(self, req, **kwargs):
        packet_sender = self.packet_sender_spp
        msg = packet_sender.hello_app()
        dic = {'messages': str(msg)}
        body = json.dumps(dic)
        return Response(status=200, content_type='application/json', body=body)

    @route('send', '/send', methods=['GET'])
    def send_pkt(self, req, **kwargs):
        packet_sender = self.packet_sender_spp
        try:
            packet_sender.send_syn_flood(10)
        except:
            return Response(status=400)

        return Response(status=201)
