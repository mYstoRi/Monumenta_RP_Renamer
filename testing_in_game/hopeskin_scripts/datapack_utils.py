import os
import json
from os.path import join

empty_pack_meta = {
    'pack':{
        'pack_format': 26,
        'description': 'empty datapack'
    }
}
tick_json = {
        "values": []
}
load_json = {
        "values": []
}

def create_empty_datapack(root: str, pack_name: str, namespace: str):

    # prep jsons
    this_tick_json, this_load_json = tick_json, load_json
    this_tick_json['values'].append(namespace + ':tick')
    this_load_json['values'].append(namespace + ':load')

    # create files
    root = mkdir_and_cd(root, pack_name)
    with open(join(root, 'pack.mcmeta'), 'w') as mcm:
        json.dump(empty_pack_meta, mcm)
    root = mkdir_and_cd(root, 'data')
    root = mkdir_and_cd(root, namespace)
    root = mkdir_and_cd(root, 'functions')
    open(join(root, 'load.mcfunction'), 'a').close()
    open(join(root, 'tick.mcfunction'), 'a').close()
    root = back_one_dir(back_one_dir(root))
    root = mkdir_and_cd(root, 'minecraft')
    root = mkdir_and_cd(root, 'tags')
    root = mkdir_and_cd(root, 'functions')
    with open(join(root, 'load.json'), 'w') as ljs:
        json.dump(this_load_json, ljs)
    with open(join(root, 'tick.json'), 'w') as tjs:
        json.dump(this_tick_json, tjs)


def mkdir_and_cd(root: str, path: str):
    if path not in os.listdir(root):
        os.mkdir(join(root, path))
    return join(root, path)

def back_one_dir(root: str):
    return os.path.normpath(root + os.sep + os.pardir)