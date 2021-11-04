from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import *
from bot.helper.ext_utils.bot_utils import get_readable_file_size, check_limit, setInterval
import random
import string


def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    uid= f"<a>{update.message.from_user.id}</a>"
    if len(args) > 1:
        link = args[1]
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.clonehelper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True)
            if smsg:
                msg3 = "File/Folder is already available in Drive.\nHere are the search results:"
                sendMarkup(msg3, context.bot, update, button)
                return
        if CLONE_LIMIT is not None:
            result = check_limit(size, CLONE_LIMIT)
            if result:
                msg2 = f'Failed, Clone limit is {CLONE_LIMIT}.\nYour File/Folder size is {get_readable_file_size(size)}.'
                sendMessage(msg2, context.bot, update)
                return
        if files < 15:
            msg = sendMessage(f"📲 Cloning: <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
            msgt = f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}"
            sendtextlog(msgt, bot, update)
        else:
            msgtt = f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}"
            sendtextlog(msgtt, bot, update)
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\nCloned by: {uname}'
            men = f'{uname} '
            msg_g = f'\n\n - 𝙽𝚎𝚟𝚎𝚛 𝚂𝚑𝚊𝚛𝚎 𝙶-𝙳𝚛𝚒𝚟𝚎\n - 𝙽𝚎𝚟𝚎𝚛 𝚂𝚑𝚊𝚛𝚎 𝙸𝚗𝚍𝚎𝚡 𝙻𝚒𝚗𝚔\n - 𝙹𝚘𝚒𝚗 𝚃𝙳 𝚃𝚘 𝙰𝚌𝚌𝚎𝚜𝚜 𝙶-𝙳𝚛𝚒𝚟𝚎 𝙻𝚒𝚗𝚔'
            fwdpm = f'\n\n𝐘𝐨𝐮 𝐂𝐚𝐧 𝐅𝐢𝐧𝐝 𝐔𝐩𝐥𝐨𝐚𝐝 𝐈𝐧 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐭 𝐨𝐫 𝐂𝐥𝐢𝐜𝐤 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐒𝐞𝐞 𝐚𝐭 𝐥𝐨𝐠 𝐜𝐡𝐚𝐧𝐧𝐞𝐥'
        if button == "cancelled" or button == "":
            sendMessage(men + result, context.bot, update)
        else:
            logmsg = sendLog(result + cc + msg_g, context.bot, update, button)
            if logmsg:
                log_m = f"\n\n<b>Link Uploaded, Click Below Button</b>"
                sendMarkup(result + cc + fwdpm, context.bot, update, InlineKeyboardMarkup([[InlineKeyboardButton(text="𝐂𝐋𝐈𝐂𝐊 𝐇𝐄𝐑𝐄", url=logmsg.link)]]))
                sendPrivate(result + cc + msg_g, context.bot, update, button)
    else:
        sendMessage('Provide G-Drive Shareable Link to Clone.', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
