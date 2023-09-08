import tkinter.messagebox
import zipfile
import time
from tkinter import filedialog
from PIL import ImageTk, Image
from main_iter import *

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
settings = Settings()
settings.selected_pack = tk.StringVar(value=cwd)
dst_pack = tk.StringVar(value=cwd)
status = "Status >> unselected"
settings.log_path = cwd + "/logs.txt"

# create ignore list
with open("ignore.txt", 'r') as ign:
    settings.ignore_list = list(ign.read().split("\n"))
print(settings.ignore_list)

sframe_dimension = (3, 4)
sframe_grids = [[] for i in range(sframe_dimension[0])]
# objects:
# | original pack | select |        path        | verify
# |     options   |   v    |       status       |
# |    dst pack   | select |        path        |

# events
def get_pack(r):
    global status
    global dst_pack
    global sframe_grids

    if r == 0:
        settings.selected_pack.set(tk.filedialog.askdirectory(title="choose rp", initialdir=cwd))
        try:
            src = os.listdir(settings.selected_pack.get() + "/assets/minecraft/optifine/cit")
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
        if settings.selected_pack.get() != dst_pack.get():
            settings.log_path = os.path.join(dst_pack.get(), "logs.txt")
        else:
            settings.log_path = os.path.join(os.path.join(dst_pack.get(), ".."), "logs.txt")



def start_rename():
    global cwd
    global status_label
    global status

    status = "Status >> Copying..."
    time.sleep(0.1)

    sframe_grids[1][1]["state"] = "active"
    sframe_grids[1][2].configure(text=status)

    # copy a new folder
    if settings.selected_pack.get() != dst_pack.get():
        needcopy = True
        folder = dst_pack.get() + "/generated"
    else:
        needcopy = False
        folder = dst_pack.get()
    if settings.options[0] or settings.options[1]:
        if zipfile.is_zipfile(settings.selected_pack.get()):
            ZIP = zipfile.ZipFile(settings.selected_pack.get())
            if needcopy and ("generated" not in os.listdir(dst_pack.get())):
                os.mkdir(folder)
            ZIP.extractall(folder)
        elif needcopy:
            shutil.copytree(settings.selected_pack.get(), folder)

    time.sleep(0.1)

    # run rename
    status = "Status >> Renaming..."
    sframe_grids[1][2].configure(text=status)

    readfolder(folder + "/assets/minecraft/optifine/cit", settings)

    # zipping
    if settings.options[0].get():
        if needcopy:
            zp = zipfile.ZipFile(dst_pack.get() + "/generated.zip", 'w')
        else:
            zp = zipfile.ZipFile(settings.selected_pack.get() + ".zip", 'w')
        for rt, dirs, files in os.walk(folder):
            for file in files:
                zp.write(os.path.join(rt, file), os.path.relpath(os.path.join(rt, file), folder))
        zp.close()
    if not settings.options[1].get():
        shutil.rmtree(folder)

    # ending
    status = "Status >> Conversion complete!"
    sframe_grids[1][2].configure(text=status)
    sframe_grids[1][1]["state"] = "disabled"

    tk.messagebox.showinfo(title="Conversion Complete",
                           message="Pack conversion is completed! The program will now be closed.")
    root.destroy()


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

sframe_grids[0].append(tk.Entry(select_frame, textvariable=settings.selected_pack, font=(gui_font, 10),
                                bg=font_color, fg=font_color_bg, width=path_box_length))

verify_img = ImageTk.PhotoImage(Image.open("assets/not_verified.png"), master=select_frame)
sframe_grids[0].append(tk.Label(select_frame, image=verify_img, bg=font_color_bg))
sframe_grids[0][3].image = verify_img

# row 1
sframe_grids[1].append(tk.Frame(select_frame, background=font_color_bg))

# [make zipped pack, make unzipped pack, log file]
settings.options[0].set(True)
settings.options[1].set(True)
settings.options[2].set(True)

option1 = tk.Checkbutton(sframe_grids[1][0], text="Make zipped pack", font=(gui_font, 8),
                         variable=settings.options[0], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
option2 = tk.Checkbutton(sframe_grids[1][0], text="Make unzipped pack", font=(gui_font, 8),
                         variable=settings.options[1], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
option3 = tk.Checkbutton(sframe_grids[1][0], text="Generate log file", font=(gui_font, 8),
                         variable=settings.options[2], bg=font_color_bg, fg=font_color, selectcolor=font_color_bg)
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

