import os
import sys
sys.path.insert(1, '{}/Database'.format(os.getcwd()))
sys.path.insert(1, '{}/Assets'.format(os.getcwd()))
import requests
import json
import random
import discord
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


client = commands.Bot(command_prefix="sneki", intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

def cmd_toggle():
    settingr = open("Database/off-switch.py")
    c_setting = settingr.read()
    settingr.close()
    return c_setting

async def cmd_log(type, message=False, ctx=False):
    logchannel = client.get_channel(logchannelid)
    if type == "slash":
        await logchannel.send('{} used the Slash-Command "{}".'.format(ctx.author, ctx.command))
    elif type == "test":
        msg = message.content
        allwords = msg.split(' ')
        if msg.startswith(prefix):
            await logchannel.send('{} used the command "{}"'.format(message.author, allwords[0]))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    c_setting = cmd_toggle()
    if (c_setting == "True"):
        print(Fore.GREEN + 'Command Toggle : {}'.format(cmd_toggle()))
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + 'Command Toggle : {}'.format(cmd_toggle()))
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

    c_setting = cmd_toggle()
    await cmd_log("slash", 0, ctx)

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
    c_setting = cmd_toggle()
    await cmd_log("slash", 0, ctx)

    if c_setting == "True":
        await ctx.send('{}'.format(command_help(command)))
    else:
        await ctx.send("Commandsss are currently turned off.")

@client.event
async def on_message(message):
    c_setting = cmd_toggle()
    msg = message.content
    allwords = msg.split(' ')
    args = msg.lower().split(' ')[1:]
    await cmd_log("text", message)

    def cmd(wanted): 
        if msg.lower().startswith('{}'.format(prefix) + wanted):
            return True
        
        else:
            return False

    if message.author.id == OwnerID:
        admin = True
    else:
        admin = False

    if message.author == client.user: 
        return

    if cmd('commandtoggle'):
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
                await message.channel.send('Set to ' + c_setting)
                settingr.close()
                cmd_toggle()
            else:
                settingr.close()
                settingw = open("Database/off-switch.py", "w")
                settingw.write("True")
                settingw.close()
                settingr = open("Database/off-switch.py")
                c_setting = settingr.read()
                await message.channel.send('Set to ' + c_setting)
                settingr.close()
                cmd_toggle()
       
        else:
             await message.channel.send('No Permisssion')

    if cmd('sneki'):
        if c_setting == "True":
            await message.channel.send('Hewwo!')

client.run(token)