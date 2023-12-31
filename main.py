main_version = 2.0
import ctypes
import platform
import os
import sys
import time
import requests
import keyboard
import subprocess
from tiktoken_ext import openai_public
import tiktoken_ext
import tiktoken
from plyer import notification
import threading
import queue
import pystray

import win32con
from win32gui import GetWindowText, GetForegroundWindow
from tkinter import Tk, Text, Scrollbar
from PIL import Image, ImageDraw, ImageTk
import win32gui, win32com.client
import win32clipboard

from config import run_config

import openai

supported_extensions_path = "supported_extensions.txt"
shell = win32com.client.Dispatch("WScript.Shell")
default_directory = os.getcwd()

config_file = "config.txt"
version_file = "versions.txt"
line_number = 3

# TRAY THINGS
# iterating log files
os.chdir(default_directory)


def get_new_filename(directory, basename):
    counter = 1
    while True:
        new_filename = os.path.join(directory, f"{basename}-{counter}.txt")
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1


def rename_logs_file(default_directory):
    print(default_directory)
    old_filename = os.path.join(default_directory, 'logs.txt')
    if os.path.exists(old_filename):
        new_filename = get_new_filename(default_directory, 'logs')
        os.rename(old_filename, new_filename)
        print(f"Renamed '{old_filename}' to '{new_filename}'")


rename_logs_file(default_directory)

# Backup the original print function
original_print = print
# Global flag to signal threads to stop
exit_flag = False


# Custom function to print to both the console and the log file
def print_and_log(*args, **kwargs):
    text = " ".join(str(arg) for arg in args)
    original_print(text, **kwargs)  # Print to the console
    with open(default_directory + '\logs.txt', 'a') as log_file:
        log_file.write(text + '\n')  # Write to the log file
        log_file.flush()  # Flush the buffer to ensure immediate write
        # log_file.close()  # Close the file after writing and save it


# Replace the built-in print with the custom print_and_log
print = print_and_log


# Function to start the GUI and display the logs
def start_gui():
    root = Tk()
    root.title("The Github Button")

    ico = Image.open(default_directory + '\icon.png')
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)

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
    def update_logs(old_logs):
        # Get the current vertical scroll position
        v_scroll_position = text_box.yview()[0]

        with open(default_directory + '\logs.txt', 'r') as log_file:
            logs = log_file.read()

        if old_logs != logs:
            text_box.config(state="normal")
            text_box.delete(1.0, "end")
            text_box.insert("end", logs)

            # Restore the previous vertical scroll position
            text_box.yview_moveto(v_scroll_position)

            text_box.config(state="disabled")

        root.after(1000, update_logs, logs)  # Update logs every 1 second with the new logs

    # Initialize old_logs
    old_logs = ""

    update_logs(old_logs)  # Start updating logs with initial value
    root.mainloop()


# Function to be executed when the tray icon is clicked

def on_left_click(icon, item):
    threading.Thread(target=start_gui).start()  # Run the GUI in a separate thread


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


# TRAY THINGS

def version_writer_main():
    if not os.path.isfile(version_file):
        with open(version_file, 'a') as file:
            for _ in range(5):
                file.write('\n')

        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(main_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Created {version_file} and wrote the line at line number {line_number}.")
    else:
        with open(version_file, 'r') as file:
            lines = file.readlines()

        lines[line_number - 1] = str(main_version) + '\n'

        with open(version_file, 'w') as file:
            file.writelines(lines)

        print(f"Wrote the line at line number {line_number} in {version_file}.")


def notify(text):
    notification.notify(
        # title of the notification,
        title="AI Commit Writer",
        # the body of the notification
        message=text, )


def select_window_by_name(window_name, EXE, git_executable, api_key):
    start_time = time.time()

    exe_path = EXE

    subprocess.run(exe_path)

    window_name = "GitHub Desktop"

    while True:
        window_handle = win32gui.FindWindow(None, window_name)
        if window_handle == 0:
            print(f"Window '{window_name}' not found.")
        else:
            # shell.SendKeys(' ')  # Undocks my focus from Python IDLE
            win32gui.SetForegroundWindow(window_handle)
            win32gui.BringWindowToTop(window_handle)
            break

        if time.time() - start_time > 3:
            break

    start_time = time.time()
    while True:
        active_window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(active_window_handle)
        if window_title != "GitHub Desktop":
            print(window_title)
        else:
            return

        if time.time() - start_time > 3:
            break


def is_git_installed(EXE, git_executable, api_key):
    try:
        result = subprocess.run([git_executable, '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def on_keypress(event, EXE, git_executable, api_key):
    if event.event_type == keyboard.KEY_DOWN:
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('c'):
            select_github_desktop(EXE, git_executable, api_key)


def select_github_desktop(EXE, git_executable, api_key):
    select_window_by_name("GitHub Desktop", EXE, git_executable, api_key)
    time.sleep(0.5)

    if GetWindowText(GetForegroundWindow()) == "GitHub Desktop":
        do_commit(EXE, git_executable, api_key)
    else:
        print("failed to select github desktop")


def type_and_submit(var1, var2):
    active_window_handle = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(active_window_handle)

    if window_title == "GitHub Desktop":
        keyboard.press_and_release('ctrl+1')
        time.sleep(0.05)
        keyboard.press_and_release('ctrl+g')
        time.sleep(0.2)

        # title
        keyboard.write(var1)
        time.sleep(0.05)
        keyboard.press_and_release('tab')
        time.sleep(0.01)
        # summary
        keyboard.write(var2)
        time.sleep(0.05)

        keyboard.press_and_release('tab')
        time.sleep(0.01)
        keyboard.press_and_release('tab')
        time.sleep(0.01)
        keyboard.press_and_release('enter')
        time.sleep(0.01)
        keyboard.press_and_release('ctrl+2')


def send_changes_request(request, token_count):
    if token_count == 4096:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-3.5-turbo-16k"

    completion = openai.ChatCompletion.create(  # Change the function Completion to ChatCompletion
        model=model,
        messages=[  # Change the prompt parameter to the messages parameter
            {'role': 'system',
             'content': "You are a programmer working in a team of developers. Your job is to neatly fillout the summarys for their github commits in a way which their boss can understand. To keep your team happy, Prioritise not missing files (modified or new) as this is bad and can lead to project delays. To help the boss understand the changes, use simple language and avoid saying code. Make sure to mention any key updates or bug fixes that were implemented. Remember, the summary should provide a high-level overview of each commit, outlining the main changes made. Never skip any files"},
            {'role': 'user', 'content': request}
        ],
        temperature=0.7
    )
    content = completion['choices'][0]['message']['content'].strip('"')
    # print(content)
    input_cost = ((count_tokens(request, "cl100k_base")) / 1000) * 0.0015
    output_cost = ((count_tokens(content, "cl100k_base")) / 1000) * 0.002
    print(request)
    print("Total cost: $" + str((input_cost + output_cost)))
    print("Model used: " + model)
    return content


def send_title_request(request, token_count):
    if token_count > 4096:
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-3.5-turbo-16k"

    completion = openai.ChatCompletion.create(  # Change the function Completion to ChatCompletion
        model=model,
        messages=[  # Change the prompt parameter to the messages parameter
            {'role': 'system',
             'content': 'You are a simple system that when given a summary of changes to a project produces a short simple and effective title. If the main change is a new methods just say its name. If things have been fixed feel free to say various bug fixes. Dont be too specific such as saying"Added player assignment in SettingsMenu" . If its like that just say small changes were made. If all the changes are correlating such as all being about logging. Say changes to the log system. Every message you recieve is one of these summaries and you are to respond with a title and nothing else Try to not write more than 5 words'},
            {'role': 'user', 'content': request}
        ],
        temperature=0.7
    )
    content = completion['choices'][0]['message']['content'].strip('"')
    # print(content)
    input_cost = ((count_tokens(request, "cl100k_base")) / 1000) * 0.0015
    output_cost = ((count_tokens(content, "cl100k_base")) / 1000) * 0.002
    print(request)

    # Format the costs to have 16 decimal places
    formatted_input_cost = "{:.16f}".format(input_cost)
    formatted_output_cost = "{:.16f}".format(output_cost)

    print("Total cost: $" + str((formatted_input_cost + formatted_output_cost)))

    print("Model used: " + model)
    return content


# solves issue with not working properly on US or other keyboards
def get_keyboard_layout():
    # Load the user32.dll library
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)

    # Retrieve the layout name as a string
    lid = klid & (2 ** 16 - 1)
    lid_hex = hex(lid)

    if lid_hex == hex(0x409):
        print("america")
        return '`'  # American keyboard layout
    else:
        print("europe")
        print(lid_hex)
        return "'"  # Non-American keyboard layout


# get windows version
def check_build_number():
    platform_info = platform.platform()
    x = platform_info.split("-")[-2]
    z = x.split(".")[-1]
    print("ver: " + str(z))
    if int(z) > 22000:
        return True
    else:
        return False


def get_filepath():
    start_time = time.time()

    while True:
        active_window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(active_window_handle)
        if window_title != "GitHub Desktop":
            print(window_title)
        else:
            break

        if time.time() - start_time > 3:
            break

    keyboard.press_and_release("ctrl+" + get_keyboard_layout())
    print("press 1")
    # time.sleep(1)

    active_window_handle = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(active_window_handle)
    window_name = "Command Prompt"

    start_time = time.time()
    while True:
        window_handle = win32gui.FindWindow(None, window_name)
        if window_handle == 0:
            print(f"Window '{window_name}' not found.")
        else:
            window_name = win32gui.GetWindowText(window_handle)
            print("Window Name:", window_name)

            active_window_handle = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(active_window_handle)

            if window_title != "Command Prompt":
                # shell.SendKeys(' ')  # Undocks my focus from Python IDLE
                win32gui.SetForegroundWindow(window_handle)
                win32gui.BringWindowToTop(window_handle)
            break

        if time.time() - start_time > 3:
            break

    start_time = time.time()
    while True:
        active_window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(active_window_handle)
        if window_title != "Command Prompt":
            print(window_title)
        else:
            time.sleep(0.3)
            if check_build_number():
                keyboard.press_and_release('ctrl+shift+a')
                print("press 2")
            else:
                keyboard.press_and_release('ctrl+a')
                print("press 3")

            time.sleep(0.1)
            keyboard.press_and_release('ctrl+c')
            print("press 4")
            time.sleep(0.1)

            win32clipboard.OpenClipboard()
            clipboard_text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
            win32clipboard.CloseClipboard()
            clipboard_text = clipboard_text.decode('utf-8')  # Assuming UTF-8 encoding

            win32gui.PostMessage(active_window_handle, win32con.WM_CLOSE, 0, 0)

            cleaned_text = clipboard_text.split(") ", 1)[-1]
            # Remove the trailing ">"
            cleaned_text = cleaned_text.strip()
            cleaned_text = cleaned_text[:-1]

            break

        if time.time() - start_time > 3:
            return

    return cleaned_text


def filter_text_files(file_list):
    os.chdir(default_directory)
    # Read the supported extensions from a text file
    with open(supported_extensions_path, 'r') as f:
        supported_extensions = f.read().splitlines()

    # Filter the file list to include only text files
    # filtered_files = [file.split('/')[-1] for file in file_list if
    #                   file.strip().lower().endswith(tuple(supported_extensions))]
    filtered_files = [file.split('/')[-1].strip() for file in file_list if
                      file.strip().lower().endswith(tuple(supported_extensions))]

    return filtered_files


def get_changed_files(repo_path, EXE, git_executable, api_key):
    os.chdir(repo_path)
    result = subprocess.run(['cd', repo_path, '&&', git_executable, 'status', '--porcelain'], shell=True,
                            capture_output=True)

    # Check if the command encountered an error
    if result.returncode != 0:
        # An error occurred
        print("An error occurred while executing the command.")
        print("Error Message:", result.stderr.decode().strip())
        return []

    # Parse the output to extract the file names
    changed_files = []
    for line in result.stdout.splitlines():
        # line = line.encode('utf-8')
        if line.startswith((b' M ', b'?? ', b' D ', b'A  ')):
            file_name = line[2:].decode('utf-8')
            file_name = file_name.replace('"', "")
            if not file_name.startswith(' '):
                file_name = ' ' + file_name
            changed_files.append(file_name)

    return changed_files


def get_individual_changes(file_path, changed_files):
    individual_changes = {}

    # Iterate over the changed files
    for file in changed_files:
        # Search for the file within the file_path and its subfolders
        for root, dirs, files in os.walk(file_path):
            if file in files:
                print("File Found: " + file)
                # Construct the absolute path to the file
                file_abs_path = os.path.join(root, file)

                # Enclose the file path in double quotation marks
                file_abs_path_quoted = f"{file_abs_path}"

                # Change working directory to file_path
                os.chdir(file_path)

                # Execute the git diff command to retrieve the changes
                cmd = ['git', 'diff', file_abs_path_quoted]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=file_path)

                # Check if the command encountered an error
                if result.returncode != 0:
                    # An error occurred
                    print("An error occurred while executing the command.")
                    print("Error Message:", result.stderr)
                    return []

                # Extract the + and - lines from the git diff output
                changes = [line for line in result.stdout.splitlines() if
                           line.startswith(('+', '-')) and not line.startswith(('--- a/', '+++ b/'))]

                # Store the changes in the dictionary with the file name as the key
                if (changes) == []:
                    changes = [
                        '+   This file  ' + file + " Is completely new. Please make sure to Say that you created it\n\n"]
                individual_changes[file] = changes

                break  # Stop searching once the file is found

    return individual_changes


def convert_list_to_lines(input_list):
    lines = '\n'.join(input_list)
    return lines


def count_tokens(input_text, encoding_name):
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(input_text))
    return num_tokens


def gpt_summary(changes, file_path):
    summaries = []
    token_count = 0

    for file, changes_list in changes.items():
        # Search for the file within the file_path and its subfolders
        for root, dirs, files in os.walk(file_path):
            if file in files:
                # Construct the absolute path to the file so that we can open it
                file_abs_path = os.path.join(root, file)

                # Read the original file text
                with open(file_abs_path, 'r', encoding='utf-8-sig') as f:
                    original_text = f.read()

                # Format the original file and changes into the summary string
                summary = f"\n\n Here is the full file for context: \n {original_text} \n \n and here are the changes which were made: \n {', '.join(changes_list)}"
                if file != list(changes.keys())[-1]:
                    summary += " \n\n, summarize this in the shortest way possible, the next object is below which you must also summarize. If the changes do not say it was created, do not say it was created."

                # Check token count
                token_count += count_tokens(summary, "cl100k_base")
                summaries.append(summary)

                break  # Stop searching once the file is found

    return summaries


def split_summaries(summaries, token_limit):
    split_lists = []
    current_list = []
    current_token_count = 0

    for summary in summaries:
        # for every summary given in the list we will see how many tokens it uses
        token_count = count_tokens(summary, "cl100k_base")

        # if the current summaries in current_list were to have this summary added on, would it go over the token limit?
        if current_token_count + token_count > token_limit:
            # if it does go over the limit, add the current_list to split lists, and then make a new current_list and add it to that instead
            split_lists.append(current_list)

            # reset the current list and token count
            current_list = []
            current_token_count = 0

            # add it to this new list and token count
            current_list.append(summary)
            current_token_count += token_count

        else:
            # if it doesn't go over the token limit, add it to the current list and add its tokens to the current count
            current_list.append(summary)
            current_token_count += token_count

    split_lists.append(current_list)

    return split_lists


def gpt_requester(split_lists, token_amount):
    final_response = None
    multiple_responses = False
    responses = []
    shortened_responses = []

    prompt = 'Below are several files, each file contains the original content, along with any changes made to it during development.Only give explanations in an easy to understand way and do not say any of the changes. Also only say the explanations.Do not write in a list. Do not skip any files or objects. ALWAYS say the filename before listing any of the changes. If a change starts with + the line was added. If it starts with - it was removed. Write only the summaries. Thank you.\n'

    combined_summary = prompt
    for split_list in split_lists:
        # Combine the summaries in the split list
        combined_summary += '\n' + split_list

    # Check token count of combined summary
    token_count = count_tokens(combined_summary, "cl100k_base")

    # makes sure we won't go over the chat gpt limit (not possible but is a safeguard)
    if token_count > token_amount:
        if token_amount == 4096:
            token_amount = 16384

    # begin generation with a notification
    notify("Beginning generation")
    # get chatgpt to do its thing
    response = send_changes_request(combined_summary, token_amount)

    # Add the response to the final response list (in case we have multiple lists of summaries)
    if final_response is None:
        final_response = response
        responses.append(response)
    else:
        responses.append(response)
        multiple_responses = True

    if multiple_responses == True:
        for split_response in responses:
            # get it to shorten its summary
            temp_summary = "Summarize this as shortly as possible:\n" + split_response
            # see if we can use a cheaper model
            temp_summary_tokens = count_tokens(temp_summary, "cl100k_base")

            # if we can use the cheaper model use it. If not oh well
            if temp_summary_tokens < 4096:
                shortened_responses.append(send_changes_request(temp_summary, 4096))
            else:
                shortened_responses.append(send_changes_request(temp_summary, 16384))

        # summarises all the summaries
        temp_summary = "Summarize this as shortly as possible:\n" + '\n'.join(
            [entry + '\n' for entry in shortened_responses])
        # see if we can use a cheaper model
        temp_summary_tokens = count_tokens(temp_summary, "cl100k_base")

        # if we can use the cheaper model use it. If not oh well
        if temp_summary_tokens < 4096:
            final_response = send_changes_request(temp_summary, 4096)
        else:
            final_response = send_changes_request(temp_summary, 16384)

    notify("Generation completed")

    return final_response


def do_commit(EXE, git_executable, api_key):
    initial_summary_tokens = 0

    print("commiting")

    if is_git_installed(EXE, git_executable, api_key):
        # file path is the path to the actual repository
        file_path = get_filepath()
        time.sleep(0.2)
        # these are the names of all the changed files in the repo
        changed_files = filter_text_files(get_changed_files(file_path, EXE, git_executable, api_key))
        if len(changed_files) == 0:
            print("No changes found")
            return
        print(get_changed_files(file_path, EXE, git_executable, api_key))

        # debug printing the path to the repo and the files changed in it
        print("repo path: " + file_path)
        print("changed files: ")
        print(changed_files)

        # this returns a dictionary where the key is the file name and the value is a list of all the changes
        changes_dict = get_individual_changes(file_path, changed_files)

        # returns a list of the prompts for chat gpt to summarise every file
        initial_summary = gpt_summary(changes_dict, file_path)

        # sees how long all those prompts are to decide what model to use
        for summary in initial_summary:
            initial_summary_tokens += count_tokens(summary, "cl100k_base")

        print("Initial summary tokens: " + str(initial_summary_tokens))

        # 16384 is the 16k limit
        # 4096 is the 4k limit
        # we subtract 200 to account for the initial prompt here

        if initial_summary_tokens >= 3896:
            if initial_summary_tokens >= 16184:
                print("total changes is greater than 16k tokens, gonna use the 16k and split it")
                splitted_summaries = split_summaries(initial_summary, 16184)
                # sends the list of prompts to the gpt requester, after splitting them up, and tells it to use the 16k model
                final_summary = (gpt_requester(splitted_summaries, 16384))
            else:
                print("total changes is less than 16k tokens but more than 4k, gonna use the 16k")
                # sends the list of prompts to the gpt requester and tells it to use the 16k model
                final_summary = (gpt_requester(initial_summary, 16384))
        else:
            print("total changes is less than 4096 tokens, gonna use the 4k")
            # sends the list of prompts to the gpt requester and tells it to use the 4k model
            final_summary = (gpt_requester(initial_summary, 4096))

        print("final summary:")
        print(final_summary)

        final_title = send_title_request(final_summary, 3896)
        print("final title:")
        print(final_title)

        select_window_by_name("GitHub Desktop", EXE, git_executable, api_key)
        # time.sleep(0.2)
        type_and_submit(final_title, final_summary)
    else:
        print("Git not installed or not on filepath")


def do_config():
    attempts = 0

    while attempts < 5:
        if os.path.isfile(config_file) and os.path.getsize(config_file) > 0:
            with open(config_file, "r") as f:
                lines = f.read().splitlines()
                if len(lines) >= 3:
                    EXE = os.path.normpath(lines[0].strip())
                    git_executable = os.path.normpath(lines[1].strip())
                    api_key = os.path.normpath(lines[2].strip())
                    return EXE, git_executable, api_key
                else:
                    # Handle invalid config file format
                    print("Invalid config file format.")
                    run_config()
        else:
            # Handle invalid config file format
            print("Config not found.")
            run_config()

        attempts += 1

    if attempts >= 5:
        print("Unable to find a valid config, exiting.")
        sys.exit(1)


def run_main():
    supported_extensions = ['.txt', '.cs', '.json', '.py']
    EXE = r''
    git_executable = r''
    api_key = r''

    myappid = u'arti.githubButton'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    version_writer_main()

    # checks to see if the config exists and is correct
    EXE, git_executable, api_key = do_config()

    if not os.path.isfile(supported_extensions_path):
        with open(supported_extensions_path, 'w') as file:
            file.write('\n'.join(supported_extensions))
        print(f"Created {supported_extensions_path} and wrote the supported extensions.")
        file.close()
    else:
        print(f"{supported_extensions_path} already exists.")

        # Create a queue to communicate between threads
        action_queue = queue.Queue()

        # Function to process actions from the queue
        def process_actions():
            while not exit_flag:
                try:
                    action = action_queue.get(timeout=1)  # Timeout to allow checking the exit flag
                    if action is None:
                        break  # Stop processing when None is received
                    action()  # Execute the action (method call)
                    action_queue.task_done()
                except queue.Empty:
                    pass
                except Exception as e:
                    print(f"Error while processing action: {e}")

        openai.api_key = api_key

        # Start the action processing thread
        action_thread = threading.Thread(target=process_actions)
        action_thread.start()

        # Create an image (you can replace this with your custom icon)
        image = Image.open("icon.png")

        # image = create_image(64, 64, "black", "white")

        def tray_thread():
            # Create the system tray icon
            icon = pystray.Icon("The Github Button", image, "The Github Button")

            def on_exit_menu():
                global exit_flag
                exit_flag = True
                action_queue.put(None)  # Put None to break the action processing loop
                icon.stop()  # Stop the tray icon
                os._exit(0)  # Terminate the process immediately

            menu = (
                pystray.MenuItem("View Logs", on_left_click),
                pystray.MenuItem("Auto Commit",
                                 lambda: action_queue.put(lambda: select_github_desktop(EXE, git_executable, api_key))),
                pystray.MenuItem("Exit", on_exit_menu)
            )
            icon.menu = pystray.Menu(*menu)
            icon.run()

        # Start the tray-related code in a separate thread
        tray_thread = threading.Thread(target=tray_thread)
        tray_thread.start()

        # Rest of the code here
        keyboard.on_press(lambda event: action_queue.put(lambda: on_keypress(event, EXE, git_executable, api_key)))
        keyboard.wait()

        # Wait for the action processing thread to finish before exiting the program
        action_queue.put(None)  # Put None to break the action processing loop
        action_thread.join()

        # Wait for the tray-related thread to finish before exiting the program
        tray_thread.join()
