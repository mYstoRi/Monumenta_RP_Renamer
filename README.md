# Monumenta_RP_Renamer
Renaming standards and conversions of the current resource pack. Make sure to read `Manual.md` for instructions! (TLDR see guide.png)

user pack link (file larger than 25MB sob)
https://drive.google.com/drive/folders/1evQ-97FzxabIjdaB4c9_zt329TuD2S7J?usp=sharing

# File Naming Rules

### Rules that might need more discussing
1. Replica item files always come without `replica_`, as most of those are in the same folder as the original item.
2. Bows' and crossbows' idle texture is named without `_standby`
3. Armor icon files have `_icon` and armor models have `_armor`
4. set armor extra rule: if some of the set items have the exact same plain text, the name would add additional `_[part]` (see t5 scout set)

### File-Style renaming
This will convert names into only using `a-z`, `0-9` and `_`.
Refer to the converted name as `converted_name` and the non-converted as `Name`.

Rules:
1. `a-z`, `0-9`, `_` -> unchanged
2. capital letters -> lowercase letters
3. `(space)` or `-` -> `_`
4. `é` -> `e`
5. `'`, `$` or other signs -> nothing
6. can only have 1 consecutive `_`. The rest of them get ignored. (see skt key, it has "(space)-(space)")

### In-Folder Format:

- Every non-emissive `.png` files can have emissive file with `_e` appended right before `.png`.
	- Ex. `converted_name_e.png`

- Every `.png` files can have an animation file with `.mcmeta` after its `.png`.
	- Ex. `converted_name.png.mcmeta`

- The way to add replica:
	1. in the same folder as the non-replica:
 		- duplicate all properties and change the plain text to `Replica Name`.
   		- Those properties would have a prefix `replica_` adding to their filename.
	2. in a different folder:
		- same as above, but in a different folder.
  		- note that the texture file names would not have `replica_`. properties are the only difference.

1. General Rule:
	1. `converted_name.png` base texture.
	2. `converted_name.properties` properties file.

2. Bows
	1. `converted_name.png` standby base texture.
	2. `converted_name_pulling_x.png` pulling texture. `x` can be 0, 1, 2, 3 or 4.
	3. `converted_name.properties` properties file.

3. Crossbows
	1. `converted_name.png` standby base texture.
	2. `converted_name_pulling_x.png` pulling texture. `x` can be 0, 1 or 2.
	3. `converted_name_arrow.png` loaded with arrow texture.
	4. `converted_name_firework.png` loaded with firework texture.
	5. `converted_name.properties` properties file.

4. Armor (non-set armor)
	1. `converted_name_icon.png` base icon texture. (non leather / dyeable part leather)
	2. (optional - leather armor) `converted_name_icon_overlay.png` override icon texture. (non dyeable part leather)
	3. `converted_name_armor.png` base armor texture. (non leather / dyeable part leather)
	4. (optional - leather armor) `converted_name_armor_overlay.png` override armor texture. (non dyeable part leather)
	5. `converted_name_icon.properties` icon properties.
	6. `converted_name_armor.properties` armor properties.

5. Armor (set armor)
	1. icons (folder)
		1. `converted_name_icon.png` base icon texture. (non leather / dyeable part leather)
		2. (optional - leather armor) `converted_name_icon_overlay.png` override icon texture. (non dyeable part leather)
		3. `converted_name_icon.properties` icon properties.
	2. armor (folder)
		1. `converted_name_layer_1.png` base armor texture for helmet, chestplate and boots. (non leather / dyeable part leather)
		2. (optional - leather armor) `converted_name_layer_1_overlay.png` override armor texture for helmet, chestplate and boots. (non dyeable part leather)
		3. `converted_name_layer_2.png` base armor texture for leggings. (non leather / dyeable part leather)
		4. (optional - leather armor) `converted_name_layer_2_overlay.png` override armor texture for leggings. (non dyeable part leather)
		5. `converted_name_armor.properties` armor properties.
	3. extra rules:
			If there are overlapping item names, add part info like "helmet", "leggings" after `converted_name`. (see r1 t5 scout set)

6. potions (potion, splash_potion, lingering_potion) (WIP)
	1. `converted_name.png` base texture.
	2. `converted_name.properties` properties file.
	3. `converted_name_overlay.png` potion overlay file. Often empty.
	4. (optional)`converted_name_cooldown.png` cooldown texture.
	5. (optional)`converted_name_cooldown.properties` properties file. Often not potion.
	6. `converted_name.json` model file (in model folder: `optifine/cit/source_models/potions/`).

7. Shields (WIP)
	1. `converted_name.png` idle texture.
	2. `converted_name_blocking.png` blocking texture.
	3. `converted_name.properties` idle properties.
	4. `converted_name_blocking.properties` blocking properties.

8. Alchemist Utensils (WIP)
	1. `converted_name_Y.png` image of different pots inside. `Y` can be:
		1. `empty`
		2. `quarter`
		3. `half`
		4. `three_quarter`
		5. `full`
	2. `converted_name_X.properties` properties of different pots inside. `X` can be `0,1,...,12`.
	3. `converted_name_overlay.png` empty overlay

9. Custom Non-Template Models (WIP)
	No specific rules. (!!)


### Folder Structure (WIP)
For the ease of access for third party apps, the folders are structured more systematically.

For items on the API, folders are sorted by:
1. Region
2. Tier
3. Location

Each layer will have a `misc` category to store everything that is missing that particular label.

Textures that are not on the api is now in a separate folder `nonapi` under `cit`.

### Folder Naming Scheme: (WIP)
1. general rule: follow the plain.display.Name nbt tag of the item, converted.
2. cooldown consumables: ignore the cooldown files and follow the general rule.
3. set armor (tiered, uncommon, gallery armor sets): ignore any phrases that specify it's part like `helm`, `chestplate`, `greaves`, etc.

### Properties:
The rules of writing properties: (in order)

Everything should always be present unless stated optional

1. properties type: `type=armor`, `type=item`, etc.
2. base item: `matchItems=BASE_ITEM`
3. model: `model=...`
4. texture files: `texture=FILE` followed by `texture.(...)=FILE`
5. plain text: `nbt.plain.display.Name=...`
6. hope infuser (optional - if any)
7. hexed, gui, other criteria
8. weight

---
## Extra Details

### Detectable Criteria
Since there are a lot of exceptions that is best treated individually, only folders meeting certain criteria will be modified. I try to include as much as possible though.

1. If there is a .properties file with base item `bow`, `crossbow`
2. If there is a .properties file with base item `potion`, `splash_potion`, `lingering_potion` and there are less than or equal to 2 properties files.
3. If there is only one image file, excluding emissive and only one properties file and that it uses a model from `source_models` folder but not any of its subfolder.
4. If there are properties with type of armor