import random
import string
from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import get_readable_file_size, is_gdrive_link, is_gdtot_link
from bot.helper.mirror_utils.download_utils.direct_link_generator import gdtot
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException


def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message

    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    uid= f"<a>{update.message.from_user.id}</a>"
    if len(args) > 1:
        link = args[1]
    elif reply_to is not None:
        link = reply_to.text
    else:
        link = ''
    gdtot_link = is_gdtot_link(link)
    if gdtot_link:
        try:
            link = gdtot(link)
        except DirectDownloadLinkException as e:
            return sendMessage(str(e), context.bot, update)
    if is_gdrive_link(link):
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "𝗙𝗶𝗹𝗲/𝗙𝗼𝗹𝗱𝗲𝗿 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗶𝗻 𝗗𝗿𝗶𝘃𝗲.\n𝗛𝗲𝗿𝗲 𝗮𝗿𝗲 𝘁𝗵𝗲 𝘀𝗲𝗮𝗿𝗰𝗵 𝗿𝗲𝘀𝘂𝗹𝘁𝘀:"
                sendMarkup(msg3, context.bot, update, button)
                if gdtot_link:
                    gd.deletefile(link)
                return
        if CLONE_LIMIT is not None:
            LOGGER.info('Checking File/Folder Size...')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'Failed, Clone limit is {CLONE_LIMIT}GB.\nYour File/Folder size is {get_readable_file_size(size)}.'
                sendMessage(msg2, context.bot, update)
                return
        if files <= 10:
            msg = sendMessage(f"📲 𝑪𝒍𝒐𝒏𝒊𝒏𝒈: <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
            msgt = f"𝗟𝗢𝗚𝗚𝗘𝗥\n\n𝑼𝒔𝒆𝒓: {uname}\n𝑼𝒔𝒆𝒓 𝑰𝑫: {uid}\n\n𝑳𝒊𝒏𝒌 𝑺𝒆𝒏𝒅𝒆𝒅:\n<code>{link}</code>"
            sendtextlog(msgt, bot, update)
        else:
            msgtt = f"𝗟𝗢𝗚𝗚𝗘𝗥\n\n𝑼𝒔𝒆𝒓: {uname}\n𝑼𝒔𝒆𝒓 𝑰𝑫: {uid}\n\n𝑳𝒊𝒏𝒌 𝑺𝒆𝒏𝒅𝒆𝒅:\n<code>{link}</code>"
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
            cc = f'\n\n𝘾𝙡𝙤𝙣𝙚𝙙 𝙗𝙮: {uname}'
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
        if gdtot_link:
            gd.deletefile(link)
    else:
        sendMessage('𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗚-𝗗𝗿𝗶𝘃𝗲 𝗦𝗵𝗮𝗿𝗲𝗮𝗯𝗹𝗲 𝗟𝗶𝗻𝗸 𝘁𝗼 𝗖𝗹𝗼𝗻𝗲', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
