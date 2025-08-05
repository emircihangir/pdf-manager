import tkinter as tk
from tkinter import filedialog

# region ui functions
def pick_file() -> str | None:
    """
    :return: The chosen file's path. Returns None if no file is selected.
    """
    filepath = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    if len(filepath) != 0: return filepath
    else: return None

def handle_file_pick() -> None:
    """
    Updates the selected_file_label content with the selected file's path.
    """
    file_path = pick_file()
    if file_path is not None: selected_file_label.config(text=file_path)

def add_placeholder(event) -> None:
    if entry2.get() == "":
        entry2.insert(0, placeholder)
        entry2.config(fg='grey')

def remove_placeholder(event) -> None:
    if entry2.get() == placeholder:
        entry2.delete(0, tk.END)
        entry2.config(fg='black')
# endregion

# region building the ui
root = tk.Tk()
root.geometry("600x400")
root.title("PDF Manager")

selected_file_label = tk.Label(root, text="No file selected")
selected_file_label.pack(pady=20)

pick_button = tk.Button(root, text="Select File", command=handle_file_pick)
pick_button.pack(pady=20)

selected_option = tk.IntVar(value=1)
radio_frame = tk.Frame(root)
radio1 = tk.Radiobutton(radio_frame, text="All pages", variable=selected_option, value=1)
radio1.pack(side="left", padx=10)
frame2 = tk.Frame(radio_frame)
radio2 = tk.Radiobutton(frame2, variable=selected_option, value=2)
radio2.pack(side="left")
entry2 = tk.Entry(frame2, width=15)
entry2.pack(side="left", padx=0)
placeholder = "range eg. 1-10"
entry2.insert(0, placeholder)
entry2.config(fg='grey')
entry2.bind("<FocusIn>", remove_placeholder)
entry2.bind("<FocusOut>", add_placeholder)
frame2.pack(side="left")
radio_frame.pack(pady=2)

confirm_button = tk.Button(root, text="Confirm", command=handle_file_pick)
confirm_button.pack(pady=20)

help_button = tk.Button(root, text="Help")
help_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

root.mainloop()
# endregion