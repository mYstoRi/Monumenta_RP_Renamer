## This script is for fetching data in the RP
## for the purpose of API related stuff like OTM

## The result would not be a RP, but rather as a
## assets folder sort of thing.

import os
import api

if __name__ == '__main__':
    root = 'output/test'
    # scan the rp for every folder to see properties of matching icons
    for dir_path, dir_names, filenames in os.walk(root):

        prop_list = []
        for filename in filenames:
            if filename.endswith('.properties'):
                prop_list.append(filename)

        if len(prop_list) > 0:

            for prop in prop_list:
                # get properties content
                with open(f'{dir_path}/{prop_list}', 'r') as p:
                    text = [p.readline().split('\n')[0]]
                    while text[-1] != "":
                        text.append(p.readline().split('\n')[0])
                text = text[:-1]
                for line in text:
                    feature = line.split('=')
                    if feature[0] == 'nbt.plain.display.Name':
                        pass ## TODO


