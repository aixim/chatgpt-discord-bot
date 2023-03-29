import discord
from discord.ext import commands
import openai
import functools
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def partition_array(arr): # We split message array into chunks of 2000 for discord
    # Find the length of the array
    n = len(arr)

    # Calculate the number of 2000-sized chunks
    num_chunks = (n + 1999) // 2000

    # Loop over the chunks and add them to a list
    chunks = [arr[i:i+2000] for i in range(0, n, 2000)]

    return chunks


# Set up the OpenAI API key
openai.api_key = os.getenv('OPEN_API_KEY')

# Create the bot client
intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
   await bot.sync_commands() #sync the command tree
   print("Bot is ready and online")

# Define a command
@bot.slash_command(name="chatgpt", description="Display available commands")
async def chatgpt(ctx):
    await ctx.respond("`/chat` - Default ChatGPT prompt\n`/animechat` - ChatGPT prompt but more kawaii\n`/restart` - Restart the bot\n")

@bot.slash_command(name="chat", description="ChatGPT prompt")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
async def chat(ctx, *, prompt): # Basic prompt to ChatGPT
    # Call the OpenAI API to get a response
    await ctx.response.defer(ephemeral=False)
    response = await bot.loop.run_in_executor(None, functools.partial(openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    for choice in response.choices:
        result += choice.message.content
    partitioned_result = partition_array(result)
    for arr in partitioned_result:
        await ctx.respond(arr)
    # Send the response back to the user

@bot.slash_command(name="animechat", description="ChatGPT prompt but more kawaii")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
async def animechat(ctx, *, prompt): # Prompt to ChatGPT pretending to be an anime girl (I'm not proud of this)
    # Call the OpenAI API to get a response
    await ctx.response.defer(ephemeral=False)
    response = await bot.loop.run_in_executor(None, functools.partial(openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt +
                    " and pretend to be an anime girl and use uwu"},
            ]
        ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    for choice in response.choices:
        result += choice.message.content
    partitioned_result = partition_array(result)
    for arr in partitioned_result:
        await ctx.respond(arr)
    # Send the response back to the user

@bot.slash_command(name="restart", description="Restart ChatGPT bot")
async def restart(ctx):
    await ctx.respond("Restarting ChatGPT...")
    os.execv(sys.executable, ['python'] + sys.argv)

# Run the bot
bot.run(os.getenv('DISCORD_BOT_KEY'))