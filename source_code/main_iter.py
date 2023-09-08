import os
import tkinter as tk
from renamer import *
from class_normies import normies
from class_bows import bow
from class_crossbow import crossbow
from class_armor import armor
from class_set_armor import set_armor
from class_potion import potion


class Settings:

    def __init__(self):
        default_option = [tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()]
        for i in range(3):
            default_option[i].set(True)
        self.options = default_option
        self.log_path = ""
        self.ignore_list = ""
        self.selected_pack = ""


def required(entry, ignore_list):
    # some files should not be touched, it will be identified by this function.
    # the files needed to be touched is roughly whitelisted (idk about uni packing stuff)

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


def readfolder(path, settings):
    # read the folder to determine if it is a texture folder or not.

    is_texture_folder = False

    for entry in os.listdir(path):
        if required(path + "/" + entry, settings.ignore_list):
            pass
        elif entry == "patron" and path.endswith("/skin"):  # hopeskin
            pass
        elif os.path.isdir(path + "/" + entry):
            readfolder(path + "/" + entry, settings)
        else:  # it is a texture folder (assumption 1)
            if ".properties" in entry:
                is_texture_folder = True
    if is_texture_folder:  # then enter rename process
        try:
            item = classify(path, settings)
        except:
            item = "error at " + path
        if type(item) != str:
            # item.show()
            item_renamer = renamer(settings.log_path)
            item.rename(path, item_renamer)
            item_renamer.rename(settings)
        # else:
            # print(item)
            # print("\n----")


def classify(path, settings):
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
        return potion(path, settings.selected_pack)
    if len(image_list) == 1 and properties_count == 1:
        if not custom_model:
            return normies(path)
    if is_armor:
        if Pieces[0] + Pieces[1] + Pieces[2] + Pieces[3] >= 2:  # case of 3: azacor demoncaller set
            return set_armor(path, settings)
        else:
            return armor(path)
    else:
        if Pieces[0] and Pieces[1] and Pieces[2] and Pieces[3]:
            return set_armor(path, settings)
        else:
            return "unclassified"
