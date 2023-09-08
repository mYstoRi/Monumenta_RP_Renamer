import shutil

# renamer

class renamer:

    def __init__(self, logpath):
        self.renamer_initialize()
        self.log_path = logpath

    def renamer_initialize(self):
        self.buffer = {}

    def print_rename(self, path1, path2):  # trust, it's worth a function.

        if path1 in self.buffer:
            temp = ".".join(path1.split('.')[:-1]) + "_temp." + path1.split('.')[-1]
            shutil.copyfile(path1, temp)
            self.buffer[temp] = path2
        else:
            self.buffer[path1] = path2

    def rename(self, settings):

        if settings.options[2].get():
            log = open(settings.log_path, 'a')

        rename_keys = list(self.buffer.keys())
        if len(rename_keys) != 0 and settings.options[2].get():
            log.write("----\n")

        for i in range(len(rename_keys)):
            path1 = rename_keys[i]
            path2 = self.buffer[path1]

            # prevent conflict
            if path2 in self.buffer:
                temp = ".".join(path2.split('.')[:-1]) + "_temp." + path2.split('.')[-1]
                shutil.move(path2, temp)
                self.buffer[temp] = self.buffer[path2]
                del self.buffer[path2]
                rename_keys[rename_keys.index(path2)] = temp

            shutil.move(path1, path2)
            del self.buffer[path1]
            if settings.options[2].get():
                log.write("- rename " + "/".join(path1.split('/')[-2:]) + " to " + "/".join(path2.split('/')[-2:]) + "\n")

        if settings.options[2].get():
            log.close()

        self.renamer_initialize()