import logging
import re
import threading
import time
import math

from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import *
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from bot.helper.telegram_helper import button_build, message_utils

LOGGER = logging.getLogger(__name__)

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"

COUNT = 0
PAGE_NO = 1


class MirrorStatus:
    STATUS_UPLOADING = "🅄🄿🄻🄾🄰🄳🄸🄽🄶"
    STATUS_DOWNLOADING = "🄳🄾🅆🄽🄻🄾🄰🄳🄸🄽🄶"
    STATUS_CLONING = "🄲🄻🄾🄽🄽🄸🄽🄶"
    STATUS_WAITING = "🅀🅄🄴🅄🄴🄳"
    STATUS_FAILED = "🄵🄰🄸🄻🄴🄳"
    STATUS_ARCHIVING = "🄰🅁🄲🄷🄸🅅🄸🄽🄶"
    STATUS_EXTRACTING = "🄴🅇🅃🅁🄰🄲🅃🄸🄽🄶"


PROGRESS_MAX_SIZE = 100 // 8
# PROGRESS_INCOMPLETE = ['▏', '▎', '▍', '▌', '▋', '▊', '▉']

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'


def getDownloadByGid(gid):
    with download_dict_lock:
        for dl in download_dict.values():
            status = dl.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                ]
                and dl.gid() == gid
            ):
                return dl
    return None


def getAllDownload():
    with download_dict_lock:
        for dlDetails in download_dict.values():
            status = dlDetails.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                    MirrorStatus.STATUS_CLONING,
                    MirrorStatus.STATUS_UPLOADING,
                ]
                and dlDetails
            ):
                return dlDetails
    return None


def get_progress_bar_string(status):
    completed = status.processed_bytes() / 8
    total = status.size_raw() / 8
    p = 0 if total == 0 else round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 8
    cPart = p % 8 - 1
    p_str = FINISHED_PROGRESS_STR * cFull
    if cPart >= 0:
        # p_str += PROGRESS_INCOMPLETE[cPart]
        p_str += FINISHED_PROGRESS_STR
    p_str += UNFINISHED_PROGRESS_STR * (PROGRESS_MAX_SIZE - cFull)
    p_str = f"[{p_str}]"
    return p_str


def progress_bar(percentage):
    """Returns a progress bar for download
    """
    #percentage is on the scale of 0-1
    comp = FINISHED_PROGRESS_STR
    ncomp = UNFINISHED_PROGRESS_STR
    pr = ""

    if isinstance(percentage, str):
        return "NaN"

    try:
        percentage=int(percentage)
    except:
        percentage = 0

    for i in range(1,11):
        if i <= int(percentage/10):
            pr += comp
        else:
            pr += ncomp
    return pr



def get_readable_message():
    with download_dict_lock:
        msg = ""
        INDEX = 0
        if STATUS_LIMIT is not None:
            dick_no = len(download_dict)
            global pages
            pages = math.ceil(dick_no/STATUS_LIMIT)
            if PAGE_NO > pages and pages != 0:
                globals()['COUNT'] -= STATUS_LIMIT
                globals()['PAGE_NO'] -= 1
        for download in list(download_dict.values()):
            INDEX += 1
            if INDEX > COUNT:
                msg += f"\n<b>ℹ️ Status ℹ️</b>\n<i>{download.status()}</i>\n"                
                msg += f"<b>📁 Filename:</b> <code>{download.name()}</code>"
                if download.status() not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                ]:
                    msg += f"\n<code>{get_progress_bar_string(download)} {download.progress()}</code>"
                    if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                        msg += f"\n<b>📥 Downloaded:</b> {get_readable_file_size(download.processed_bytes())}<b>\n💾 Size</b>: {download.size()}"
                    elif download.status() == MirrorStatus.STATUS_CLONING:
                        msg += f"\n<b>♻️ Cloning:</b> {get_readable_file_size(download.processed_bytes())}<b>\n<b>⚙️ Engine: ʀᴄʟᴏɴᴇ</b>\n💾 Size</b>: {download.size()}"
                    else:
                        msg += f"\n<b>📤 Uploaded:</b> {get_readable_file_size(download.processed_bytes())}<b>\n<b>⚙️ Engine: ʀᴄʟᴏɴᴇ</b>\n💾 Size</b>: {download.size()}"
                    msg += f"\n<b>⚡ Speed:</b> {download.speed()}" \
                            f"\n<b>⏳ ETA:</b> {download.eta()} "
                    # if hasattr(download, 'is_torrent'):
                    try:
                        msg += f"\n<b>👥 User:</b> <b>{download.message.from_user.first_name}</b>\n<b>⚠️ Warn:</b><code>/warn {download.message.from_user.id}</code>"
                    except:
                        pass
                    try:
                        msg += f"\n<b>⚙️ Engine: Aria2</b>\n<b>📶:</b> {download.aria_download().connections}"
                    except:
                        pass
                    try:
                        msg += f" | <b>🌱:</b> {download.aria_download().num_seeders}"
                    except:
                        pass
                    msg += f"\n<b>⛔ Cancel:</b> <code>/{BotCommands.CancelMirror} {download.gid()}</code>"
                msg += "\n\n"
                if STATUS_LIMIT is not None and INDEX >= COUNT + STATUS_LIMIT:
                        break
        if STATUS_LIMIT is not None:
            if INDEX > COUNT + STATUS_LIMIT:
                return None, None
            if dick_no > STATUS_LIMIT:
                msg += f"📖 Page: <code>{PAGE_NO}/{pages}</code> | <code>📄 Tasks: {dick_no}</code>\n"
                buttons = button_build.ButtonMaker()
                buttons.sbutton("⬅️", "pre")
                buttons.sbutton("➡️", "nex")
                button = InlineKeyboardMarkup(buttons.build_menu(2))
                return msg, button
        return msg, ""


def flip(update, context):
    query = update.callback_query
    query.answer()
    global COUNT, PAGE_NO
    if query.data == "nex":
        if PAGE_NO == pages:
            COUNT = 0
            PAGE_NO = 1
        else:
            COUNT += STATUS_LIMIT
            PAGE_NO += 1
    elif query.data == "pre":
        if PAGE_NO == 1:
            COUNT = STATUS_LIMIT * (pages - 1)
            PAGE_NO = pages
        else:
            COUNT -= STATUS_LIMIT
            PAGE_NO -= 1
    message_utils.update_all_messages()


def check_limit(size, limit, tar_unzip_limit=None, is_tar_ext=False):
    LOGGER.info('Checking File/Folder Size...')
    if is_tar_ext and tar_unzip_limit is not None:
        limit = tar_unzip_limit
    if limit is not None:
        limit = limit.split(' ', maxsplit=1)
        limitint = int(limit[0])
        if 'G' in limit[1] or 'g' in limit[1]:
            if size > limitint * 1024**3:
                return True
        elif 'T' in limit[1] or 't' in limit[1]:
            if size > limitint * 1024**4:
                return True

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def is_url(url: str):
    url = re.findall(URL_REGEX, url)
    return bool(url)


def is_gdrive_link(url: str):
    return "drive.google.com" in url


def is_mega_link(url: str):
    return "mega.nz" in url or "mega.co.nz" in url


def get_mega_link_type(url: str):
    if "folder" in url:
        return "folder"
    elif "file" in url:
        return "file"
    elif "/#F!" in url:
        return "folder"
    return "file"


def is_magnet(url: str):
    magnet = re.findall(MAGNET_REGEX, url)
    return bool(magnet)


def new_thread(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


next_handler = CallbackQueryHandler(flip, pattern="nex", run_async=True)
previous_handler = CallbackQueryHandler(flip, pattern="pre", run_async=True)
dispatcher.add_handler(next_handler)
dispatcher.add_handler(previous_handler)
