# Monumenta_RP_Renamer
Renaming standards and conversions of the current resource pack.

# File Naming Rules

### File-Style renaming
This will convert names into only using `a-z`, `0-9` and `_`.
Refer to the converted name as `Converted_Name` and the non-converted as `Name`.

Rules:
1. `(space)` or `-` -> `_`
2. `'`, `$` or other signs -> nothing

### In-Folder Format:

- Every non-emissive `.png` files can have emissive file with `_e` appended right before `.png`.
	- Ex. `Converted_Name_e.png`

- Every `.png` files can have an animation file with `.mcmeta` after its `.png`.
	- Ex. `Converted_Name.png.mcmeta`

- The way to add replica:
	1. in the same folder as the non-replica:
 		- duplicate all properties and change the plain text to `Replica Name`.
   		- Those properties would have a prefix `replica_` adding to their filename.
	2. in a different folder:
		- same as above, but in a different folder.
  		- note that the texture file names would not have `replica_`. properties are the only difference.

1. General Rule:
	1. `Converted_Name.png` base texture.
	2. `Converted_Name.properties` properties file.

2. Bows
	1. `Converted_Name.png` standby base texture.
	2. `Converted_Name_pulling_x.png` pulling texture. `x` can be 0, 1, 2, 3 or 4.
	3. `Converted_Name.properties` properties file.

3. Crossbows
	1. `Converted_Name.png` standby base texture.
	2. `Converted_Name_pulling_x.png` pulling texture. `x` can be 0, 1 or 2.
	3. `Converted_Name_arrow.png` loaded with arrow texture.
	4. `Converted_Name_firework.png` loaded with firework texture.
	5. `Converted_Name.properties` properties file.

4. Armor (non-set armor)
	1. `Converted_Name_icon.png` base icon texture. (non leather / dyeable part leather)
	2. (optional - leather armor) `Converted_Name_icon_overlay.png` override icon texture. (non dyeable part leather)
	3. `Converted_Name_armor.png` base armor texture. (non leather / dyeable part leather)
	4. (optional - leather armor) `Converted_Name_armor_overlay.png` override armor texture. (non dyeable part leather)
	5. `Converted_Name_icon.properties` icon properties.
	6. `Converted_Name_armor.properties` armor properties.

5. Armor (set armor)
	1. icons (folder)
		1. `Converted_Name_icon.png` base icon texture. (non leather / dyeable part leather)
		2. (optional - leather armor) `Converted_Name_icon_overlay.png` override icon texture. (non dyeable part leather)
		3. `Converted_Name_icon.properties` icon properties.
	2. armor (folder)
		1. `Converted_Name_layer_1.png` base armor texture for helmet, chestplate and boots. (non leather / dyeable part leather)
		2. (optional - leather armor) `Converted_Name_layer_1_overlay.png` override armor texture for helmet, chestplate and boots. (non dyeable part leather)
		3. `Converted_Name_layer_2.png` base armor texture for leggings. (non leather / dyeable part leather)
		4. (optional - leather armor) `Converted_Name_layer_2_overlay.png` override armor texture for leggings. (non dyeable part leather)
		5. `Converted_Name_armor.properties` armor properties.
	3. extra rules:
			If there are overlapping item names, add part info like "helmet", "leggings" after `Converted_Name`. (see r1 t5 scout set)

6. potions (potion, splash_potion, lingering_potion) (WIP)
	1. `potion.png` base texture.
	2. `Converted_Name.properties` properties file.
	3. `potion_overlay.png` potion overlay file. Often empty.
	4. (optional)`potion_cooldown.png` cooldown texture.
	5. (optional)`Converted_Name_cooldown.properties` properties file.
	6. (in model folder)`Converted_Name.json` model file.

7. Shields (WIP)
	1. `Converted_Name.png` idle texture.
	2. `Converted_Name_blocking.png` blocking texture.
	3. `Converted_Name.properties` idle properties.
	4. `Converted_Name_blocking.properties` blocking properties.

8. Alchemist Utensils (WIP)
	1. `Converted_Name_Y.png` image of different pots inside. `Y` can be:
		1. `empty`
		2. `quarter`
		3. `half`
		4. `three_quarter`
		5. `full`
	2. `Converted_Name_X.properties` properties of different pots inside. `X` can be `0,1,...,12`.
	3. `Converted_Name_overlay.png` empty overlay

9. Custom Non-Template Models (WIP)
	No specific rules. (!!)


### Folder Naming Scheme:
1. general rule: follow the plain.display.Name nbt tag of the item, converted.
2. cooldown consumables: ignore the cooldown files and follow the general rule.
3. set armor (tiered, uncommon, gallery armor sets): ignore any phrases that specify it's part like `helm`, `chestplate`, `greaves`, etc.

### Properties:
The rules of writing properties: (in order)

1. properties type: `type=armor`, ignored if the type is `item`.
2. base item: `items=BASE_ITEM`
3. model: `model=...`
4. texture files: `texture=FILE` followed by `texture.(...)=FILE`
5. plain text: `nbt.plain.display.Name=...`
6. hope infuser
7. weight