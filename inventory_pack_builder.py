import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk, ImageSequence
import zipfile
import shutil
import random
import json
import sys


APP_SIZE = "760x740"

FRAME_W = 704
FRAME_H = 664

TEMP_DIR = "GeneratedInventoryPack"
ZIP_NAME = "AnimatedInventory.zip"


def resource_path(relative):
    try:
        base = sys._MEIPASS
    except Exception:
        base = Path(".").absolute()

    return str(Path(base) / relative)


DEFAULT_INVENTORY = resource_path("inventory.png")


class App:

    def __init__(self, root):

        self.root = root
        self.root.title("Inventory Pack Builder")
        self.root.geometry(APP_SIZE)
        self.root.resizable(False, False)

        self.gif_path = None
        self.inventory_path = DEFAULT_INVENTORY

        self.preview_frames = []
        self.preview_index = 0

        self.overlay = tk.BooleanVar(value=True)

        self.build_ui()

    def build_ui(self):

        top = tk.Frame(self.root)

        top.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        tk.Label(
            top,
            text="Animated GIF Preview",
            font=("Segoe UI", 16)
        ).pack()

        preview_frame = tk.Frame(
            top,
            width=520,
            height=260,
            bg="#222"
        )

        preview_frame.pack(
            pady=(10, 15)
        )

        preview_frame.pack_propagate(False)

        self.gif_label = tk.Label(
            preview_frame,
            bg="#222"
        )

        self.gif_label.pack(
            expand=True
        )

        tk.Label(
            top,
            text="Inventory Preview",
            font=("Segoe UI", 12)
        ).pack()

        inv_frame = tk.Frame(
            top,
            width=240,
            height=120
        )

        inv_frame.pack(
            pady=(8, 15)
        )

        inv_frame.pack_propagate(False)

        self.inventory_label = tk.Label(
            inv_frame
        )

        self.inventory_label.pack(
            expand=True
        )

        self.show_inventory_preview()

        tk.Checkbutton(
            top,
            text="Overlay inventory on frames",
            variable=self.overlay
        ).pack(
            pady=(0, 15)
        )

        buttons = tk.Frame(top)

        buttons.pack(
            fill="x"
        )

        tk.Button(
            buttons,
            text="Select GIF",
            height=2,
            command=self.select_gif
        ).pack(
            fill="x",
            pady=4
        )

        tk.Button(
            buttons,
            text="Replace inventory.png",
            height=2,
            command=self.replace_inventory
        ).pack(
            fill="x",
            pady=4
        )

        tk.Button(
            buttons,
            text="Create ZIP",
            height=2,
            command=self.create_zip
        ).pack(
            fill="x",
            pady=4
        )

    def select_gif(self):

        path = filedialog.askopenfilename(
            filetypes=[("GIF", "*.gif")]
        )

        if not path:
            return

        self.gif_path = path

        self.load_preview()

    def replace_inventory(self):

        path = filedialog.askopenfilename(
            filetypes=[("PNG", "*.png")]
        )

        if not path:
            return

        self.inventory_path = path

        self.show_inventory_preview()

    def show_inventory_preview(self):

        try:
            img = Image.open(self.inventory_path)

            img.thumbnail((220, 120))

            tkimg = ImageTk.PhotoImage(img)

            self.inventory_label.configure(image=tkimg)
            self.inventory_label.image = tkimg

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def load_preview(self):

        self.preview_frames.clear()

        gif = Image.open(self.gif_path)

        for frame in ImageSequence.Iterator(gif):

            img = frame.convert("RGBA")

            img.thumbnail((500, 260))

            self.preview_frames.append(
                ImageTk.PhotoImage(img)
            )

        self.preview_index = 0

        self.animate()

    def animate(self):

        if not self.preview_frames:
            return

        self.gif_label.configure(
            image=self.preview_frames[self.preview_index]
        )

        self.preview_index += 1

        if self.preview_index >= len(self.preview_frames):
            self.preview_index = 0

        self.root.after(
            60,
            self.animate
        )

    def colored_description(self):

        colors = [
            "§8",
            "§7",
            "§4",
            "§c"
        ]

        chunks = [
            "Anim",
            "ated ",
            "inv",
            "entory ",
            "by ",
            "matem",
            "atik"
        ]

        result = ""

        for c in chunks:
            result += random.choice(colors) + c

        return result

    def build_mcmeta(self):

        return {
            "pack": {
                "pack_format": 3,
                "description": self.colored_description()
            }
        }

    def create_zip(self):

        if not self.gif_path:

            messagebox.showwarning(
                "No GIF",
                "Select GIF first"
            )
            return

        try:

            temp = Path(TEMP_DIR)

            if temp.exists():
                shutil.rmtree(temp)

            assets = (
                temp
                / "assets"
                / "minecraft"
            )

            tex = (
                assets
                / "textures"
                / "gui"
                / "container"
            )

            anim = (
                assets
                / "mcpatcher"
                / "anim"
                / "inventory"
            )

            tex.mkdir(parents=True)
            anim.mkdir(parents=True)
            
            inv = (
                Image
                .open(self.inventory_path)
                .convert("RGBA")
            )

            inventory_overlay = inv.crop(
                (
                    0,
                    0,
                    FRAME_W,
                    FRAME_H
                )
            )

            gif = Image.open(self.gif_path)

            first = None

            frames = []

            for i, frame in enumerate(
                ImageSequence.Iterator(gif)
            ):

                img = (
                    frame
                    .convert("RGBA")
                    .resize(
                        (
                            FRAME_W,
                            FRAME_H
                        ),
                        Image.LANCZOS
                    )
                )

                canvas = img.copy()

                if i == 0:
                    first = canvas.copy()

                if self.overlay.get():

                    canvas.alpha_composite(
                        inventory_overlay,
                        (0,0)
                    )

                frames.append(
                    canvas
                )

            sprite = Image.new(

                "RGBA",

                (
                    FRAME_W,
                    FRAME_H * len(frames)
                )
            )

            y = 0

            for f in frames:

                sprite.paste(
                    f,
                    (
                        0,
                        y
                    )
                )

                y += FRAME_H

            sprite.save(
                anim
                / "inventory.png"
            )

            inventory_overlay.save(
                tex
                / "inventory.png"
            )

            first.save(
                temp
                / "pack.png"
            )

            props = """duration=1
w=704
h=664
x=0
y=0
from=./inventory.png
to=textures/gui/container/inventory.png
"""

            (
                anim
                / "inventory.properties"
            ).write_text(
                props,
                encoding="utf8"
            )

            (
                temp
                / "pack.mcmeta"
            ).write_text(
                json.dumps(
                    self.build_mcmeta(),
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf8"
            )

            out = (
                Path(
                    self.gif_path
                ).parent
                / ZIP_NAME
            )

            with zipfile.ZipFile(
                out,
                "w",
                zipfile.ZIP_DEFLATED
            ) as z:

                for f in temp.rglob("*"):

                    z.write(
                        f,
                        f.relative_to(temp)
                    )

            shutil.rmtree(temp)

            messagebox.showinfo(
                "Done",
                f"Created:\n{out}"
            )

        except Exception as e:

            if Path(TEMP_DIR).exists():
                shutil.rmtree(TEMP_DIR)

            messagebox.showerror(
                "Error",
                str(e)
            )


root = tk.Tk()

app = App(root)

root.mainloop()