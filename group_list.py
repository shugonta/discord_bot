import json


def load_json(filename):
    try:
        f = open(filename, 'r')
        data = json.load(f)
        print(data)
        f.close()
        return data
    except:
        return []


def write_json(filename, data):
    f = open(filename, 'w')
    json.dump(data, f)
    print(json.dumps(data))
    f.close()
