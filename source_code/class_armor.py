import os
from util import *


class armor:
    def __init__(self, path):

        self.icon_has_e = [False, False]
        self.armor_has_e = [False, False]
        self.is_leather = False
        self.non_replica = False
        self.replica = False

        for file in os.listdir(path):
            seg = file.split('.')

            if seg[-1] == "properties":
                # read properties
                prop = parse_prop(path + "/" + file)

                if "type" in prop.keys() and prop["type"] == "armor":
                    # armor file

                    ## base item
                    try:
                        self.base = prop["items"]
                    except:
                        self.base = prop["matchItems"]

                    self.material = self.base.split('_')[0]
                    if self.material == "leather": self.is_leather = True
                    if self.material == "golden": self.material = "gold"

                    ## plain text
                    if prop["nbt.plain.display.Name"].startswith("Replica "):
                        self.replica = True
                        self.Name = prop["nbt.plain.display.Name"][8:]
                        self.reduced_name = reduce(self.Name)
                    else:
                        self.non_replica = True
                        self.Name = prop["nbt.plain.display.Name"]
                        self.reduced_name = reduce(self.Name)

                    ## texture
                    if self.is_leather:
                        if self.base == "leather_leggings":
                            self.texture_armor = [prop["texture.leather_layer_2"],
                                                  prop["texture.leather_layer_2_overlay"]]
                        else:
                            self.texture_armor = [prop["texture.leather_layer_1"],
                                                  prop["texture.leather_layer_1_overlay"]]
                        for i in range(2):
                            if self.texture_armor[i] + "_e.png" in os.listdir(path):
                                self.armor_has_e[i] = True
                    else:
                        if "golden" in self.base:
                            if self.base == "golden_leggings":
                                self.texture_armor = prop["texture.gold_layer_2"]
                            else:
                                self.texture_armor = prop["texture.gold_layer_1"]
                        else:
                            if "leggings" in self.base:
                                self.texture_armor = prop["texture." + self.base.split('_')[0] + "_layer_2"]
                            else:
                                self.texture_armor = prop["texture." + self.base.split('_')[0] + "_layer_1"]
                        if self.texture_armor[0] + "_e.png" in os.listdir(path):
                            self.armor_has_e[0] = True

                    ## weight
                    try:
                        self.weight = prop["weight"]
                    except:
                        pass

                    ## record properties location
                    if "replica_" in seg[0]:
                        self.rep_properties_armor = path + "/" + file

                    else:
                        self.properties_armor = path + "/" + file

                else:
                    # icon file

                    ## base item
                    try:
                        self.base = prop["items"]
                    except:
                        self.base = prop["matchItems"]

                    self.material = self.base.split('_')[0]
                    if self.material == "leather": self.is_leather = True
                    if self.material == "golden": self.material = "gold"

                    ## plain text
                    if prop["nbt.plain.display.Name"].startswith("Replica "):
                        self.replica = True
                        self.Name = prop["nbt.plain.display.Name"][8:]
                        self.reduced_name = reduce(self.Name)
                    else:
                        self.non_replica = True
                        self.Name = prop["nbt.plain.display.Name"]
                        self.reduced_name = reduce(self.Name)

                    ## texture
                    if self.is_leather:
                        self.texture_icon = [prop["texture." + self.base], prop["texture." + self.base + "_overlay"]]
                        for i in range(2):
                            if self.texture_icon[i] + "_e.png" in os.listdir(path):
                                self.icon_has_e[i] = True
                    else:
                        try:
                            self.texture_icon = prop["texture"]
                        except:  # some icon properties can use "material_layer_1/2" (why bro why) (see c tiara)
                            if "leggings" in self.base:
                                self.texture_icon = prop["texture." + self.material + "_layer_2"]
                            else:
                                self.texture_icon = prop["texture." + self.material + "_layer_1"]
                        if self.texture_icon + "_e.png" in os.listdir(path):
                            self.icon_has_e[0] = True

                    ## weight
                    try:
                        self.weight = prop["weight"]
                    except:
                        pass

                    ## record properties location
                    if "replica_" in seg[0]:
                        self.rep_properties_icon = path + "/" + file

                    else:
                        self.properties_icon = path + "/" + file

    def show(self):
        print("base: " + self.base)
        print("Name: " + self.Name)
        print("is leather: " + str(self.is_leather))
        print("icon texture: ")
        print(self.texture_icon)
        print("armor texture: ")
        print(self.texture_armor)
        print("----")

    def rename(self, path, renamer):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_icon_properties = path + "/" + self.reduced_name + "_icon.properties"
        new_rep_icon_properties = path + "/replica_" + self.reduced_name + "_icon.properties"
        new_armor_properties = path + "/" + self.reduced_name + "_armor.properties"
        new_rep_armor_properties = path + "/replica_" + self.reduced_name + "_armor.properties"

        # rewrite properties & rename

        p = ""

        p += "items=" + self.base + "\n"

        if self.is_leather:
            p += "texture." + self.base + "=" + self.reduced_name + "_icon\n"
            p += "texture." + self.base + "_overlay=" + self.reduced_name + "_icon_overlay\n"
        else:
            p += "texture=" + self.reduced_name + "_icon\n"

        rep_p = p
        p += "nbt.plain.display.Name=" + self.Name + "\n"
        rep_p += "nbt.plain.display.Name=Replica " + self.Name + "\n"

        try:
            p += "weight=" + self.weight + "\n"
        except:
            pass

        ## non_replica
        if self.non_replica:
            if self.properties_icon != new_icon_properties:  # check if rename is needed
                renamer.print_rename(self.properties_icon, new_icon_properties)

            with open(self.properties_icon, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties_icon != new_rep_icon_properties:  # check if rename is needed
                renamer.print_rename(self.rep_properties_icon, new_rep_icon_properties)

            with open(self.rep_properties_icon, 'w') as f:
                f.write(rep_p)

        ## armor properties

        p = ""

        p += "type=armor\n"

        p += "items=" + self.base + "\n"

        l = 1 + ("leggings" in self.base)
        p += "texture." + self.material + "_layer_" + str(l) + "=" + self.reduced_name + "_armor\n"
        if self.is_leather:
            p += "texture." + self.material + "_layer_" + str(l) + "_overlay=" + self.reduced_name + "_armor_overlay\n"

        rep_p = p
        p += "nbt.plain.display.Name=" + self.Name + "\n"
        rep_p += "nbt.plain.display.Name=Replica " + self.Name + "\n"

        try:
            p += "weight=" + self.weight + "\n"
        except:
            pass

        ## non-replica
        if self.non_replica:
            if self.properties_armor != new_armor_properties:  # check if rename is needed
                renamer.print_rename(self.properties_armor, new_armor_properties)

            with open(self.properties_armor, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties_armor != new_rep_armor_properties:  # check if rename is needed
                renamer.print_rename(self.rep_properties_armor, new_rep_armor_properties)

            with open(self.rep_properties_armor, 'w') as f:
                f.write(rep_p)

        # rename files

        if self.is_leather:

            if self.texture_icon[0] != self.reduced_name + "_icon":
                renamer.print_rename(path + "/" + self.texture_icon[0] + ".png", new_texture + "_icon.png")
                if self.icon_has_e[0]:
                    renamer.print_rename(path + "/" + self.texture_icon[0] + "_e.png", new_texture + "_icon_e.png")

            if self.texture_icon[1] != self.reduced_name + "_icon_overlay":
                renamer.print_rename(path + "/" + self.texture_icon[1] + ".png", new_texture + "_icon_overlay.png")
                if self.icon_has_e[1]:
                    renamer.print_rename(path + "/" + self.texture_icon[1] + "_e.png", new_texture + "_icon_overlay_e.png")

            if self.texture_armor[0] != self.reduced_name + "_armor":
                renamer.print_rename(path + "/" + self.texture_armor[0] + ".png", new_texture + "_armor.png")
                if self.armor_has_e[0]:
                    renamer.print_rename(path + "/" + self.texture_armor[0] + "_e.png", new_texture + "_armor_e.png")

            if self.texture_armor[1] != self.reduced_name + "_armor_overlay":
                renamer.print_rename(path + "/" + self.texture_armor[1] + ".png", new_texture + "_armor_overlay.png")
                if self.armor_has_e[1]:
                    renamer.print_rename(path + "/" + self.texture_armor[1] + "_e.png", new_texture + "_icon_overlay_e.png")

        else:

            if self.texture_icon != self.reduced_name + "_icon":
                renamer.print_rename(path + "/" + self.texture_icon + ".png", new_texture + "_icon.png")
                if self.icon_has_e[0]:
                    renamer.print_rename(path + "/" + self.texture_icon + "_e.png", new_texture + "_icon_e.png")

            if self.texture_armor != self.reduced_name + "_armor":
                renamer.print_rename(path + "/" + self.texture_armor + ".png", new_texture + "_armor.png")
                if self.armor_has_e[0]:
                    renamer.print_rename(path + "/" + self.texture_armor + "_e.png", new_texture + "_armor_e.png")
