import asyncio


import discord
from discord.ext import commands
import logging
import dotenv
import os


import requests


dotenv.load_dotenv()


token = os.getenv('TEXT')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True



bot = commands.Bot(command_prefix='!', intents=intents)

user_data = {}


def get_movie_data(movie_title):

    data_url = f"http://www.omdbapi.com/?apikey=ad68219f&t={movie_title}"
    data = requests.get(data_url).json()
    if data.get("Response") == "True":
        return data
    else:
        print(f"Movie {movie_title} not found.")
        return None
def get_movie_type(data):
    return data.get("Type")

def get_movie_title(data):
    return data.get("Title")
def get_movie_poster_url(data):
    return data.get("Poster")

def get_movie_rating(data):
    return data.get("imdbRating")
def is_movie_valid(requested_title):
    data_url = f"http://www.omdbapi.com/?apikey=ad68219f&t={requested_title}"
    response = requests.get(data_url)
    data = response.json()

    if data.get("Response") == "True":
        return True
    return False
def save_poster(poster_url, movie_title):
    filename = f"{movie_title}.jpg"
    with open(filename, "wb") as file:
        file.write(requests.get(poster_url).content)
        print(f"Saved poster {filename}")
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

    await changeToIdle()

async def changeToIdle():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.custom, name="custom",
                                  state="Чекаю на повідомлення !heplme")
    )
async def changeToReplying():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.custom, name="custom",
                                  state="Працюю з користувачами !heplme")
    )
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    global user_data

    if message.author.id not in user_data:
        user_data[message.author.id] = \
            {
                'movie_data': 0,
                'movie_title': "",
                'movie_poster_url': "",
                'movie_type': "",
                'user_rating': 0,
                'user_review': "",
                'waiting_for_review': False
            }

    if isinstance(message.channel, discord.DMChannel):
        if user_data[message.author.id]['waiting_for_review']:
            if message.content != "!send":
                user_data[message.author.id]['user_review'] = message.content
                user_data[message.author.id]['wating_for_review'] = False
            await send(message.author.id)


    await bot.process_commands(message)

@bot.command()
async def movie(ctx, *, message):
    global user_data

    await changeToReplying()
    print(f"Called !movie from {ctx.author.name}")
    user_id = ctx.author.id


    user_data[ctx.author.id] = \
        {
            'movie_data': 0,
            'movie_title': "",
            'movie_poster_url': "",
            'movie_type': "",
            'user_rating': 0,
            'movie_rating': 0,
            'user_review': "",
            'waiting_for_review': False,
            'user_name': ""
        }
    if is_movie_valid(message):

        user_data[user_id]['movie_data'] = get_movie_data(message)
        user_data[user_id]['movie_title'] = get_movie_title(user_data[user_id]['movie_data'])
        user_data[user_id]['movie_poster_url'] = get_movie_poster_url(user_data[user_id]['movie_data'])
        user_data[user_id]['movie_type'] = get_movie_type(user_data[user_id]['movie_data'])
        user_data[user_id]['movie_rating'] = get_movie_rating(user_data[user_id]['movie_data'])
        user_data[user_id]['user_name'] = ctx.author.display_name
        print(f"Movie {user_data[user_id]['movie_title']} found.")
        await validateMovie(ctx, user_id)
    else:
        embed = discord.Embed(title = "Фільму чи серіалу з такою назвою не знайдено")
        await ctx.send(embed=embed)
        await changeToIdle()

async def validateMovie(ctx, user_id):
    global user_data
    movie_type = "фільм" if get_movie_type(user_data[user_id]['movie_data']) == "movie" else "серіал"
    embed = discord.Embed(title = f"Це правильний {movie_type}?", color = discord.Color.blurple(), description = f"{user_data[user_id]['movie_title']}")
    embed.set_image(url = user_data[user_id]['movie_poster_url'])
    embed_message = await ctx.send(embed=embed)
    await embed_message.add_reaction("✅")
    await embed_message.add_reaction("❎")

    def ckeck (reaction, user):
        return reaction.message.id == embed_message.id

    reaction, user = await bot.wait_for("reaction_add", check=ckeck)
    if str(reaction.emoji) == '✅':
        await RequestRating(ctx, user_id)
        await Request_review(ctx, user_id)

async def RequestRating(ctx, user_id):
    global user_data
    movie_type = "фільм" if get_movie_type(user_data[user_id]['movie_data']) == "movie" else "серіал"
    embed = discord.Embed(title = f"Наскільки тобі сподобався {movie_type}?", color = discord.Color.red())
    embed_message = await ctx.send(embed=embed)
    await embed_message.add_reaction("1️⃣")
    await embed_message.add_reaction("2️⃣")
    await embed_message.add_reaction("3️⃣")
    await embed_message.add_reaction("4️⃣")
    await embed_message.add_reaction("5️⃣")
    await embed_message.add_reaction("6️⃣")
    await embed_message.add_reaction("7️⃣")
    await embed_message.add_reaction("8️⃣")
    await embed_message.add_reaction("9️⃣")
    await embed_message.add_reaction("🔟")

    def check(reaction, user):
        return reaction.message.id == embed_message.id

    try:
        reaction, user = await bot.wait_for("reaction_add", check=check)
    except asyncio.TimeoutError:
        await embed_message.clear_reactions()
    else:
        print(reaction.emoji)
        if str(reaction.emoji) == '1️⃣':
            user_data[user_id]['user_rating'] = 1
        elif str(reaction.emoji) == '2️⃣':
            user_data[user_id]['user_rating'] = 2
        elif str(reaction.emoji) == '3️⃣':
            user_data[user_id]['user_rating'] = 3
        elif str(reaction.emoji) == '4️⃣':
            user_data[user_id]['user_rating'] = 4
        elif str(reaction.emoji) == '5️⃣':
            user_data[user_id]['user_rating'] = 5
        elif str(reaction.emoji) == '6️⃣':
            user_data[user_id]['user_rating'] = 6
        elif str(reaction.emoji) == '7️⃣':
            user_data[user_id]['user_rating'] = 7
        elif str(reaction.emoji) == '8️⃣':
            user_data[user_id]['user_rating'] = 8
        elif str(reaction.emoji) == '9️⃣':
            user_data[user_id]['user_rating'] = 9
        elif str(reaction.emoji) == '🔟':
            user_data[user_id]['user_rating'] = 10

async def Request_review(ctx, user_id):
    global user_data
    film_type = "фільм" if get_movie_type(user_data[user_id]['movie_data']) == "movie" else "серіал"
    embed = discord.Embed(title = f"Даси якийсь відгук про {film_type}?", description = "Це не обов'язково! Щоб опублікувати відгук напиши !send",color=discord.Color.red())
    await ctx.send(embed=embed)
    user_data[user_id]['waiting_for_review'] = True

async def send(user_id):
    global user_data

    guild = bot.guilds[0]
    channel_id = 1396835931872563331
    channel = bot.get_channel(channel_id)
    print(f"sending info to guild {guild.name}, channel {channel.name}")
    text_without_review = f"Подивився(-лася) {user_data[user_id]['user_name']} \n Оцінка від {user_data[user_id]['user_name']}: {user_data[user_id]['user_rating']}, Оцінка на IMDB: {user_data[user_id]['movie_rating']}"
    text = text_without_review
    if user_data[user_id]['user_review'] != "":
        text = text_without_review  + f" \n Відгук: {user_data[user_id]['user_review']}"
    print(f"Відгук: {user_data[user_id]['user_review']}")
    embed = discord.Embed(title = user_data[user_id]['movie_title'], color = discord.Color.blurple(), description = text)
    embed.set_image(url=user_data[user_id]['movie_poster_url'])
    await channel.send(embed=embed)
    await changeToIdle()

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(title = "Допомога", description = "Щоб зробити пост про фільм напиши !movie <назва фільму/серіалу> (бажано офіційну)", color = discord.Color.red())
    await ctx.send(embed=embed)
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
