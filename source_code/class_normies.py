import os
from util import *

class normies:

    def __init__(self, path):

        self.replica = False
        self.non_replica = False
        self.has_e = False
        self.anim = False
        self.e_anim = False

        for file in os.listdir(path):
            seg = file.split('.')

            if seg[-1] == "properties":
                # read properties
                prop = parse_prop(path + "/" + file)

                ## base item
                try:
                    self.base = prop["items"]
                except:
                    self.base = prop["matchItems"]

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
                self.texture = prop["texture"]
                if self.texture.endswith(".png"):
                    self.texture = self.texture[:-4]

                if self.texture + "_e.png" in os.listdir(path):
                    self.has_e = True
                if self.texture + ".png.mcmeta" in os.listdir(path):
                    self.anim = True
                if self.texture + "_e.png.mcmeta" in os.listdir(path):
                    self.e_anim = True

                ## weight (if there is one)
                try:
                    self.weight = prop["weight"]
                except:
                    pass

                ## record properties location
                if "replica_" in seg[0]:
                    self.rep_properties = path + "/" + file

                else:
                    self.properties = path + "/" + file

    def show(self):

        print("base: " + self.base)
        print("Name: " + self.Name)
        print("model: " + self.model)
        print("texture: " + self.texture)
        print("----")

    def rename(self, path, renamer):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        if self.replica:
            new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"

        # rewrite properties & rename

        p = ""

        p += "items=" + self.base + "\n"

        if self.model != "None":
            p += "model=" + self.model + "\n"

        p += "texture=" + self.reduced_name + "\n"
        rep_p = p  ## for replica

        p += "nbt.plain.display.Name=" + self.Name + "\n"
        rep_p += "nbt.plain.display.Name=Replica " + self.Name + "\n"

        try:
            p += "weight=" + self.weight + "\n"
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
            if self.rep_properties != new_rep_properties:
                renamer.print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files

        if self.texture != self.reduced_name:

            renamer.print_rename(path + "/" + self.texture + ".png", new_texture + ".png")

            if self.has_e:
                renamer.print_rename(path + "/" + self.texture + "_e.png", new_texture + "_e.png")

            if self.anim:
                renamer.print_rename(path + "/" + self.texture + ".png.mcmeta", new_texture + ".png.mcmeta")

            if self.e_anim:
                renamer.print_rename(path + "/" + self.texture + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")
