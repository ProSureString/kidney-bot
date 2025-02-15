# kidney bot

## Don't want to host yourself? Add the bot [here](https://discord.com/oauth2/authorize?client_id=870379086487363605&permissions=8&scope=applications.commands%20bot)!

**Want to use my code in your bot?**
- That's great! Make sure to credit me, and according to GNU GPLv3, your license must also be GNU GPLv3

Want to host the bot yourself? Follow these instructions:

- Create a bot through the [discord developer portal](https://discord.com/developers/applications)
- Create a [MongoDB Database](https://www.mongodb.com/)
- Create a cluster in the database. It can have any name.
- Create a user for the server. It can have any name and password.
- **Linux**
    - Update package lists `sudo apt update`
    - Make sure some necessary packages are installed `sudo apt install -y gcc g++ python3-dev git ffmpeg`
- **Windows**
    
    We need to install ffmpeg for music to work.
    - Go to this website https://www.gyan.dev/ffmpeg/builds/. Find the latest version, and download the full version.
    - Extract this file where you want it. You may need to install [7zip](https://www.7-zip.org/) to extract the file.
    - Press `windows + r`, and type `systempropertiesadvanced.exe`
    - Click environment variables at the bottom. Under user variables, find path
    - Press new, and enter the full path to the bin of ffmpeg. (ex: if we downloaded ffmpeg to `C:\ffmpeg`, we would put `C:\ffmpeg\bin` in path)
    - Press ok on all the windows to exit them.
- Create a virtual environment `python3 -m venv venv`
- Enter the virtual environment Linux/MacOS: `source venv/bin.active` Windows: `.\venv\Scripts\activate`
- Install the required packages `python3 -m pip install -r requirements.txt`
- Run the setup `python3 setup.py` Make sure to run this in the venv, and provide all requested information **EXACTLY**

Start the bot with `python3 main.py`

todo: setup.py file to automatically ask for these then setup database.
