import json


def store_file(info, filename):
    path = '../config/' + filename
    with open(path, 'w') as f:
        f.write(json.dumps(info))
    f.close()


def read_file(filename):
    path = '../config/' + filename
    with open(path, 'r') as f:
        data = json.load(f)

    return data
