# RP Renamer User Manual
### Introduction
This renamer is made for the Monumenta official resourcepack. For naming conventions, please check out the `README.md`.
This project aims to unify some common textures in terms of their file names, so other community projects involving the resourcepack can have an easier time accessing particular textures.

### Installation

Latest Version: https://drive.google.com/drive/folders/1evQ-97FzxabIjdaB4c9_zt329TuD2S7J?usp=sharing
unzip the downloaded file and run the executable and should be good to go!
(might need python 3? idk how it works)

### How to Use

The downloaded files are put in a folder. There will be one executable (.exe) file you can run. After launching, it would open up an interface.
- First, press the top select button to select the original texture pack you want converted. The program will check if it contains the optifine/cit folder as a check, shown at the end of the path box.
- Next, choose the options to generate unzipped pack, zipped pack and change log. 
- Then, press the bottom select button to set the destination of the files generated.
- Finally, press the adown arrow button to start converting!

TL; DR see `guide.png`

**Note: Since Python runs on a single thread, the GUI will freeze after converting is started. It is normal and has no easy way of fixing. Just wait until it is done and everything will be good.**

Extra technical information:
- The files that are generated will be put in a folder called `generated` under selected destination directory.
- If the original pack is selected as the destination, the program will, instead of copying the pack over, change the pack directly. It helps saving the copying time. **Please make sure you have a backup before doing so.** The zipped files and log will not be put in a `generated` folder in this case.
- If you find something broken, you can DM me or ping me for them, but until it is fixed, you can also add folder names to the `ignore.txt` list, so the program will ignore said folder.
- `pack_gen` folder is only there for your convenience. You can rename, use it however you want.

---

The program does not cover everything that need to be renamed. Things might need to be manually fixed. Some cases are not worth fixing because there are too few of them that it is faster to fix manually.
