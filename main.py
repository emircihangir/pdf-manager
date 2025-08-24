import tkinter as tk
from tkinter import filedialog, messagebox
import re
from issues_and_errors import InputIssue, FaultyEndIndexError

# region global variables
selected_file: str | None = None
operations: dict[str, list[int]] = {}
# endregion

# region ui functions
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

    # check if there are unclosed parentheses.
    faulty_parentheses = False
    for c in _range_input:
        if c == '(': faulty_parentheses = True
        elif c == ')': faulty_parentheses = False
    if faulty_parentheses: return InputIssue.UNCLOSED_PARENTHESES

    # check if the dash character is present between parentheses.
    matches = re.findall(r'\((.*?)\)', _range_input)
    for match in matches:
        if "-" not in match: return InputIssue.NO_DASH_PRESENT

    # check if the input is empty.
    if len(_range_input) == 0: return InputIssue.EMPTY_INPUT
    # TODO: Check if the range is out of bounds by checking the pdf page size.
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
        validation_result = is_valid_range_input()
        if isinstance(validation_result, InputIssue):
            messagebox.showwarning(message=validation_result.value)
            return

    try: operations[selected_file] = parse_range_input()
    except FaultyEndIndexError as e:
        messagebox.showwarning(message=f"Faulty range '({e.args[0]})'. End index must be greater than start index.")
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

# radio button
selected_option = tk.IntVar(value=1)
radio_frame = tk.Frame(root)
radio1 = tk.Radiobutton(radio_frame, text="All pages", variable=selected_option, value=1)
radio1.pack(side="left", padx=10)
frame2 = tk.Frame(radio_frame)
radio2 = tk.Radiobutton(frame2, variable=selected_option, value=2, command=lambda: remove_placeholder(None))
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

root.mainloop()
# endregion
