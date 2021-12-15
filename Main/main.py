import os
import sys
sys.path.insert(1, '{}/Database'.format(os.getcwd()))
sys.path.insert(1, '{}/Assets'.format(os.getcwd()))
import requests
import json
import random
import discord
import time
import datetime
from discord.ext import commands
from discord import guild
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option, create_permission
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
from discord_slash.model import SlashCommandPermissionType as SlashCMDPermType
from discord_slash.model import ButtonStyle
from important import token, OwnerID
from commandhelp import command_help
from servers import my_guilds
from settings import prefix, logchannelid
from colorama import Fore, Back, Style

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot("{}".format(prefix), intents=intents)
slash = SlashCommand(bot, sync_commands=True)

async def cmd_log(type, ctx=False):
    logchannel = bot.get_channel(logchannelid)
    if type == "slash":
        await logchannel.send('{} used the Slash-Command "{}".'.format(ctx.author, ctx.command))
    elif type == "text":
        msg = ctx.content
        allwords = msg.split(' ')
        await logchannel.send('{} used the command "{}"'.format(ctx.author, allwords[0]))

def permcheck(message=None, adminrequired=False):
    def cmd_toggle():
        settingr = open("Database/off-switch.py")
        c_setting = settingr.read()
        settingr.close()
        if c_setting == "True":
            return True
        elif c_setting == "False":
            return False
    if not message == None:   
        if not message.author == bot.user:
            if cmd_toggle():
                if adminrequired:
                    if message.author.id == OwnerID:
                        return True
                    else:
                        return False 
                else:
                    return True
            else:
                return False
        else:
            return False
    else:
        if cmd_toggle():
            if adminrequired:
                if message.author.id == OwnerID:
                    return True
                else:
                    return False 
            else:
                return True
        else:
            return False

cmd_off = "Commandsss are currently turned off."

async def grab_msginfo(message):
    msg = message.content
    allwords = msg.split(' ')
    args = msg.lower().split(' ')[1:]
    await cmd_log("text", message)
    return msg, allwords, args

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
    name="database",
    description         = "Interactsss with the DB. (Owner Only)",
    guild_ids           = [736975456636633199],
    default_permission  = False,
    permissions         =  {736975456636633199: [
        create_permission(OwnerID, SlashCMDPermType.USER, True)
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
async def _database(ctx:SlashContext, action:str, file:str, variable:str=False, content=False):

    await cmd_log("slash", ctx)

    if action == "read":
        data = open('Database/{}.py'.format(file))
        datar = data.read()
        
        await ctx.send('{}'.format(datar))
    elif action == "write":
        if not variable == False:
            
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

            importedfile = __import__(file)
            data = open('Database/{}.py'.format(file), "w")
            exec('importedfile.' + variable + ' = ' + content)
            newvars = module_variables(importedfile)
            data.write(newvars)
            data.close
            await ctx.send('New Content:\n{}'.format(newvars))

        elif variable == False:
            data = open('Database/{}.py'.format(file), "w")
            data.write(content)
            data.close()
            await ctx.send('New Content:\n{}'.format(content))


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
                    name    = "/Database",
                    value   = "database"
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

    if permcheck():
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
 
    if permcheck():
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

@bot.command()
async def test(ctx, arg):
    await cmd_log("text", ctx.message)
    if permcheck(ctx.message):
        print("test")
        await ctx.send(arg)
    else:
        await ctx.send(cmd_off)

# Command Template:
"""
@bot.command()
async def command(ctx):
    if permcheck():
    else:
        await ctx.send(cmd_off)
"""

@bot.command()
async def commandtoggle(ctx):
    await cmd_log("text", ctx.message)
    message = ctx.message
    if message.author.id == OwnerID:
        admin = True
    else:
        admin = False

    if admin == True:
        settingr = open("Database/off-switch.py")
        c_setting = settingr.read()
        if c_setting == "True":
            settingr.close()
            settingw = open("Database/off-switch.py", "w")
            settingw.write("False")
            settingw.close()
            settingr = open("Database/off-switch.py")
            c_setting = settingr.read()
            await ctx.send('Set to ' + c_setting)
            settingr.close()
        else:
            settingr.close()
            settingw = open("Database/off-switch.py", "w")
            settingw.write("True")
            settingw.close()
            settingr = open("Database/off-switch.py")
            c_setting = settingr.read()
            await ctx.send('Set to ' + c_setting)
            settingr.close()
    
    else:
            await ctx.send('No Permisssion')

@bot.command()
async def sneki(ctx):
    await cmd_log("text", ctx.message)
    if permcheck(ctx.message):
        await ctx.send('Hewwo!')
    else:
        await ctx.send(cmd_off)


bot.run(token)