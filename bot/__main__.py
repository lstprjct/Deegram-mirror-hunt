import shutil, psutil
import signal
import os
import asyncio
import importlib
from speedtest import Speedtest

from pyrogram import idle, filters, types, emoji
from bot import *
from sys import executable
from datetime import datetime
import pytz
import time
import threading

from telegram.error import BadRequest, Unauthorized
from telegram import ParseMode, BotCommand, InputTextMessageContent, InlineQueryResultArticle, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters, InlineQueryHandler, MessageHandler, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram.ext import CommandHandler
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from bot.helper import get_text, check_heroku
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, delete, usage, count
now=datetime.now(pytz.timezone(f'{TIMEZONE}'))

IMAGE_X = f"{IMAGE_URL}"

def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime('📅: %d/%m/%Y\n⏲️: %I:%M:%S %p')
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>ℹ️ Bot Uptime ℹ️</b>\n<b>{currentTime}</b>\n\n' \
            f'<b>▶️ Start Time ▶️</b>\n<b>{current}</b>\n\n' \
            f'<b>⚙️ System Usage ⚙️</b>\n' \
            f'<b>💿 Disk Space:</b> <b>{total}</b>\n' \
            f'<b>📀 Used:</b> <b>{used}</b>\n' \
            f'<b>🕊️ Free:</b> <b>{free}</b>\n' \
            f'<b>💻 CPU:</b> <b>{cpuUsage}%</b>\n' \
            f'<b>🖥️ RAM:</b> <b>{memory}%</b>\n' \
            f'<b>💽 DISK:</b> <b>{disk}%</b>\n\n' \
            f'<b>📊Data Usage📊</b>\n<b>📤 Upload:</b> <b>{sent}</b>\n' \
            f'<b>📥 Download:</b> <b>{recv}</b>'

    update.effective_message.reply_photo(IMAGE_X, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Channel", f"{CHANNEL_LINK}")
    buttons.buildbutton("Support Group", f"{SUPPORT_LINK}")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince: <code>{uptime}</code>", context.bot, update)
        else :
            sendMarkup(start_string, context.bot, update, reply_markup)
    else :
        sendMessage(f"Oops! not a Authorized user.", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("🔄️ 𝐑𝐄𝐒𝐓𝐀𝐑𝐓𝐈𝐍𝐆...", context.bot, update)
    LOGGER.info(f'Restarting The Bot...')
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")

def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.CloneCommand} [drive_url]: Copy file/folder to Google Drive

/{BotCommands.CountCommand} [drive_url]: Count file/folder of Google Drive Links

/{BotCommands.DeleteCommand} [drive_url]: Delete file from Google Drive (Only Owner & Sudo)

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.CancelAllCommand}: Cancel all running tasks

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, If found replies with the link

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner)

/{BotCommands.RestartCommand}: Restart the bot

/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner & Sudo only)

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports
'''

    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.CloneCommand} [drive_url]: Copy file/folder to Google Drive

/{BotCommands.CountCommand} [drive_url]: Count file/folder of Google Drive Links

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, If found replies with the link

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner & Sudo only).

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)

botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start mirroring and upload as .tar'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as .tar'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.AuthorizeCommand}','Auth chat [owner/sudo only]'),
        (f'{BotCommands.UnAuthorizeCommand}','Unauth chat [owner/sudo only]'),
        (f'{BotCommands.UsageCommand}','See dyno [owner/sudo only]'),
        (f'{BotCommands.AddSudoCommand}','Add sudo [owner/sudo only]'),
        (f'{BotCommands.RmSudoCommand}','Remove sudo [owner/sudo only]')
    ]


def main():
    # Heroku restarted
    GROUP_ID = f'{RESTARTED_GROUP_ID}'
    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
    jam = kie.strftime('\n📅 𝘿𝘼𝙏𝙀: %d/%m/%Y\n⏲️ 𝙏𝙄𝙈𝙀: %I:%M%P')
    if GROUP_ID is not None and isinstance(GROUP_ID, str):        
        try:
            dispatcher.bot.sendMessage(f"{GROUP_ID}", f"♻️ 𝐁𝐎𝐓 𝐆𝐎𝐓 𝐑𝐄𝐒𝐓𝐀𝐑𝐓𝐄𝐃 ♻️\n{jam}\n\n🗺️ 𝙏𝙄𝙈𝙀 𝙕𝙊𝙉𝙀\n{TIMEZONE}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝚁𝙴-𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙰𝙶𝙰𝙸𝙽\n\n#Restarted")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

# Heroku restarted
    GROUP_ID2 = f'{RESTARTED_GROUP_ID2}'
    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
    jam = kie.strftime('\n📅 𝘿𝘼𝙏𝙀: %d/%m/%Y\n⏲️ 𝙏𝙄𝙈𝙀: %I:%M%P')
    if GROUP_ID2 is not None and isinstance(GROUP_ID2, str):        
        try:
            dispatcher.bot.sendMessage(f"{GROUP_ID2}", f"♻️ 𝐁𝐎𝐓 𝐆𝐎𝐓 𝐑𝐄𝐒𝐓𝐀𝐑𝐓𝐄𝐃 ♻️\n{jam}\n\n🗺️ 𝙏𝙄𝙈𝙀 𝙕𝙊𝙉𝙀\n{TIMEZONE}\n\n𝙿𝙻𝙴𝙰𝚂𝙴 𝚁𝙴-𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙰𝙶𝙰𝙸𝙽\n\n#Restarted")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)            
            
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("📶𝐑𝐄𝐒𝐓𝐀𝐑𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("⚠️ If Any optional vars not be filled it will use Defaults vars")
    LOGGER.info("📶 Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
