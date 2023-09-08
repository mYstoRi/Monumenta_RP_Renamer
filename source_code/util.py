def reduce(name):
    # convert name into compatible format
    output = ""
    for c in name:
        if c.isalpha() or c.isnumeric():
            output += c.lower()
        elif (c == ' ' or c == '-') and output[-1] != '_':
            output += '_'
        elif c == 'é':
            output += 'e'
    return output


def parse_prop(path):
    prop = {}
    with open(path, 'r') as p:
        done = False
        while not done:
            content = p.readline().split('\n')[0].split('=')
            if len(content) > 1:
                prop[content[0]] = content[1]
            else:
                done = True

    return prop


def pathsimplify(path):
    output = ""
    p = ''
    for c in path:
        if c not in ['/', '\\']:
            output += c
        elif c == '\\' and output[-1] != '\\':
            output += '/'
        if p == '.' and c == '.':
            output = "/".join(output.split('/')[:-2])
    return output


def pathjoin(path1, path2):
    if path1.endswith('/'):
        path1 = path1[:-1]
    if path2.startswith('/'):
        path2 = path1[1:]
    if ".." in path2:
        return "/".join(path1.split('/'))
    else:
        return path1 + '/' + path2