from json import JSONDecodeError
from pomo_logic import Pomo, Thread_With_Exception
from time import sleep

def keepOutputtingToFile(filename: str, channel: str, interval: float):
    while True:
        with open(filename, 'w') as f:
            try:
                for timer in sorted(Pomo.get_active_timers(channel), key=lambda x: x.startTime):
                    f.write(str(timer))
                for task in sorted(Pomo.get_active_tasks(channel), key=lambda x: x.startTime):
                    f.write(str(task))
                for task in sorted(Pomo.get_done_tasks_all(channel), key=lambda x: x.startTime):
                    f.write(str(task))
            except JSONDecodeError: pass
        sleep(interval)


def runFileOutput(filename: str, channel: str, interval: int = 5):
    keepOutputtingToFile(filename, channel.lower(), interval)


def startFileOutput(filename: str, channel: str, interval: int = 5):
    t = Thread_With_Exception(target=runFileOutput, name="FileOutput", kwargs={"filename": filename, "channel": channel, "interval": interval})
    t.start()
    return t


def stopFileOutput(t: Thread_With_Exception):
    t.raise_exception() 
    t.join()