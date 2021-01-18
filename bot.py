#Import the required modules
import discord
import datetime as dt
import os
import asyncio as aio
import asyncpg as apg

from dotenv import load_dotenv
from discord.ext import commands


#Load the discord token into this file to use
load_dotenv()
TOKEN = os.getenv('TOKEN')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DATABASE = os.getenv('DATABASE')


#Set bot prefix
bot = commands.Bot(command_prefix="t")


#Print in console that the bot is online as a visual check for when commands can be processed
@bot.event
async def on_ready():
    print(f'{bot.user.name} is online')


#A ping command to check latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)}')


#Add new users to the database
@bot.command(aliases=['register'])
async def signup(ctx):
    #Setting up the person who used the command information for future reference
    user_id = ctx.author.id
    name = ctx.author.name
    dis = ctx.author.discriminator
    # Connect to database
    conn = await apg.connect(user= USER, password= PASSWORD, host= HOST, port=PORT, database=DATABASE, ssl='require')

    # Try to get user information. If information is returned, print else alert user they are not part of the database
    try:
        data = await conn.fetchrow(f'SELECT * FROM users WHERE id = {user_id}')

        # If information is gathered, alert user that they are already part of the database
        if data != None:
            await ctx.send('You have already signed up. Please use `tinfo` to see what information you have currently stored in our database')
        # If no information is found, enter user into database
        else:
            await conn.execute(f"""INSERT INTO users (dis,id,start_date,phone,name)
                               VALUES({dis},{user_id}, NULL, NULL, '{name}');""")
            await ctx.send('You have signed up for TrackIt!')

    except Exception as e:
        print(e)
        await ctx.send(f'Sorry, we\'re having problems processing your request')
    
    finally:
        await conn.close()


# Recieve all information currently stored in database
@bot.command()
async def info(ctx):
    # Gather user information for SQL query
    user_id = ctx.author.id
    conn = await apg.connect(user= USER, password= PASSWORD, host= HOST, port=PORT, database=DATABASE, ssl='require')

    try:
        # Try to find user in database
        data = await conn.fetchrow(f'SELECT * FROM users WHERE id = {user_id}')
        if data != None:
            # Generate discord embed
            embed = discord.Embed(title="User information", description="The information that is currently stored in the database")
            embed.add_field(name='Discriminator', value=data[0], inline=False)
            embed.add_field(name='User ID', value=data[1], inline=False)
            embed.add_field(name='Start Date', value=data[2], inline=False)
            embed.add_field(name='Phone Number', value=data[3], inline=False)
            embed.add_field(name='Name', value=data[4], inline=False)
            # DM embed to user
            await ctx.author.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send(f'Sorry, we\'re having problems processing your request')

    finally:
        await conn.close()


@bot.command()
async def record(ctx):
    # Gather user info for SQL query
    user_id = ctx.author.id
    conn = await apg.connect(user= USER, password= PASSWORD, host= HOST, port=PORT, database=DATABASE, ssl='require')

    try:
        # Update start_time in database with current time stamp
        await conn.execute(f'''UPDATE users
        SET start_date = CURRENT_TIMESTAMP 
        WHERE id = {user_id};''')
        # Alert the user that their info has been updated
        await ctx.send(f'User start time has been updated to {dt.datetime.now()+dt.timedelta(hours=5)}')

    except Exception as e:
        print(e)
        await ctx.send(f'Sorry, we\'re having problems processing your request')

    finally:
        await conn.close()


@bot.command()
async def delta(ctx):
    # Collect user data for SQL query
    user_id = ctx.author.id
    current_time = dt.datetime.now() + dt.timedelta(hours=5)
    conn = await apg.connect(user= USER, password= PASSWORD, host= HOST, port=PORT, database=DATABASE, ssl='require')

    try:
        # Find user information, set variable to start time and fix current time for UTC standard
        data = await conn.fetchrow(f'SELECT * FROM users WHERE id= {user_id}')
        start_time = data[2]
        delta_time = current_time - start_time
        print(delta_time)
        await ctx.author.send(f'It has been {delta_time}. Keep it going!')

    except Exception as e:
        print(e)
        await ctx.send(f'Sorry, we\'re having problems processing your request')

    finally:
        await conn.close()


# Run discord bot loop
bot.run(TOKEN)