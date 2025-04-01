import util
import api

class item:
    def __init__(self):

        # only contains things that should be always specified here.
        self.properties = {
            'type': '',
            'items': '',
            'model': {},
            'texture': {},
            'nbt.plain.display.Name': '',
            'weight': 0,
        }
        self.cwd = ''
        self.region = ''
        self.location = ''
        self.tier = ''

    def write_properties(self, prefix='', suffix=''):
        if self.cwd == '':
            raise ValueError(f'{self.__name__}\'s cwd is not specified!')
        filename = prefix + util.reduce(self.properties['nbt.plain.display.Name']) + suffix + '.properties'
        with open(f'{self.cwd}/{filename}', 'w') as f:
            for p in self.properties:
                v = self.properties[p]
                if type(v) == str:
                    f.write(f'{p}={v}\n')
                elif type(v) == dict: # assumes only 1 layer deep
                    for p_sub in v:
                        f.write(f'{p}.{p_sub}={v}\n')

    def update_from_api(self):
        self.region = api.data[self.properties['nbt.plain.display.Name']]['region']
        self.location = api.data[self.properties['nbt.plain.display.Name']]['location']
        self.tier = api.data[self.properties['nbt.plain.display.Name']]['tier']

