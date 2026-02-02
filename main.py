import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

WINDOW_OPACITY = 0.95

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", WINDOW_OPACITY)

label = tk.Label(root, borderwidth=0, highlightthickness=0)
label.pack()

current_image = None
tk_img = None

def load_image(path, keep_position=True):
    global current_image, tk_img
    x, y = root.winfo_x(), root.winfo_y()

    current_image = Image.open(path)
    tk_img = ImageTk.PhotoImage(current_image)
    label.config(image=tk_img)

    if keep_position:
        root.geometry(f"{current_image.width}x{current_image.height}+{x}+{y}")
    else:
        root.geometry(f"{current_image.width}x{current_image.height}+200+200")



drag = {"dx": 0, "dy": 0}

def start_drag(event):
    drag["dx"] = event.x_root - root.winfo_x()
    drag["dy"] = event.y_root - root.winfo_y()

def do_drag(event):
    x = event.x_root - drag["dx"]
    y = event.y_root - drag["dy"]
    root.geometry(f"+{x}+{y}")

label.bind("<ButtonPress-1>", start_drag)
label.bind("<B1-Motion>", do_drag)

menu_win = None
opacity_var = tk.DoubleVar(value=WINDOW_OPACITY)

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

def close_menu():
    global menu_win
    if menu_win is not None and menu_win.winfo_exists():
        menu_win.destroy()
    menu_win = None

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

    btn_change = tk.Button(frame, text="Change Image…", command=lambda: (change_image(), close_menu()), anchor="w")
    btn_change.pack(fill="x")

    tk.Label(frame, text="Opacity", anchor="w").pack(fill="x", padx=8, pady=(6, 0))

    scale = tk.Scale(
        frame,
        from_=0.1, to=1.0,
        resolution=0.01,
        orient="horizontal",
        variable=opacity_var,
        command=set_opacity,
        length=180
    )
    scale.pack(padx=8, pady=6)

    tk.Frame(frame, height=1, bd=0).pack(fill="x", pady=(0, 2))

    btn_close = tk.Button(frame, text="Close", command=root.destroy, anchor="w")
    btn_close.pack(fill="x")

    menu_win.focus_force()

label.bind("<Button-3>", open_menu)  
label.bind("<Button-2>", open_menu)  

label.bind("<ButtonPress-1>", lambda e: (close_menu(), start_drag(e)), add=True)

root.mainloop()
