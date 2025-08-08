import tkinter as tk
from tkinter import filedialog, messagebox

# region global variables
selected_file: str | None = None
# endregion

# region ui functions
def open_help_window() -> None:
    new_window = tk.Toplevel(root)
    new_window.title("Help")
    new_window.geometry("600x300")
    tk.Label(new_window, text="How do I define range?",
             anchor='w', font=("Arial", 14, "bold")).pack(fill='x', padx=10)
    _text="""With the dash (-) character. (1-10) means pages from 1 to 10 (both included).
You can add other pages by seperating them with commas. For example:
(1-4),8,6 means pages 1,2,3,4,8,6
5,2,(3-7),1 means pages 5,2,3,4,5,6,7,1"""
    tk.Label(new_window, text=_text, anchor="w", justify='left').pack(fill='x', padx=10)

def pick_file() -> str | None:
    """
    :return: The chosen file's path. Returns None if no file is selected.
    """
    filepath = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    if len(filepath) != 0: return filepath
    else: return None

def handle_file_pick() -> None:
    """
    Updates the selected_file_label content and the selected_file
    global variable with the selected file's path.
    """
    global selected_file
    file_path = pick_file()
    if file_path is not None:
        selected_file = file_path
        selected_file_label.config(text=file_path)

# noinspection PyUnusedLocal
def add_placeholder(event) -> None:
    if entry2.get() == "":
        entry2.insert(0, placeholder)
        entry2.config(fg='grey')

# noinspection PyUnusedLocal
def remove_placeholder(event) -> None:
    if entry2.get() == placeholder:
        entry2.delete(0, tk.END)
        entry2.config(fg='black')

def is_valid_range_input() -> bool:
    pass

def confirm_process() -> None:
    if selected_file is None:
        messagebox.showwarning(message="Please select a PDF file")
        return

    if selected_option.get() == 2 and not is_valid_range_input():
        messagebox.showwarning(message="Invalid range input")
        return

    listbox.insert(tk.END, selected_file)

# endregion

# region building the ui
root = tk.Tk()
root.geometry("600x500")
root.title("PDF Manager")

selected_file_label = tk.Label(root, text="No file selected")
selected_file_label.pack(pady=20, fill='x', padx=10, anchor='w')

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
placeholder = "range eg. (1-10)"
entry2.insert(0, placeholder)
entry2.config(fg='grey')
entry2.bind("<FocusIn>", remove_placeholder)
entry2.bind("<FocusOut>", add_placeholder)
frame2.pack(side="left")
radio_frame.pack(pady=2)

confirm_button = tk.Button(root, text="Confirm", command=confirm_process)
confirm_button.pack(pady=20)

help_button = tk.Button(root, text="Help", command=open_help_window)
help_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

listbox = tk.Listbox(root)
listbox.pack(padx=10, pady=10, fill='x')
root.mainloop()
# endregion