from typing import Iterable, Union
# from varname import nameof
import json


class BotConfig():
    def __init__(self,
                 botPrefix: str = "!",
                 oAuthToken: str = None,
                 streamerUsername: str = None,

                 helloCmdEnabled: bool = True,
                 pomoCmdEnabled: bool = True,
                 timerCmdEnabled: bool = True,
                 grindersCmdEnabled: bool = True,
                 sleepersCmdEnabled: bool = True,
                 taskCmdEnabled: bool = True,
                 doneCmdEnabled: bool = True,
                 finishCmdEnabled: bool = True,
                 rmvTaskCmdEnabled: bool = True,
                 rmvDoneCmdEnabled: bool = True,
                 flipCmdEnabled: bool = True,
                 unflipCmdEnabled: bool = True,
                 joinCmdEnabled: bool = False,
                 leaveCmdEnabled: bool = False,

                 fileOutputEnabled: bool = False,
                 fileOutputLocation: str = None,

                 webOutputEnabled: bool = True,
                 webOutputHost: str = "localhost",
                 webOutputPort: int = 8080,
                 ):
        self.botPrefix: str = botPrefix
        self.oAuthToken: str = oAuthToken
        self.streamerUsername: str = streamerUsername

        self.helloCmdEnabled: bool = helloCmdEnabled
        self.pomoCmdEnabled: bool = pomoCmdEnabled
        self.timerCmdEnabled: bool = timerCmdEnabled
        self.grindersCmdEnabled: bool = grindersCmdEnabled
        self.sleepersCmdEnabled: bool = sleepersCmdEnabled
        self.taskCmdEnabled: bool = taskCmdEnabled
        self.doneCmdEnabled: bool = doneCmdEnabled
        self.finishCmdEnabled: bool = finishCmdEnabled
        self.rmvTaskCmdEnabled: bool = rmvTaskCmdEnabled
        self.rmvDoneCmdEnabled: bool = rmvDoneCmdEnabled
        self.flipCmdEnabled: bool = flipCmdEnabled
        self.unflipCmdEnabled: bool = unflipCmdEnabled
        self.joinCmdEnabled: bool = joinCmdEnabled
        self.leaveCmdEnabled: bool = leaveCmdEnabled

        self.fileOutputEnabled: bool = fileOutputEnabled
        self.fileOutputLocation: str = fileOutputLocation

        self.webOutputEnabled: bool = webOutputEnabled
        self.webOutputHost: str = webOutputHost
        self.webOutputPort: int = webOutputPort

    def getDisabledCommands(self) -> Iterable[str]:
        disabledCommands = []
        for cmd, value in self.__dict__.items():
            if type(value) is bool and cmd.endswith("CmdEnabled") and value == False:
                disabledCommands.append(cmd.removesuffix("CmdEnabled"))
        return disabledCommands

    def loadFromFile(botConfigPath) -> "BotConfig":
        botConfigJson = open(botConfigPath).read()
        botConfig: BotConfig = json.loads(
            botConfigJson, object_hook=lambda d: BotConfig(**d))
        return botConfig

    def setValues(self,
                  botPrefix: str = None,
                  oAuthToken: str = None,
                  streamerUsername: str = None,

                  helloCmdEnabled: bool = None,
                  pomoCmdEnabled: bool = None,
                  timerCmdEnabled: bool = None,
                  grindersCmdEnabled: bool = None,
                  sleepersCmdEnabled: bool = None,
                  taskCmdEnabled: bool = None,
                  doneCmdEnabled: bool = None,
                  finishCmdEnabled: bool = None,
                  rmvTaskCmdEnabled: bool = None,
                  rmvDoneCmdEnabled: bool = None,
                  flipCmdEnabled: bool = None,
                  unflipCmdEnabled: bool = None,
                  joinCmdEnabled: bool = None,
                  leaveCmdEnabled: bool = None,

                  fileOutputEnabled: bool = None,
                  fileOutputLocation: str = None,

                  webOutputEnabled: bool = None,
                  webOutputHost: str = None,
                  webOutputPort: int = None,
                  ) -> Union[str, None]:

        if (botPrefix is None):
            return "Your bot prefix is required"
        if(len(botPrefix) != 1):
            return "Your bot prefix has to be 1 character long"
        if(oAuthToken is None):
            return "Your OAuthToken is required"
        if(len(oAuthToken) != 30):
            return "Your OAuth/Access Token has to be 30 characters long"
        if(streamerUsername is None):
            return "Your Streamer Username is required"
        if(len(streamerUsername) < 4):
            return "Your Streamer Username has to be at least 4 characters long"

        if(webOutputHost is None):
            if(webOutputEnabled):
                return "Your Web Output Host is required"
            else:
                self.webOutputHost = webOutputHost
        else:
            try:
                self.webOutputPort = int(webOutputPort)
                self.webOutputHost = webOutputHost
            except:
                return "Your Web Output Port has to be an integer"

        if(fileOutputLocation is None):
            if(fileOutputEnabled):
                return "Your File Output Location is required"
        else:
            self.fileOutputLocation = fileOutputLocation

        self.botPrefix = botPrefix
        self.oAuthToken = oAuthToken
        self.streamerUsername = streamerUsername

        self.helloCmdEnabled = helloCmdEnabled if helloCmdEnabled is not None else self.helloCmdEnabled
        self.pomoCmdEnabled = pomoCmdEnabled if pomoCmdEnabled is not None else self.pomoCmdEnabled
        self.timerCmdEnabled = timerCmdEnabled if timerCmdEnabled is not None else self.timerCmdEnabled
        self.grindersCmdEnabled = grindersCmdEnabled if grindersCmdEnabled is not None else self.grindersCmdEnabled
        self.sleepersCmdEnabled = sleepersCmdEnabled if sleepersCmdEnabled is not None else self.sleepersCmdEnabled
        self.taskCmdEnabled = taskCmdEnabled if taskCmdEnabled is not None else self.taskCmdEnabled
        self.doneCmdEnabled = doneCmdEnabled if doneCmdEnabled is not None else self.doneCmdEnabled
        self.finishCmdEnabled = finishCmdEnabled if finishCmdEnabled is not None else self.finishCmdEnabled
        self.rmvTaskCmdEnabled = rmvTaskCmdEnabled if rmvTaskCmdEnabled is not None else self.rmvTaskCmdEnabled
        self.rmvDoneCmdEnabled = rmvDoneCmdEnabled if rmvDoneCmdEnabled is not None else self.rmvDoneCmdEnabled
        self.flipCmdEnabled = flipCmdEnabled if flipCmdEnabled is not None else self.flipCmdEnabled
        self.unflipCmdEnabled = unflipCmdEnabled if unflipCmdEnabled is not None else self.unflipCmdEnabled
        self.joinCmdEnabled = joinCmdEnabled if joinCmdEnabled is not None else self.joinCmdEnabled
        self.leaveCmdEnabled = leaveCmdEnabled if leaveCmdEnabled is not None else self.leaveCmdEnabled

        self.fileOutputEnabled = fileOutputEnabled if fileOutputEnabled is not None else self.fileOutputEnabled

        self.webOutputEnabled = webOutputEnabled if webOutputEnabled is not None else self.webOutputEnabled


if __name__ == '__main__':
    botConfigJson = open('BotResources/resources/botConfig.json').read()
    botConfig: BotConfig = json.loads(
        botConfigJson, object_hook=lambda d: BotConfig(**d))
    print(botConfig)
    print(json.dumps(BotConfig().__dict__))
