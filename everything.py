import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import json
import copy
import zipfile
import time

# global renamer space
global rename_buffer

# global ignore by program
global ignore_list

# global frames
global root
global title_frame
global select_frame

# global variables
global selected_pack
global dst_pack
global options

# global labels
global sframe_grids

# global strings
global cwd
global select_new_pack
global log_path


# util functions
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


# renamer
def renamer_initialize():
    global rename_buffer

    rename_buffer = {}


def print_rename(path1, path2):  # trust, it's worth a function.
    global rename_buffer

    if path1 in rename_buffer:
        temp = "".join(path1.split('.')[:-1]) + "_temp." + path1.split('.')[-1]
        shutil.copyfile(path1, temp)
        rename_buffer[temp] = path2
    else:
        rename_buffer[path1] = path2


def renamer_rename():
    global rename_buffer
    global log_path
    global options

    if options[2].get():
        log = open(log_path, 'a')

    rename_keys = list(rename_buffer.keys())
    if len(rename_keys) != 0 and options[2].get():
        log.write("----\n")

    for i in range(len(rename_keys)):
        path1 = rename_keys[i]
        path2 = rename_buffer[path1]

        # prevent conflict
        if path2 in rename_buffer:
            temp = "".join(path2.split('.')[:-1]) + "_temp." + path2.split('.')[-1]
            shutil.move(path2, temp)
            rename_buffer[temp] = rename_buffer[path2]
            del rename_buffer[path2]
            rename_keys[rename_keys.index(path2)] = temp

        shutil.move(path1, path2)
        del rename_buffer[path1]
        if options[2].get():
            log.write("- rename " + "/".join(path1.split('/')[-2:]) + " to " + "/".join(path2.split('/')[-2:]) + "\n")

    if options[2].get():
        log.close()

    renamer_initialize()


# classes
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

    def rename(self, path):

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
                print_rename(self.properties, new_properties)

            with open(self.properties, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties != new_rep_properties:
                print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files

        if self.texture != self.reduced_name:

            print_rename(path + "/" + self.texture + ".png", new_texture + ".png")

            if self.has_e:
                print_rename(path + "/" + self.texture + "_e.png", new_texture + "_e.png")

            if self.anim:
                print_rename(path + "/" + self.texture + ".png.mcmeta", new_texture + ".png.mcmeta")

            if self.e_anim:
                print_rename(path + "/" + self.texture + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")


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

    def rename(self, path):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"

        # rewrite properties & rename

        p = ""

        p += "items=bow\n"

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
                print_rename(self.properties, new_properties)

            with open(self.properties, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties != new_rep_properties:  # check if rename is needed
                print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files
        if self.texture[0] != self.reduced_name:
            print_rename(path + "/" + self.texture[0] + ".png", new_texture + ".png")

            if self.has_e[0]:
                print_rename(path + "/" + self.texture[0] + "_e.png", new_texture + "_e.png")

            if self.anim[0]:
                print_rename(path + "/" + self.texture[0] + ".png.mcmeta", new_texture + ".png.mcmeta")

            if self.e_anim[0]:
                print_rename(path + "/" + self.texture[0] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        for i in range(self.pull_count):

            ind = self.pull_mapping.index(i) + 1

            if self.texture[ind] != self.reduced_name + "_pulling_" + str(i):

                print_rename(path + "/" + self.texture[ind] + ".png", new_texture + "_pulling_" + str(i) + ".png")

                if self.has_e[ind]:
                    print_rename(path + "/" + self.texture[ind] + "_e.png",
                                 new_texture + "_pulling_" + str(i) + "_e.png")

                if self.anim[ind]:
                    print_rename(path + "/" + self.texture[ind] + ".png.mcmeta",
                                 new_texture + "_pulling_" + str(i) + ".png.mcmeta")

                if self.e_anim[ind]:
                    print_rename(path + "/" + self.texture[ind] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")


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

    def rename(self, path):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"

        # rewrite properties & rename

        p = ""

        p += "items=crossbow\n"

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
                print_rename(self.properties, new_properties)

            with open(self.properties, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties != new_rep_properties:  # check if rename is needed
                print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files
        if self.texture[0] != self.reduced_name:
            print_rename(path + "/" + self.texture[0] + ".png", new_texture + ".png")

            if self.has_e[0]:
                print_rename(path + "/" + self.texture[0] + "_e.png", new_texture + "_e.png")

            if self.anim[0]:
                print_rename(path + "/" + self.texture[0] + ".png.mcmeta", new_texture + ".png.mcmeta")

            if self.e_anim[0]:
                print_rename(path + "/" + self.texture[0] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        for i in range(3):

            if self.texture[i + 1] != self.reduced_name + "_pulling_" + str(i):

                print_rename(path + "/" + self.texture[i + 1] + ".png", new_texture + "_pulling_" + str(i) + ".png")

                if self.has_e[i + 1]:
                    print_rename(path + "/" + self.texture[i + 1] + "_e.png",
                                 new_texture + "_pulling_" + str(i) + "_e.png")

                if self.anim[i + 1]:
                    print_rename(path + "/" + self.texture[i + 1] + ".png.mcmeta",
                                 new_texture + "_pulling_" + str(i) + ".png.mcmeta")

                if self.e_anim[i + 1]:
                    print_rename(path + "/" + self.texture[i + 1] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        if self.texture[4] != self.reduced_name + "_arrow":
            print_rename(path + "/" + self.texture[4] + ".png", new_texture + "_arrow.png")

            if self.has_e[4]:
                print_rename(path + "/" + self.texture[4] + "_e.png", new_texture + "_arrow_e.png")

            if self.anim[4]:
                print_rename(path + "/" + self.texture[4] + ".png.mcmeta", new_texture + "_arrow.png.mcmeta")

            if self.e_anim[4]:
                print_rename(path + "/" + self.texture[4] + "_e.png.mcmeta", new_texture + "_arrow_e.png.mcmeta")

        if self.texture[5] != self.reduced_name + "_firework" and self.has_fw:
            print_rename(path + "/" + self.texture[5] + ".png", new_texture + "_firework.png")

            if self.has_e[5]:
                print_rename(path + "/" + self.texture[5] + "_e.png", new_texture + "_firework_e.png")

            if self.anim[5]:
                print_rename(path + "/" + self.texture[5] + ".png.mcmeta", new_texture + "_firework.png.mcmeta")

            if self.e_anim[5]:
                print_rename(path + "/" + self.texture[5] + "_e.png.mcmeta", new_texture + "_firework_e.png.mcmeta")


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

    def rename(self, path):

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
                print_rename(self.properties_icon, new_icon_properties)

            with open(self.properties_icon, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties_icon != new_rep_icon_properties:  # check if rename is needed
                print_rename(self.rep_properties_icon, new_rep_icon_properties)

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
                print_rename(self.properties_armor, new_armor_properties)

            with open(self.properties_armor, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties_armor != new_rep_armor_properties:  # check if rename is needed
                print_rename(self.rep_properties_armor, new_rep_armor_properties)

            with open(self.rep_properties_armor, 'w') as f:
                f.write(rep_p)

        # rename files

        if self.is_leather:

            if self.texture_icon[0] != self.reduced_name + "_icon":
                print_rename(path + "/" + self.texture_icon[0] + ".png", new_texture + "_icon.png")
                if self.icon_has_e[0]:
                    print_rename(path + "/" + self.texture_icon[0] + "_e.png", new_texture + "_icon_e.png")

            if self.texture_icon[1] != self.reduced_name + "_icon_overlay":
                print_rename(path + "/" + self.texture_icon[1] + ".png", new_texture + "_icon_overlay.png")
                if self.icon_has_e[1]:
                    print_rename(path + "/" + self.texture_icon[1] + "_e.png", new_texture + "_icon_overlay_e.png")

            if self.texture_armor[0] != self.reduced_name + "_armor":
                print_rename(path + "/" + self.texture_armor[0] + ".png", new_texture + "_armor.png")
                if self.armor_has_e[0]:
                    print_rename(path + "/" + self.texture_armor[0] + "_e.png", new_texture + "_armor_e.png")

            if self.texture_armor[1] != self.reduced_name + "_armor_overlay":
                print_rename(path + "/" + self.texture_armor[1] + ".png", new_texture + "_armor_overlay.png")
                if self.armor_has_e[1]:
                    print_rename(path + "/" + self.texture_armor[1] + "_e.png", new_texture + "_icon_overlay_e.png")


        else:

            if self.texture_icon != self.reduced_name + "_icon":
                print_rename(path + "/" + self.texture_icon + ".png", new_texture + "_icon.png")
                if self.icon_has_e[0]:
                    print_rename(path + "/" + self.texture_icon + "_e.png", new_texture + "_icon_e.png")

            if self.texture_armor != self.reduced_name + "_armor":
                print_rename(path + "/" + self.texture_armor + ".png", new_texture + "_armor.png")
                if self.armor_has_e[0]:
                    print_rename(path + "/" + self.texture_armor + "_e.png", new_texture + "_armor_e.png")


class set_armor:
    def __init__(self, path):

        base_suffix = {"helmet": 0, "chestplate": 1, "leggings": 2, "boots": 3}

        self.suffix = ["", "", "",
                       ""]  # helmet, chestplate, leggings, boots (suffix like "robe", "sabotons", based on name)
        self.reduced_suffix = ["", "", "", ""]  # reduced version of suffix
        self.texture_icon = ["", "", "", "", "", "", "", ""]  # helmet, chestplate, leggings, boots, overlays
        self.icon_has_e = [False, False, False, False, False, False, False, False]
        self.texture_armor = ["", "", "", ""]  # layer 1, layer 2, overlay
        self.armor_has_e = [False, False, False, False]

        self.path_modified_icons_folder = False
        self.opened_icon = False
        self.opened_armor = False
        self.properties_icon = ["", "", "", ""]
        self.properties_armor = ["", "", "", ""]

        self.replica = False
        self.non_replica = False
        self.rep_properties_icon = ["", "", "", ""]
        self.rep_properties_armor = ["", "", "", ""]

        # in case misnamed path
        if path.endswith("/icon"):
            print_rename(path, path + "s")
            renamer_rename()
            path += "s"
            self.path_modified_icons_folder = True

        for file in os.listdir(path):
            seg = file.split('.')

            if seg[-1] == "properties":
                # read properties
                prop = parse_prop(path + "/" + file)

                try:
                    items = prop["items"]
                except:
                    items = prop["matchItems"]

                part = base_suffix[items.split('_')[-1]]

                # material

                self.material = items.split('_')[0]

                # name
                if prop["nbt.plain.display.Name"].startswith("Replica "):
                    self.replica = True
                    crop = prop["nbt.plain.display.Name"].split(' ')[-1]
                    self.Name = prop["nbt.plain.display.Name"][8:(-len(crop) - 1)]
                    self.reduced_name = reduce(self.Name)
                else:
                    self.non_replica = True
                    crop = prop["nbt.plain.display.Name"].split(' ')[-1]
                    self.Name = prop["nbt.plain.display.Name"][:(-len(crop) - 1)]
                    self.reduced_name = reduce(self.Name)

                ## suffix
                self.suffix[part] = prop["nbt.plain.display.Name"].split(' ')[-1]
                self.reduced_suffix[part] = reduce(self.suffix[part])

                if "type" in prop.keys() and prop["type"] == "armor":
                    # armor file

                    self.opened_armor = True

                    ## texture (armor)
                    if part == 2:
                        if self.material == "golden":
                            self.texture_armor[1] = prop["texture.gold_layer_2"]
                        else:
                            self.texture_armor[1] = prop["texture." + self.material + "_layer_2"]
                        if self.material == "leather":
                            self.texture_armor[3] = prop["texture.leather_layer_2_overlay"]
                    else:
                        if self.material == "golden":
                            self.texture_armor[0] = prop["texture.gold_layer_1"]
                        else:
                            self.texture_armor[0] = prop["texture." + self.material + "_layer_1"]
                        if self.material == "leather":
                            self.texture_armor[2] = prop["texture.leather_layer_1_overlay"]

                    ## record properties location
                    if "replica_" in seg[0]:
                        self.rep_properties_armor[part] = path + "/" + file

                    else:
                        self.properties_armor[part] = path + "/" + file

                else:
                    # icon file

                    self.opened_icon = True
                    self.properties_icon[part] = path + "/" + file

                    ## texture (icon)
                    if self.material == "leather":
                        self.texture_icon[part] = prop["texture." + items]
                        self.texture_icon[part + 4] = prop["texture." + items + "_overlay"]
                    else:
                        self.texture_icon[part] = prop["texture"]

                    ## record properties location
                    if "replica_" in seg[0]:
                        self.rep_properties_icon[part] = path + "/" + file

                    else:
                        self.properties_icon[part] = path + "/" + file

                # emissive
                for i in range(8):
                    if self.texture_icon[i] != "":
                        if self.texture_icon[i] + "_e.png" in os.listdir(path):
                            self.icon_has_e[i] = True
                for i in range(4):
                    if self.texture_armor[i] != "":
                        if self.texture_armor[i] + "_e.png" in os.listdir(path):
                            self.armor_has_e[i] = True

        # preventing repeating item names (ex. Scout's Leather set)

        part_list = ["helmet", "chestplate", "leggings", "boots"]
        repeated = [False, False, False, False]

        for i in range(4):
            for j in range(i + 1, 4):
                if self.reduced_suffix[i] == self.reduced_suffix[j]:
                    repeated[i] = True
                    repeated[j] = True

        for i in range(4):
            if repeated[i]:
                self.reduced_suffix[i] = self.reduced_suffix[i] + "_" + part_list[i]

    def show(self):
        print("material: " + self.material)
        print("Name: " + self.Name)
        print("has replica: " + str(self.replica))
        print("suffix:")
        print(self.suffix)
        print("jammed: " + str(self.opened_armor and self.opened_icon))
        print("icon texture: ")
        print(self.texture_icon)
        print("armor texture: ")
        print(self.texture_armor)
        print("----")

    def rename(self, path):

        if self.path_modified_icons_folder:
            path += "s"

        asuffix = "/"
        isuffix = "/"
        base_suffix = {"helmet": 0, "chestplate": 1, "leggings": 2, "boots": 3}

        # mixed folder (separate first)
        if self.opened_armor and self.opened_icon:
            # separate into folders
            os.mkdir(path + "/icons")
            os.mkdir(path + "/armor")
            isuffix = "/icons/"
            asuffix = "/armor/"

        # icon-only folder
        if self.opened_icon:

            # doing properties with pngs
            for part in base_suffix:

                # properties

                pno = base_suffix[part]

                # protection for 3-item sets
                if self.reduced_suffix[pno] == "":
                    continue

                old = self.properties_icon[pno]
                old_rep = self.rep_properties_icon[pno]
                new = path + isuffix + self.reduced_name + '_' + self.reduced_suffix[pno] + "_icon.properties"
                new_rep = path + isuffix + "replica_" + self.reduced_name + '_' + self.reduced_suffix[
                    pno] + "_icon.properties"

                p = ""

                p += "items=" + self.material + "_" + part + "\n"

                filename = self.reduced_name + '_' + self.reduced_suffix[pno] + "_icon"

                if self.material == "leather":
                    p += "texture.leather_" + part + "=" + filename + "\n"
                    p += "texture.leather_" + part + "_overlay=" + filename + "_overlay"
                else:
                    p += "texture=" + filename
                p += "\n"

                rep_p = p
                p += "nbt.plain.display.Name=" + self.Name + " " + self.suffix[pno]
                rep_p += "nbt.plain.display.Name=Replica " + self.Name + " " + self.suffix[pno]

                ## non-replica
                if self.non_replica:
                    if old != new:
                        print_rename(old, new)

                    with open(old, 'w') as f:
                        f.write(p)

                ## replica
                if self.replica:
                    if old_rep != new_rep:
                        print_rename(old_rep, new_rep)

                    with open(old_rep, 'w') as f:
                        f.write(rep_p)

                # pngs

                old = path + "/" + self.texture_icon[pno]
                new = path + isuffix + self.reduced_name + '_' + self.reduced_suffix[base_suffix[part]] + "_icon"

                if old != new:
                    print_rename(old + ".png", new + ".png")

                    if self.icon_has_e[pno]:
                        print_rename(old + "_e.png", new + "_e.png")

                if self.material == "leather":

                    old = path + "/" + self.texture_icon[pno + 4]
                    new = new + "_overlay"

                    if old != new:
                        print_rename(old + ".png", new + ".png")

                        if self.icon_has_e[pno + 4]:
                            print_rename(old + "_e.png", new + "_e.png")

        # armor-only folder
        if self.opened_armor:

            # properties
            for part in base_suffix:

                pno = base_suffix[part]

                # protection for 3-item sets
                if self.reduced_suffix[pno] == "":
                    continue

                old = self.properties_armor[pno]
                old_rep = self.rep_properties_armor[pno]
                new = path + asuffix + self.reduced_name + '_' + self.reduced_suffix[pno] + "_armor.properties"
                new_rep = path + asuffix + "replica_" + self.reduced_name + '_' + self.reduced_suffix[
                    pno] + "_armor.properties"

                p = ""

                p += "type=armor\n"

                p += "items=" + self.material + "_" + part + "\n"

                l = str(1 + (part == "leggings"))
                if self.material == "golden":
                    p += "texture.gold_layer_" + l + "=" + self.reduced_name + "_layer_" + l
                else:
                    p += "texture." + self.material + "_layer_" + l + "=" + self.reduced_name + "_layer_" + l
                p += "\n"
                if self.material == "leather":
                    p += "texture.leather_layer_" + l + "_overlay=" + self.reduced_name + "_layer_" + l + "_overlay\n"

                rep_p = p
                p += "nbt.plain.display.Name=" + self.Name + " " + self.suffix[pno]
                rep_p += "nbt.plain.display.Name=Replica " + self.Name + " " + self.suffix[pno]

                ## non-replica
                if self.non_replica:
                    if old != new:
                        print_rename(old, new)

                    with open(old, 'w') as f:
                        f.write(p)

                ## replica
                if self.replica:
                    if old_rep != new_rep:
                        print_rename(old_rep, new_rep)

                    with open(old_rep, 'w') as f:
                        f.write(rep_p)

            # pngs
            for i in range(2):

                old = "/" + self.texture_armor[i]
                new = asuffix + self.reduced_name + "_layer_" + str(i + 1)

                if old != new:
                    print_rename(path + old + ".png", path + new + ".png")
                    if self.armor_has_e[i]:
                        print_rename(path + old + "_e.png", path + new + "_e.png")

                if self.material == "leather":
                    old_overlay = "/" + self.texture_armor[i + 2]
                    new_overlay = asuffix + self.reduced_name + "_layer_" + str(i + 1) + "_overlay"

                    if old_overlay != new_overlay:
                        print_rename(path + old_overlay + ".png", path + new_overlay + ".png")
                        if self.armor_has_e[i + 2]:
                            print_rename(path + old_overlay + "_e.png", path + new_overlay + "_e.png")


class potion:
    def __init__(self, path):

        self.replica = False
        self.non_replica = False
        self.texture = ["", ""]
        self.has_e = [False, False]
        self.anim = [False, False]
        self.e_anim = [False, False]

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
                self.model = prop["model"]
                if self.model.endswith(".json"):
                    self.model = self.model[:-5]

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

        with open(selected_pack.get() + "/assets/minecraft/" + self.model + ".json", 'r') as jsn:
            text = jsn.read()

        self.model_content = json.loads(text)
        self.texture[0] = copy.deepcopy(self.model_content["textures"]["layer0"].split('/')[-1])

        self.texture[1] = copy.deepcopy(self.model_content["textures"]["layer1"].split('/')[-1])

        # emissive/animation
        src = os.listdir(path)
        for i in range(2):
            if self.texture[i] + ".png" not in os.listdir(path):
                self.texture[i] = "potion"
                if i == 0:
                    self.texture[i] += "_overlay"
            if path + "/" + self.texture[i] + "_e.png" in src:
                self.has_e[i] = True
            if path + "/" + self.texture[i] + ".png.mcmeta" in src:
                self.anim[i] = True
            if path + "/" + self.texture[i] + "_e.png.mcmeta" in src:
                self.e_anim[i] = True

    def show(self):

        print("Name: " + self.Name)
        print("model: " + self.model)
        print("texture: " + self.texture[1])
        print("----")

    def rename(self, path):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        new_model = "/".join(self.model.split('/')[:-1]) + "/" + self.reduced_name
        if self.replica:
            new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"

        # rewrite properties & rename

        p = ""

        p += "items=" + self.base + "\n"

        if self.model != "None":
            p += "model=" + new_model + "\n"

        rep_p = p  # for replica

        p += "nbt.plain.display.Name=" + self.Name + "\n"
        rep_p += "nbt.plain.display.Name=Replica " + self.Name + "\n"

        try:
            p += "weight=" + self.weight + "\n"
        except:
            pass

        ## non-replica
        if self.non_replica:
            if self.properties != new_properties:  # check if rename is needed
                print_rename(self.properties, new_properties)

            with open(self.properties, 'w') as f:
                f.write(p)

        ## replica
        if self.replica:
            if self.rep_properties != new_rep_properties:
                print_rename(self.rep_properties, new_rep_properties)

            with open(self.rep_properties, 'w') as f:
                f.write(rep_p)

        # rename files

        for i in range(2):
            if i == 0:
                correct_name = self.reduced_name + "_overlay"
            else:
                correct_name = self.reduced_name

            if self.texture[i] != correct_name:

                new_texture = path + "/" + correct_name

                print_rename(path + "/" + self.texture[i] + ".png", new_texture + ".png")

                if self.has_e[i]:
                    print_rename(path + "/" + self.texture[i] + "_e.png", new_texture + "_e.png")

                if self.anim[i]:
                    print_rename(path + "/" + self.texture[i] + ".png.mcmeta", new_texture + ".png.mcmeta")

                if self.e_anim[i]:
                    print_rename(path + "/" + self.texture[i] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        new = os.path.join(os.path.join(self.model_content["textures"]["layer0"], ".."), self.reduced_name)
        self.model_content["textures"]["layer0"] = new + "_overlay"
        self.model_content["textures"]["layer1"] = new

        if not self.model.endswith(self.reduced_name):
            print_rename(selected_pack.get() + "/assets/minecraft/" + self.model + ".json",
                         selected_pack.get() + "/assets/minecraft/" + new_model + ".json")

        with open(selected_pack.get() + "/assets/minecraft/" + self.model + ".json", 'w') as jsn:
            dumping = json.dumps(self.model_content, indent=4)
            jsn.write(dumping)


# main iteration functions
def required(entry):
    # some files should not be touched, it will be identified by this function.
    # the files needed to be touched is roughly whitelisted (idk about uni packing stuff)
    global ignore_list

    if entry.split('/')[-1] in ignore_list:
        return True
    elif ".png" in entry:
        return False
    elif ".properties" in entry:
        return False
    elif os.path.isdir(entry):
        return False
    else:
        return True


def readfolder(path):
    # read the folder to determine if it is a texture folder or not.
    global ignore_list

    is_texture_folder = False

    for entry in os.listdir(path):
        if required(path + "/" + entry):
            pass
        elif entry == "patron" and path.endswith("/skin"):  # hopeskin
            pass
        elif os.path.isdir(path + "/" + entry):
            readfolder(path + "/" + entry)
        else:  # it is a texture folder (assumption 1)
            if ".properties" in entry:
                is_texture_folder = True
    if is_texture_folder:  # then enter rename process
        try:
            item = classify(path)
        except:
            item = "error at " + path
        if type(item) != type("123"):
            # item.show()
            item.rename(path)
            renamer_rename()
        # else:
            # print(item)
            # print("\n----")


def classify(path):
    # classify the folder and store information respectively

    is_armor = False
    Pieces = [False, False, False, False]
    is_bow = False
    is_crossbow = False
    is_potion = False
    has_cd = False
    custom_model = False
    image_list = []
    properties_count = 0
    for file in os.listdir(path):

        # properties
        if ".properties" in file:

            # get properties content
            with open(path + "/" + file, 'r') as p:
                text = [p.readline().split('\n')[0]]
                while text[-1] != "":
                    text.append(p.readline().split('\n')[0])
            text = text[:-1]

            for line in text:
                feature = line.split('=')
                if feature[0] == "type" and feature[1] == "armor":
                    is_armor = True
                if feature[0] == "items" or feature[0] == "matchItems":
                    if "helmet" in feature[1]:
                        Pieces[0] = True
                    elif "chestplate" in feature[1]:
                        Pieces[1] = True
                    elif "leggings" in feature[1]:
                        Pieces[2] = True
                    elif "boots" in feature[1]:
                        Pieces[3] = True
                    elif feature[1] == "bow":
                        is_bow = True
                    elif feature[1] == "crossbow":
                        is_crossbow = True
                    elif feature[1] == "potion" or feature[1] == "splash_potion" or feature[1] == "lingering_potion":
                        is_potion = True
                if feature[0] == "model":
                    if feature[1].split('/')[-2] != "source_models":
                        custom_model = True
            properties_count += 1

            # pngs
        elif file.endswith(".png"):  # then get the "true name" of pngs, that is without _e or .mcmeta
            seg = file.split('.')
            if seg[0].endswith("_cooldown_e"):
                truename = seg[0][:-11]
                has_cd = True
            elif seg[0].endswith("_e"):
                truename = seg[0][:-2]
                is_emissive = True
            elif seg[0].endswith("_cooldown"):
                truename = seg[0][:-9]
                has_cd = True
            else:
                truename = seg[0]
            if truename not in image_list:
                image_list.append(truename)
    # actually classify
    if is_bow:
        return bow(path)
    if is_crossbow:
        return crossbow(path)
    if is_potion and not has_cd:
        return potion(path)
    if len(image_list) == 1 and properties_count == 1:
        if not custom_model:
            return normies(path)
    if is_armor:
        if Pieces[0] + Pieces[1] + Pieces[2] + Pieces[3] >= 2:  # case of 3: azacor demoncaller set
            return set_armor(path)
        else:
            return armor(path)
    else:
        if Pieces[0] and Pieces[1] and Pieces[2] and Pieces[3]:
            return set_armor(path)
        else:
            return "unclassified"


# main gui loop
# settings
width = 640
height = 300

program_title = "Monumenta >> Resource Pack Renamer v1.0"

font_color_bg = "#58778a"
font_color = "#ffffff"
gui_font = "Verdana"
grid_wrap_length = 256
path_box_length = 30

generate_new_pack = True

# setup gui
root = tk.Tk()
root.geometry(str(width) + "x" + str(height))
root.title(program_title)
root.iconbitmap("assets/type.ico")
root.configure(bg=font_color_bg)

# preprocess
cwd = os.getcwd()
selected_pack = tk.StringVar(value="unselected")
dst_pack = tk.StringVar(value="unselected")
status = "Status >> unselected"
log_path = cwd + "/logs.txt"

sframe_dimension = (3, 4)
sframe_grids = [[] for i in range(sframe_dimension[0])]
# objects:
# | original pack | select |        path        | verify
# |     options   |   v    |       status       |
# |    dst pack   | select |        path        |

# events
def get_pack(r):
    global status
    global selected_pack
    global dst_pack
    global sframe_grids
    global log_path

    if r == 0:
        selected_pack.set(tk.filedialog.askdirectory(title="choose rp", initialdir=cwd))
        dst_pack.set(selected_pack.get())
        try:
            src = os.listdir(selected_pack.get() + "/assets/minecraft/optifine/cit")
            sframe_grids[1][1]["state"] = "normal"

            craft_img_new = ImageTk.PhotoImage(Image.open("assets/craft.png"), master=select_frame)
            sframe_grids[1][1].configure(image=craft_img_new)
            sframe_grids[1][1].newimage = craft_img_new

            verify_img_new = ImageTk.PhotoImage(Image.open("assets/verified.png"), master=select_frame)
            sframe_grids[0][3].configure(image=verify_img_new)
            sframe_grids[0][3].newimage = verify_img_new

            status = "Status >> Ready for conversion"

            sframe_grids[1][2].configure(text=status)

        except:
            status = "Status >> Invalid Pack! Please make sure to include optifine/cit folder."
            sframe_grids[1][2].configure(text=status)
            sframe_grids[1][1]["state"] = "disabled"

            verify_img_new = ImageTk.PhotoImage(Image.open("assets/not_verified.png"), master=select_frame)
            sframe_grids[0][3].configure(image=verify_img_new)
            sframe_grids[0][3].newimage = verify_img_new

    elif r == 2:
        dst_pack.set(tk.filedialog.askdirectory(title="choose destination", initialdir=cwd))
        log_path = dst_pack.get() + "/logs.txt"


def start_rename():
    global cwd
    global log_path
    global status_label
    global status
    global ignore_list
    global options

    status = "Status >> Copying..."
    time.sleep(0.1)

    sframe_grids[1][1]["state"] = "active"
    sframe_grids[1][2].configure(text=status)

    # create ignore list
    with open("ignore.txt", 'r') as ign:
        ignore_list = list(ign.read().split("\n"))
    print(ignore_list)

    # copy a new folder
    folder = dst_pack.get() + "/generated"
    if options[0] or options[1]:
        if zipfile.is_zipfile(selected_pack.get()):
            ZIP = zipfile.ZipFile(selected_pack.get())
            if "generated" not in os.listdir(dst_pack.get()):
                os.mkdir(folder)
            ZIP.extractall(folder)
        else:
            shutil.copytree(selected_pack.get(), folder)

    time.sleep(0.1)

    # run rename
    status = "Status >> Renaming..."
    sframe_grids[1][2].configure(text=status)

    renamer_initialize()
    readfolder(folder + "/assets/minecraft/optifine/cit")

    # zipping
    if options[0].get():
        zp = zipfile.ZipFile(dst_pack.get() + "/generated.zip", 'w')
        for rt, dirs, files in os.walk(folder):
            for file in files:
                zp.write(os.path.join(rt, file), os.path.relpath(os.path.join(rt, file), folder))
        zp.close()
    if not options[1].get():
        shutil.rmtree(folder)

    # ending
    status = "Status >> Conversion complete!"
    sframe_grids[1][2].configure(text=status)
    sframe_grids[1][1]["state"] = "disabled"


def debug(options):
    print([options[0].get(), options[1].get()])


## title
title_img = ImageTk.PhotoImage(Image.open("assets/title.png"), master=root)
main_title = tk.Label(root, pady=15, image=title_img, bg=font_color_bg)
main_title.pack(fill='x')

## row 0
select_frame = tk.Frame(root, padx=20, background=font_color_bg)
select_frame.pack()

select_img = ImageTk.PhotoImage(Image.open("assets/original_pack.png"), master=select_frame)
sframe_grids[0].append(tk.Label(select_frame, image=select_img, bg=font_color_bg))

select_button_img = ImageTk.PhotoImage(Image.open("assets/select_button.png"), master=select_frame)
sframe_grids[0].append(tk.Button(select_frame, image=select_button_img, bg=font_color_bg, command=lambda: get_pack(0)))

sframe_grids[0].append(tk.Entry(select_frame, textvariable=selected_pack, font=(gui_font, 10),
                                bg=font_color, fg=font_color_bg, width=path_box_length))

verify_img = ImageTk.PhotoImage(Image.open("assets/not_verified.png"), master=select_frame)
sframe_grids[0].append(tk.Label(select_frame, image=verify_img, bg=font_color_bg))
sframe_grids[0][3].image = verify_img

# row 1
sframe_grids[1].append(tk.Frame(select_frame, background=font_color_bg))

# [make zipped pack, make unzipped pack, log file]
options = [tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()]
options[0].set(True)
options[1].set(True)
options[2].set(True)

option1 = tk.Checkbutton(sframe_grids[1][0], text="Make zipped pack", font=(gui_font, 8),
                         variable=options[0], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
option2 = tk.Checkbutton(sframe_grids[1][0], text="Make unzipped pack", font=(gui_font, 8),
                         variable=options[1], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
option3 = tk.Checkbutton(sframe_grids[1][0], text="Generate log file", font=(gui_font, 8),
                         variable=options[2], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
option1.pack()
option2.pack()
option3.pack()

craft_img = ImageTk.PhotoImage(Image.open("assets/cant_craft.png"), master=select_frame)
sframe_grids[1].append(tk.Button(select_frame, image=craft_img, bg=font_color_bg, command=start_rename,
                         state="disabled"))
sframe_grids[1][1].image = craft_img

sframe_grids[1].append(tk.Label(select_frame, text=status, font=(gui_font, 11),
                                bg=font_color_bg, fg=font_color, wraplength=grid_wrap_length))

# sframe_grids[1].append(tk.Button(select_frame, text="debug", command=lambda: debug(options)))

## row 2
dst_pack_img = ImageTk.PhotoImage(Image.open("assets/dst_pack.png"), master=select_frame)
sframe_grids[2].append(tk.Label(select_frame, image=dst_pack_img, bg=font_color_bg))

sframe_grids[2].append(tk.Button(select_frame, image=select_button_img, bg=font_color_bg, command=lambda: get_pack(2)))

sframe_grids[2].append(tk.Entry(select_frame, textvariable=dst_pack, font=(gui_font, 10),
                             bg=font_color, fg=font_color_bg, width=path_box_length))

# gridding
for i in range(sframe_dimension[0]):
    for j in range(len(sframe_grids[i])):
        sframe_grids[i][j].grid(row=i, column=j, sticky=tk.W+tk.E, padx=5)

# info

print(sframe_grids)

# call gui
root.mainloop()

