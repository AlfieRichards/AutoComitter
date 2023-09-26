config_version = 1.2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import getpass

# Get the current user's name
current_user = getpass.getuser()

version_file = "versions.txt"
line_number = 2


def version_writer_config():
    if not os.path.isfile(version_file):
        with open(version_file, 'a') as file:
            for _ in range(5):
                file.write('\n')

        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(config_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Created {version_file} and wrote the line at line number {line_number}.")
    else:
        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(config_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Wrote the line at line number {line_number} in {version_file}.")


def browse_file_path(i, file_paths):
    file_path = filedialog.askopenfilename()
    file_paths[i].set(file_path)


def submit(file_paths, api_key):
    # Check if any file paths are empty
    if any(not path.get() for path in file_paths):
        messagebox.showerror("Error", "Please select both file paths and the api key.")
    else:
        # Check if the file paths are valid
        invalid_paths = [path.get() for path in file_paths if not os.path.isfile(path.get())]
        if invalid_paths:
            messagebox.showerror("Error", "Invalid file paths:\n" + "\n".join(invalid_paths))
        else:
            # Write the user's input to a file
            with open("config.txt", "w") as f:
                f.write(file_paths[0].get() + "\n")
                f.write(file_paths[1].get() + "\n")
                f.write(api_key[0].get() + "\n")

            # Display a message box to inform the user
            messagebox.showinfo("Config Saved", "Configurations saved successfully!")


def run_config():
    version_writer_config()

    root = tk.Tk()
    root.title("Github Button Config")
    root.geometry("575x325")

    file_paths = [tk.StringVar() for _ in range(2)]
    api_key = [tk.StringVar() for _ in range(1)]

    # Check if GitHub Desktop executable exists
    github_desktop_path = f"C:/Users/{current_user}/AppData/Local/GitHubDesktop/GitHubDesktop.exe"
    if os.path.isfile(github_desktop_path):
        file_paths[0].set(github_desktop_path)
        messagebox.showinfo("GitHub Desktop Found", "GitHub Desktop executable found at the expected location.")

    # Check if Git executable exists
    git_path = "C:/Program Files/Git/cmd/git.exe"
    if os.path.isfile(git_path):
        file_paths[1].set(git_path)
        messagebox.showinfo("Git Found", "Git executable found at the expected location.")

    # if os.path.isfile(git_path) and os.path.isfile(github_desktop_path):
    #     submit(file_paths)  # Automatically submit the file paths

    # Heading
    tk.Label(root, text="Github Button Config", font=("Arial", 16, "bold")).grid(row=0, columnspan=3, pady=10)

    # File Path 1
    tk.Label(root, text="GitHub EXE Path:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.E, padx=10)
    tk.Entry(root, textvariable=file_paths[0], width=30).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_file_path(0, file_paths)).grid(row=1, column=2)

    # File Path 2
    tk.Label(root, text="GitHub Desktop EXE Path:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.E,
                                                                                     padx=10)
    tk.Entry(root, textvariable=file_paths[1], width=30).grid(row=2, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_file_path(1, file_paths)).grid(row=2, column=2)

    # Api key
    tk.Label(root, text="API Key:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.E, padx=10)
    tk.Entry(root, textvariable=api_key[0], width=30).grid(row=3, column=1)

    # Submit Button
    tk.Button(root, text="Submit", command=lambda: submit(file_paths, api_key), font=("Arial", 12, "bold")).grid(row=4, columnspan=3,
                                                                                                pady=20)

    # Hint
    tk.Label(root, text="The default locations are:", font=("Arial", 10), fg="gray").grid(row=5, columnspan=3,
                                                                                          pady=(0, 10))
    tk.Label(root, text=github_desktop_path, font=("Arial", 10), fg="gray").grid(row=6, columnspan=3)
    tk.Label(root, text=git_path, font=("Arial", 10), fg="gray").grid(row=7, columnspan=3)

    root.mainloop()
