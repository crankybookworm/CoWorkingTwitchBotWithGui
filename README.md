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
- '!pomo complete' --> Cancel your sessions
- '!pomo check' --> Check your timer
- '!pomo +/-\<mins\>' --> Edit your timer
- '!task \<task\>' --> Create a task (and replace the done task if any)
- '!done' --> Complete your task but keep it on the board
- '!finish' --> Complete your task and remove it from the board
- '!rmvdone [all/#]' --> Remove done task (all or specific) from board
- '!pomo stats' --> Get User Stats

Mod Commands:
- '!rmvdone [all/#] @Username' --> Remove done of user
- '!rmvtask @Username' --> Remove done of user
- '!purgeboard' --> Clean the board from all tasks
- '!purgedone' --> Remove all done tasks
## How to Run the Bot
### On Replit:


[![Run on Repl.it](https://repl.it/badge/github/crankybookworm/CoWorkingTwitchBotWithGui)](https://repl.it/github/crankybookworm/CoWorkingTwitchBotWithGui)
1) Create an account for the Bot
2) Create an application in the bot account using <a href="https://dev.twitch.tv/console">twitch.tv dev console</a> (you will need to activate 2FA for this). Set the URL to "https://twitchtokengenerator.com"
3) Use the <a href="https://twitchtokengenerator.com">token generator link</a> to generate an Auth token.
4) Create a Replit Account
5) Fork this <a href="https://replit.com/@CrankyBookworm/CoWorkingTwitchBotWithGui?v=1">Repl</a>
6) Set the Environment Variables from the left hand bar of Repl (set the key "AUTH_TOKEN" with value of the auth token you get from Step 3 and key "USER_NAME" with value of your stream account username)<br/><img src="https://cdn.discordapp.com/attachments/817504246240247868/992519493811179550/unknown.png" />
7) Run it. You should see "Logged in as | \<bot name\>"
8) Using your streaming account visit the streamer's twitch chat and type in "!hello" to test if bot is working.
9)  Type "!hello" in your stream chat to test the bot
10) Type "!pomo \<work mins\> [break mins] [num sessions] [topic]" to run the bot
11) Open up the website window from the right hand side of the Replit and then type in your stream account username to see the board. Add the URL to your OBS browser source

When running next time just run the Repl and it should work. Indicated by a message of "\<bot name\> has landed!"

### Locally:
1) Follow steps 1-3
2) Download the zip and extract it
3) Enter the Auth token and your stream account username in the Bot Settings Tab then save. <br/><img src="https://cdn.discordapp.com/attachments/817504246240247868/992520605570179252/unknown.png" alt="Bot Configurations" />
4) Start the Bot
5) Type "!hello" in your stream chat to test the bot
6) Type "!pomo \<work mins\> [break mins] [num sessions] [topic]" to run the bot
7) For Web Output make sure to enable it from Bot Settings.<br/>Then Open the link (http://localhost:8080 or whatever you set) in the browser. Type in your streamer username as input and submit. Copy the URL and add the link to OBS Browser source.<br/><img src="https://cdn.discordapp.com/attachments/817504246240247868/992503146431655946/unknown.png" />
8) For File Output select the text file to be your output. Add it to your stream setup as a text source.
    <img src="https://cdn.discordapp.com/attachments/817504246240247868/992504558163083346/unknown.png" />


Please <a href="mailto:bookworm.cranky@gmail.com">Email</a> or <a href="https://discord.com/channels/@me/492972880787931147/">DM on Discord</a> me for any questions or suggestions.