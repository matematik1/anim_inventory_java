
import random, shutil, zipfile, tkinter as tk
from tkinter import filedialog,messagebox
from pathlib import Path
from PIL import Image,ImageSequence,ImageTk

FRAME_W=704
FRAME_H=664
MC=["8","7","4","c"]

def desc():
    text="Animated inventory by matematik"

    chunks=[]
    i=0
    while i<len(text):
        n=random.randint(4,8)
        chunks.append(text[i:i+n])
        i+=n

    cols=random.sample(MC,random.randint(3,5))

    out=""
    for i,c in enumerate(chunks):
        out+="§"+cols[i%len(cols)]+c
    return out

def mcmeta():
    return """{
  "pack": {
     "pack_format": 3,
     "description": "%s"
  }
}
""" % desc()

def resource(name):
    return Path(__file__).parent/name

def build(gif,inv=None):
    gif=Path(gif)
    temp=gif.parent/"GeneratedInventoryPack"

    if temp.exists():
        shutil.rmtree(temp)

    (temp/"assets/minecraft/textures/gui/container").mkdir(parents=True)
    (temp/"assets/minecraft/mcpatcher/anim/inventory").mkdir(parents=True)

    frames=[]

    for fr in ImageSequence.Iterator(Image.open(gif)):
        img=fr.convert("RGBA")
        img=img.resize((FRAME_W,FRAME_H),Image.Resampling.LANCZOS)
        frames.append(img)

    frames[0].save(temp/"pack.png")

    (temp/"pack.mcmeta").write_text(
        mcmeta(),
        encoding="utf-8"
    )

    shutil.copy(
        inv if inv else resource("inventory.png"),
        temp/"assets/minecraft/textures/gui/container/inventory.png"
    )

    sheet=Image.new(
        "RGBA",
        (FRAME_W,FRAME_H*len(frames))
    )

    for i,f in enumerate(frames):
        sheet.paste(f,(0,i*FRAME_H))

    sheet.save(
        temp/"assets/minecraft/mcpatcher/anim/inventory/inventory.png"
    )

    (temp/"assets/minecraft/mcpatcher/anim/inventory/inventory.properties").write_text(
"""duration=1
w=704
h=664
x=0
y=0

from=./inventory.png
to=textures/gui/container/inventory.png
"""
)

    out=gif.parent/"AnimatedInventory.zip"

    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for f in temp.rglob("*"):
            z.write(f,f.relative_to(temp))

    shutil.rmtree(temp)

    return out

class App:
    def __init__(self):
        self.root=tk.Tk()
        self.root.geometry("550x500")
        self.root.title("Inventory Pack Builder")

        self.gif=None
        self.inv=None

        self.preview=tk.Label(
            self.root,
            text="Select GIF",
            width=60,
            height=18
        )
        self.preview.pack()

        tk.Button(
            self.root,
            text="Select GIF",
            command=self.pick
        ).pack(fill="x")

        tk.Button(
            self.root,
            text="Replace inventory.png",
            command=self.pick_inv
        ).pack(fill="x")

        tk.Button(
            self.root,
            text="Create ZIP",
            command=self.create
        ).pack(fill="x")

    def pick(self):
        p=filedialog.askopenfilename(
            filetypes=[("GIF","*.gif")]
        )
        if not p:return

        self.gif=p

        img=next(
            ImageSequence.Iterator(
                Image.open(p)
            )
        ).convert("RGB")

        img.thumbnail((480,320))

        self.tk=ImageTk.PhotoImage(img)

        self.preview.configure(
            image=self.tk,
            text=""
        )

    def pick_inv(self):
        self.inv=filedialog.askopenfilename(
            filetypes=[("PNG","*.png")]
        )

    def create(self):
        if not self.gif:
            return

        out=build(
            self.gif,
            self.inv
        )

        messagebox.showinfo(
            "Done",
            str(out)
        )

App().root.mainloop()
