#Import the required modules
import discord
import datetime as dt
import os
import psycopg2 as p

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


#Print in console that the bot is online
@bot.event
async def on_ready():
    print(f'{bot.user.name} is online')


#A ping command to check latency
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency*1000)}')


#Unused commond to verify user information
'''
@bot.command()
async def info(ctx):
    did = ctx.author.id
    info = ctx.author.name
    dis = ctx.author.discriminator
    
    await ctx.send(f"User info is ID:{did}, name:{info} and dis:{dis}")
'''


#Add new users to the database
@bot.command(aliases=['register'])
async def signup(ctx):
    #Setting up the person who used the command information for future reference
    user_id = ctx.author.id
    name = ctx.author.name
    dis = ctx.author.discriminator

    #Try to connect to the database and run SQL commands
    try:
        #Connection Information
        connection = p.connect( user= USER,
                                password= PASSWORD,
                                host= HOST,
                                port=PORT,
                                database=DATABASE)
        #Create the database cursor
        cursor = connection.cursor()
        #Find the author of the command in the database using their user id from discord
        cursor.execute(f"SELECT * FROM users WHERE id ={user_id}")
        data = cursor.fetchone()
        #If user is already in database, send user information
        if data != None:
            print(data)
            await ctx.send(data)
        # If user isn't in database, add user to database and save changes
        else:
            cursor.execute(f"""INSERT INTO users (dis,id,start_date,phone,name)
                               VALUES({dis},{user_id}, NULL, NULL, '{name}');""")
            connection.commit()
            await ctx.send('You have been added')

    # Error handling
    except (Exception, p.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        await ctx.send('Sorry, having troubles connecting to the database')
    # Once finished, close connection
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


#Run bot loop
bot.run(TOKEN)