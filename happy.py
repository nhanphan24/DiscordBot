'''
discord chat bot
by: Nhan Phan

This discord bot stays in the server and answer to the users' requests. It
can kick members, report back information, and help users choose between
some given choices
'''

import discord
from discord.ext import commands
import random

bot = commands.Bot(command_prefix = '!')

@bot.event
async def on_ready():
    '''This function is called after the bot ran. It prints the username,
    id of the bot, and that the bot is ready
    '''
    print(bot.user.name, 'bot is online')

@bot.command()
async def kick(member: discord.Member):
    '''This function allows the user to kick another user'''
    await bot.say('bye :hand_splayed: ' + member.name) 
    await bot.kick(member)

@bot.command()
async def choose(*items):
    '''Use when the user wants to randomly choose between any number of
    choices
    '''
    await bot.say(random.choice(items))

@bot.command(pass_context = True)
async def role(context):
    '''This function allows the user to check what their role is'''
    user_role = ''
    for role in context.message.author.roles:
        if str(role) != '@everyone':
            user_role += str(role) + ', '
    if user_role == '':
        user_role = 'member'
    await bot.say('You are ' + user_role.rstrip(', '))

@bot.command()
async def info(user: discord.Member):
    '''This function gets the information of the user and say it in the
    chat, which includes the name, ID, status, game playing, date joined 
    channel, and the highest role of the user
    ''' 
    await bot.say('the user\'s name: ' + user.name)
    await bot.say('the user\'s ID: ' + user.id)
    await bot.say('the user\'s status: ' + str(user.status))
    if user.game == None:
        await bot.say('the user is not playing any game right now')
    else:
        await bot.say('the user is playing ' + user.game)
    await bot.say('the user joined the channel on ' + str(user.joined_at))
    await bot.say('the user\'s highest role: ' + str(user.top_role))
    
    
if __name__ == '__main__':
    bot.run('Token')
