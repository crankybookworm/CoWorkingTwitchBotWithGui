import json
from flask import Flask, redirect, url_for, request, render_template
from pomo_logic import Pomo, Thread_With_Exception
# from replit import db

app = Flask(__name__)

# config file has STATIC_FOLDER='/core/static'
# app.static_url_path="BotResources/static"
app.template_folder="BotResources/templates"

# set the absolute path to the static folder
app.static_folder="BotResources/static"

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        user = request.form['channel']
        return redirect(url_for('pomoAllTasks', channel=user))
    else:
        user = request.args.get('channel')
        if (user):
            return redirect(url_for('pomoAllTasks', channel=user))
        else:
            return render_template("index.html")


@app.route('/allTasksData/<channel>')
def pomoAllTasksData(channel: str):
    channel = channel.lower()
    if (channel in list(Pomo.get_all_channels())):
        return json.dumps(Pomo.get_all_task_dicts(channel))
    return f'Bot instance not running for {channel}'


@app.route('/tasksData/<channel>')
def pomoTasksData(channel: str):
    channel = channel.lower()
    if (channel in list(Pomo.get_all_channels())):
        return json.dumps(Pomo.get_active_task_dicts(channel))
    return f'Bot instance not running for {channel}'


@app.route('/timersData/<channel>')
def pomoTimersData(channel: str):
    channel = channel.lower()
    if (channel in list(Pomo.get_all_channels())):
        return json.dumps(Pomo.get_active_timer_dicts(channel))
    return f'Bot instance not running for {channel}'

@app.route('/doneTasksData/<channel>')
def pomoDoneTasksData(channel: str):
    channel = channel.lower()
    if (channel in list(Pomo.get_all_channels())):
        return json.dumps(Pomo.get_done_task_dicts(channel))
    return f'Bot instance not running for {channel}'



@app.route('/allTasks/<channel>')
def pomoAllTasks(channel: str):
    channel = channel.lower()
    return render_template('pomoBoard.html',
                           title=f'Pomos on {channel}',
                           channel=channel,
                           dataPath="pomoAllTasksData",
                           tableTitle="All Tasks")

@app.route('/tasks/<channel>')
def pomoTasks(channel: str):
    channel = channel.lower()
    return render_template('pomoBoard.html',
                           title=f'Pomos on {channel}',
                           channel=channel,
                           dataPath="pomoTasksData",
                           tableTitle="Tasks")

@app.route('/timers/<channel>')
def pomoTimers(channel: str):
    channel = channel.lower()
    return render_template('pomoBoard.html',
                           title=f'Pomos on {channel}',
                           channel=channel,
                           dataPath="pomoTimersData",
                           tableTitle="Timers")

@app.route('/doneTasks/<channel>')
def pomoDoneTasks(channel: str):
    channel = channel.lower()
    return render_template('pomoBoard.html',
                           title=f'Pomos on {channel}',
                           channel=channel,
                           dataPath="pomoDoneTasksData",
                           tableTitle="Done Tasks")



def runWebOutput(host='0.0.0.0', port=8080):
    app.config.from_mapping({
        "ENV": "development", 
        "TESTING": True,
        'TEMPLATES_AUTO_RELOAD': True,
    })
    app.run(host=host, port=port)


def startWebOutput(host='0.0.0.0', port=8080):
    t = Thread_With_Exception(target=runWebOutput, name="WebOutput", kwargs={"host": host, "port": port})
    t.start()
    return t


def stopWebOutput(t: Thread_With_Exception):
    t.raise_exception() 
    t.join()

if __name__ == "__main__":
    runWebOutput()