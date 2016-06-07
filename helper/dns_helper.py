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
        ip = target.split(':')[1]
        port = int(target.split(':')[0])

    return (ip, port)
