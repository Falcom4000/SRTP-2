import ujson


def load_from_json_file(filename: str) -> dict:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                dic = ujson.load(file)
            except ValueError:
                dic = {}
    except IOError:
        dic = {}
    return dic


def register(filename, key: str, value):
    dic = load_from_json_file(filename + '.json')
    with open(filename + '.json', 'w', encoding='utf-8') as file:
        temp = []
        try:
            temp.append(dic[key])
        except:
            pass
        temp.append(value)
        dic[key]=temp
        ujson.dump(dic, file, ensure_ascii=False, escape_forward_slashes=False)

def write_voice(filename, dir_name, res_str):
    logid = dir_name
    results = load_from_json_file(filename + '.json')
    results[logid][1]['voice'].extend(res_str)
    with open(filename + '.json', 'w', encoding='utf-8') as file:
        ujson.dump(results, file, ensure_ascii=False, escape_forward_slashes=False)

def read(filename, key: str):
    dic = load_from_json_file(filename + '.json')
    if key in dic:
        return dic[key]
    else:
        return None
