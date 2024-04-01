import os
from util import *

class crossbow:
    def __init__(self, path):

        src = os.listdir(path)
        self.non_replica = False
        self.replica = False

        self.has_e = [False, False, False, False, False, False]
        self.anim = [False, False, False, False, False, False]
        self.e_anim = [False, False, False, False, False, False]

        for file in src:
            seg = file.split('.')

            if seg[-1] == "properties":
                # read properties
                prop = parse_prop(path + "/" + file)

                ## we already know base item
                self.base = "crossbow"

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
                self.texture = ["", "", "", "", "", ""]  # crossbow_standby, pulling 0-2, arrow, firework
                self.texture[0] = prop["texture"]
                self.texture[1] = prop["texture.crossbow_pulling_0"]
                self.texture[2] = prop["texture.crossbow_pulling_1"]
                self.texture[3] = prop["texture.crossbow_pulling_2"]
                self.texture[4] = prop["texture.crossbow_arrow"]
                try:
                    self.texture[5] = prop["texture.crossbow_firework"]
                    if self.texture[5] != self.texture[4]:
                        self.has_fw = True
                    else:
                        self.has_fw = False
                except:
                    self.texture[5] = prop["texture.crossbow_arrow"]
                    self.has_fw = False

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

        for i in range(6):
            if self.texture[i] + "_e.png" in src:
                self.has_e[i] = True
            if self.texture[i] + ".png.mcmeta" in src:
                self.anim[i] = True
            if self.texture[i] + "_e.png.mcmeta" in src:
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

        p += "matchItems=crossbow\n"

        if self.model != "None":
            p += "model=" + self.model + "\n"

        p += "texture=" + self.reduced_name + "\n"

        for i in range(3):
            p += "texture.crossbow_pulling_" + str(i) + "=" + self.reduced_name + "_pulling_" + str(i) + "\n"

        p += "texture.crossbow_arrow=" + self.reduced_name + "_arrow\n"

        if self.has_fw:
            p += "texture.crossbow_firework=" + self.reduced_name + "_firework\n"
        else:
            p += "texture.crossbow_firework=" + self.reduced_name + "_arrow\n"

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

        for i in range(3):

            if self.texture[i + 1] != self.reduced_name + "_pulling_" + str(i):

                renamer.print_rename(path + "/" + self.texture[i + 1] + ".png", new_texture + "_pulling_" + str(i) + ".png")

                if self.has_e[i + 1]:
                    renamer.print_rename(path + "/" + self.texture[i + 1] + "_e.png",
                                 new_texture + "_pulling_" + str(i) + "_e.png")

                if self.anim[i + 1]:
                    renamer.print_rename(path + "/" + self.texture[i + 1] + ".png.mcmeta",
                                 new_texture + "_pulling_" + str(i) + ".png.mcmeta")

                if self.e_anim[i + 1]:
                    renamer.print_rename(path + "/" + self.texture[i + 1] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        if self.texture[4] != self.reduced_name + "_arrow":
            renamer.print_rename(path + "/" + self.texture[4] + ".png", new_texture + "_arrow.png")

            if self.has_e[4]:
                renamer.print_rename(path + "/" + self.texture[4] + "_e.png", new_texture + "_arrow_e.png")

            if self.anim[4]:
                renamer.print_rename(path + "/" + self.texture[4] + ".png.mcmeta", new_texture + "_arrow.png.mcmeta")

            if self.e_anim[4]:
                renamer.print_rename(path + "/" + self.texture[4] + "_e.png.mcmeta", new_texture + "_arrow_e.png.mcmeta")

        if self.texture[5] != self.reduced_name + "_firework" and self.has_fw:
            renamer.print_rename(path + "/" + self.texture[5] + ".png", new_texture + "_firework.png")

            if self.has_e[5]:
                renamer.print_rename(path + "/" + self.texture[5] + "_e.png", new_texture + "_firework_e.png")

            if self.anim[5]:
                renamer.print_rename(path + "/" + self.texture[5] + ".png.mcmeta", new_texture + "_firework.png.mcmeta")

            if self.e_anim[5]:
                renamer.print_rename(path + "/" + self.texture[5] + "_e.png.mcmeta", new_texture + "_firework_e.png.mcmeta")
