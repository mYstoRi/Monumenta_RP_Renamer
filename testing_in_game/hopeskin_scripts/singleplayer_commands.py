import pandas as pd
from os.path import join

from datapack_utils import create_empty_datapack, mkdir_and_cd

def generate(fn_name, df, is_alch_bag=False):
    with open(join(root, f'{fn_name}.mcfunction'), 'w') as fn:
        for idx, item in df.iterrows():
            # generate items in chests (every 27 items)
            if idx % 27 == 0:
                if idx != 0:
                    wrap += ']}}\n'
                    fn.write(wrap)
                wrap = 'give @s chest{BlockEntityTag:{Items:['

            # item code
            try:
                base = item['Base Item Type'][10:]
                if is_alch_bag:
                    plain_text = 'Alchemist Utensil'
                else:
                    plain_text = item['Base Item Name']
                plain_text_no_prime = plain_text.replace('\'', '\\\'')
                uuid = item['Skin Owner\'s UUID']
                owner = item['Skin Owner\'s Name']
                line = ('{Slot:' + str(idx % 27) + ', id:' + base + ', Count:1, tag:{'
                            'plain:{display:{Name:\"' + plain_text + '\"}},'
                            'Monumenta:{PlayerModified:{Infusions:{Hope:{Infuser:' + uuid + '}}}},'
                            'display:{'
                                'Name: \'["' + plain_text_no_prime + '"]\','
                                'Lore:[\'[\"Hoped by ' + owner + '\"]\']'
                            '}'
                        '}}')
                wrap += line
                if idx % 27 != 26:
                    wrap += ','
            except:
                wrap += ']}}\n'
                fn.write(wrap)
                break

if __name__ == '__main__':

    # settings
    root = 'output'
    pack_name = 'RP-Single-Player-Toolbox'
    namespace = 'hope'

    # load from csv
    r1_skins = pd.read_csv('Hope Skin List - King\'s Valley.csv')
    r2_skins = pd.read_csv('Hope Skin List - Celsian Isles.csv')
    r3_skins = pd.read_csv('Hope Skin List - Architect\'s Ring.csv')
    alch_bag_skins = pd.read_csv('Hope Skin List - Alchemist Bags.csv')

    print(r1_skins['Base Item Type'])

    # go to directory
    create_empty_datapack(root, pack_name, namespace)
    root = join(root, pack_name, 'data', namespace, 'functions')

    # generate mcfunction
    generate('get_r1', r1_skins)
    generate('get_r2', r2_skins)
    generate('get_r3', r3_skins)
    generate('get_alch_bags', alch_bag_skins, is_alch_bag=True)
