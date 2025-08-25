import tkinter as tk
from tkinter import filedialog, messagebox
import re
from issues_and_errors import InputIssue, FaultyEndIndexError, ExceedingIndexError
from pypdf import PdfWriter, PdfReader
from pathlib import Path
from uuid import uuid1

# region global variables
selected_file: str | None = None
"""Represents the selected file's path as a string."""

operations: list[tuple[str, list[int]]] = []
"""
A list that contains tuple with two elements.
The first element of the tuple is a string representing the file's path.
The second element is a list of int representing the page numbers.
"""
# endregion

# region ui functions
def clear_list() -> None:
    """
    Clears the list and the global 'operations' variable.
    :return: None
    """
    global operations
    operations = []
    listbox.delete(0, tk.END)

def show_snackbar(message: str, duration: int = 3000):
    snackbar = tk.Toplevel(root)
    snackbar.overrideredirect(True)  # remove window decorations
    snackbar.configure(bg="#323232")

    # position it at the bottom center of the root window
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    snackbar.geometry(f"+{root_x + root_width//2 - 100}+{root_y + root_height - 60}")

    label = tk.Label(snackbar, text=message, fg="white", bg="#323232", padx=20, pady=10)
    label.pack()

    # destroy after duration ms
    # noinspection PyTypeChecker
    snackbar.after(duration, snackbar.destroy)


def open_help_window() -> None:
    new_window = tk.Toplevel(root)
    new_window.title("Help")
    new_window.geometry("600x300")
    tk.Label(new_window, text="How do I define range?",
             anchor='w', font=("Arial", 14, "bold")).pack(fill='x', padx=10)
    _text = """With the dash (-) character. (1-10) means pages from 1 to 10 (both included).
You can add other pages by separating them with commas. For example:
(1-4),8,6 means pages 1,2,3,4,8,6
5,2,(3-7),1 means pages 5,2,3,4,5,6,7,1"""
    tk.Label(new_window, text=_text, anchor="w", justify='left').pack(fill='x', padx=10)


def pick_file() -> str | None:
    """
    :return: The chosen file's path. Returns None if no file is selected.
    """
    filepath = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    if len(filepath) != 0:
        return filepath
    else:
        return None


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
    if range_input.get() == "":
        range_input.insert(0, placeholder)
        range_input.config(fg='grey')


# noinspection PyUnusedLocal
def remove_placeholder(event) -> None:
    if range_input.get() == placeholder:
        range_input.delete(0, tk.END)
        range_input.config(fg='black')


def is_valid_range_input() -> bool | InputIssue:
    _range_input = clean_range_input()

    # Check if there are unclosed parentheses.
    faulty_parentheses = False
    for c in _range_input:
        if c == '(': faulty_parentheses = True
        elif c == ')': faulty_parentheses = False
    if faulty_parentheses: return InputIssue.UNCLOSED_PARENTHESES

    # Check if the dash character is present between parentheses.
    matches = re.findall(r'\((.*?)\)', _range_input)
    for match in matches:
        if "-" not in match: return InputIssue.NO_DASH_PRESENT

    # Check if the input is empty.
    if len(_range_input) == 0: return InputIssue.EMPTY_INPUT

    # TODO: User must not enter zero.


    # Check for invalid characters.
    for c in _range_input:
        if c in "(),-": continue # These characters are allowed.

        try: int(c)
        except ValueError: return InputIssue.INVALID_CHARACTER_PRESENT

    # Check if the range is out of bounds.
    page_count = len(PdfReader(selected_file).pages)
    for page_number in parse_range_input():
        if page_number + 1 > page_count:
            raise ExceedingIndexError(page_count)

    return True


def clean_range_input() -> str:
    """
    Removes space characters, and the leading and trailing commas.
    :return: The cleaned version of range_input.
    """
    _range_input = range_input.get()  # make a copy of input value
    _range_input = _range_input.replace(' ', '')  # remove space characters
    _range_input = _range_input.strip(',')  # remove leading and trailing commas if present
    return _range_input


def parse_range_input() -> list[int]:
    """
    Converts range input to a list containing page numbers.
    :return: A list of numbers representing page numbers. If the option "All Pages" is selected, returns a list that just contains the number -1.
    """
    if selected_option.get() == 1:  # "All Pages" option is selected.
        return [-1]
    else:  # Custom range is entered.
        result: list[int] = []
        range_input_split = clean_range_input().split(',')
        for n in range_input_split:
            if n.startswith("(") and n.endswith(")"): # Is a range eg. (4-10)
                n = n.strip("()")  # Remove parentheses.
                start, end = map(int, n.split("-"))
                end += 1 # Include end page in range.
                if end <= start: raise FaultyEndIndexError(n)
                result.extend(range(start, end))
            else: # Is a number.
                result.append(int(n))

        result = [x - 1 for x in result]  # Page index must start with 0, while the user input starts with one.
        return result


def confirm_process() -> None:
    """
    Modifies the operations variable and adds the selected file path to listbox.
    """
    global operations
    if selected_file is None:
        messagebox.showwarning(message="Please select a PDF file")
        return

    # validate the range input.
    if selected_option.get() == 2:
        try: validation_result = is_valid_range_input()
        except ExceedingIndexError as e:
            messagebox.showwarning(message=f"The selected file has {e.args[0]} pages, but the range input exceeds that number.")
            return

        if isinstance(validation_result, InputIssue):
            messagebox.showwarning(message=validation_result.value)
            return

    try: operations.append((selected_file, parse_range_input()))
    except FaultyEndIndexError as e:
        messagebox.showwarning(message=f"Faulty range '({e.args[0]})'. End index must be greater than start index.")
        return

    pages = "All pages"
    if selected_option.get() == 2: # Custom range is defined.
        pages = range_input.get()
    listbox.insert(tk.END, f"{selected_file}\t{pages}")


def finish_process() -> None:
    """
    Reads the value of the global 'operations' variable and executes the PDF manipulation functions.
    :return: None
    """

    # Check if the operations list is empty.
    if len(operations) == 0:
        messagebox.showwarning(message="Please confirm a process first.")
        return

    writer = PdfWriter()
    for file_path, pages in operations:
        if pages[0] == -1: writer.append(file_path) # Option 'All Pages' is selected.
        else:
            writer.append(file_path, pages=pages) # Custom range is defined.
    output_path: str = str(Path.home() / "Downloads" / f"output{uuid1().hex[:5]}.pdf")
    writer.write(output_path)
    writer.close()

    show_snackbar(f"File saved to {output_path}")
# endregion

# region building the ui
root = tk.Tk()
root.geometry("600x500")
root.title("PDF Manager")

selected_file_label = tk.Label(root, text="No file selected")
selected_file_label.pack(pady=20, fill='x', padx=10, anchor='w')

pick_button = tk.Button(root, text="Select File", command=handle_file_pick)
pick_button.pack(pady=20)

# radio button
selected_option = tk.IntVar(value=1)
radio_frame = tk.Frame(root)
radio1 = tk.Radiobutton(radio_frame, text="All pages", variable=selected_option,
                        value=1, command=lambda: root.focus_set())
radio1.pack(side="left", padx=10)
frame2 = tk.Frame(radio_frame)
radio2 = tk.Radiobutton(frame2, variable=selected_option,
                        value=2, command=lambda: remove_placeholder(None))
radio2.pack(side="left")
range_input = tk.Entry(frame2, width=15)
range_input.pack(side="left", padx=0)
placeholder = "range eg. (1-10)"
range_input.insert(0, placeholder)
range_input.config(fg='grey')
range_input.bind("<FocusIn>", remove_placeholder)
range_input.bind("<FocusOut>", add_placeholder)
frame2.pack(side="left")
radio_frame.pack(pady=2)

# confirm button
confirm_button = tk.Button(root, text="Confirm", command=confirm_process)
confirm_button.pack(pady=20)

# help button
help_button = tk.Button(root, text="Help", command=open_help_window)
help_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

# listbox and scrollbar
listbox_frame = tk.Frame(root)
listbox_frame.pack(padx=10, pady=10, fill='x')
listbox = tk.Listbox(listbox_frame, height=8)
listbox.pack(side="left", fill="x", expand=True)
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)

# frame for horizontal buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# clear list button
clear_list_button = tk.Button(button_frame, text="Clear list", command=clear_list)
clear_list_button.pack(side="left", padx=10)

# finish button
finish_button = tk.Button(button_frame, text="Finish", command=finish_process)
finish_button.pack(side="left", padx=30)

root.mainloop()
# endregion
