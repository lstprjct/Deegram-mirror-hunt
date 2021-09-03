import requests
from telegram.ext import CommandHandler
from telegram.message import Message
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot import GD_BUTTON, INDEX_BUTTON, VIEW_BUTTON
from bot import Interval, INDEX_URL, BUTTON_FOUR_NAME, BUTTON_FOUR_URL, BUTTON_FIVE_NAME, BUTTON_FIVE_URL, BUTTON_SIX_NAME, BUTTON_SIX_URL, BLOCK_MEGA_FOLDER, BLOCK_MEGA_LINKS, VIEW_LINK, aria2
from bot import dispatcher, DOWNLOAD_DIR, download_dict, download_dict_lock, SHORTENER, SHORTENER_API, TAR_UNZIP_LIMIT, DOWNLOAD_STATUS_UPDATE_INTERVAL
from bot.helper.ext_utils import fs_utils, bot_utils
from bot.helper.ext_utils.bot_utils import *
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException, NotSupportedExtractionArchive
from bot.helper.mirror_utils.download_utils.aria2_download import AriaDownloadHelper
from bot.helper.mirror_utils.download_utils.mega_downloader import MegaDownloadHelper
from bot.helper.mirror_utils.download_utils.direct_link_generator import direct_link_generator
from bot.helper.mirror_utils.download_utils.telegram_downloader import TelegramDownloadHelper
from bot.helper.mirror_utils.status_utils import listeners
from bot.helper.mirror_utils.status_utils.extract_status import ExtractStatus
from bot.helper.mirror_utils.status_utils.tar_status import TarStatus
from bot.helper.mirror_utils.status_utils.upload_status import UploadStatus
from bot.helper.mirror_utils.status_utils.gdownload_status import DownloadStatus
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper import button_build
from bot.helper.ext_utils.shortenurl import short_url
import urllib
import pathlib
import os
import subprocess
import threading
import re
import random
import string
import time
import shutil

ariaDlManager = AriaDownloadHelper()
ariaDlManager.start_listener()

class MirrorListener(listeners.MirrorListeners):
    def __init__(self, bot, update, pswd, isTar=False, tag=None, extract=False, isZip=False):
        super().__init__(bot, update)
        self.isTar = isTar
        self.tag = tag
        self.extract = extract
        self.isZip = isZip
        self.pswd = pswd

    def onDownloadStarted(self):
        pass

    def onDownloadProgress(self):
        # We are handling this on our own!
        pass

    def clean(self):
        try:
            aria2.purge()
            Interval[0].cancel()
            del Interval[0]
            delete_all_messages()
        except IndexError:
            pass

    def onDownloadComplete(self):
        with download_dict_lock:
            LOGGER.info(f"Download completed: {download_dict[self.uid].name()}")
            download = download_dict[self.uid]
            name = download.name()
            gid = download.gid()
            size = download.size_raw()
            if name is None: # when pyrogram's media.file_name is of NoneType
                name = os.listdir(f'{DOWNLOAD_DIR}{self.uid}')[0]
            m_path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        if self.isTar:
            try:
                with download_dict_lock:
                    download_dict[self.uid] = TarStatus(name, m_path, size)
                path = fs_utils.zip(name, m_path) if self.isZip else fs_utils.tar(m_path)
            except FileNotFoundError:
                LOGGER.info('File to archive not found!')
                self.onUploadError('Internal error occurred!!')
                return
            try:
                shutil.rmtree(m_path)
            except:
                os.remove(m_path)
        elif self.extract:
            try:
                path = fs_utils.get_base_name(m_path)
                LOGGER.info(f"Extracting: {name}")
                with download_dict_lock:
                    download_dict[self.uid] = ExtractStatus(name, m_path, size)
                pswd = self.pswd
                if pswd is not None:
                    archive_result = subprocess.run(["pextract", m_path, pswd])
                else:
                    archive_result = subprocess.run(["extract", m_path])
                if archive_result.returncode == 0:
                    threading.Thread(target=os.remove, args=(m_path)).start()
                    LOGGER.info(f"Deleting archive: {m_path}")
                else:
                    LOGGER.warning('Unable to extract archive! Uploading anyway')
                    path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
                LOGGER.info(f'got path: {path}')

            except NotSupportedExtractionArchive:
                LOGGER.info("Not any valid archive, uploading file as it is.")
                path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        else:
            path = f'{DOWNLOAD_DIR}{self.uid}/{name}'
        up_name = pathlib.PurePath(path).name
        up_path = f'{DOWNLOAD_DIR}{self.uid}/{up_name}'
        LOGGER.info(f"Upload Name: {up_name}")
        drive = gdriveTools.GoogleDriveHelper(up_name, self)
        size = fs_utils.get_path_size(up_path)
        upload_status = UploadStatus(drive, size, gid, self)
        with download_dict_lock:
            download_dict[self.uid] = upload_status
        update_all_messages()
        drive.upload(up_name)

    def onDownloadError(self, error):
        error = error.replace('<', ' ')
        error = error.replace('>', ' ')
        with download_dict_lock:
            try:
                download = download_dict[self.uid]
                del download_dict[self.uid]
                fs_utils.clean_download(download.path())
            except Exception as e:
                LOGGER.error(str(e))
            count = len(download_dict)
        if self.message.from_user.username:
            uname = f"@{self.message.from_user.username}"
        else:
            uname = f'<a href="tg://user?id={self.message.from_user.id}">{self.message.from_user.first_name}</a>'
        msg = f"{uname} your download has been stopped due to: {error}"
        sendMessage(msg, self.bot, self.update)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onUploadStarted(self):
        pass

    def onUploadProgress(self):
        pass

    def onUploadComplete(self, link: str, size, files, folders, typ):
        with download_dict_lock:
            msg = f'<b>Filename: </b><code>{download_dict[self.uid].name()}</code>\n<b>Size: </b><code>{size}</code>'
            if os.path.isdir(f'{DOWNLOAD_DIR}/{self.uid}/{download_dict[self.uid].name()}'):
                msg += '\n<b>Type: </b><code>Folder</code>'
                msg += f'\n<b>SubFolders: </b><code>{folders}</code>'
                msg += f'\n<b>Files: </b><code>{files}</code>'
            else:
                msg += f'\n<b>Type: </b><code>{typ}</code>'
            buttons = button_build.ButtonMaker()
            if SHORTENER is not None and SHORTENER_API is not None:
                surl = short_url(link)
                buttons.buildbutton(f"{GD_BUTTON}", surl)
            else:
                buttons.buildbutton(f"{GD_BUTTON}", link)
            LOGGER.info(f'Done Uploading {download_dict[self.uid].name()}')
            if INDEX_URL is not None:
                url_path = requests.utils.quote(f'{download_dict[self.uid].name()}')
                share_url = f'{INDEX_URL}/{url_path}'
                if os.path.isdir(f'{DOWNLOAD_DIR}/{self.uid}/{download_dict[self.uid].name()}'):
                    share_url += '/'
                    if SHORTENER is not None and SHORTENER_API is not None:
                        siurl = short_url(share_url)
                        buttons.buildbutton(f"{INDEX_BUTTON}", siurl)
                    else:
                        buttons.buildbutton(f"{INDEX_BUTTON}", share_url)
                else:
                    share_urls = f'{INDEX_URL}/{url_path}?a=view'
                    if SHORTENER is not None and SHORTENER_API is not None:
                        siurl = short_url(share_url)
                        buttons.buildbutton(f"{INDEX_BUTTON}", siurl)
                        if VIEW_LINK:
                            siurls = short_url(share_urls)
                            buttons.buildbutton(f"{VIEW_BUTTON}", siurls)
                    else:
                        buttons.buildbutton(f"{INDEX_BUTTON}", share_url)
                        if VIEW_LINK:
                            buttons.buildbutton(f"{VIEW_BUTTON}", share_urls)
            if BUTTON_FOUR_NAME is not None and BUTTON_FOUR_URL is not None:
                buttons.buildbutton(f"{BUTTON_FOUR_NAME}", f"{BUTTON_FOUR_URL}")
            if BUTTON_FIVE_NAME is not None and BUTTON_FIVE_URL is not None:
                buttons.buildbutton(f"{BUTTON_FIVE_NAME}", f"{BUTTON_FIVE_URL}")
            if BUTTON_SIX_NAME is not None and BUTTON_SIX_URL is not None:
                buttons.buildbutton(f"{BUTTON_SIX_NAME}", f"{BUTTON_SIX_URL}")
            if self.message.from_user.username:
                uname = f"@{self.message.from_user.username}"
            else:
                uname = f'<a href="tg://user?id={self.message.from_user.id}">{self.message.from_user.first_name}</a>'
            if uname is not None:
                msg += f'\n\n<b>#Uploaded By {uname}</b>'
                msg_g = f'\n\n - <b><i>Never Share G-Drive/Index Link.</i></b>\n - <b><i>Join TD To Access G-Drive Link.</i></b>'
            try:
                fs_utils.clean_download(download_dict[self.uid].path())
            except FileNotFoundError:
                pass
            del download_dict[self.uid]
            count = len(download_dict)
        fwdpm = f'\n\n<b>You Can Find Upload In Private Chat</b>'
        logmsg = sendLog(msg + msg_g, self.bot, self.update, InlineKeyboardMarkup(buttons.build_menu(2)))
        if logmsg:
            log_m = f"\n\n<b>Link Uploaded, Click Below Button</b>"
        else:
            pass
        sendMarkup(msg + log_m + fwdpm, self.bot, self.update, InlineKeyboardMarkup([[InlineKeyboardButton(text="CLICK HERE", url=logmsg.link)]]))
        sendPrivate(msg + msg_g, self.bot, self.update, InlineKeyboardMarkup(buttons.build_menu(2)))
        if count == 0:
            self.clean()
        else:
            update_all_messages()

    def onUploadError(self, error):
        e_str = error.replace('<', '').replace('>', '')
        with download_dict_lock:
            try:
                fs_utils.clean_download(download_dict[self.uid].path())
            except FileNotFoundError:
                pass
            del download_dict[self.message.message_id]
            count = len(download_dict)
        if self.message.from_user.username:
            uname = f"@{self.message.from_user.username}"
        else:
            uname = f'<a href="tg://user?id={self.message.from_user.id}">{self.message.from_user.first_name}</a>'
        if uname is not None:
            men = f'{uname} '
        sendMessage(men + e_str, self.bot, self.update)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

def _mirror(bot, update, isTar=False, extract=False, isZip=False):
    mesg = update.message.text.split('\n')
    message_args = mesg[0].split(' ')
    name_args = mesg[0].split('|')
    user_id = update.effective_user.id
    bot_d = bot.get_me()
    b_uname = bot_d.username
    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    uid= f"<a>{update.message.from_user.id}</a>"
    
    try:
        link = message_args[1]
        print(link)
        if link.startswith("|") or link.startswith("pswd: "):
            link = ''
    except IndexError:
        link = ''
    try:
        name = name_args[1]
        name = name.strip()
        if name.startswith("pswd: "):
            name = ''
    except IndexError:
        name = ''
    try:
        ussr = urllib.parse.quote(mesg[1], safe='')
        pssw = urllib.parse.quote(mesg[2], safe='')
    except:
        ussr = ''
        pssw = ''
    if ussr != '' and pssw != '':
        link = link.split("://", maxsplit=1)
        link = f'{link[0]}://{ussr}:{pssw}@{link[1]}'
    pswd = re.search('(?<=pswd: )(.*)', update.message.text)
    if pswd is not None:
      pswd = pswd.groups()
      pswd = " ".join(pswd)
    if link != '':
        LOGGER.info(link)
    link = link.strip()
    reply_to = update.message.reply_to_message
    if reply_to is not None:
        file = None
        tag = reply_to.from_user.username
        media_array = [reply_to.document, reply_to.video, reply_to.audio]
        for i in media_array:
            if i is not None:
                file = i
                break
        if (
            not bot_utils.is_url(link)
            and not bot_utils.is_magnet(link)
            or len(link) == 0
        ) and file is not None:
            if isQbit:
                file_name = str(time.time()).replace(".", "") + ".torrent"
                file.get_file().download(custom_path=f"{file_name}")
                link = f"{file_name}"
            elif file.mime_type != "application/x-bittorrent":
                    listener = MirrorListener(bot, update, pswd, isTar, extract, isZip)
                    tg_downloader = TelegramDownloadHelper(listener)
                    ms = update.message
                    tg_downloader.add_download(ms, f'{DOWNLOAD_DIR}{listener.uid}/', name)
                    editMessage(f"<b>{uname} has sent - \n\nFilename:</b> <code>{download_dict[listener.uid].name()}</code>\n\n<b>Type:</b> <code>{file.mime_type}</code>\n<b>Size:</b> {download_dict[listener.uid].size()}\n\nUser ID : {uid}", tgs)
                    time.sleep(1)
                    sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested Telegram File Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
                    if len(Interval) == 0:
                        Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))
                    return
            else:
                    link = file.get_file().file_path

    else:
        tag = None

    if not bot_utils.is_url(link) and not bot_utils.is_magnet(link):
        if isTar:
            sendMessage(f"<b><i>No download source provided</i></b>\n\n<b>Support Format:\n❋Google drive link\n❋Youtube link(only tar)\n❋Direct link\n❋Mega Link\n❋Magnet\n❋Torrent link\n❋Torrent File(.torrent, need reply)\n❋Telegram File(need reply)</b>\n\n•Use /{BotCommands.TarMirrorCommand} for make tar\n•Use /{BotCommands.ZipMirrorCommand} for make zip", bot, update)
        elif extract:
            sendMessage(f"<b><i>No download source provided</i></b>\n\n<b>Support Format:\n❋Google drive link\n❋Direct link\n❋Mega Link\n❋Magnet\n❋Torrent link\n❋Torrent File(.torrent, need reply)\n❋Telegram File(need reply)</b>\n\n•Use /{BotCommands.UnzipMirrorCommand} for extract file", bot, update)
        else:
            sendMessage(f"<b><i>No download source provided</i></b>\n\n<b>Support Format:\n❋Google drive link\n❋Direct link\n❋Mega Link\n❋Magnet\n❋Torrent link\n❋Torrent File(.torrent, need reply)\n❋Telegram File(need reply)</b>\n\n•Use /{BotCommands.MirrorCommand} for mirror file", bot, update)
        return
        
    if not os.path.exists(link) and not bot_utils.is_mega_link(link) and not bot_utils.is_gdrive_link(link) and not bot_utils.is_magnet(link):
        try:
            link = direct_link_generator(link)
        except DirectDownloadLinkException as e:
            LOGGER.info(e)
            if "ERROR:" in str(e):
                sendMessage(f"{e}", bot, update)
                return
            if "Youtube" in str(e):
                sendMessage(f"{e}", bot, update)
                return

    listener = MirrorListener(bot, update, pswd, isTar, extract, isZip, tag)

    if bot_utils.is_gdrive_link(link):
        if not isTar and not extract:
            sendMessage(f"•Use /{BotCommands.CloneCommand} to clone Google Drive file/folder\n•Use /{BotCommands.TarMirrorCommand} to make tar of Google Drive folder\n•Use /{BotCommands.ZipMirrorCommand} to make zip of Google Drive folder\n•Use /{BotCommands.UnzipMirrorCommand} to extracts archive Google Drive file", bot, update)
            return
        res, size, name, files = gdriveTools.GoogleDriveHelper().clonehelper(link)
        if res != "":
            sendMessage(res, bot, update)
            return
        if TAR_UNZIP_LIMIT is not None:
            result = bot_utils.check_limit(size, TAR_UNZIP_LIMIT)
            if result:
                msg = f'Failed, Tar/Unzip limit is {TAR_UNZIP_LIMIT}.\nYour File/Folder size is {get_readable_file_size(size)}.'
                sendMessage(msg, listener.bot, listener.update)
                return
        LOGGER.info(f"Download Name : {name}")
        drive = gdriveTools.GoogleDriveHelper(name, listener)
        gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
        download_status = DownloadStatus(drive, size, listener, gid)
        with download_dict_lock:
            download_dict[listener.uid] = download_status
        if len(Interval) == 0:
            Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))
        gmgs = sendMessage("<b>Processing Your G-Drive Link...</b>", bot, update)
        time.sleep(2)
        editMessage(f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}", gmgs)
        time.sleep(1)
      # sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested G-Drive Folder Has Been Added To The Status For Archiving</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        if not isTar:
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested G-Drive File Has Been Added To The Status For Extracting</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        else:
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested G-Drive Folder Has Been Added To The Status For Archiving</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        drive.download(link)

    elif bot_utils.is_mega_link(link):
        if BLOCK_MEGA_LINKS:
            sendMessage("Mega links are blocked!", bot, update)
            return
        link_type = bot_utils.get_mega_link_type(link)
        if link_type == "folder" and BLOCK_MEGA_FOLDER:
            sendMessage("Mega folder are blocked!", bot, update)
        elif BLOCK_MEGA_LINKS:
            sendMessage("<b>Mega Links Are Blocked🚫 in Mirror Bots</b>", bot, update)
        else:
            mgs = sendMessage("<b>Processing Your Mega.nz Link...</b>", bot, update)
            time.sleep(2)
            mega_dl = MegaDownloadHelper()
            mega_dl.add_download(link, f'{DOWNLOAD_DIR}{listener.uid}/', listener)
            editMessage(f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}", mgs)
            time.sleep(1)
            if link_type == "folder":
                sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested MEGA Folder Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
            else:
                sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested MEGA File Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
    else:
        bot_start = f"http://t.me/{b_uname}?start=start"
        mssg = sendMessage("<b>Processing Your URI...</b>", bot, update)
        time.sleep(2)
        ariaDlManager.add_download(link, f'{DOWNLOAD_DIR}/{listener.uid}/', listener, name)
        if reply_to is not None:
            editMessage(f"{uname} has sent - \n\n<b>Filename:</b> <code>{file.file_name}</code>\n\n<b>Type:</b> <code>{file.mime_type}</code>\n<b>Size:</b> {get_readable_file_size(file.file_size)}\n\nUser ID : {uid}", mssg)
            time.sleep(1)         
        else:
            editMessage(f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}", mssg)
            time.sleep(1)
        if reply_to is not None:
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested Torrent File Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        elif link.startswith("magnet"):
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested Magnet Link Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        elif link.endswith(".torrent"):
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested Torrent Link Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        elif '0:/' in link or '1:/' in link or '2:/' in link or '3:/' in link or '4:/' in link or '5:/' in link or '6:/' in link or "workers.dev" in link:
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested Index Link Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
        else:
            sendMessage(f"<b>Hei {uname}</b>\n\n<b>Your Requested DDL Has Been Added To The Status</b>\n\n<b>Use /{BotCommands.StatusCommand} To Check Your Progress</b>\n", bot, update)
    if len(Interval) == 0:
        Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))



def mirror(update, context):
    _mirror(context.bot, update)



def tar_mirror(update, context):
    _mirror(context.bot, update, True)


def unzip_mirror(update, context):
    _mirror(context.bot, update, extract=True)

def zip_mirror(update, context):
    _mirror(context.bot, update, True, isZip=True)

mirror_handler = CommandHandler(BotCommands.MirrorCommand, mirror,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
tar_mirror_handler = CommandHandler(BotCommands.TarMirrorCommand, tar_mirror,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
unzip_mirror_handler = CommandHandler(BotCommands.UnzipMirrorCommand, unzip_mirror,
                                      filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
zip_mirror_handler = CommandHandler(BotCommands.ZipMirrorCommand, zip_mirror,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(tar_mirror_handler)
dispatcher.add_handler(unzip_mirror_handler)
dispatcher.add_handler(zip_mirror_handler)
