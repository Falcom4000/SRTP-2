import ujson


def write(qqnum, key: str, value):
    with open(str(qqnum) + '.json', 'r', encoding='utf-8') as file:
        try:
            dic = ujson.load(file)
        except ValueError:
            dic = {}

    with open(str(qqnum) + '.json', 'w', encoding='utf-8') as file:
        dic[key] = value
        ujson.dump(dic, file, ensure_ascii=False, escape_forward_slashes=False)


def read(qqnum: int, key: str):
    try:
        with open(str(qqnum) + '.json', 'r', encoding='utf-8') as file:
            dic = ujson.load(file)
            if key in dic:
                return dic[key]
            else:
                return None
    except IOError:
        return None
