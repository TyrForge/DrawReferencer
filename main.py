import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

DEFAULT_OPACITY = 0.95

root = tk.Tk()
root.overrideredirect(True)         
root.attributes("-topmost", True)   
root.attributes("-alpha", DEFAULT_OPACITY)


orig_image = None       
tk_img = None           
aspect = None           

MIN_W = 80
MIN_H = 80

label = tk.Label(root, borderwidth=0, highlightthickness=0)
label.pack()

def apply_size(w, h, x=None, y=None):
    """Resize displayed image to (w,h) and resize window. Keeps position unless x/y given."""
    global tk_img

    if orig_image is None:
        return

    w = max(MIN_W, int(w))
    h = max(MIN_H, int(h))

    resized = orig_image.resize((w, h), Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized)
    label.config(image=tk_img)

    if x is None:
        x = root.winfo_x()
    if y is None:
        y = root.winfo_y()

    root.geometry(f"{w}x{h}+{x}+{y}")

def load_image(path, keep_position=True):
    """Load new image; keep window position and current size (scaled) if possible."""
    global orig_image, aspect
    orig_image = Image.open(path)
    aspect = orig_image.width / orig_image.height

    if keep_position:
        cur_w = root.winfo_width() or orig_image.width
        cur_h = root.winfo_height() or orig_image.height

        new_w = max(MIN_W, cur_w)
        new_h = max(MIN_H, int(new_w / aspect))
        apply_size(new_w, new_h)
    else:
        apply_size(orig_image.width, orig_image.height, x=200, y=200)

menu_win = None
drag = {"dx": 0, "dy": 0}

def close_menu():
    global menu_win
    if menu_win is not None and menu_win.winfo_exists():
        menu_win.destroy()
    menu_win = None

def start_drag(event):
    close_menu()
    drag["dx"] = event.x_root - root.winfo_x()
    drag["dy"] = event.y_root - root.winfo_y()

def do_drag(event):
    x = event.x_root - drag["dx"]
    y = event.y_root - drag["dy"]
    root.geometry(f"+{x}+{y}")

label.bind("<ButtonPress-1>", start_drag)
label.bind("<B1-Motion>", do_drag)

opacity_var = tk.DoubleVar(value=DEFAULT_OPACITY)

def set_opacity(val):
    root.attributes("-alpha", float(val))

def change_image():
    path = filedialog.askopenfilename(
        title="Choose an image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp")]
    )
    if path:
        load_image(path, keep_position=True)


change_image()

def open_menu(event):
    global menu_win
    close_menu()

    menu_win = tk.Toplevel(root)
    menu_win.overrideredirect(True)
    menu_win.attributes("-topmost", True)
    menu_win.geometry(f"+{event.x_root}+{event.y_root}")

    menu_win.bind("<FocusOut>", lambda e: close_menu())
    menu_win.bind("<Escape>", lambda e: close_menu())

    frame = tk.Frame(menu_win, bd=1, relief="solid")
    frame.pack()

    tk.Button(frame, text="Change Image…", anchor="w",
              command=lambda: (change_image(), close_menu())).pack(fill="x")

    tk.Label(frame, text="Opacity", anchor="w").pack(fill="x", padx=8, pady=(6, 0))
    tk.Scale(
        frame,
        from_=0.1, to=1.0,
        resolution=0.01,
        orient="horizontal",
        variable=opacity_var,
        command=set_opacity,
        length=180
    ).pack(padx=8, pady=6)

    tk.Button(frame, text="Close", anchor="w", command=root.destroy).pack(fill="x")

    menu_win.focus_force()

label.bind("<Button-3>", open_menu)
label.bind("<Button-2>", open_menu)


GRIP = 16
resize_state = {
    "start_w": 0, "start_h": 0,
    "start_x": 0, "start_y": 0,
    "win_x": 0, "win_y": 0
}

def start_resize(event):
    close_menu()
    resize_state["start_w"] = root.winfo_width()
    resize_state["start_h"] = root.winfo_height()
    resize_state["start_x"] = event.x_root
    resize_state["start_y"] = event.y_root
    resize_state["win_x"] = root.winfo_x()
    resize_state["win_y"] = root.winfo_y()

def resize_from_right(event):
    """Bottom-right corner resize: keeps left edge fixed."""
    if orig_image is None or aspect is None:
        return

    dx = event.x_root - resize_state["start_x"]
    dy = event.y_root - resize_state["start_y"]

    cand_w = resize_state["start_w"] + dx
    cand_h = resize_state["start_h"] + dy

    if abs(dx) >= abs(dy):
        new_w = max(MIN_W, cand_w)
        new_h = max(MIN_H, int(new_w / aspect))
    else:
        new_h = max(MIN_H, cand_h)
        new_w = max(MIN_W, int(new_h * aspect))

    apply_size(new_w, new_h, x=resize_state["win_x"], y=resize_state["win_y"])

def resize_from_left(event):
    """Bottom-left corner resize: keeps right edge fixed (so x moves)."""
    if orig_image is None or aspect is None:
        return

    dx = event.x_root - resize_state["start_x"]
    dy = event.y_root - resize_state["start_y"]

    cand_w = resize_state["start_w"] - dx
    cand_h = resize_state["start_h"] + dy

    if abs(dx) >= abs(dy):
        new_w = max(MIN_W, cand_w)
        new_h = max(MIN_H, int(new_w / aspect))
    else:
        new_h = max(MIN_H, cand_h)
        new_w = max(MIN_W, int(new_h * aspect))

    old_w = resize_state["start_w"]
    new_x = resize_state["win_x"] + (old_w - new_w)

    apply_size(new_w, new_h, x=new_x, y=resize_state["win_y"])

grip_br = tk.Frame(root, width=GRIP, height=GRIP, cursor="size_nw_se")
grip_bl = tk.Frame(root, width=GRIP, height=GRIP, cursor="size_ne_sw")

grip_br.place(relx=1.0, rely=1.0, anchor="se")
grip_bl.place(relx=0.0, rely=1.0, anchor="sw")

grip_br.bind("<ButtonPress-1>", start_resize)
grip_br.bind("<B1-Motion>", resize_from_right)

grip_bl.bind("<ButtonPress-1>", start_resize)
grip_bl.bind("<B1-Motion>", resize_from_left)

root.mainloop()
