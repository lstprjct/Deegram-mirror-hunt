import os

def getCommand(name: str, command: str):
    try:
        if len(os.environ[name]) == 0:
            raise KeyError
        return os.environ[name]
    except KeyError:
        return command

class _BotCommands:
    def __init__(self):
        self.StartCommand = getCommand('START_BOT', 'start')
        self.MirrorCommand = getCommand('MIRROR_BOT', 'mir')
        self.UnzipMirrorCommand = getCommand('UNZIP_BOT', 'unzipmir')
        self.TarMirrorCommand = getCommand('TARMIR_BOT', 'tarmir')
        self.ZipMirrorCommand = getCommand('ZIP_BOT', 'zipmir')
        self.CancelMirror = getCommand('CANCEL_BOT', 'cancel')
        self.CancelAllCommand = getCommand('CANCEL_ALL_BOT', 'cancelall')
        self.ListCommand = getCommand('LIST_BOT', 'list')
        self.StatusCommand = getCommand('STATUS_BOT', 'status')
        self.AuthorizedUsersCommand = getCommand('USERS_BOT', 'users')
        self.UsageCommand = getCommand('USAGE_BOT', 'usage')
        self.AuthorizeCommand = getCommand('AUTH_BOT', 'auth')
        self.UnAuthorizeCommand = getCommand('UNAUTH_BOT', 'unauth')
        self.AddSudoCommand = getCommand('ADDSUDO_BOT', 'addsudo')
        self.RmSudoCommand = getCommand('RMSUDO_BOT', 'rmsudo')
        self.RestartCommand = getCommand('RESTART_BOT', 'restart')
        self.StatsCommand = getCommand('STATS_BOT', 'stats')
        self.HelpCommand = getCommand('HELP_BOT', 'help')
        self.LogCommand = getCommand('LOG_BOT', 'logs')
        self.CloneCommand = getCommand('CLONE_BOT', 'clone')
        self.CountCommand = getCommand('COUNT_BOT', 'count')
        self.WatchCommand = getCommand('YTDL_BOT', 'yt')
        self.TarWatchCommand = getCommand('TARYTDL_BOT', 'taryt')
        self.DeleteCommand = getCommand('DELETE_BOT', 'del')
        self.ShellCommand = getCommand('SHELL_BOT', 'shell')
        self.ExecHelpCommand = getCommand('EXEHELP_BOT', 'exehelp')

BotCommands = _BotCommands()
