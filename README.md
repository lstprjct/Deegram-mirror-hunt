# <b>MIRROR-NEW</b>

![MIRROR-NEW](https://sinnerdrive.jack-need-boost.workers.dev/0:/mirr//20210824_150544_1_1.jpg)

<p>
  <a href="https://www.python.org">
    <img src="http://ForTheBadge.com/images/badges/made-with-python.svg">

  </a>
</P>

<p>
  <a href="https://github.com/Anime-Republic/Mirror-New/stargazers">
    <img src="https://img.shields.io/github/stars/Anime-Republic/Mirror-New?style=social">

  </a>
  
  <a href="https://github.com/Anime-Republic/Mirror-New/fork">
    <img src="https://img.shields.io/github/forks/Anime-Republic/Mirror-New?label=Fork&style=social">

  </a>
</p>

**This Mirror Bot** is a _multipurpose_ Telegram Bot writen in Python for mirroring files on the Internet to our beloved Google Drive.

# Support chat

<a href="https://t.me/XcodersHubChat">
    <img src="https://sinnerdrive.jack-need-boost.workers.dev/0:/mirr//xcoders%20%282%29.jpg">

</a>

# Features supported:
<details>
    <summary><b>Click Here For More Details</b></summary>

## Additional Features
- Updater (**NOTE**: You must upload your **token.pickle** to Index and fill your **token.pickle** url to **TOKEN_PICKLE_URL**, because your **token.pickle** will deleted after update, for more info please check [Setting up config file](https://github.com/Anime-Republic/Mirror-New#setting-up-config-file))
- Limiting size Torrent/Direct, Tar/Unzip, Mega, cloning Google Drive support
- Stop duplicate cloning Google Drive & mirroring Mega support
- Tar/Unzip Google Drive link support
- Select files from Torrent before downloading
- Sudo with Database support
- Multiple Trackers support
- Extracting **tar.xz** support
- Counting Google Drive link
- Heroku config support
- View Link button
- Shell and Executor
- YT-DLP
- Direct links Supported:
```
letsupload.io, hxfile.co, anonfiles.com, bayfiles.com, antfiles,
fembed.com, fembed.net, femax20.com, layarkacaxxi.icu, fcdn.stream,
sbplay.org, naniplay.com, naniplay.nanime.in, naniplay.nanime.biz, sbembed.com,
streamtape.com, streamsb.net, feurl.com, pixeldrain.com, racaty.net,
1fichier.com, 1drv.ms (Only works for file not folder or business account),
uptobox.com (Uptobox account must be premium), solidfiles.com
```

## From Original Repos
- Mirroring direct download links, Torrent, and Telegram files to Google Drive
- Mirroring Mega.nz links to Google Drive (If your Mega account not premium, it will limit 5GB/6 hours)
- Copy files from someone's Drive to your Drive (Using Autorclone)
- Download/Upload progress, Speeds and ETAs
- Mirror all Youtube-dl supported links
- Docker support
- Uploading to Team Drive
- Index Link support
- Service Account support
- Delete files from Drive
- Shortener support
- Custom Filename (Only for URL, Telegram files and Youtube-dl. Not for Mega links and Magnet/Torrents)
- Extracting password protected files, using custom filename and download from password protected Index Links see these examples:
<p><a href="https://telegra.ph/Magneto-Python-Aria---Custom-Filename-Examples-01-20"> <img src="https://img.shields.io/badge/see%20on%20telegraph-grey?style=for-the-badge" width="190""/></a></p>

- Extract these filetypes and uploads to Google Drive
```
ZIP, RAR, TAR, 7z, ISO, WIM, CAB, GZIP, BZIP2, 
APM, ARJ, CHM, CPIO, CramFS, DEB, DMG, FAT, 
HFS, LZH, LZMA, LZMA2, MBR, MSI, MSLZ, NSIS, 
NTFS, RPM, SquashFS, UDF, VHD, XAR, Z.
```

</details>

# How to deploy?
Deploying is pretty much straight forward and is divided into several steps as follows:
## Installing requirements

- Clone this repo:
```
git clone https://github.com/Anime-Republic/Mirror-New mirrorbot/
cd mirrorbot
```

- Install requirements
For Debian based distros
```
sudo apt install python3
```
Install Docker by following the [official Docker docs](https://docs.docker.com/engine/install/debian/)

OR
```
sudo snap install docker 
```
- For Arch and it's derivatives:
```
sudo pacman -S docker python
```
- Install dependencies for running setup scripts:
```
pip3 install -r requirements-cli.txt
```
Fill up the `config.env` then
    
- Start Docker daemon (skip if already running):
```
sudo dockerd
```
- Build Docker image:
```
docker build . --rm --force-rm --compress --no-cache=true --pull --file Dockerfile -t mirrorbot
```
- Run the image:
```
sudo docker run mirrorbot
```
  
- To stop Docker run 
```
  sudo docker ps
```
```
sudo docker stop id
```
## Deploying on Heroku with Github Workflow
<p><a href="https://github.com/Anime-Republic/Mirror-New/blob/main/HerokuGuide.md"> <img src="https://img.shields.io/badge/Deploy%20Guide-blueviolet?style=for-the-badge&logo=heroku" width="180""/></a></p>

## Setting up config file
<details>
    <summary><b>Click Here For More Details</b></summary>
    
## Mandotory Variables

- **BOT_TOKEN**: Get it from [@botfather](t.me/botfather)
- **GDRIVE_FOLDER_ID**: This is the folder ID of the Google Drive Folder to which you want to upload all the mirrors.    
- **OWNER_ID**:  The Telegram user ID (not username) of the Owner of the bot    
- **DOWNLOAD_DIR**:  Download location where files will be downloaded(for heroku keep  /usr/src/app/downloads )
- **AUTO_DELETE_MESSAGE_DURATION**: interval of time (in seconds), after which the bot deletes it's message (and command message) which is expected to be viewed instantly. (Note: Set to -1 to never automatically delete messages)
- **TELEGRAM_API**: This is to authenticate to your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org DO NOT put this in quotes.
- **TELEGRAM_HASH**: This is to authenticate to your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org
- **DOWNLOAD_STATUS_UPDATE_INTERVAL**: A short interval of time in seconds after which the Mirror progress message is updated. (I recommend to keep it `5` seconds at least).
    
## Optional Vars
- **DATABASE_URL**: Your Database URL. See [Generate Database](https://github.com/Anime-Republic/Mirror-New/tree/master#generate-database) to generate database (**NOTE**: If you use database you can save your sudo id permanent using `/addsudo` command)
- **AUTHORIZED_CHATS**: Fill user_id and chat_id (not username) of you want to authorize, Seprate them with space, Examples: `-0123456789 -1002489569`.
- **SUDO_USERS**: Fill user_id (not username) of you want to sudoers, Seprate them with space, Examples: `0123456789 181568167` (**NOTE**: If you want save sudo id permanent without database, you must fill your sudo id there)
- **IGNORE_PENDING_REQUESTS**: If you want the bot to ignore pending requests after it restarts, set this to `True`.
- **USE_SERVICE_ACCOUNTS**: (Leave empty if unsure) Whether to use Service Accounts or not. For this to work see [Using Service Accounts](https://github.com/Anime-Republic/Mirror-New/blob/main/CreateSA.md)
- **INDEX_URL**: Refer to [Bhadoo Index](https://gitlab.com/ParveenBhadooOfficial/Google-Drive-Index) The URL should not have any trailing '/'
- **STATUS_LIMIT**: Status limit with buttons (**NOTE**: Recommend limit status to `4` tasks max).
- **MEGA_API_KEY**: Mega.nz api key to mirror mega.nz links. Get it from [Mega SDK Page](https://mega.nz/sdk)
- **MEGA_EMAIL_ID**: Your email id you used to sign up on mega.nz for using premium accounts.
- **MEGA_PASSWORD**: Your password for your mega.nz account.
- **UPTOBOX_TOKEN**: Uptobox token to mirror uptobox links. Get it from [Uptobox Premium Account](https://uptobox.com/my_account).
- **BLOCK_MEGA_FOLDER**: If you want to remove mega.nz folder support, set it to `True`.
- **BLOCK_MEGA_LINKS**: If you want to remove mega.nz mirror support, set it to `True`.
- **STOP_DUPLICATE_CLONE**: (Leave empty if unsure) if this field is set to `True`, bot will check file in Drive, if it is present in Drive,cloning will be stopped. 
- **STOP_DUPLICATE_MEGA**: (Leave empty if unsure) if this field is set to `True`, bot will check file in Drive, if it is present in Drive,Mega Downloading  will be stopped. 
- **STOP_DUPLICATE_MIRROR**: (Leave empty if unsure) if this field is set to `True`, bot will check file in Drive, if it is present in Drive, downloading will be stopped.
- **VIEW_LINK**: View Link button to open file Index Link in browser instead of direct download link, you can figure out if it's compatible with your Index code or not, open any video from you Index and check if the END of link from browser link bar is `?a=view`, if yes make it `True` it will work Compatible with [Bhadoo Index](https://gitlab.com/ParveenBhadooOfficial/Google-Drive-Index)
- **SHORTENER_API**: Fill your Shortener api key if you are using Shortener.
- **SHORTENER**: if you want to use Shortener in Gdrive and index link, fill Shortener url here. Examples:
```
exe.io, gplinks.in, shrinkme.io, urlshortx.com, shortzon.com
```
## If you want to use Credentials externally from Index Links, fill these vars with the direct links.These are optional, if you don't know, simply leave them, don't fill anything in them.
- **TOKEN_PICKLE_URL**: Only if you want to load your **token.pickle** externally from an Index Link. Fill this with the direct link of that file.
- **ACCOUNTS_ZIP_URL**: Only if you want to load your Service Account externally from an Index Link. Archive the accounts folder to a zip file. Fill this with the direct link of that file.
    If  you don't know how to create token.pickle, [Click Here](https://github.com/Anime-Republic/Mirror-New/blob/main/CreateSA.md)
    
## Heroku Details
- **HEROKU_APP_NAME**: (Only if you deploying on Heroku) Your Heroku app name.
- **HEROKU_API_KEY**: (Only if you deploying on Heroku) Your Heroku API key, get it from [Heroku Settings](https://dashboard.heroku.com/account)

## To Use Limits
- **CLONE_LIMIT**: To limit cloning Google Drive (leave space between number and unit, Available units is (gb or GB, tb or TB), Examples: `100 gb, 100 GB`
- **MEGA_LIMIT**: To limit downloading Mega (leave space between number and unit, Available units is (gb or GB, tb or TB), Examples: `100 gb, 100 GB`
- **TORRENT_DIRECT_LIMIT**: To limit the Torrent/Direct mirror size, Leave space between number and unit. Available units is (gb or GB, tb or TB), Examples: `100 gb, 100 GB`
- **TAR_UNZIP_LIMIT**: To limit mirroring as Tar or unzipmirror. Available units is (gb or GB, tb or TB), Examples: `100 gb, 100 GB`
    
## Button
Three buttons are already added of Drive Link, Index Link, and View Link, you can add extra buttons, these are optional, if you don't know what are below entries, simply leave them, don't fill anything in them
    
- **BUTTON_FOUR_NAME**:    
- **BUTTON_FOUR_URL**:     
- **BUTTON_FIVE_NAME**:    
- **BUTTON_FIVE_URL**:    
- **BUTTON_SIX_NAME**:    
- **BUTTON_SIX_URL**:
  
## Others
- **CHANNEL_LINK**: Link of your Channenl
- **SUPPORT_LINK**: Link of Your Support Group
- **RESTARTED_GROUP_ID**: ID of group where Bot will send restart message
- **RESTARTED_GROUP_ID2**:  Second ID of group where Bot will send restart message

## Progress bar    
- **FINISHED_PROGRESS_STR**: Single character for finished progress. #Get yours from https://coolsymbol.com    
- **UNFINISHED_PROGRESS_STR**: Single character for unfinished progress. #Get yours from https://coolsymbol.com
    

## Generate Database
<details>
    <summary><b>Click Here For More Details</b></summary>

**1. Using ElephantSQL**
- Go to https://elephantsql.com/ and create account (skip this if you already have ElephantSQL account)
- Hit **Create New Instance**
- Follow the further instructions in the screen
- Hit **Select Region**
- Hit **Review**
- Hit **Create instance**
- Select your database name
- Copy your database url, and fill to **DATABASE_URL** in config

**2. Using Heroku PostgreSQL**
<p><a href="https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1"> <img src="https://img.shields.io/badge/see%20on%20dev.to-black?style=for-the-badge&logo=dev-dot-to" width="190""/></a></p>
    
