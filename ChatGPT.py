import discord
from discord.ext import tasks, commands
from groq import Groq
#import openai
import functools
import os
from dotenv import load_dotenv
import requests
import io
import base64
import asyncio

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
#openai.api_key = os.getenv('OPEN_API_KEY')
#openai.api_base = "http://127.0.0.1:5000/v1"
#openai.api_version = "2023-05-15"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Create the bot client
intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
currentModel = "anime"

@bot.event
async def on_ready():
   await bot.sync_commands() #sync the command tree
   print("Bot is ready and online")
   bot.loop.create_task(status_task())

@tasks.loop()
async def status_task() -> None:
    while True:
        try:
            response = requests.get("http://127.0.0.1:7860/sdapi/v1/progress")
            if response.status_code == 200:
                await bot.change_presence(activity=discord.Game(name="Stable Diffusion"))
            else:
                await bot.change_presence(activity=None)
        except:
            await bot.change_presence(activity=None)
        await asyncio.sleep(10)
    
    

# Define a command
@bot.slash_command(name="help", description="Display available commands")
async def help(ctx):
    await ctx.respond("`/chat` - Default ChatGPT prompt\n" +
                      "`/animechat` - ChatGPT prompt but more kawaii\n" +
                      "`/scottishchat` - ChatGPT prompt but more scottish\n" +
                      "`/unhingedchat` - ChatGPT prompt but unhinged\n" +
                      #"`/restart` - Restart the bot\n" + 
                      "`/img` - Stable Diffusion image prompt\n" +
                      "`/model` - Change Stable Diffusion model")

@bot.slash_command(name="chat", description="ChatGPT prompt")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
async def chat(ctx, *, prompt): # Basic prompt to ChatGPT
    # Call the OpenAI API to get a response
    await ctx.response.defer(ephemeral=False)
    response = await bot.loop.run_in_executor(None, functools.partial(client.chat.completions.create,
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": prompt},
                ]
            ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    result += response.choices[0].message.content
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
    response = await bot.loop.run_in_executor(None, functools.partial(client.chat.completions.create,
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt +
                    " and pretend to be an anime girl and use uwu"},
            ]
        ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    result += response.choices[0].message.content
    partitioned_result = partition_array(result)
    for arr in partitioned_result:
        await ctx.respond(arr)
    # Send the response back to the user

@bot.slash_command(name="scottishchat", description="ChatGPT prompt but more scottish")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
async def scottishchat(ctx, *, prompt): # Prompt to ChatGPT pretending to be scottish
    # Call the OpenAI API to get a response
    await ctx.response.defer(ephemeral=False)
    response = await bot.loop.run_in_executor(None, functools.partial(client.chat.completions.create,
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt +
                    " and pretend to be scottish with a very emphasized accent"},
            ]
        ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    result += response.choices[0].message.content
    partitioned_result = partition_array(result)
    for arr in partitioned_result:
        await ctx.respond(arr)

    # Send the response back to the user
@bot.slash_command(name="unhingedchat", description="ChatGPT prompt but unhinged")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
async def unhingedchat(ctx, *, prompt): # Prompt to ChatGPT (unhinged)
    # Call the OpenAI API to get a response
    await ctx.response.defer(ephemeral=False)
    response = await bot.loop.run_in_executor(None, functools.partial(client.chat.completions.create,
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt +
                    " and answer in a very unhinged way with caps lock"},
            ]
        ))
    result = ''
    result += "**" + prompt + "** - " + ctx.author.mention + "\n"
    result += response.choices[0].message.content
    partitioned_result = partition_array(result)
    for arr in partitioned_result:
        await ctx.respond(arr)
    # Send the response back to the user

@bot.slash_command(name="img", description="Stable Diffusion prompt")
@discord.option(
    "prompt",
    str,
    description="Prompt message"
)
@discord.option(
    "negative_prompt",
    str,
    description="Negative prompt (what you don't want to see)"
)
@discord.option(
    "width",
    str,
    description="Image width (max 1280 pixels)"
)
@discord.option(
    "height",
    str,
    description="Image height (max 720 pixels)"
)
async def img(ctx, *, prompt, negative_prompt='', width='512', height='512'): # Image prompt to Stable Diffusion
    await ctx.response.defer(ephemeral=False)
    if int(width) > 1280: width='512'
    if int(height) > 720: height='512'
    negative_prompt += ', (worst quality), bad quality, naked, nude, (nsfw)'
    json = '{"prompt": "' + prompt + '", "steps": 25, "cfg_scale": 7, "width": '+ width +', "height": '+ height +', "negative_prompt": "' + negative_prompt + '", "sampler_name": "DPM++ 3M SDE"}'
    try:
        response = await bot.loop.run_in_executor(None, functools.partial(requests.post, url="http://127.0.0.1:7860/sdapi/v1/txt2img", data=json))
        images = []
        for image in response.json()['images']:
            images.append(discord.File(io.BytesIO(base64.b64decode(image)), "image.png"))
        await ctx.respond(files=images)
    except Exception as e:
        print(e)
        await ctx.respond("Failed to connect to Stable Diffusion")
    # Send the response back to the user

"""@bot.slash_command(name="restart", description="Restart ChatGPT bot")
async def restart(ctx):
    await ctx.respond("Restarting ChatGPT...")
    os.execv(sys.executable, ['python'] + sys.argv)"""
    
@bot.slash_command(name="model", description="Change Stable Diffusion model")
@discord.option(
    "model",
    str,
    description="Model name"
)
async def model(ctx, *, model=''): # Image prompt to Stable Diffusion
    await ctx.response.defer(ephemeral=False)
    global currentModel
    if model == "":
        await ctx.respond("Current model - `" + currentModel + "`\nAvailable models - `anime`, `realistic`, `fantasy`, `dream`")
    else:
        try:
            if model == "anime":
                json = '{"sd_model_checkpoint": "meinamix_meinaV11.safetensors"}'
                response = await bot.loop.run_in_executor(None, functools.partial(requests.post, url="http://127.0.0.1:7860/sdapi/v1/options", data=json))
                if response.status_code != 200:
                    raise Exception
                await ctx.respond("Switched to `anime` model")
                currentModel = "anime"
            elif model == "realistic":
                json = '{"sd_model_checkpoint": "cyberrealistic_v42.safetensors"}'
                response = await bot.loop.run_in_executor(None, functools.partial(requests.post, url="http://127.0.0.1:7860/sdapi/v1/options", data=json))
                if response.status_code != 200:
                    raise Exception
                await ctx.respond("Switched to `realistic` model")
                currentModel = "realistic"
            elif model == "fantasy":
                json = '{"sd_model_checkpoint": "dreamscapesDragonfireNEWV20_dsDv20.safetensors"}'
                response = await bot.loop.run_in_executor(None, functools.partial(requests.post, url="http://127.0.0.1:7860/sdapi/v1/options", data=json))
                if response.status_code != 200:
                    raise Exception
                await ctx.respond("Switched to `fantasy` model")
                currentModel = "fantasy"
            elif model == "dream":
                json = '{"sd_model_checkpoint": "dreamshaper_8.safetensors"}'
                response = await bot.loop.run_in_executor(None, functools.partial(requests.post, url="http://127.0.0.1:7860/sdapi/v1/options", data=json))
                if response.status_code != 200:
                    raise Exception
                await ctx.respond("Switched to `dream` model")
                currentModel = "dream"
            else:
                await ctx.respond("Unknown model specified")
        except:
            await ctx.respond("Failed to connect to Stable Diffusion")
    # Send the response back to the user

# Run the bot
bot.run(os.getenv('DISCORD_BOT_KEY'))