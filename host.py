host_version = 1.1
import os
import requests
import tkinter as tk
import webbrowser
from main import run_main
from config import version_writer_config
from main import version_writer_main

version_file_url = "https://alfiedev.co.uk/versions.txt"
version_file_path = "versions.txt"
version_file = "versions.txt"
line_number = 1


def version_writer():
    if not os.path.isfile(version_file):
        with open(version_file, 'a') as file:
            for _ in range(5):
                file.write('\n')

        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(host_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Created {version_file} and wrote the line at line number {line_number}.")
    else:
        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(host_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Wrote the line at line number {line_number} in {version_file}.")


def check_for_updates(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            downloaded_version_file = response.text

            with open(version_file_path, 'r') as file:
                lines = file.readlines()

            lines = [line.strip() for line in lines if line.strip()]
            downloaded_version_file = downloaded_version_file.strip()  # Remove leading/trailing whitespace
            downloaded_version_list = [line.rstrip() for line in downloaded_version_file.split('\n') if line.strip()]

            if lines != downloaded_version_list:
                print(lines)
                print(downloaded_version_list)
                # show the update thing
                show_update_popup()
            else:
                # run main
                run_main()

        else:
            print("Failed to fetch update.")
    except requests.exceptions.RequestException as e:
        print("Error occurred during update check:", e)


def show_update_popup():
    def open_webpage():
        webbrowser.open('https://alfiedev.co.uk/GithubButtonInstaller.exe')  # Replace with the URL you want to open

    # Create a new window
    popup = tk.Tk()
    popup.title("Update Required")

    # Message label
    message_label = tk.Label(popup, text="An update is available. Please update your application.")
    message_label.pack(pady=10)

    # Button to open the webpage
    button = tk.Button(popup, text="Update", command=open_webpage)
    button.pack(pady=10)

    # Run the popup window
    popup.mainloop()


version_writer()
version_writer_config()
version_writer_main()

check_for_updates(version_file_url)
