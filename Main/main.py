import  os
import  sys
import  requests
import  json
import  random
import  discord
import  time
import  datetime
from    discord.ext                             import commands
from    discord                                 import guild
from    discord_slash                           import SlashCommand, SlashContext, context
from    discord_slash.utils.manage_commands     import create_choice, create_option, create_permission
from    discord_slash.utils.manage_components   import create_select, create_select_option, create_actionrow
from    discord_slash.model                     import SlashCommandPermissionType as SlashCMDPermType
from    discord_slash.model                     import ButtonStyle
from    colorama                                import Fore, Back, Style
from    importlib                               import reload

# Custom Modules
from    commandhelp                             import command_help

# DATABASE:
# adding additional paths
sys.path.insert(1, '{}/Database'.format(os.getcwd()))
sys.path.insert(1, '{}/Assets'.format(os.getcwd()))
# .py files (For Statics):
from important  import token, DevID, prefix
# .json files:
LOGIDS      = "Database/logids.json"
OFF_SWITCH  = "Database/off-switch.json"
SERVERS     = "Database/servers.json"
REMINDERS   = "Database/reminders.json"

# Assigning Bot and Slash variables to Modules and setting some settings
bot     = commands.Bot("{}".format(prefix), intents=discord.Intents.all())
slash   = SlashCommand(bot, sync_commands=True)

# Returns List of Guild IDs (Currently static)
def get_myguilds():
    with open(SERVERS, 'r') as f:
        servers = json.load(f)
    my_guilds = servers.get(f"my_guilds")
    return my_guilds
my_guilds = get_myguilds()

# Returns all variables from specified module. if no module, returns variable of current file
def module_variables(module_name=None):
    module_name = sys.modules[__name__] if not module_name else module_name
    variables = [
        (key, value)
        for (key, value) in vars(module_name).items()
        if (type(value) == str or type(value) == int or type(value) == float)
        and not key.startswith("_")
    ]
    
    thingies = ""
    for (key, value) in variables:
        if type(value) == int:
            thingies = thingies + (f"{key} = {value}\n")
        if type(value) == str:
            thingies = thingies + (f'{key} = "{value}"\n')
    return thingies

# Gets the ID of the Channel to log in. Dependant on Server
def get_logID(ctx):
    with open(LOGIDS, 'r') as f:
        logs = json.load(f)
    return logs.get(f'server_{ctx.guild.id}')

# Logs the executed Command
async def cmd_log(type, ctx=False):
    logchannelid = get_logID(ctx)
    logchannel = bot.get_channel(int(logchannelid))
    if logchannelid == 0:
        return
    else:
        if type == "slash":
            await logchannel.send('{} used the Slash-Command "{}".'.format(ctx.author, ctx.name))
        elif type == "text":
            msg = ctx.message.content
            allwords = msg.split(' ')
            await logchannel.send('{} used the command "{}"'.format(ctx.author, ctx.command))

# Checks if all Command toggles are turned on, and, if specified, if the commands Author has Admin privileges
def permcheck(ctx=None, adminrequired=False):

    with open(OFF_SWITCH, 'r') as f:
        settings = json.load(f)
        g_setting = settings.get(f'GLOBAL')
        if not ctx == None:
            try:
                command = ctx.name
            except AttributeError:
                command = ctx.command
 
        else: return g_setting
        c_setting = settings.get(f'{command}')

        if g_setting == "True":
            if c_setting == "True":
                if adminrequired == True:
                    if ctx.channel.permissions_for(ctx.author).administrator:
                        
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return False
        else:
            return False

cmd_off = "Commandsss are currently turned off."

# Prints a message that the Bot has logged in, and also prints the current Setting of the global command toggle
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    if permcheck():
        print(Fore.GREEN + 'Command Toggle : {}'.format(permcheck()))
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + 'Command Toggle : {}'.format(permcheck()))
        print(Style.RESET_ALL)

@slash.slash(
    name                = "setlogs",
    description         = "Specify a Channel to log cammands in",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "action",
            description = "What to do with the logchannel?",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "Remove",
                    value   = "remove"
                ),
                create_choice(
                    name    = "Set",
                    value   = "set"
                )
            ]
        ),
        create_option(
            name        = "new_logchannel",
            description = "Specify a new Channel(ID) to put logs into",
            required    = False,
            option_type = 3
        )
    ]
)
async def _setlogs(ctx:SlashContext, action:str, new_logchannel:str=None):
    
    cmd_log("slash", ctx)

    if permcheck(ctx, True):
        if action == "set":

            with open(LOGIDS, 'r') as f:
                logs = json.load(f)
            logs[f"server_{ctx.guild.id}"] = new_logchannel
            with open(LOGIDS, 'w') as f:
                f.write(f"{json.dumps(logs, indent=2)}\n")

        if action == "remove":

            with open(LOGIDS, 'r') as f:
                logs = json.load(f)
            logs[f"server_{ctx.guild.id}"] = 0
            with open(LOGIDS, 'w') as f:
                f.write(f"{json.dumps(logs, indent=2)}\n")

            
        await ctx.send("Log Channel set to: {}".format(get_logID(ctx)))
    else:
        await ctx.send(cmd_off + " Or you do not have permisssion.")

@slash.slash(
    name                = "database",
    description         = "Interactsss with the DB. (Developer Only)",
    guild_ids           = [736975456636633199],
    default_permission  = False,
    permissions         =  {736975456636633199: [
        create_permission(DevID, SlashCMDPermType.USER, True)
    ]},
    options             = [
        create_option(
            name        = "action",
            description = "What do you want to do?",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "Read!",
                    value   = "read"
                ),
                create_choice(
                    name    = "Write!",
                    value   = "write"
                )
            ]
        ),
        create_option(
            name        = "file",
            description = "Insert a filename",
            required    = True,
            option_type = 3   
        ),
        create_option(
            name        = "variable",
            description = "Specify a Variable to edit",
            required    = False,
            option_type = 3
        ),
        create_option(
            name        = "content",
            description = "New content to write",
            required    = False,
            option_type = 3
        )
    ]
)
async def _database(ctx:SlashContext, action:str, file:str, variable:str=False, content:str=False):

    await cmd_log("slash", ctx)
    
    jsonfile = 'Database/{}.json'.format(file)

    if action == "read":
        with open(jsonfile, 'r') as f:
            filedata = json.load(f)
        filecontent = "```{}```".format(filedata).replace("{", "").replace("}", "").replace(", ", "\n")
        await ctx.send(filecontent)
    elif action == "write":
        
        if variable == False:
            await ctx.send("Please provide a variable to change.")
        else:
            if content == False:
                await ctx.send("Please provide the new value")
            elif not content == "delete":
                with open(jsonfile, 'r') as f:
                    filedata = json.load(f)
                filedata[f"{variable}"] = content
                with open(jsonfile, 'w') as f:
                    f.write(f"{json.dumps(filedata)}\n")
                await ctx.send("File has been updated.")
            elif content == "delete":
                with open(jsonfile, 'r') as f:
                    filedata = json.load(f)
                del filedata[f"{variable}"]
                with open(jsonfile, 'w') as f:
                    f.write(f"{json.dumps(filedata, indent=2)}\n")
                await ctx.send("File has been updated.")

@slash.slash(
    name="help",
    description         = "Need sssomething?",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "command",
            description = "Pick the command you need help with",
            required    = True,
            option_type = 3,
            choices     = [
                create_choice(
                    name    = "/Help",
                    value   = "help"
                ),
                create_choice(
                    name    = "/Setlogs",
                    value   = "setlogs"
                ),
                create_choice(
                    name    = "/Database",
                    value   = "database"
                ),
                create_choice(
                    name    = "/Reminder",
                    value   = "reminder"
                ),
                create_choice(
                    name    = "{}commandtoggle".format(prefix),
                    value   = "commandtoggle"
                ),
                create_choice(
                    name    = "{}sneki".format(prefix),
                    value   = "sneki"
                )
            ]
        )
    ]
)
async def _help(ctx:SlashContext, command:str):

    await cmd_log("slash", ctx)

    if permcheck(ctx):
        await ctx.send('{}'.format(command_help(command)))
    else:
        await ctx.send("Commandsss are currently turned off.")

@slash.slash(
    name="reminder",
    description         = "Ssset a timer to remind you of sssometing?",
    guild_ids           = my_guilds,
    default_permission  = True,
    options             = [
        create_option(
            name        = "reminder",
            description = "What should the Bot remind you of?",
            required    = True,
            option_type = 3
        ),
        create_option(
            name        = "hours",
            description = "Enter time in hours",
            required    = False,
            option_type = 4
        ),
        create_option(
            name        = "minutes",
            description = "Enter time in minutes",
            required    = False,
            option_type = 4
        ),
        create_option(
            name        = "seconds",
            description = "Enter time in seconds",
            required    = False,
            option_type = 4
        )
    ]
)
async def _reminder(ctx:SlashContext, hours:int=0, minutes:int=0, seconds:int=0, reminder:str=""):

    await cmd_log("slash", ctx)
 
    if permcheck(ctx):
        if len(reminder) < 1950:
            author = bot.get_user(ctx.author.id)
            await ctx.send('Registered Reminder: {}'.format(reminder))
            # Calculate the total number of seconds
            total_seconds = hours * 3600 + minutes * 60 + seconds
        
            # While loop that checks if total_seconds reaches zero
            # If not zero, decrement total time by one second
            while total_seconds > 0:
    
                # Timer represents time left on countdown
                timer = datetime.timedelta(seconds = total_seconds)
        
                # Delays the program one second
                time.sleep(1)
        
                # Reduces total time by one second
                total_seconds -= 1
            await author.send('Here is your Reminder:\n\n{}'.format(reminder))
        else:
            await ctx.send('Please provide a smaller reminder')
    else:
        await ctx.send("Commandsss are currently turned off.")

# @slash.slash(
#     name="test",
#     description="Its a test",
#     guild_ids           = my_guilds,
#     default_permission  = True
# )
# async def _test(ctx:SlashContext):
#     await cmd_log("slash", ctx)
#     await ctx.send('LogID: {}'.format(get_logID(ctx)))

# @bot.command()
# async def test(ctx, arg):
#     await ctx.send()

# Command Template:
"""
@bot.command()
async def command(ctx):

    cmd_log("text", ctx)

    if permcheck(ctx):
    else:
        await ctx.send(cmd_off)
"""

@bot.command()
async def commandtoggle(ctx, arg1):

    await cmd_log("text", ctx)

    message = ctx.message
    if message.author.id == DevID:
        
        with open(OFF_SWITCH, "r") as f:
            switch = json.load(f)
            setting = switch.get(f"{arg1}")
        
        if setting == "True":
            switch[f"{arg1}"] = "False"
            with open(OFF_SWITCH, "w") as f:
                f.write(f"{json.dumps(switch, indent=2)}\n")
            await ctx.send('Set to False')

        elif setting == "False":
            switch[f"{arg1}"] = "True"
            with open(OFF_SWITCH, "w") as f:
                f.write(f"{json.dumps(switch, indent=2)}\n")
            await ctx.send('Set to True')
    else:
            await ctx.send('No Permisssion')

@bot.command()
async def sneki(ctx):

    await cmd_log("text", ctx)

    if permcheck(ctx):
        await ctx.send('Hewwo!')
    else:
        await ctx.send(cmd_off)

# Starts the bot and logs in using the specified token
bot.run(token)