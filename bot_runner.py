import asyncio
import json
from multiprocessing import Process
from time import sleep
from unittest.mock import Mock
import webbrowser
import PyQt5
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import traceback
from bot import CoWorkingBot, startBot, stopBot
from pomo_logic import Pomo
from file_output import startFileOutput, stopFileOutput
from web_output import startWebOutput, stopWebOutput
import os
from twitchio.http import TwitchHTTP

from bot_config import BotConfig
from chatbot_config import ChatBotConfig
import logging

logging.basicConfig(filename='BotResources/bot.log', level=logging.ERROR)
logger = logging.getLogger(__name__)

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = u'CrankyLibrary.Bot.CoWorkingTwitch.0.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError as e:
    pass

class PomoBotUi(QtWidgets.QMainWindow):
    def __init__(self, botConfig: BotConfig, chatBotConfig: ChatBotConfig):
        super(PomoBotUi, self).__init__()

        self.botConfig = botConfig
        self.chatBotConfig = chatBotConfig

        self.setWindowIcon(QtGui.QIcon(
            'BotResources/static/images/CoWorkingBotIcon.png'))
        uic.loadUi('BotResources/resources/PomoBotUI.ui', self)

        qssFile = "BotResources/resources/darkeum.qss"
        with open(qssFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.setUpButtons()
        self.resetBotConfig()
        
        self.botOn = False
        self.fileOutputThread = None
        self.webOutputThread = None
        self.botThread = None
        self.pomoMonitorThread = None
        
        if(self.chatBotConfig.getText("helloResponse") is not None):
            self.resetChatBotConfig()

        self.show()

    def setUpButtons(self):
        self.SetupStatusOnControl()
        self.SetupButtonsOnBotSettings()
        self.SetupsCheckboxesOnBotSettings()
        self.SetupsEntriesOnBotSettings()
        self.SetupEntriesOnChatBotConfig()


    def SetupStatusOnControl(self):
        # Trigger Bot Button
        self.triggerBotButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QPushButton, "botTriggerButton")
        self.triggerBotButton.clicked.connect(self.triggerBot)

        # Setups Status on Control
        self.pomoBrdStsLabel: QtWidgets.QLabel = self.window(
        ).findChild(QtWidgets.QLabel, "pomoBrdStsLabel")
        self.botStatusLabel: QtWidgets.QLabel = self.window(
        ).findChild(QtWidgets.QLabel, "botStatusLabel")
        self.pomsNumLabel: QtWidgets.QLCDNumber = self.window(
        ).findChild(QtWidgets.QLCDNumber, "pomsNumLabel")


    def SetupButtonsOnBotSettings(self):
        # Save Button on Bot Settings
        saveBotConfigButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QDialogButtonBox, "saveOrResetBotConfig").children()[1]
        saveBotConfigButton.clicked.connect(self.saveBotConfig)

        # Reset Button on Bot Settings
        resetBotConfigButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QDialogButtonBox, "saveOrResetBotConfig").children()[2]
        resetBotConfigButton.clicked.connect(self.resetBotConfig)

        # Save Button on Bot Settings
        saveChatBotConfigButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QDialogButtonBox, "saveOrResetChatBotConfig").children()[1]
        saveChatBotConfigButton.clicked.connect(self.saveChatBotConfig)

        # Reset Button on Bot Settings
        resetChatBotConfigButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QDialogButtonBox, "saveOrResetChatBotConfig").children()[2]
        resetChatBotConfigButton.clicked.connect(self.resetChatBotConfig)
        
        # Browse Button on Bot Settings
        fileBrowseButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QPushButton, "fileBrowseButton")
        fileBrowseButton.clicked.connect(self.openFileBrowser)
        
        # Browse Button on Bot Settings
        oAuthLinkButton: QtWidgets.QPushButton = self.window().findChild(
            QtWidgets.QPushButton, "oAuthLinkButton")
        oAuthLinkButton.clicked.connect(self.openTokenLink)


    def SetupsCheckboxesOnBotSettings(self):
        # Setups Checkboxes on Bot Settings
        self.pomoCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "pomoCheck")
        self.timerCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "timerCheck")
        self.grindersCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "grindersCheck")
        self.sleepersCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "sleepersCheck")
        self.taskCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "taskCheck")
        self.doneCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "doneCheck")
        self.finishCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "finishCheck")
        self.rmvTaskCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "rmvTaskCheck")
        self.rmvDoneCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "rmvDoneCheck")
        self.flipCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "flipCheck")
        self.unflipCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "unflipCheck")
        self.joinCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "joinCheck")
        self.leaveCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "leaveCheck")

        self.fileOutputCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "fileOutputCheck")
        self.webOutputCheck: QtWidgets.QCheckBox = self.window(
        ).findChild(QtWidgets.QCheckBox, "webOutputCheck")


    def SetupsEntriesOnBotSettings(self):
        # Setups Entries on Bot Settings
        self.prefixEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "prefixEntry")
        self.oAuthEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "oAuthEntry")
        self.streamerUsernameEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "streamerUsernameEntry")

        self.fileLocationEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "fileLocationEntry")
        self.webHostEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "webHostEntry")
        self.webPortEntry: QtWidgets.QLineEdit = self.window(
        ).findChild(QtWidgets.QLineEdit, "webPortEntry")


    def SetupEntriesOnChatBotConfig(self):
        # Setups Entries on ChatBot Config
        self.chatModeOn: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "chatModeOn")
        self.chatModeOff: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "chatModeOff")
        self.pauseInfo: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "pauseInfo")
        self.pauseTrigger: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "pauseTrigger")
        self.resumeTrigger: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "resumeTrigger")
        self.noPaused: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noPaused")
        self.pomoInfo: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "pomoInfo")
        self.startWorkMultiple: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "startWorkMultiple")
        self.workCompleteMultiple: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "workCompleteMultiple")
        self.startWorkSingle: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "startWorkSingle")
        self.workCompleteSingle: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "workCompleteSingle")
        self.completeAll: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "completeAll")
        self.modifyAdd: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "modifyAdd")
        self.modifySubtract: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "modifySubtract")
        self.modifyError: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "modifyError")
        self.timeLeftGTOne: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "timeLeftGTOne")
        self.timeLeftOne: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "timeLeftOne")
        self.timeLeftLTOne: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "timeLeftLTOne")
        self.runningPomoTask: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "runningPomoTask")
        self.runningTask: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "runningTask")
        self.completedTask: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "completedTask")
        self.noRunningTask: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noRunningTask")
        self.grindersSuffix: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "grindersSuffix")
        self.noGrinders: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noGrinders")
        self.sleepersSuffix: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "sleepersSuffix")
        self.noSleepers: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noSleepers")
        self.helloResponse: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "helloResponse")
        self.purgingCompleted: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "purgingCompleted")
        self.purgingBoard: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "purgingBoard")
        self.noRunningPomo: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noRunningPomo")
        self.invalidWorkPeriod: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "invalidWorkPeriod")
        self.invalidBreakPeriod: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "invalidBreakPeriod")
        self.invalidIterations: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "invalidIterations")
        self.invalidPermMod: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "invalidPermMod")
        self.invalidPermStreamer: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "invalidPermStreamer")
        self.userStats: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "userStats")
        self.noUserStats: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "noUserStats")
        self.rmvDoneInfo: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneInfo")
        self.rmvDone: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDone")
        self.rmvDoneFail: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneFail")
        self.rmvDoneNum: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneNum")
        self.rmvDoneNumFail: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneNumFail")
        self.rmvDoneUser: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneUser")
        self.rmvDoneUserFail: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneUserFail")
        self.rmvDoneUserNum: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneUserNum")
        self.rmvDoneUserNumFail: QtWidgets.QPlainTextEdit = self.window(
        ).findChild(QtWidgets.QPlainTextEdit, "rmvDoneUserNumFail")
        

    def raiseError(self, error):
        error_dialog = QtWidgets.QErrorMessage(self.window())
        error_dialog.showMessage(error)
        return

    def openFileBrowser(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self.window(), 'Open a file', '',
                                            'Text Files (*.txt)')
            if path != ('', ''):
                self.fileLocationEntry.setText(path[0])
            else:
                self.raiseError("Invalid Path")
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    def openTokenLink(self):
        try:
            webbrowser.open("https://twitchapps.com/tmi/")
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    def saveBotConfig(self):
        try:
            errorMsg = self.botConfig.setValues(
                botPrefix=self.prefixEntry.text(),
                oAuthToken=self.oAuthEntry.text(),
                streamerUsername=self.streamerUsernameEntry.text(),

                pomoCmdEnabled=self.pomoCheck.isChecked(),
                timerCmdEnabled=self.timerCheck.isChecked(),
                grindersCmdEnabled=self.grindersCheck.isChecked(),
                sleepersCmdEnabled=self.sleepersCheck.isChecked(),
                taskCmdEnabled=self.taskCheck.isChecked(),
                doneCmdEnabled=self.doneCheck.isChecked(),
                finishCmdEnabled=self.finishCheck.isChecked(),
                rmvTaskCmdEnabled=self.rmvTaskCheck.isChecked(),
                rmvDoneCmdEnabled=self.rmvDoneCheck.isChecked(),
                flipCmdEnabled=self.flipCheck.isChecked(),
                unflipCmdEnabled=self.unflipCheck.isChecked(),
                joinCmdEnabled=self.joinCheck.isChecked(),
                leaveCmdEnabled=self.leaveCheck.isChecked(),

                fileOutputEnabled=self.fileOutputCheck.isChecked(),
                webOutputEnabled=self.webOutputCheck.isChecked(),

                fileOutputLocation=self.fileLocationEntry.text(),
                webOutputHost=self.webHostEntry.text(),
                webOutputPort=self.webPortEntry.text(),
            )

            if(errorMsg is not None):
                self.raiseError(errorMsg)
                return

            with open("BotResources/resources/botConfig.json", 'w') as f:
                f.write(json.dumps(self.botConfig.__dict__,
                    default=str, sort_keys=True, indent=4))
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    def resetBotConfig(self):
        try:
            self.prefixEntry.setText(self.botConfig.botPrefix)
            self.oAuthEntry.setText(self.botConfig.oAuthToken)
            self.streamerUsernameEntry.setText(self.botConfig.streamerUsername)

            self.pomoCheck.setChecked(self.botConfig.pomoCmdEnabled)
            self.timerCheck.setChecked(self.botConfig.timerCmdEnabled)
            self.grindersCheck.setChecked(self.botConfig.grindersCmdEnabled)
            self.sleepersCheck.setChecked(self.botConfig.sleepersCmdEnabled)
            self.taskCheck.setChecked(self.botConfig.taskCmdEnabled)
            self.doneCheck.setChecked(self.botConfig.doneCmdEnabled)
            self.finishCheck.setChecked(self.botConfig.finishCmdEnabled)
            self.rmvTaskCheck.setChecked(self.botConfig.rmvTaskCmdEnabled)
            self.rmvDoneCheck.setChecked(self.botConfig.rmvDoneCmdEnabled)
            self.flipCheck.setChecked(self.botConfig.flipCmdEnabled)
            self.unflipCheck.setChecked(self.botConfig.unflipCmdEnabled)
            self.joinCheck.setChecked(self.botConfig.joinCmdEnabled)
            self.leaveCheck.setChecked(self.botConfig.leaveCmdEnabled)

            self.fileOutputCheck.setChecked(self.botConfig.fileOutputEnabled)
            self.webOutputCheck.setChecked(self.botConfig.webOutputEnabled)

            self.fileLocationEntry.setText(self.botConfig.fileOutputLocation)
            self.webHostEntry.setText(self.botConfig.webOutputHost)
            self.webPortEntry.setText(str(self.botConfig.webOutputPort))
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    def saveChatBotConfig(self):
        try:
            self.chatBotConfig.setValues(
                chatModeOn=self.chatModeOn.toPlainText(),
                chatModeOff=self.chatModeOff.toPlainText(),
                pauseInfo=self.pauseInfo.toPlainText(),
                pauseTrigger=self.pauseTrigger.toPlainText(),
                resumeTrigger=self.resumeTrigger.toPlainText(),
                noPaused=self.noPaused.toPlainText(),
                pomoInfo=self.pomoInfo.toPlainText(),
                startWorkMultiple=self.startWorkMultiple.toPlainText(),
                workCompleteMultiple=self.workCompleteMultiple.toPlainText(),
                startWorkSingle=self.startWorkSingle.toPlainText(),
                workCompleteSingle=self.workCompleteSingle.toPlainText(),
                completeAll=self.completeAll.toPlainText(),
                modifyAdd=self.modifyAdd.toPlainText(),
                modifySubtract=self.modifySubtract.toPlainText(),
                modifyError=self.modifyError.toPlainText(),
                timeLeftGTOne=self.timeLeftGTOne.toPlainText(),
                timeLeftOne=self.timeLeftOne.toPlainText(),
                timeLeftLTOne=self.timeLeftLTOne.toPlainText(),
                runningPomoTask=self.runningPomoTask.toPlainText(),
                runningTask=self.runningTask.toPlainText(),
                completedTask=self.completedTask.toPlainText(),
                noRunningTask=self.noRunningTask.toPlainText(),
                grindersSuffix=self.grindersSuffix.toPlainText(),
                noGrinders=self.noGrinders.toPlainText(),
                sleepersSuffix=self.sleepersSuffix.toPlainText(),
                noSleepers=self.noSleepers.toPlainText(),
                helloResponse=self.helloResponse.toPlainText(),
                purgingCompleted=self.purgingCompleted.toPlainText(),
                purgingBoard=self.purgingBoard.toPlainText(),
                noRunningPomo=self.noRunningPomo.toPlainText(),
                invalidWorkPeriod=self.invalidWorkPeriod.toPlainText(),
                invalidBreakPeriod=self.invalidBreakPeriod.toPlainText(),
                invalidIterations=self.invalidIterations.toPlainText(),
                invalidPermMod=self.invalidPermMod.toPlainText(),
                invalidPermStreamer=self.invalidPermStreamer.toPlainText(),
                userStats=self.userStats.toPlainText(),
                noUserStats=self.noUserStats.toPlainText(),
                rmvDoneInfo=self.rmvDoneInfo.toPlainText(),
                rmvDone=self.rmvDone.toPlainText(),
                rmvDoneFail=self.rmvDoneFail.toPlainText(),
                rmvDoneNum=self.rmvDoneNum.toPlainText(),
                rmvDoneNumFail=self.rmvDoneNumFail.toPlainText(),
                rmvDoneUser=self.rmvDoneUser.toPlainText(),
                rmvDoneUserFail=self.rmvDoneUserFail.toPlainText(),
                rmvDoneUserNum=self.rmvDoneUserNum.toPlainText(),
                rmvDoneUserNumFail=self.rmvDoneUserNumFail.toPlainText(),
            )

            with open("BotResources/resources/chatBotConfig.json", 'w') as f:
                f.write(json.dumps(self.chatBotConfig.__dict__,
                    default=str, sort_keys=True, indent=4))
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    def resetChatBotConfig(self):
        try:
            self.chatModeOn.setPlainText(self.chatBotConfig.chatModeOn)
            self.chatModeOff.setPlainText(self.chatBotConfig.chatModeOff)
            self.pauseInfo.setPlainText(self.chatBotConfig.pauseInfo)
            self.pauseTrigger.setPlainText(self.chatBotConfig.pauseTrigger)
            self.resumeTrigger.setPlainText(self.chatBotConfig.resumeTrigger)
            self.noPaused.setPlainText(self.chatBotConfig.noPaused)
            self.pomoInfo.setPlainText(self.chatBotConfig.pomoInfo)
            self.startWorkMultiple.setPlainText(
                self.chatBotConfig.startWorkMultiple)
            self.workCompleteMultiple.setPlainText(
                self.chatBotConfig.workCompleteMultiple)
            self.startWorkSingle.setPlainText(self.chatBotConfig.startWorkSingle)
            self.workCompleteSingle.setPlainText(
                self.chatBotConfig.workCompleteSingle)
            self.completeAll.setPlainText(self.chatBotConfig.completeAll)
            self.modifyAdd.setPlainText(self.chatBotConfig.modifyAdd)
            self.modifySubtract.setPlainText(self.chatBotConfig.modifySubtract)
            self.modifyError.setPlainText(self.chatBotConfig.modifyError)
            self.timeLeftGTOne.setPlainText(self.chatBotConfig.timeLeftGTOne)
            self.timeLeftOne.setPlainText(self.chatBotConfig.timeLeftOne)
            self.timeLeftLTOne.setPlainText(self.chatBotConfig.timeLeftLTOne)
            self.runningPomoTask.setPlainText(self.chatBotConfig.runningPomoTask)
            self.runningTask.setPlainText(self.chatBotConfig.runningTask)
            self.completedTask.setPlainText(self.chatBotConfig.completedTask)
            self.noRunningTask.setPlainText(self.chatBotConfig.noRunningTask)
            self.grindersSuffix.setPlainText(self.chatBotConfig.grindersSuffix)
            self.noGrinders.setPlainText(self.chatBotConfig.noGrinders)
            self.sleepersSuffix.setPlainText(self.chatBotConfig.sleepersSuffix)
            self.noSleepers.setPlainText(self.chatBotConfig.noSleepers)
            self.helloResponse.setPlainText(self.chatBotConfig.helloResponse)
            self.purgingCompleted.setPlainText(self.chatBotConfig.purgingCompleted)
            self.purgingBoard.setPlainText(self.chatBotConfig.purgingBoard)
            self.noRunningPomo.setPlainText(self.chatBotConfig.noRunningPomo)
            self.invalidWorkPeriod.setPlainText(
                self.chatBotConfig.invalidWorkPeriod)
            self.invalidBreakPeriod.setPlainText(
                self.chatBotConfig.invalidBreakPeriod)
            self.invalidIterations.setPlainText(
                self.chatBotConfig.invalidIterations)
            self.invalidPermMod.setPlainText(self.chatBotConfig.invalidPermMod)
            self.invalidPermStreamer.setPlainText(
                self.chatBotConfig.invalidPermStreamer)
            self.userStats.setPlainText(self.chatBotConfig.userStats)
            self.noUserStats.setPlainText(self.chatBotConfig.noUserStats)
            self.rmvDoneInfo.setPlainText(self.chatBotConfig.rmvDoneInfo)
            self.rmvDone.setPlainText(self.chatBotConfig.rmvDone)
            self.rmvDoneFail.setPlainText(self.chatBotConfig.rmvDoneFail)
            self.rmvDoneNum.setPlainText(self.chatBotConfig.rmvDoneNum)
            self.rmvDoneNumFail.setPlainText(self.chatBotConfig.rmvDoneNumFail)
            self.rmvDoneUser.setPlainText(self.chatBotConfig.rmvDoneUser)
            self.rmvDoneUserFail.setPlainText(self.chatBotConfig.rmvDoneUserFail)
            self.rmvDoneUserNum.setPlainText(self.chatBotConfig.rmvDoneUserNum)
            self.rmvDoneUserNumFail.setPlainText(self.chatBotConfig.rmvDoneUserNumFail)
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))

    @staticmethod
    def format_exception(e):
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(
            sys.exc_info()[0], sys.exc_info()[1]))

        exception_str = "Traceback (most recent call last):\n"
        exception_str += "".join(exception_list)
        # Removing the last \n
        exception_str = exception_str[:-1]

        return exception_str

    def triggerBot(self):
        self.botTriggerThread = QtCore.QThread(self)
        self.botTriggerThread.run = self.toggleBot
        self.botTriggerThread.start()

    def toggleBot(self):
        sender = self.triggerBotButton
        sender.setEnabled(False)
        if(self.botOn):
            if(self.stopBot()):
                self.botStatusLabel.setText("OFF")
                sender.setText("Start the Bot")
                self.botOn = False
            else:
                self.botStatusLabel.setText("ON")
                sender.setText("Stop the Bot")
                self.botOn = True
        else:
            if(self.startBot()):
                self.botStatusLabel.setText("ON")
                sender.setText("Stop the Bot")
                self.botOn = True
            else:
                self.botStatusLabel.setText("OFF")
                sender.setText("Start the Bot")
                self.botOn = False
        sender.setEnabled(True)
        
    def startBot(self):
        try:
            class MockHttpClient:
                def __init__(self, token):
                    self.session = None
                    self.nick = True
                    self.token = token
            
            asyncio.run(TwitchHTTP.validate(self=MockHttpClient(self.botConfig.oAuthToken)))

            self.bot = CoWorkingBot(self.botConfig, self.chatBotConfig)
            
            print("Initiated...")
            disabledCmds = self.botConfig.getDisabledCommands()
            
            for cmd in disabledCmds:
                self.bot.remove_command(cmd)
            
            self.botThread = startBot(self.bot)
            print("Started...")


            if (self.botConfig.fileOutputEnabled):
                self.fileOutputThread = startFileOutput(filename=self.botConfig.fileOutputLocation,
                                channel=self.botConfig.streamerUsername)
                self.pomoBrdStsLabel.setText("ON")

            if (self.botConfig.webOutputEnabled):
                self.webOutputThread = startWebOutput(host=self.botConfig.webOutputHost,
                               port=self.botConfig.webOutputPort)
                self.pomoBrdStsLabel.setText("ON")

            self.pomoMonitorThread = QtCore.QThread()
            self.pomoMonitorThread.run = lambda: PomoBotUi.monitorPomos(self.pomsNumLabel, self.botConfig.streamerUsername, )
            self.pomoMonitorThread.start()

            return True
        except Exception as e:
            logger.log(logging.ERROR, "Error starting bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(str(e))
            return False

    def stopBot(self):
        if(self.webOutputThread):
            try:
                stopWebOutput(self.webOutputThread)
                self.webOutputThread = None
            except AttributeError:
                self.webOutputThread = None
            except Exception as e:
                logger.log(logging.ERROR, "Error stopping WebOutput: %s", PomoBotUi.format_exception(e))
                self.raiseError(PomoBotUi.format_exception(e))
            finally:
                self.pomoBrdStsLabel.setText("OFF")

        if(self.fileOutputThread):
            try:
                stopFileOutput(self.fileOutputThread)
                self.fileOutputThread = None
            except AttributeError:
                self.fileOutputThread = None
            except Exception as e:
                logger.log(logging.ERROR, "Error stopping FileOutput: %s", PomoBotUi.format_exception(e))
                self.raiseError("Error stopping FileOutput: %s" % PomoBotUi.format_exception(e))
            finally:
                self.pomoBrdStsLabel.setText("OFF")
        
        if(self.pomoMonitorThread):
            try:
                self.pomoMonitorThread.terminate()
                self.pomoMonitorThread = None
            except AttributeError:
                self.pomoMonitorThread = None
            except Exception as e:
                logger.log(logging.ERROR, "Error stopping PomoMonitor: %s", PomoBotUi.format_exception(e))
                self.raiseError(PomoBotUi.format_exception(e))

        try:
            stopBot(self.bot, self.botThread)
            
            return True
        except AttributeError as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError("Bot Not Running")
            return True
        except Exception as e:
            logger.log(logging.ERROR, "Error stopping bot: %s", PomoBotUi.format_exception(e))
            self.raiseError(PomoBotUi.format_exception(e))
            return False

    @staticmethod
    def monitorPomos(pomsNumLabel: QtWidgets.QLCDNumber, streamerUsername: str):
        while True:
            try:
                pomsNumLabel.display(len(Pomo.get_all_task_dicts(streamerUsername)))
            except Exception as e:
                logger.log(logging.ERROR, PomoBotUi.format_exception(e))
                print(PomoBotUi.format_exception(e))
            QtCore.QThread.sleep(5)


try:
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("BotResources/static/images/CoWorkingBotIcon.png"))

    try:
        botConfig = BotConfig.loadFromFile('BotResources/resources/botConfig.json')
        chatBotConfig = ChatBotConfig.loadFromFile('BotResources/resources/chatBotConfig.json')
    except FileNotFoundError:
        botConfig = BotConfig()
        chatBotConfig = ChatBotConfig()

    botUI = PomoBotUi(botConfig, chatBotConfig)
    app.exec_()
except Exception as e:
    logger.log(logging.ERROR, PomoBotUi.format_exception(e))
    print(PomoBotUi.format_exception(e))
