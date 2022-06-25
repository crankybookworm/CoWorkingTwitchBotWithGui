from argparse import ArgumentTypeError
import datetime
from typing import Optional, Union, Dict, List
from dateutil import parser
import tinydb
from tinydb import TinyDB, where
from tinydb.queries import QueryInstance
from tinydb.storages import MemoryStorage
from tinydb.table import Document
from twitchio import Chatter, PartialChatter
import threading
import ctypes
import os
import pytz
import asyncio

filepath = "BotResources/resources/botDatabase.json"
if not os.path.exists(filepath.rsplit('/', 1)[0]):
    os.makedirs(filepath.rsplit('/', 1)[0])

if(not os.path.exists(filepath)):
    with open(filepath, 'w') as f:
        pass

db = TinyDB(filepath, sort_keys=True, indent=4, )



class Thread_With_Exception(threading.Thread):
    def __init__(self, **kwargs): 
        threading.Thread.__init__(self, **kwargs) 

    def start_with_async(self):
        self.get_or_create_eventloop(self)
        self.start()

    def get_id(self): 
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
            ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure')

    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex) or \
                "Event loop is closed" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()


class Task(object):
    def __init__(
        self,
        username: str,
        userDisplayName: str = None,
        work: str = "Work",
        done: bool = False,
        startTime: Union[datetime.datetime, str] = None,
        endTime: Union[datetime.datetime, str] = None,
        **kwargs,
    ):
        self.username = username
        self.userDisplayName = userDisplayName if userDisplayName else username
        self.work = work
        self.done = done

        if (startTime is None):
            self.startTime = datetime.datetime.now(pytz.utc)
        elif (type(startTime) is str):
            self.startTime = parser.parse(startTime)
        elif(type(startTime) is datetime.datetime):
            self.startTime = startTime.astimezone(pytz.utc)
        else:
            raise ValueError(f"Invalid Value for 'startTime' of type {type(startTime)}: {startTime}")

        if (endTime is None):
            self.endTime = None
        elif (type(endTime) is str):
            self.endTime = parser.parse(endTime)
        elif(type(endTime) is datetime.datetime):
            self.endTime = endTime.astimezone(pytz.utc)
        else:
            raise ValueError(f"Invalid Value for 'endTime' of type {type(endTime)}: {endTime}")

    @property
    def timeTaken(self) -> datetime.timedelta:
        if(self.done):
            return self.endTime.astimezone(pytz.utc) - self.startTime.astimezone(pytz.utc)
        return datetime.datetime.now(pytz.utc) - self.startTime

    @property
    def timeTakenM(self) -> int:
        return round(self.timeTaken.total_seconds() / 60)

    @property
    def taskWork(self) -> str:
        return self.work if len(self.work) <= 50 else self.work[0:50] + '…'

    def endTask(self):
        self.done = True
        self.endTime = datetime.datetime.now(pytz.utc)

    def __str__(self) -> str:
        if(self.done):
            text = f"✔\t{self.userDisplayName}: {self.work}"
        else:
            text = f"\t{self.userDisplayName}: {self.work}"
        return text

    def to_dict(self) -> dict:
        variables = vars(self)
        variablesDict = {}
        for k, v in variables.items():
            if (type(v) is datetime.datetime):
                variablesDict[k] = str(v)
            elif(type(v) is datetime.timedelta):
                variablesDict[k] = v.total_seconds()
            else:
                variablesDict[k] = v
        return variablesDict


class Timer(Task):
    def __init__(
        self,
        username: str,
        workPeriod: int,
        breakPeriod: int,
        iterations: int,
        iterStartTime: Union[datetime.datetime, str] = None,
        work: str = "work",
        done: bool = False,
        userDisplayName: str = None,
        currentIteration: int = 1,
        workMode: bool = True,
        startTime: Union[datetime.datetime, str] = None,
        endTime: Union[datetime.datetime, str] = None,
        iterEndTime: Union[datetime.datetime, str] = None,
        pausedAtTimeLeft: Union[datetime.timedelta, float] = None,
        chatMode=False,
        totalWorkTime: Union[datetime.timedelta, float] = datetime.timedelta(),
    ):
        super().__init__(username, userDisplayName,
                       work, done, startTime, endTime)
        self.workPeriod: float = workPeriod
        self.breakPeriod: float = breakPeriod
        self.iterations: int = iterations
        self.work: str = work
        self.currentIteration: int = currentIteration
        self.workMode: bool = workMode
        self.chatMode: bool = chatMode

        if(iterStartTime is None):
            self.iterStartTime = datetime.datetime.now(pytz.utc)
        elif(type(iterStartTime) is str):
            self.iterStartTime = parser.parse(iterStartTime)
        elif(type(iterStartTime) is datetime.datetime):
            self.iterStartTime = iterStartTime
        else:
            raise ValueError(f"Invalid Value for 'iterStartTime' of type {type(iterStartTime)}: {iterStartTime}")

        if(iterEndTime is None):
            self.iterEndTime = self.iterStartTime.astimezone(pytz.utc) + datetime.timedelta(minutes=self.workPeriod)
        elif(type(iterEndTime) is str):
            self.iterEndTime = parser.parse(iterEndTime)
        elif(type(iterEndTime) is datetime.datetime):
            self.iterEndTime = iterEndTime.astimezone(pytz.utc)
        else:
            raise ValueError(f"Invalid Value for 'iterEndTime' of type {type(iterEndTime)}: {iterEndTime}")

        if(type(pausedAtTimeLeft) is float):
            self.pausedAtTimeLeft = datetime.timedelta(seconds=pausedAtTimeLeft)
        elif(type(pausedAtTimeLeft) is datetime.timedelta):
            self.pausedAtTimeLeft = pausedAtTimeLeft
        else:
            self.pausedAtTimeLeft = None

        if(type(totalWorkTime) is str):
            self.totalWorkTime = datetime.timedelta(seconds=totalWorkTime)
        elif(type(totalWorkTime) is datetime.timedelta):
            self.totalWorkTime = totalWorkTime
        else:
            self.totalWorkTime = datetime.timedelta()

    def nextIter(self, restoring: bool = False) -> bool:
        if(self.paused):
            self.resume()
            return True

        if(self.workMode):
            if(not restoring):
                self.totalWorkTime += self.iterEndTime.astimezone(pytz.utc) - self.iterStartTime.astimezone(pytz.utc)
            else:
                self.totalWorkTime += datetime.datetime.now(pytz.utc) - self.iterStartTime.astimezone(pytz.utc)

        self.iterStartTime = datetime.datetime.now(pytz.utc)

        if (self.workMode and self.breakPeriod != 0):
            self.workMode = False
            self.iterEndTime = self.iterStartTime.astimezone(pytz.utc) + datetime.timedelta(
                minutes=self.breakPeriod)

        elif (not (self.workMode)
              and self.currentIteration + 1 <= self.iterations):
            self.workMode = True
            self.currentIteration += 1
            self.iterEndTime = self.iterStartTime.astimezone(pytz.utc) + datetime.timedelta(
                minutes=self.workPeriod)

        else:
            return False
        return True

    def addTime(self, minutes: float) -> None:
        self.iterEndTime += datetime.timedelta(minutes=minutes)

    def trigger_chat_mode(self, set=True) -> None:
        self.chatMode = set

    def pause(self, pausePeriod) -> None:
        self.iterStartTime = datetime.datetime.now(pytz.utc)
        self.pausedAtTimeLeft = self.timeLeft
        self.iterEndTime = self.iterStartTime.astimezone(pytz.utc) + datetime.timedelta(
            minutes=pausePeriod)

    def resume(self) -> None:
        self.iterStartTime = datetime.datetime.now(pytz.utc)
        self.iterEndTime = self.iterStartTime.astimezone(pytz.utc) + self.pausedAtTimeLeft
        self.pausedAtTimeLeft = None

    def endTask(self) -> None:
        if(not self.done):
            self.done = True
            self.totalWorkTime += (datetime.datetime.now(pytz.utc) -
                                   self.iterStartTime.astimezone(pytz.utc))
            self.endTime = datetime.datetime.now(pytz.utc)

    @property
    def timeTaken(self) -> datetime.timedelta:
        if(self.done):
            return self.totalWorkTime
        return self.totalWorkTime + (datetime.datetime.now(pytz.utc) - self.iterStartTime.astimezone(pytz.utc))

    @property
    def paused(self) -> bool:
        return not(self.pausedAtTimeLeft is None)

    @property
    def timeLeft(self) -> datetime.timedelta:
        return self.iterEndTime.astimezone(pytz.utc) - datetime.datetime.now(pytz.utc)

    @property
    def timeLeftM(self) -> int:
        return round(self.timeLeft.total_seconds() / 60)

    def __str__(self) -> str:
        if(self.done):
            return super().__str__()
        if(self.workMode):
            text = f"{self.userDisplayName}: {self.work} {self.timeLeftM}"
            if (self.iterations > 1):
                text += f" ({self.currentIteration} of {self.iterations})"
        else:
            text = f"{self.userDisplayName}: Relax! {self.timeLeftM}"
            if (self.iterations > 1):
                text += f" ({self.currentIteration} of {self.iterations})"
        return text


class WorkingUser():
    def __init__(
        self,
        username: str,
        userDisplayName: str = None,
        totalWorkTime: Union[datetime.timedelta, float] = None,
        totalTasksCompleted: int = 0,
        totalPomosCompleted: int = 0,
    ):
        self.username = username
        self.userDisplayName = userDisplayName if userDisplayName else username
        if(totalWorkTime):
            if(type(totalWorkTime) is float or type(totalWorkTime) is int):
                self.totalWorkTime = datetime.timedelta(seconds=totalWorkTime)
            elif(type(totalWorkTime) is datetime.timedelta):
                self.totalWorkTime = totalWorkTime
        else:
            self.totalWorkTime: datetime.timedelta = datetime.timedelta()

        self.totalTasksCompleted = totalTasksCompleted
        self.totalPomosCompleted = totalPomosCompleted

    def to_dict(self) -> Dict:
        variables = vars(self)
        for k, v in variables.items():
            if (type(v) is datetime.datetime):
                variables[k] = str(v)
            if (type(v) is datetime.timedelta):
                variables[k] = v.total_seconds()
        return variables
    
    @property
    def totalTimeM(self) -> int:
        return round(self.totalWorkTime.total_seconds() / 60)
    
    def __str__(self) -> str:
        return f"{self.userDisplayName}: Total Work Time={self.totalTimeM} Completed Tasks={self.totalTasksCompleted} Completed Pomos={self.totalPomosCompleted}"


class Pomo():

    # Channel methods
    @staticmethod
    def get_all_channels():
        return [channel for channel in db.tables() if not("-" in channel)]

    @staticmethod
    def remove_channel(channel: str):
        db.drop_table(channel.lower())
        db.drop_table(channel.lower()+"-Task")
        db.drop_table(channel.lower()+"-Timer")
        db.drop_table(channel.lower()+"-DoneTasks")
        return

    @staticmethod
    def create_channel(channel: str):
        table = db.table(channel.lower())
        table.insert(Document({"name": channel.lower()}, doc_id=0))
        table.remove(doc_ids=[0])
        table = db.table(channel.lower()+"-Task")
        table.insert(Document({"name": channel.lower()}, doc_id=0))
        table.remove(doc_ids=[0])
        table = db.table(channel.lower()+"-Timer")
        table.insert(Document({"name": channel.lower()}, doc_id=0))
        table.remove(doc_ids=[0])
        table = db.table(channel.lower()+"-DoneTasks")
        table.insert(Document({"name": channel.lower()}, doc_id=0))
        table.remove(doc_ids=[0])

    @staticmethod
    def remove_all_data(channel: str):
        Pomo.remove_channel(channel)
        Pomo.create_channel(channel)

    @staticmethod
    def purge_tasks(channel: str):
        table = db.table(channel.lower()+"-Task")
        table.update(Pomo.tinyDbOperations("finishAllTasks"))

    # Task methods

    def get_userQuery(user: Union[Chatter, PartialChatter, str], multiple: bool = False) -> Union[Dict[str, QueryInstance], Dict[str, int]]:
        if(type(user) is Chatter):
            if(multiple):
                userQuery = {"doc_ids": [int(user.id)]}
            else:
                userQuery = {"doc_id": int(user.id)}
        elif(type(user) is PartialChatter):
            userQuery = {"cond": where("username") == user.name}
        else:
            userQuery = {"cond": where("username") == user.lower()}
        return userQuery

    # Get data
    @staticmethod
    def get_workingUser(channel: str, user: Union[Chatter, PartialChatter, str]) -> WorkingUser:
        table = db.table(channel)
        userQuery = Pomo.get_userQuery(user)
        workingUserDict = table.get(**userQuery)
        if(workingUserDict):
            return WorkingUser(**workingUserDict)

    @staticmethod
    def get_all_dicts(channel: str) -> Dict[str, List[Dict]]:
        allDicts = {}
        allDicts["Timers"] = Pomo.get_active_timer_dicts(channel)
        allDicts["Tasks"] = Pomo.get_active_task_dicts(channel)
        allDicts["DoneTasks"] = Pomo.get_done_task_dicts(channel)
        return allDicts

    @staticmethod
    def get_all_task_dicts(channel: str) -> List[Dict]:
        allDicts = []
        allDicts += Pomo.get_active_timer_dicts(channel)
        allDicts += Pomo.get_active_task_dicts(channel)
        allDicts += Pomo.get_done_task_dicts(channel)
        return allDicts

    @staticmethod
    def get_active_timer_dicts(channel: str) -> List[Dict]:
        table = db.table(channel.lower()+"-Timer")
        timerDicts = table.all()
        return timerDicts

    @staticmethod
    def get_active_task_dicts(channel: str) -> List[Dict]:
        table = db.table(channel.lower()+"-Task")
        taskDicts = table.all()
        return taskDicts
    
    
    def get_all_tasks(channel: str) -> List[Task]:
        allTasks = []
        allTasks += Pomo.get_active_timers(channel)
        allTasks += Pomo.get_active_tasks(channel)
        allTasks += Pomo.get_done_tasks_all(channel)
        return allTasks

    @staticmethod
    def get_done_task_dicts(channel: str) -> List[Dict]:
        table = db.table(channel.lower()+"-DoneTasks")
        doneTasksWrapperDicts: List[Document] = table.all()
        doneTaskDicts: List[dict] = []
        for doneTasksWrapperDict in doneTasksWrapperDicts:
            for doneTasksDict in doneTasksWrapperDict.get("doneTasks"):
                doneTaskDicts.append(doneTasksDict)
        return doneTaskDicts

    @staticmethod
    def get_active_timers(channel: str) -> List[Timer]:
        table = db.table(channel.lower()+"-Timer")
        timerDicts = table.all()
        timers = []
        for timerDict in timerDicts:
            timers.append(Timer(**timerDict))
        return timers

    @staticmethod
    def get_active_tasks(channel: str) -> List[Task]:
        table = db.table(channel.lower()+"-Task")
        taskDicts = table.all()
        tasks = []
        for taskDict in taskDicts:
            tasks.append(Task(**taskDict))
        return tasks

    @staticmethod
    def get_done_tasks_all(channel: str) -> List[Task]:
        table = db.table(channel.lower()+"-DoneTasks")
        doneTasksWrapperDicts: List[Document] = table.all()
        doneTasks: List[Task] = []
        for doneTasksWrapperDict in doneTasksWrapperDicts:
            for doneTasksDict in doneTasksWrapperDict.get("doneTasks"):
                doneTasks.append(Task(**doneTasksDict))
        return doneTasks

    @staticmethod
    def get_done_tasks(channel: str, user: Union[Chatter, PartialChatter, str]) -> List[Task]:
        table = db.table(channel.lower()+"-DoneTasks")
        userQuery = Pomo.get_userQuery(user)
        doneTasksDict: Document = table.get(**userQuery)
        doneTasks: List[Task] = []
        for doneTasksDict in doneTasksDict.get("doneTasks"):
            doneTasks.append(Task(**doneTasksDict))
        return doneTasks

    @staticmethod
    def get_timer(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Timer]:
        table = db.table(channel.lower()+"-Timer")
        userQuery = Pomo.get_userQuery(user)
        timerDict: dict = table.get(**userQuery)

        if timerDict is not None:
            timer = Timer(**timerDict)
            return timer
        return None

    @staticmethod
    def get_task(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Task]:
        table = db.table(channel.lower()+"-Task")
        userQuery = Pomo.get_userQuery(user)
        taskDict: dict = table.get(**userQuery)

        if taskDict is not None:
            task = Task(**taskDict)
            return task
        return None

    @staticmethod
    def time_left(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[int]:
        timer = Pomo.get_timer(channel.lower(), user)
        if timer is not None:
            return timer.timeLeftM

    @staticmethod
    def has_active_timer(channel: str, user: Union[Chatter, PartialChatter, str]):
        table = db.table(channel.lower()+"-Timer")
        userQuery = Pomo.get_userQuery(user)
        return table.contains(**userQuery)

    @staticmethod
    def has_active_task(channel: str, user: Union[Chatter, PartialChatter, str]):
        table = db.table(channel.lower()+"-Task")
        userQuery = Pomo.get_userQuery(user)
        return table.contains(**userQuery)

    @staticmethod
    def has_done_tasks(channel: str, user: Union[Chatter, PartialChatter, str]):
        table = db.table(channel.lower()+"-DoneTasks")
        userQuery = Pomo.get_userQuery(user)
        doneTasks = table.contains(**userQuery)
        return doneTasks and doneTasks.doneTasks.count() > 0

    # Manipulate data
    @staticmethod
    def write_timer(channel: str, user: Union[Chatter, PartialChatter, str], timer: Timer) -> None:
        table = db.table(channel.lower()+"-Timer")
        userQuery = Pomo.get_userQuery(user)
        if table.contains(**userQuery):
            if(type(user) is Chatter):
                table.upsert(Document(timer.to_dict(), doc_id=user.id))
            elif(type(user) is PartialChatter):
                table.upsert(timer.to_dict(), where("username")==user.name)
            elif(type(user) is str):
                table.upsert(timer.to_dict(), where("username")==user)
        else:
            if(type(user) is not Chatter):
                raise ArgumentTypeError(f"{user} is not of Type Chatter")
            table.insert(Document(timer.to_dict(), doc_id=user.id))
            Pomo.create_workingUser(channel, user)

    @staticmethod
    def set_timer(
        channel: str,
        user: Union[Chatter, PartialChatter, str],
        workPeriod: int,
        breakPeriod: int = 0,
        iterations: int = 1,
        work: str = "work",
        **kwargs
    ) -> Timer:

        current_time = datetime.datetime.now(pytz.utc)

        timer = Timer(
            username=user if type(user) is str else user.name,
            userDisplayName=user.display_name if type(
                user) is Chatter else None,
            workPeriod=workPeriod,
            breakPeriod=breakPeriod,
            iterations=iterations,
            iterStartTime=current_time,
            work=work,
            **kwargs,
        )

        Pomo.write_timer(channel, user, timer)
        return timer

    @staticmethod
    def write_workingUser(channel: str, user: Union[Chatter, PartialChatter, str], workingUser: WorkingUser):
        table = db.table(channel.lower())
        userQuery = Pomo.get_userQuery(user)
        if table.contains(**userQuery):
            if(type(user) is Chatter):
                table.upsert(Document(workingUser.to_dict(), doc_id=user.id))
            elif(type(user) is PartialChatter):
                table.upsert(workingUser.to_dict(), where("username")==user.name)
            elif(type(user) is str):
                table.upsert(workingUser.to_dict(), where("username")==user)
        else:
            if(type(user) is not Chatter):
                raise ArgumentTypeError(f"{user} is not of Type Chatter")
            table.insert(Document(workingUser.to_dict(), doc_id=user.id))

    @staticmethod
    def create_workingUser(channel: str, user: Chatter) -> Optional[WorkingUser]:
        table = db.table(channel.lower())
        if(not table.contains(doc_id=user.id)):
            workingUser = WorkingUser(
                username=user.name,
                userDisplayName=user.display_name,
            )
            table.insert(Document(workingUser.to_dict(), doc_id=user.id))
            return workingUser

    @staticmethod
    def write_task(channel: str, user: Union[Chatter, PartialChatter, str], task: Task) -> None:
        table = db.table(channel.lower()+"-Task")
        userQuery = Pomo.get_userQuery(user)
        if table.contains(**userQuery):
            if(type(user) is Chatter):
                table.upsert(Document(task.to_dict(), doc_id=user.id))
            elif(type(user) is PartialChatter):
                table.upsert(task.to_dict(), where("username")==user.name)
            elif(type(user) is str):
                table.upsert(task.to_dict(), where("username")==user)
        else:
            if(type(user) is not Chatter):
                raise ArgumentTypeError(f"{user} is not of Type Chatter")
            table.insert(Document(task.to_dict(), doc_id=user.id))
            Pomo.create_workingUser(channel, user)

    @staticmethod
    def set_task(
        channel: str,
        user: Union[Chatter, PartialChatter, str],
        work: str = "work",
        **kwargs
    ) -> Task:

        current_time = datetime.datetime.now(pytz.utc)

        task = Task(
            username=user if type(user) is str else user.name,
            userDisplayName=user.display_name if
            type(user) is Chatter else None,
            startTime=current_time,
            work=work,
            **kwargs,
        )

        Pomo.write_task(channel, user, task)
        return task

    @staticmethod
    def set_chat_mode(channel: str, user: Union[Chatter, PartialChatter, str], chatMode: bool):
        table = db.table(channel.lower()+"-Timer")
        userQuery = Pomo.get_userQuery(user, multiple=True)
        table.update(Pomo.tinyDbOperations(
            "setChatMode", chatMode), **userQuery)

    @staticmethod
    def add_done_task(channel: str, user: Union[Chatter, PartialChatter, str], doneTask: Union[Task, Timer]):
        table = db.table(channel.lower()+"-DoneTasks")
        userQuery = Pomo.get_userQuery(user)
        if(type(doneTask) is Timer):
            doneTask = Task(**(doneTask.to_dict()))

        if(table.contains(**userQuery)):
            userQuery = Pomo.get_userQuery(user, multiple=True)
            table.update(Pomo.tinyDbOperations(
                "addDoneTask", doneTask), **userQuery)
        else:
            if(type(user) is not Chatter):
                raise ArgumentTypeError(f"{user} is not of Type Chatter")
            table.insert(Document(dict(username=user.name, doneTasks=[
                         doneTask.to_dict()]), doc_id=user.id))

    @staticmethod
    def add_to_workingUser(channel: str, user: Union[Chatter, PartialChatter, str], task: Union[Task, Timer, datetime.timedelta]):
        table = db.table(channel.lower())
        userQuery = Pomo.get_userQuery(user)
        userQueryUpdate = Pomo.get_userQuery(user, multiple=True)

        if(table.contains(**userQuery)):
            table.update(Pomo.tinyDbOperations(
                "addToWorkingUser", task), **userQueryUpdate)
        else:
            if(type(user) is not Chatter):
                raise ArgumentTypeError(f"{user} is not of Type Chatter")
            Pomo.write_workingUser(channel, user)
            table.update(Pomo.tinyDbOperations(
                "addToWorkingUser", task), **userQueryUpdate)

    # Finish stuff

    @staticmethod
    def remove_done_index(channel: str, user: Union[Chatter, PartialChatter, str], index: int) -> None:
        userQuery = Pomo.get_userQuery(user)

        table = db.table(channel.lower()+"-DoneTasks")
        doneTasks = table.get(**userQuery)
        if(doneTasks and doneTasks.get("doneTasks") and len(doneTasks.get("doneTasks")) >= abs(index)):
            userQuery = Pomo.get_userQuery(user, multiple=True)
            if(index > 0): index -= 1
            table.update(Pomo.tinyDbOperations("removeDoneTask", index), **userQuery)
            return True
        return False

    @staticmethod
    def remove_done_all(channel: str, user: Union[Chatter, PartialChatter, str]) -> bool:
        userQuery = Pomo.get_userQuery(user, multiple=True)

        table = db.table(channel.lower()+"-DoneTasks")
        return bool(len(table.update(Pomo.tinyDbOperations("removeDoneTasks"), **userQuery)))

    @staticmethod
    def remove_all_done(channel: str) -> None:
        table = db.table(channel.lower()+"-DoneTasks")
        table.update(Pomo.tinyDbOperations("removeDoneTasks"))

    @staticmethod
    def remove_timer(channel: str, user: Union[Chatter, PartialChatter]) -> bool:
        userQuery = Pomo.get_userQuery(user, multiple=True)
        table = db.table(channel.lower()+"-Timer")
        return bool(table.remove(**userQuery))

    @staticmethod
    def finish_timer(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Timer]:
        timer = Pomo.get_timer(channel, user)

        if timer is not None:
            timer.endTask()
            Pomo.add_to_workingUser(channel, user, timer)
            Pomo.remove_timer(channel, user)
            return timer
        return None

    @staticmethod
    def complete_task(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Timer]:
        userQuery = Pomo.get_userQuery(user)
        userQueryMultiple = Pomo.get_userQuery(user, multiple=True)

        table = db.table(channel.lower()+"-Task")
        taskDict = table.get(**userQuery)
        if(taskDict):
            task: Task = Task(**taskDict)
            task.endTask()
            Pomo.add_to_workingUser(channel, user, task)
            Pomo.add_done_task(channel, user, task)
            table.remove(**userQueryMultiple)
            return task
        return None

    @staticmethod
    def complete_timer(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Timer]:
        userQuery = Pomo.get_userQuery(user)
        userQueryMultiple = Pomo.get_userQuery(user, multiple=True)

        table = db.table(channel.lower()+"-Timer")
        timerDict = table.get(**userQuery)
        if(timerDict):
            timer: Timer = Timer(**timerDict)
            timer.endTask()
            Pomo.add_to_workingUser(channel, user, timer)
            Pomo.add_done_task(channel, user, timer)
            table.remove(**userQueryMultiple)
            return timer
        return None

    @staticmethod
    def finish_task(channel: str, user: Union[Chatter, PartialChatter, str]) -> Optional[Task]:
        userQuery = Pomo.get_userQuery(user)

        table = db.table(channel.lower()+"-Task")
        taskDict = table.get(**userQuery)
        if(taskDict):
            task: Task = Task(**taskDict)
            task.endTask()
            Pomo.add_to_workingUser(channel, user, task)
            userQuery = Pomo.get_userQuery(user, multiple=True)
            table.remove(**userQuery)
            return task
        return None

    # TinyDB Operations

    @staticmethod
    def tinyDbOperations(operation: str, item: Union[Timer, Task, int, bool] = None, channel: str = None):

        def addDoneTask(doc: Document):
            doc["doneTasks"].append(item.to_dict())

        def removeDoneTask(doc: Document):
            if(item):
                doc["doneTasks"].pop(item)
            else:
                doc["doneTasks"].pop()

        def removeDoneTasks(doc: Document):
            doc["doneTasks"] = []

        def addToWorkingUser(doc: Document):
            totalWorkTime = datetime.timedelta(seconds=doc.get("totalWorkTime"))
            if(type(item) is datetime.timedelta):
                totalWorkTime += item
            elif(type(item) is float or type(item) is int):
                totalWorkTime += datetime.timedelta(minutes=item)
            elif(type(item) is Task):
                totalWorkTime += item.timeTaken
                doc["totalTasksCompleted"] += 1
            elif(type(item) is Timer):
                totalWorkTime += item.timeTaken
                doc["totalPomosCompleted"] += 1
            else:
                raise ValueError(f"Item of type '{type(item)}' is not Valid.")
            doc["totalWorkTime"] = totalWorkTime.total_seconds()


        def finishAllTasks(doc: Document):
            Pomo.finish_timer(channel, doc.get("username"))
            Pomo.finish_task(channel, doc.get("username"))
            Pomo.remove_done_all(channel, doc.get("username"))

        def setChatMode(doc: Document):
            doc["chatMode"] = item

        operationsDict: dict = {
            "addDoneTask": addDoneTask,
            "setChatMode": setChatMode,
            "addToWorkingUser": addToWorkingUser,
            "removeDoneTask": removeDoneTask,
            "finishAllTasks": finishAllTasks,
            "removeDoneTasks": removeDoneTasks,
        }
        # getattr(operation)
        return operationsDict[operation]
