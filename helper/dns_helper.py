import socket


def find_host(hostname):
    ip = socket.gethostbyname(hostname)
    return ip


def handle_hostname(target):
    return find_host(target)


def translate_target(target):
    if ':' not in target:
        ip = find_host(target)
        port = 80
    else:
        ip = target.split(':')[0]
        port = int(target.split(':')[1])

    return (ip, port)
