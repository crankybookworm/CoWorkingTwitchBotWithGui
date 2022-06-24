# bot.py
# bot.commands
# Developers - twitch.tv/00mb1, twitch.tv/CrankyBookworm

import os
from twitchio.abcs import Messageable
from twitchio import Message, Channel
from twitchio.ext import commands
from twitchio.ext.commands import Bot
from pomo_logic import *
from typing import Dict
import asyncio
import re
import json
import logging
from bot_config import BotConfig
from chatbot_config import ChatBotConfig
from file_output import startFileOutput
from web_output import startWebOutput

################ Setup Section Started ################

logging.basicConfig(filename='BotResources/bot.log', level=logging.ERROR)



class CoWorkingBot(Bot):
    def __init__(self, botConfig: BotConfig, chatBotConfig: ChatBotConfig):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        self.botConfig = botConfig
        self.chatBotConfig = chatBotConfig

        self.allChannels: list = [
            channel.lower() for channel in Pomo.get_all_channels()
        ]
        if (botConfig.streamerUsername.lower() not in self.allChannels):
            self.allChannels.append(botConfig.streamerUsername.lower())
        
        self.loop = self.get_or_create_eventloop()
        super().__init__(
            token=self.botConfig.oAuthToken,
            prefix=self.botConfig.botPrefix,
            initial_channels=self.allChannels,
        )
        self.flipDict = json.load(
            open('./BotResources/resources/flipDict.json', encoding='utf-8'))
        self.asyncTasks: Dict[str, Dict[str, asyncio.Task]] = dict()
    
    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex) or \
                "Event loop is closed" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()
            else:
                raise ex

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        if not (self.nick in [chan.name for chan in self.connected_channels]):
            self.allChannels.append(self.nick)
            await self.join_channels([self.nick])
        for channel in self.connected_channels:
            self.asyncTasks[channel.name] = dict()
            Pomo.create_channel(channel.name)
            await self.restoreOldTimers(channel)
            await channel.send(f"/me has landed!")

    async def event_message(self, ctx: Message):
        'Runs every time a message is sent in chat.'
        # make sure the bot ignores itself
        if (ctx.echo or not (ctx.channel.name in self.allChannels)):
            return
        cmd = ctx.content.split(' ', 1)[0].lower()
        if (cmd.startswith(self._prefix)):
            cmd = cmd[1:]
            if (cmd in list(self.commands.keys())):
                await self.handle_commands(ctx)
        else:  # If user has a Timer Running
            timer: Timer = Pomo.get_timer(ctx.channel.name, ctx.author.name)
            if (timer is not None and timer.workMode and not (timer.paused)
                    and not (timer.chatMode)):
                await ctx.channel.send(
                    f"{ctx.author.name}, " +
                    self.chatBotConfig.getText("pomoReminder", timer=timer)
                )


################ Setup Section Ended ################

    @commands.command(name='hello')
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.reply(self.chatBotConfig.getText("helloResponse", username=ctx.author.display_name))

################ Pomo Section Started ################
# Pomodoro

    @commands.command(name='pomo')
    async def pomoCommand(self,
                          ctx: commands.Context,
                          workPeriod='',
                          breakPeriod='',
                          iterations='',
                          work=''):
        channel = ctx.channel.name.lower()
        prefix = '^' + self._prefix + ctx.command.name
        dRe = "(\\d*\\.|)\\d+"

        if bool(re.match(prefix + " " + dRe + "( .*)?$", ctx.message.content)):
            return await self.startPomo(ctx, channel, ctx.author, dRe, workPeriod, breakPeriod, iterations, work)

        # !pomo complete
        if (workPeriod.lower() == "complete"):
            timer = Pomo.finish_timer(channel, ctx.author)
            if timer:
                await ctx.reply(
                    self.chatBotConfig.getText("completeAll", timer=timer)
                )
                self.asyncTasks[channel][ctx.author.name].cancel()
            else:
                await ctx.reply(self.chatBotConfig.getText("noRunningPomo",username=ctx.author.display_name))
            return

        # !pomo chat
        elif (workPeriod.lower() == "chat"):
            if (Pomo.has_active_timer(channel, ctx.author)):
                Pomo.set_chat_mode(channel, ctx.author, True)
                await ctx.reply(
                    self.chatBotConfig.getText("chatModeOn",
                        username=ctx.author.display_name)
                )
                return
            await ctx.reply(self.chatBotConfig.getText("noRunningPomo",username=ctx.author.display_name))
            return

        # !pomo focus
        elif (workPeriod.lower() == "focus"):
            if (Pomo.has_active_timer(channel, ctx.author)):
                Pomo.set_chat_mode(channel, ctx.author, False)
                await ctx.reply(
                    self.chatBotConfig.getText("chatModeOff",
                        username=ctx.author.display_name)
                )
                return
            await ctx.reply(self.chatBotConfig.getText("noRunningPomo", username=ctx.author.display_name))
            return

        # !pomo stats
        elif (workPeriod.lower() == "stats"):
            workingUser = Pomo.get_workingUser(channel, ctx.author)
            if(workingUser):
                await ctx.reply(self.chatBotConfig.getText("userStats", workingUser=workingUser))
            else:
                await ctx.reply(self.chatBotConfig.getText("noUserStats", username=ctx.author.display_name))
            return

        # !pomo +/-time
        elif (bool(re.match("^(\\+|\\-)" + dRe + "$", workPeriod))
              or (bool(re.match("^(\\+|\\-)$", workPeriod))
                  and bool(re.match("^" + dRe + "$", breakPeriod)))):
            timer = Pomo.get_timer(channel, ctx.author)
            if (timer is None):
                await ctx.reply(self.chatBotConfig.getText("noRunningPomo", username=ctx.author.display_name))
                return

            self.asyncTasks[channel][ctx.author.name].cancel()
            self.asyncTasks[channel][ctx.author.name] = asyncio.create_task(self.nextIter(
                ctx, timer, float(workPeriod)),
                name=ctx.author.name)
            return

        # !pomo check
        elif (workPeriod.lower() == "check"):
            if (Pomo.has_active_task(channel, ctx.author)):
                await self.addTask(ctx)
            else:
                await self.timer(ctx)
            return

        # !pomo pause [Pause Period]
        elif (workPeriod.lower() == "pause"):
            if (not (bool(re.match(dRe + "$", breakPeriod)) and
                     float(breakPeriod) <= 300 and float(breakPeriod) >= 5)):
                await ctx.reply(
                    self.chatBotConfig.getText("pauseInfo", 
                        username=ctx.author.display_name)
                )
                return
            timer = Pomo.get_timer(channel, ctx.author)
            if (timer is None):
                await ctx.reply(self.chatBotConfig.getText("noRunningPomo", username=ctx.author.display_name))
                return
            self.asyncTasks[channel][ctx.author.name].cancel()
            timer.pause(float(breakPeriod))
            Pomo.write_timer(channel,  timer.username, timer)
            await ctx.reply(f"Pausing timer for {int(breakPeriod)}")
            self.asyncTasks[channel][ctx.author.name] = asyncio.create_task(
                self.restoreWait(ctx, timer), name=ctx.author.name)
            return

        # !pomo resume
        elif (workPeriod.lower() == "resume"):
            timer: Timer = Pomo.get_timer(channel, ctx.author)
            if (timer is None):
                await ctx.reply(self.chatBotConfig.getText("noRunningPomo", username=ctx.author.display_name))
                return
            if (not (timer.paused)):
                await ctx.reply(self.chatBotConfig.getText("noPaused", username=ctx.author.display_name))
                return
            self.asyncTasks[channel][ctx.author.name].cancel()
            timer.resume()
            await ctx.reply(self.chatBotConfig.getText("resumeTrigger", timer=timer))
            self.asyncTasks[channel][ctx.author.name] = asyncio.create_task(
                self.restoreWait(ctx, timer), name=ctx.author.display_name)
            return

        # !pomo help
        else:
            await ctx.reply(
                self.chatBotConfig.getText("pomoInfo", 
                    username=ctx.author.display_name)
            )
            return

    # Handles the start of Pomo

    async def startPomo(self,
                        ctx: commands.Context,
                        channel: str,
                        user: Union[Chatter, PartialChatter, str],
                        dRe: str,
                        workPeriod: str = '',
                        breakPeriod: str = '',
                        iterations: str = '',
                        work: str = '',
                        ) -> None:

        timer = Pomo.get_timer(channel, user)
        if (Pomo.has_active_timer(channel, user)):
            await self.addTask(ctx)
            return
        elif (Pomo.has_active_task(channel, user)):
            await self.timer(ctx)
            return

        # !pomo [Study Period] [Break Period] [Sessions] [Work]

        # if bool(re.match(dRe, workPeriod)):
        workPeriod = float(workPeriod)

        if bool(re.match(dRe, breakPeriod)):
            breakPeriod = float(breakPeriod)
            if bool(re.match(dRe, iterations)):
                iterations = int(iterations)
                try:
                    work = ctx.message.content.split(' ', 4)[4]
                except IndexError:
                    work = "Work"

            else:
                iterations = 1
                try:
                    work = ctx.message.content.split(' ', 3)[3]
                except IndexError:
                    work = "Work"
        else:
            breakPeriod = 0
            iterations = 1
            try:
                work = ctx.message.content.split(' ', 2)[2]
            except IndexError:
                work = "Work"

        # Validate Time Periods
        if (workPeriod < 5 and workPeriod != 0):
            await ctx.reply(
                self.chatBotConfig.getText("invalidWorkPeriod", 
                    username=ctx.author.display_name, workPeriod=workPeriod)
            )
            return
        elif (breakPeriod < 5 and breakPeriod != 0):
            await ctx.reply(
                self.chatBotConfig.getText("invalidBreakPeriod", 
                    username=ctx.author.display_name, breakPeriod=breakPeriod)
            )
            return
        elif (iterations < 1 or iterations > 10):
            await ctx.reply(
                self.chatBotConfig.getText("invalidIterations", 
                    username=ctx.author.display_name, iterations=iterations)
            )
            return
        elif (workPeriod == 0 and breakPeriod == 0) or (workPeriod == 0 and iterations > 1):
            await ctx.reply(
                self.chatBotConfig.getText("invalidWorkPeriod", 
                    username=ctx.author.display_name, workPeriod=workPeriod)
            )
            return
        elif(breakPeriod == 0 and iterations > 1):
            await ctx.reply(
                self.chatBotConfig.getText("invalidBreakPeriod", 
                    username=ctx.author.display_name, breakPeriod=breakPeriod)
            )
            return
        elif(((breakPeriod * iterations) + (workPeriod * iterations)) > 300):
            await ctx.reply(
                self.chatBotConfig.getText("invalidTotalTime", 
                    username=ctx.author.display_name, breakPeriod=breakPeriod)
            )
            return

        timer = Pomo.set_timer(
            channel=channel,
            user=ctx.author,
            workPeriod=workPeriod,
            breakPeriod=breakPeriod,
            iterations=iterations,
            work=work,
            chatMode=ctx.author.is_mod,
        )

        self.asyncTasks[channel][ctx.author.name] = asyncio.create_task(
            self.nextIter(ctx, timer), name=ctx.author.name)

    async def nextIter(self, ctx: Messageable, timer: Timer, modify: float = 0):
        # Regular Pomo Sessions
        if (modify == 0):
            if (timer.workMode):
                if (timer.iterations > 1):
                    await ctx.send(f"{timer.userDisplayName}, " +
                                   self.chatBotConfig.getText(
                                       "startWorkMultiple", timer=timer)
                                   )
                else:
                    await ctx.send(f"{timer.userDisplayName}, " +
                                   self.chatBotConfig.getText(
                                       "startWorkSingle", timer=timer)
                                   )
                Pomo.write_timer(ctx._fetch_channel().name, timer.username, timer)
                await asyncio.sleep(timer.workPeriod * 60)
            else:
                if (timer.iterations > 1):
                    await ctx.send(f"{timer.userDisplayName}, " +
                                   self.chatBotConfig.getText(
                                       "workCompleteMultiple", timer=timer)
                                   )
                else:
                    await ctx.send(f"{timer.userDisplayName}, " +
                                   self.chatBotConfig.getText(
                                       "workCompleteSingle", timer=timer)
                                   )
                Pomo.write_timer(ctx._fetch_channel().name, timer.username, timer)
                await asyncio.sleep(timer.breakPeriod * 60)

        # Modify the Pomo Session and Resume
        elif (modify > 0):
            if (timer.timeLeftM + modify > 300):
                await ctx.reply(
                    self.chatBotConfig.getText(
                        "modifyError", timer=timer, modify=modify)
                )
            else:
                timer.addTime(modify)
                await ctx.reply(
                    self.chatBotConfig.getText(
                        "modifyAdd", timer=timer, modify=modify)
                )
                Pomo.write_timer(ctx._fetch_channel().name,
                                 timer.username, timer)
            await asyncio.sleep(timer.timeLeft.total_seconds())
        else:
            timer.addTime(modify)
            await ctx.reply(
                self.chatBotConfig.getText(
                    "modifySubtract", timer=timer, modify=modify)
            )
            if (timer.timeLeft.total_seconds() > 0):
                Pomo.write_timer(ctx._fetch_channel().name,
                                 timer.username, timer)
                await asyncio.sleep(timer.timeLeft.total_seconds())

        # Iterate to Next Session
        if Pomo.has_active_timer(ctx._fetch_channel().name, timer.username) is not None:
            if (timer.nextIter()):
                await self.nextIter(ctx, timer)
            else:
                Pomo.finish_timer(ctx._fetch_channel().name, timer.username)
                await ctx.send(
                    f'{timer.userDisplayName}, ' +
                    self.chatBotConfig.getText("completeAll", timer=timer)
                )

    async def restoreOldTimers(self, channel: Channel):
        for timer in Pomo.get_active_timers(channel.name):
            timeLost = timer.timeLeft
            if (timer.timeLeft.total_seconds() > 0):
                self.asyncTasks[channel.name][timer.username] = asyncio.create_task(
                    self.restoreWait(channel, timer), name=timer.username)

            elif (timer.nextIter()):
                iterLeft = True
                if (((timeLost + timer.timeLeft).total_seconds()) < 0):
                    iterLeft = True
                    while ((timeLost + timer.timeLeft).total_seconds() < 0):
                        timeLost += timer.timeLeft
                        if not (timer.nextIter()):
                            iterLeft = False
                            break

                if not (iterLeft):
                    Pomo.finish_timer(channel.name, timer.username)
                    continue
                else:
                    timer.iterEndTime += timeLost

                Pomo.write_timer(channel.name, timer.username, timer)
                self.asyncTasks[channel.name][timer.username] = asyncio.create_task(
                    self.restoreWait(channel, timer), name=timer.username)
            else:
                Pomo.finish_timer(channel.name, timer.username)

    async def restoreWait(self, ctx: Channel, timer: Timer):
        await asyncio.sleep(timer.timeLeft.total_seconds())
        if (timer.nextIter()):
            await self.nextIter(ctx, timer)
        else:
            Pomo.finish_timer(ctx._fetch_channel().name, timer.username)
            await ctx.send(f'{timer.username}, ' + self.chatBotConfig.getText("completeAll", timer=timer))

    @commands.command(name='timer')
    async def timer(self, ctx: commands.Context):
        if Pomo.has_active_timer(ctx.channel.name, ctx.author.name):
            timer = Pomo.get_timer(ctx.channel.name, ctx.author)
            if timer.timeLeftM < 1:
                await ctx.reply(self.chatBotConfig.getText("timeLeftLTOne", timer=timer))
            elif timer.timeLeftM == 1:
                await ctx.reply(self.chatBotConfig.getText("timeLeftOne", timer=timer))
            else:
                await ctx.reply(self.chatBotConfig.getText("timeLeftGTOne", timer=timer))
        else:
            await ctx.reply(self.chatBotConfig.getText("noRunningPomo", username=ctx.author.display_name))

    @commands.command(name='grinders')
    async def grinders(self, ctx: commands.Context):
        timer_array: list[Timer] = Pomo.get_active_timers(
            ctx.channel.name.lower())

        users = ""
        for timer in timer_array:
            if timer.workMode:
                users += timer.userDisplayName + " "
        if len(timer_array) == 0:
            message = self.chatBotConfig.getText("noGrinders",
                username=ctx.author.display_name)
        else:
            message = self.chatBotConfig.getText("sleepersSuffix",
                users=users, username=ctx.author.display_name)
        await ctx.reply(message)

    @commands.command(name='sleepers')
    async def sleepers(self, ctx: commands.Context):
        timer_array: list[Timer] = Pomo.get_active_timers(
            ctx.channel.name.lower())

        users = ""
        for timer in timer_array:
            if not timer.workMode:
                users += timer.userDisplayName + " "
        if len(timer_array) == 0:
            message = self.chatBotConfig.getText("noSleepers",
                username=ctx.author.display_name)
        else:
            message = self.chatBotConfig.getText("sleepersSuffix",
                users=users, username=ctx.author.display_name)
        await ctx.reply(message)

    @commands.command(name='purgeboard')
    async def purgeBoard(self, ctx: commands.Context):
        if (ctx.author.name == ctx.channel.name):
            users = self.asyncTasks[ctx.channel.name].keys()
            for user in users:
                self.asyncTasks[ctx.channel.name].pop(user).cancel()
            Pomo.purge_tasks(ctx.channel.name)
            await ctx.reply(self.chatBotConfig.getText("purgingBoard", username=ctx.author.display_name))
        else:
            await ctx.reply(self.chatBotConfig.getText("invalidPermStreamer", username=ctx.author.display_name))

################ Pomo Section Ended ################

################ Tasks Section Started ################

    @commands.command(name='task')
    async def addTask(self, ctx: commands.Context, work: str = ''):
        if Pomo.has_active_timer(ctx.channel.name, ctx.author):
            timer = Pomo.get_timer(ctx.channel.name, ctx.author)
            await ctx.reply(
                self.chatBotConfig.getText("runningPomoTask", timer=timer)
            )
            return
        elif Pomo.has_active_task(ctx.channel.name, ctx.author):
            task = Pomo.get_task(ctx.channel.name, ctx.author)
            await ctx.reply(self.chatBotConfig.getText("runningTask", task=task))
            return
        elif len(work) == 0:
            await ctx.reply(self.chatBotConfig.getText("noRunningTask", username=ctx.channel.name))
            return

        work = ctx.message.content.split(' ', 1)[1]
        task = Pomo.set_task(ctx.channel.name, ctx.author, work)
        await ctx.reply(f"Task '{task.taskWork}' added.")

    @commands.command(name='done')
    async def doneTask(self, ctx: commands.Context):
        if Pomo.has_active_timer(ctx.channel.name, ctx.author):
            timer = Pomo.complete_timer(ctx.channel.name, ctx.author)
            await ctx.reply(
                self.chatBotConfig.getText("completeAll", timer=timer)
            )
            self.asyncTasks[ctx.channel.name][ctx.author.name].cancel()
            return
        if not Pomo.has_active_task(ctx.channel.name, ctx.author):
            await ctx.reply(self.chatBotConfig.getText("noRunningTask", username=ctx.channel.name))
            return
        task: Task = Pomo.complete_task(ctx.channel.name, ctx.author)
        await ctx.reply(
            self.chatBotConfig.getText("completedTask", task=task)
        )

    @commands.command(name='finish')
    async def finishTasks(self, ctx: commands.Context):
        if Pomo.has_active_timer(ctx.channel.name, ctx.author):
            ctx.view.words[1] = 'complete'
            await self.pomoCommand(ctx)
            return
        if not Pomo.has_active_task(ctx.channel.name, ctx.author):
            await ctx.reply(self.chatBotConfig.getText("noRunningTask", username=ctx.channel.name))
            return
        task: Task = Pomo.finish_task(ctx.channel.name, ctx.author)
        task.done = True
        await ctx.reply(
            self.chatBotConfig.getText("completedTask", task=task)
        )

    @commands.command(name='rmvtask')
    async def rmvTaskFromBoard(self, ctx: commands.Context, username: str = ''):
        if (ctx.author.is_mod):
            if (len(username) == 0):
                username = ctx.author.name.lower()
            else:
                username = username.lower().replace('@', '')

            if (Pomo.has_active_timer(ctx.channel.name, username)):
                Pomo.finish_timer(ctx.channel.name, username)
                await ctx.reply(f"Removed Pomo found for user '{username}'.")
            elif (Pomo.has_active_task(ctx.channel.name, username)):
                Pomo.finish_task(ctx.channel.name, username)
                await ctx.reply(f"Removed Task found for user '{username}'.")
            else:
                await ctx.reply(f"No Task/Pomo found for user '{username}'.")
        else:
            await ctx.reply(self.chatBotConfig.getText("invalidPermMod", username=ctx.author.display_name))

    @commands.command(name='rmvdone')
    async def rmvDoneTasksFromBoard(self,
                                    ctx: commands.Context,
                                    arg1: str = '',
                                    username: str = ''):
        if(username != ''):
            if (ctx.author.is_mod):
                user = username.lower().replace('@', '')
                if(not Pomo.has_done_tasks(ctx.channel.name, user)):
                    await ctx.reply(f"{username} has no completed tasks.")
            else:
                await ctx.reply(f"Nice Try! Only Mods can do this.")
                return
        else: user = ctx.author

        if(Pomo.has_done_tasks(ctx.channel.name, user)):
            if(arg1 == '' or arg1.lower() == 'all'):
                if(Pomo.remove_done_all(ctx.channel.name, user)):
                    if(username == ''):
                        await ctx.reply(self.chatBotConfig.getText("rmvDone", username=user.display_name))
                    else:
                        await ctx.reply(self.chatBotConfig.getText("rmvDoneUser", username=username))
                else:
                    if(username == ''):
                        await ctx.reply(self.chatBotConfig.getText("rmvDoneFail", username=user.display_name))
                    else:
                        await ctx.reply(self.chatBotConfig.getText("rmvDoneUserFail", username=username))
            else:
                try:
                    taskNumber = int(arg1)
                    if(Pomo.remove_done_index(ctx.channel.name, user, taskNumber)):
                        if(username == ''):
                            await ctx.reply(self.chatBotConfig.getText("rmvDoneNum", username=user.display_name, index=taskNumber))
                        else:
                            await ctx.reply(self.chatBotConfig.getText("rmvDoneUserNum", username=username, index=taskNumber))
                    else:
                        if(username == ''):
                            await ctx.reply(self.chatBotConfig.getText("rmvDoneNumFail", username=user.display_name, index=taskNumber))
                        else:
                            await ctx.reply(self.chatBotConfig.getText("rmvDoneUserNumFail", username=username, index=taskNumber))
                except ValueError:
                    await ctx.reply(self.chatBotConfig.getText("rmvDoneInfo", username=username))
        else:
            if(username == ''):
                await ctx.reply(self.chatBotConfig.getText("rmvDoneFail", username=user.display_name))
            else:
                await ctx.reply(self.chatBotConfig.getText("rmvDoneUserFail", username=username))

    @commands.command(name='purgedone')
    async def purgeDone(self, ctx: commands.Context):
        if(ctx.author.is_mod):
            Pomo.remove_all_done(ctx.channel.name)
        else:
            await ctx.reply(self.chatBotConfig.getText("invalidPermMod", username=ctx.author.display_name))

################ Tasks Section Ended ################

################ Joining Section Started ################

    @commands.command(name='join')
    async def addCoWorkingStreamer(self,
                                   ctx: commands.Context,
                                   username=''):
        if (ctx.channel.name == self.nick):
            if (len(username) == 0):
                username = ctx.author.name.lower()
            else:
                username = username.lower().replace('@', '')
                if (not (username == ctx.author.name.lower()
                         or ctx.author.is_mod)):
                    await ctx.reply(f"You must be a Mod or Joining yourself")
                    return
            if (username in self.allChannels):
                await ctx.reply(f"The bot is already running on this channel.")
                return
            await self.join_channels([username])
            self.allChannels.append(username)
            Pomo.create_channel(username)
            await ctx.reply(
                f"Joined channel {username}. Please visit the website /pomo/{username} to get the browser output. Use '!hello' in {username} channel to test if the bot has arrived."
            )

    @commands.command(name='leave')
    async def removeCoWorkingStreamer(self,
                                      ctx: commands.Context,
                                      username: str = ''):
        if (ctx.channel.name == self.nick):
            if (len(username) == 0):
                username = ctx.author.name.lower()
            else:
                username = username.lower().replace('@', '')
                if (not (username == ctx.author.name.lower()
                         or ctx.author.is_mod)):
                    await ctx.reply(f"You must be a Mod or Leaving yourself.")
                    return
            if (username in self.allChannels):
                Pomo.remove_channel(username)
                for task in list(self.asyncTasks[username].values()):
                    task.cancel()
                await ctx.reply(
                    f"The bot will stop running on this channel."
                )
            else:
                await ctx.reply(f"The bot is not running on {username} channel")

################ Joining Section Ended ################

################ Fun Commands Section Started ################

    @commands.command(name='flip')
    async def flip(self, ctx: commands.Context, text: str = ''):
        if (len(text) == 0):
            text = ctx.author.display_name
        flippedText = ""
        for chr in text[::-1]:
            if (chr in self.flipDict.keys()):
                flippedText += self.flipDict[chr]
            else:
                flippedText += chr
        await ctx.reply(f"(╯°□°）╯︵{flippedText}")

    @commands.command(name='unflip')
    async def unflip(self, ctx: commands.Context, text: str = ''):
        if (len(text) == 0):
            text = ctx.author.display_name
        await ctx.reply(f"{text}ノ( ゜-゜ノ)")

################ Fun Commands Section Ended ################


def startBot(bot: Bot):
    t = Thread_With_Exception(target=bot.run, name='CoWorkingBot')
    t.start()
    return t


def stopBot(bot: Bot, t: Thread_With_Exception):
    asyncio.run(asyncio.wait([bot.close()]))
    t.raise_exception()
    t.join()


# Original Author: https://github.com/00MB/
if __name__ == "__main__":
    botConfig = BotConfig.loadFromFile('BotResources/resources/botConfig.json')

    botConfig.oAuthToken=os.environ['AUTH_TOKEN']
    botConfig.streamerUsername=os.environ['USER_NAME']

    chatBotConfig = ChatBotConfig.loadFromFile('BotResources/resources/chatBotConfig.json')

    if (botConfig.fileOutputEnabled):
        startFileOutput(filename=botConfig.fileOutputLocation, channel=botConfig.streamerUsername)
    if (botConfig.webOutputEnabled):
        startWebOutput(host=botConfig.webOutputHost, port=botConfig.webOutputPort)

    bot = CoWorkingBot(botConfig, chatBotConfig)
    
    disabledCmds = botConfig.getDisabledCommands()
    for cmd in disabledCmds:
        bot.remove_command(cmd)
    
    bot.run()
