# CoWorkingTwitchBot
A Twitch Co-Working Bot that will allow chat to run their Pomodoros and add tasks. Sends a message in the chat once the time for a session is up.
Also outputs the tasks to the website or file output that can be added on stream as an input for your stream set-up.

Credits to:
- <a href="https://twitch.tv/YakkyStudy">@Patriick</a> for the Testing and suggestions.
- <a href="https://twitch.tv/RumpleStudy">@RumpleStudy</a> for the original Bot idea.
- <a href="https://twitch.tv/tabi_katze">@tabi_katze</a> and <a href="https://twitch.tv/undefined_dot_json">@undefined_dot_json</a>, the devs of the original pomo bot.

### ❖ How to use the !pomo command ❖
You can use the !pomo command to set your own personalised timer and appear on the stream! Simply type !pomo [number] to set a timer in minutes.

More details:
- '!pomo \<work mins\> [break mins] [num sessions] [task]'. E.g. !pomo 25 5 4 Essay.
- '!pomo complete' --> cancel your sessions
- '!pomo check' --> check your timer
- '!pomo +/-\<mins\>' --> edit your timer
- '!task \<task\>' --> create a task (and replace the done task if any)
- '!done' --> complete your task but keep it on the board
- '!finish' --> complete your task and remove it from the board

## How to Run the Bot
### On Replit:


[![Run on Repl.it](https://repl.it/badge/github/crankybookworm/CoWorkingTwitchBotWithGui)](https://repl.it/github/crankybookworm/CoWorkingTwitchBotWithGui)
1) Create an account for the Bot
2) Create an application in the bot account using <a href="https://dev.twitch.tv/console">twitch.tv dev console</a> (you will need to activate 2FA for this). Set the URL to "https://twitchtokengenerator.com"
3) Use the <a href="https://twitchtokengenerator.com">token generator link</a> to generate an Auth token.
4) Create a Replit Account
5) Fork this <a href="https://replit.com/@CrankyBookworm/CoWorkingTwitchBotWithGui?v=1">Repl</a>
6) Set the Environment Variables from the left hand bar of Repl (set the "AUTH_TOKEN" to the auth token you get from Step 3 and "USER_NAME" to your stream account username)
7) Run it. You should see "Logged in as | \<bot name\>"
8) Using your streaming account visit the streamer's twitch chat and type in "!hello" to test if bot is working.
10) Type "!hello" in your stream chat to test the bot
11) Type "!pomo \<work mins\> [break mins] [num sessions] [topic]" to run the bot
12) Open up the website window from the right hand side of the Replit and then type in your stream account username to see the board. Add the URL to your OBS browser source

When running next time just run the Repl and it should work. Indicated by a message of "\<bot name\> has landed!"

### Locally:
1) Follow steps 1-3
2) Download the zip and extract it
3) Enter the Auth token and your stream account username in the Bot Settings Tab then save.
4) Start the Bot
5) Type "!hello" in your stream chat to test the bot
6) Type "!pomo \<work mins\> [break mins] [num sessions] [topic]" to run the bot
7) Add the text file named "\<your stream account username\>pomoboard.txt" to your stream setup as a text source


Please <a href="mailto:bookworm.cranky@gmail.com">Email</a> or <a href="https://discord.com/channels/@me/492972880787931147/">DM on Discord</a> me for any questions or suggestions.