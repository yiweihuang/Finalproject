from ryu.ofproto import ether, inet
from ryu.lib.packet import ethernet, ipv4, tcp, packet


def build_syn_packet():
    print 'build pkt'
    e = ethernet.ethernet(dst='ff:ff:ff:ff:ff:ff',
                          src='00:1e:68:bb:b5:2e',
                          ethertype=ether.ETH_TYPE_IP)
    i = ipv4.ipv4(dst='140.114.71.177',
                  src='192.168.11.21',
                  proto=inet.IPPROTO_TCP)
    t = tcp.tcp(src_port=5566,
                dst_port=9292,
                bits=tcp.TCP_SYN)

    p = packet.Packet()
    p.add_protocol(e)
    p.add_protocol(i)
    p.add_protocol(t)
    p.serialize()
    print repr(p)
    return p
