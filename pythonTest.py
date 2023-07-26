import os
import sys
import threading
import pystray
from tkinter import Tk, Text, Scrollbar
from PIL import Image, ImageDraw

if os.path.exists('logs.txt'):
    os.remove('logs.txt')

# Backup the original print function
original_print = print


# Custom function to print to both the console and the log file
def print_and_log(*args, **kwargs):
    text = " ".join(str(arg) for arg in args)
    original_print(text, **kwargs)  # Print to the console
    with open('logs.txt', 'a') as log_file:
        log_file.write(text + '\n')  # Write to the log file


# Replace the built-in print with the custom print_and_log
print = print_and_log


# Function to start the GUI and display the logs
def start_gui():
    root = Tk()
    root.title("The Github Button")

    # Create a text box to display the logs
    text_box = Text(root, wrap="none", font=("Comic Sans", 12), state="disabled")
    text_box.grid(row=0, column=0, sticky="nsew")

    # Create a vertical scrollbar for the text box
    v_scrollbar = Scrollbar(root, command=text_box.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    text_box.config(yscrollcommand=v_scrollbar.set)

    # Create a horizontal scrollbar for the text box
    h_scrollbar = Scrollbar(root, command=text_box.xview, orient='horizontal')
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    text_box.config(xscrollcommand=h_scrollbar.set)

    # Configure grid weights to make text_box resize with the window
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Function to update the logs in the GUI
    def update_logs():
        with open('logs.txt', 'r') as log_file:
            logs = log_file.read()
            text_box.config(state="normal")
            text_box.delete(1.0, "end")
            text_box.insert("end", logs)
            text_box.config(state="disabled")

        root.after(1000, update_logs)  # Update logs every 1 second

    update_logs()  # Start updating logs
    root.mainloop()

# Function to be executed when the tray icon is clicked

def on_left_click(icon, item):
    threading.Thread(target=start_gui).start()  # Run the GUI in a separate thread

def on_exit(icon, item):
    icon.stop()
    sys.exit(0)

def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


# Create an image (you can replace this with your custom icon)
# image = Image.open("path/to/your/icon.png")
image = create_image(64, 64, "black", "white")

# Create the system tray icon
icon = pystray.Icon("The Github Button", image, "The Github Button")
menu = (pystray.MenuItem("View Logs", on_left_click), pystray.MenuItem("Exit", on_exit))
icon.menu = pystray.Menu(*menu)
icon.run()
