import os
from util import *

class bow:
    def __init__(self, path):

        self.non_replica = False
        self.replica = False

        for file in os.listdir(path):
            seg = file.split('.')

            if seg[-1] == "properties":
                # read properties
                prop = parse_prop(path + "/" + file)

                ## we already know base item
                self.base = "bow"

                ## plain text
                if prop["nbt.plain.display.Name"].startswith("Replica "):
                    self.replica = True
                    self.Name = prop["nbt.plain.display.Name"][8:]
                    self.reduced_name = reduce(self.Name)
                else:
                    self.non_replica = True
                    self.Name = prop["nbt.plain.display.Name"]
                    self.reduced_name = reduce(self.Name)

                ## model
                try:
                    self.model = prop["model"]
                except:
                    self.model = "None"

                ## texture
                self.texture = ["", "", "", "", "", ""]  # bow, pulling 0-4
                self.texture[0] = prop["texture"]
                self.texture[1] = prop["texture.bow_pulling_0"]
                self.texture[2] = prop["texture.bow_pulling_1"]
                self.texture[3] = prop["texture.bow_pulling_2"]
                self.texture[4] = prop["texture.bow_pulling_3"]
                self.texture[5] = prop["texture.bow_pulling_4"]

                self.pull_mapping = [0] * 5
                num = 0
                for i in range(5):
                    dupe = False
                    for j in range(i):
                        if self.texture[j] == self.texture[i]:
                            dupe = True
                            self.pull_mapping[i] = self.pull_mapping[j]
                    if i != 0 and not dupe:
                        num += 1
                        self.pull_mapping[i] = num
                self.pull_count = num + 1

                ## weight
                try:
                    self.weight = prop["weight"]
                except:
                    pass

                ## record properties location
                if "replica_" in seg[0]:
                    self.rep_properties = path + "/" + file

                else:
                    self.properties = path + "/" + file

        self.has_e = [False, False, False, False, False, False]
        self.anim = [False, False, False, False, False, False]
        self.e_anim = [False, False, False, False, False, False]

        for i in range(6):
            if self.texture[i] + "_e.png" in os.listdir(path):
                self.has_e[i] = True
            if self.texture[i] + ".png.mcmeta" in os.listdir(path):
                self.anim[i] = True
            if self.texture[i] + "_e.png.mcmeta" in os.listdir(path):
                self.e_anim[i] = True

    def show(self):

        print("base: " + self.base)
        print("Name: " + self.Name)
        print("model: " + self.model)
        print("texture: ")
        print(self.texture)
        print("----")

    def rename(self, path, renamer):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"

        # rewrite properties & rename

        p = ""

        p += "type=item\n"

        p += "matchItems=bow\n"

        if self.model != "None":
            p += "model=" + self.model + "\n"

        p += "texture=" + self.reduced_name + "\n"

        for i in range(5):
            filename = self.reduced_name + "_pulling_" + str(self.pull_mapping[i]) + "\n"
            p += "texture.bow_pulling_" + str(i) + "=" + filename

        rep_p = p
        p += "nbt.plain.display.Name=" + self.Name + "\n"
        rep_p += "nbt.plain.display.Name=Replica " + self.Name + "\n"

        try:
            p += "weight=" + self.weight
        except:
            pass

        ## non-replica
        if self.non_replica:
            if self.properties != new_properties:  # check if rename is needed
                renamer.print_rename(self.properties, new_properties)

            with open(self.properties, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties != new_rep_properties:  # check if rename is needed
                renamer.print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files
        if self.texture[0] != self.reduced_name:
            renamer.print_rename(path + "/" + self.texture[0] + ".png", new_texture + ".png")

            if self.has_e[0]:
                renamer.print_rename(path + "/" + self.texture[0] + "_e.png", new_texture + "_e.png")

            if self.anim[0]:
                renamer.print_rename(path + "/" + self.texture[0] + ".png.mcmeta", new_texture + ".png.mcmeta")

            if self.e_anim[0]:
                renamer.print_rename(path + "/" + self.texture[0] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        for i in range(self.pull_count):

            ind = self.pull_mapping.index(i) + 1

            if self.texture[ind] != self.reduced_name + "_pulling_" + str(i):

                renamer.print_rename(path + "/" + self.texture[ind] + ".png", new_texture + "_pulling_" + str(i) + ".png")

                if self.has_e[ind]:
                    renamer.print_rename(path + "/" + self.texture[ind] + "_e.png",
                                 new_texture + "_pulling_" + str(i) + "_e.png")

                if self.anim[ind]:
                    renamer.print_rename(path + "/" + self.texture[ind] + ".png.mcmeta",
                                 new_texture + "_pulling_" + str(i) + ".png.mcmeta")

                if self.e_anim[ind]:
                    renamer.print_rename(path + "/" + self.texture[ind] + "_e.png.mcmeta",
                                         new_texture + "_pulling_" + str(i) + "_e.png.mcmeta")
