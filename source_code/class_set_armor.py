import os
from util import *
from renamer import *

class set_armor:
    def __init__(self, path, settings):

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
            tmp_rnmr = renamer(settings.log_path)
            tmp_rnmr.print_rename(path, path + "s")
            tmp_rnmr.rename(settings)
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

    def rename(self, path, renamer):

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

                p += "type=item\n"

                p += "matchItems=" + self.material + "_" + part + "\n"

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
                        renamer.print_rename(old, new)

                    with open(old, 'w') as f:
                        f.write(p)

                ## replica
                if self.replica:
                    if old_rep != new_rep:
                        renamer.print_rename(old_rep, new_rep)

                    with open(old_rep, 'w') as f:
                        f.write(rep_p)

                # pngs

                old = path + "/" + self.texture_icon[pno]
                new = path + isuffix + self.reduced_name + '_' + self.reduced_suffix[base_suffix[part]] + "_icon"

                if old != new:
                    renamer.print_rename(old + ".png", new + ".png")

                    if self.icon_has_e[pno]:
                        renamer.print_rename(old + "_e.png", new + "_e.png")

                if self.material == "leather":

                    old = path + "/" + self.texture_icon[pno + 4]
                    new = new + "_overlay"

                    if old != new:
                        renamer.print_rename(old + ".png", new + ".png")

                        if self.icon_has_e[pno + 4]:
                            renamer.print_rename(old + "_e.png", new + "_e.png")

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

                p += "matchItems=" + self.material + "_" + part + "\n"

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
                        renamer.print_rename(old, new)

                    with open(old, 'w') as f:
                        f.write(p)

                ## replica
                if self.replica:
                    if old_rep != new_rep:
                        renamer.print_rename(old_rep, new_rep)

                    with open(old_rep, 'w') as f:
                        f.write(rep_p)

            # pngs
            for i in range(2):

                old = "/" + self.texture_armor[i]
                new = asuffix + self.reduced_name + "_layer_" + str(i + 1)

                if old != new:
                    renamer.print_rename(path + old + ".png", path + new + ".png")
                    if self.armor_has_e[i]:
                        renamer.print_rename(path + old + "_e.png", path + new + "_e.png")

                if self.material == "leather":
                    old_overlay = "/" + self.texture_armor[i + 2]
                    new_overlay = asuffix + self.reduced_name + "_layer_" + str(i + 1) + "_overlay"

                    if old_overlay != new_overlay:
                        renamer.print_rename(path + old_overlay + ".png", path + new_overlay + ".png")
                        if self.armor_has_e[i + 2]:
                            renamer.print_rename(path + old_overlay + "_e.png", path + new_overlay + "_e.png")
