import os
import copy
import json
from util import *


class potion:
    def __init__(self, path, selected_pack):

        self.replica = False
        self.non_replica = False
        self.texture = ["", ""]
        self.has_e = [False, False]
        self.anim = [False, False]
        self.e_anim = [False, False]
        self.selected_pack = selected_pack

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
            if self.texture[i] + ".png" not in src:
                self.texture[i] = "potion"
                if i == 0:
                    self.texture[i] += "_overlay"
            if self.texture[i] + "_e.png" in src:
                self.has_e[i] = True
            if self.texture[i] + ".png.mcmeta" in src:
                self.anim[i] = True
            if self.texture[i] + "_e.png.mcmeta" in src:
                self.e_anim[i] = True

    def show(self):

        print("Name: " + self.Name)
        print("model: " + self.model)
        print("texture: " + self.texture[1])
        print("----")

    def rename(self, path, renamer):

        # print(path + ":")

        # generate new names

        new_texture = path + "/" + self.reduced_name
        new_properties = path + "/" + self.reduced_name + ".properties"
        new_model = "/".join(self.model.split('/')[:-1]) + "/" + self.reduced_name
        if self.replica and not self.non_replica:
            new_rep_properties = path + "/replica_" + self.reduced_name + ".properties"
            new_model = "/".join(self.model.split('/')[:-1]) + "/replica_" + self.reduced_name

        # rewrite properties & rename

        p = ""

        p += "type=item\n"

        p += "matchItems=" + self.base + "\n"

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

        for i in range(2):
            if i == 0:
                correct_name = self.reduced_name + "_overlay"
            else:
                correct_name = self.reduced_name

            if self.texture[i] != correct_name:

                new_texture = path + "/" + correct_name

                renamer.print_rename(path + "/" + self.texture[i] + ".png", new_texture + ".png")

                if self.has_e[i]:
                    renamer.print_rename(path + "/" + self.texture[i] + "_e.png", new_texture + "_e.png")

                if self.anim[i]:
                    renamer.print_rename(path + "/" + self.texture[i] + ".png.mcmeta", new_texture + ".png.mcmeta")

                if self.e_anim[i]:
                    renamer.print_rename(path + "/" + self.texture[i] + "_e.png.mcmeta", new_texture + "_e.png.mcmeta")

        new = "/".join(self.model_content["textures"]["layer0"].split('/')[:-1])
        if new.endswith('/'):
            new = new[:-1]
        new += "/" + self.reduced_name
        self.model_content["textures"]["layer0"] = new + "_overlay"
        self.model_content["textures"]["layer1"] = new

        if not self.model.endswith(self.reduced_name):
            renamer.print_rename(self.selected_pack.get() + "/assets/minecraft/" + self.model + ".json",
                         self.selected_pack.get() + "/assets/minecraft/" + new_model + ".json")

        with open(self.selected_pack.get() + "/assets/minecraft/" + self.model + ".json", 'w') as jsn:
            dumping = json.dumps(self.model_content, indent=4)
            jsn.write(dumping)
