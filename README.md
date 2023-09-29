
# The GitHub Button

The GitHub Button uses the Chatgpt API to autonomously write commit titles and summaries with a single button press



## Authors

- [@AlfieRichards](https://github.com/AlfieRichards)
- [@DexterParris](https://github.com/DexterParris)


## Installation Methods

Install using my website:

Head over to my website at https://alfiedev.co.uk/GithubButtonInstaller.exe here you can download the Inno Installer for the project. This installs the compiled exe into your appData roaming folder and also adds it to startup so the GitHub Button is always running.

Compile yourself:
Compiling the GitHub button is extremely easy using the line of code below. This uses pyinstaller to compile the program into an exe

```bash
pyinstaller --noconsole --onefile --name "TheGithubButton" --icon "C:\Users\asdaFemboy\Desktop\Github Repos\AutoComitter\icon.ico" --paths "C:\Users\asdaFemboy\Desktop\Github Repos\AutoComitter\venv\Lib\site-packages" --hidden-import plyer.platforms.win.notification .\host.py
```
Note that you will need to change the absolute paths of the icon and packages.

If wanted you may also compile your own installer as the inno script is contained within this repository and you should just be able to run that once again making sure file paths are set correctly.


## Usage/Examples

Using the GitHub button is pretty simple.
First open GitHub desktop with your desired repository selected as is shown in the image below

![Repo Image](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)

Then press the shortcut keybind ("ctrl + alt + c") or the physical github button. This will start the commit process. Once this is pressed it should do the shortcut to view this repository in command prompt, it will then copy the contents of this window to get the path to the repository. If you do not have access to command prompt for whatever reason issues will arise. Once it has done this you will recieve a notification that the ai request has been submitted and it will shortly be filled into the title and description boxes in github desktop.

![Demo Image](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/th5xamgrr6se0x5ro4g6.png)

Throughout this process I reccomend not touching anything and just letting it do its thing, it shouldnt try and enter text on any windows that arent GitHub desktop however it will stop it from functioning if the wrong window is selected.

If it doesent work for whatever reason feel free to just try it again, if it still isnt working there may be an issue so check out the issues page to see if its reported!
## Contributing

Contributions are always welcome!

Please open reports when you find bugs and just submit your logs, if you think you may be able to fix it go ahead and make a fork!


## Roadmap

- Better integration with GitHub desktop (no more open in terminal)

- Increased speed with ChatGPT

- Custom tailored ChatGPT model for better responses

- Custom lighter weight installer (fully portable)
## Hardware

There is a hardware version of the github button that is literally a single button. This can be made using the components below

https://thepihut.com/products/seeed-xiao-rp2040 (main pcb)
https://thepihut.com/products/adafruit-neokey-bff (keyboard switch board)

The 3D print files are in the repository under "3D print files" Feel free to alter them in any way you want!
The arduino script for you to flash is also contained in the "3D print files" folder


## License

[MIT](https://choosealicense.com/licenses/mit/)

