from ryu.base import app_manager
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
import json
import time
from scapy.all import *
import random

from route import urls
from helper import file_helper, dns_helper

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


class PacketSender(app_manager.RyuApp):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(PacketSender, self).__init__(*args, **kwargs)
        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(PacketSenderController,
                      {packet_sender_instance_name: self})

    # Hostname
    def send_time_hostname(self):
        total = 0
        json_data = file_helper.read_file('target.json')

        ip = json_data['ip']
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

    def send_count_hostname(self):
        total = 0
        json_data = file_helper.read_file('target.json')

        ip = json_data['ip']
        port = json_data['port']
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

        ip = json_data['ip']
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

    def send_count_ip(self):
        total = 0
        json_data = file_helper.read_file('target.json')

        ip = json_data['ip']
        port = json_data['port']
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
        try:
            packet_sender = self.packet_sender_spp
            req = json.loads(req.body)

            ip, port = dns_helper.translate_target(req['target'])
            info = file_helper.info_builder(ip, port, req['count'])
            file_helper.store_file(info, 'target.json')

            packet_sender.send_time_hostname()
        except:
            return Response(status=500)

    @route('packet_sender', urls.hostname_count, methods=['POST'])
    def hn_sendpacket_bycount(self, req, **kwargs):
        try:
            packet_sender = self.packet_sender_spp
            req = json.loads(req.body)

            ip, port = dns_helper.translate_target(req['target'])
            info = file_helper.info_builder(ip, port, req['count'])
            file_helper.store_file(info, 'target.json')

            packet_sender.send_count_hostname()
        except:
            return Response(status=500)

    # IP address
    @route('packet_sender', urls.ip_time, methods=['POST'])
    def ip_sendpacket_bytime(self, req, **kwargs):
        try:
            packet_sender = self.packet_sender_spp
            req = json.loads(req.body)

            ip, port = dns_helper.translate_target(req['target'])
            info = file_helper.info_builder(ip, port, req['count'])
            file_helper.store_file(info, 'target.json')

            packet_sender.send_time_ip()
        except:
            return Response(status=500)

    @route('packet_sender', urls.ip_count, methods=['POST'])
    def ip_sendpacket_bycount(self, req, **kwargs):
        try:
            packet_sender = self.packet_sender_spp
            req = json.loads(req.body)

            ip, port = dns_helper.translate_target(req['target'])
            info = file_helper.info_builder(ip, port, req['count'])
            file_helper.store_file(info, 'target.json')

            packet_sender.send_count_ip()
        except:
            return Response(status=500)
