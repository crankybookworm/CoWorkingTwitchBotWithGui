import json
from pomo_logic import Task, Timer

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

class ChatBotConfig():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def setValues(self, **kwargs):
        self.__dict__.update(kwargs)

    def loadFromFile(chatBotConfigPath):
        chatBotConfigJson = open(chatBotConfigPath).read()
        chatBotConfig: ChatBotConfig = json.loads(
            chatBotConfigJson, object_hook=lambda d: ChatBotConfig(**d))
        return chatBotConfig
    
    def getText(self, textName: str, timer: Timer=None, task: Task=None, **kwargs):
        try:
            message: str = vars(self)[textName]
            if(timer):
                message = message.format_map(SafeDict(
                    username=timer.userDisplayName, 
                    currentIteration=timer.currentIteration, 
                    iterations=timer.iterations, 
                    taskWork=timer.taskWork, 
                    workPeriod=timer.workPeriod, 
                    breakPeriod=timer.breakPeriod, 
                    timeLeft=timer.timeLeftM, 
                    timeTaken=timer.timeTakenM, 
                ))
            elif(task):
                message = message.format_map(SafeDict(
                    username=task.userDisplayName, 
                    taskWork=task.taskWork, 
                    timeTaken=task.timeTakenM, 
                ))
            if(len(kwargs)>0):
                message = message.format_map(SafeDict(**kwargs))
            return message
        except KeyError:
            return None


if __name__ == '__main__':
    chatBotConfigJson = open('BotResources/resources/chatBotConfig.json').read()
    chatBotConfig: ChatBotConfig = json.loads(
        chatBotConfigJson, object_hook=lambda d: ChatBotConfig(**d))
    print(chatBotConfig.__dict__)
