import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = discord.Object(id=1236902125406257192)

intents = discord.Intents.default()
intents.message_content = True

HELP_TEXT=(
    "** TickBit help menu **\n\n"
    "Prefix : !\n\n"
    "/ping → Check if bot is alive\n"
    "/echo <message> → Echo your message\n"
    "/help → Show this help message\n\n"
)

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


# ===================
#        BODY
# ===================

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

    try:
        synced = await bot.tree.sync(guild=GUILD_ID)
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.lower() == "hello":
        await message.channel.send(f"Hi there {message.author}!")

    # Mention-based help
    if bot.user in message.mentions and "help" in message.content.lower():
        await message.channel.send(HELP_TEXT)

    # VERY IMPORTANT: allows prefix commands to work
    await bot.process_commands(message)

# =========================
#    PREFIX COMMANDS (!)
# =========================

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hi there {ctx.author}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def echo(ctx, *, message: str):
    await ctx.send(message)

@bot.command()
async def help(ctx):
    await ctx.send(HELP_TEXT)

# =========================
#     SLASH COMMANDS (/)
# =========================

@bot.tree.command(name="ping", description="Replies with pong!", guild=GUILD_ID)
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.tree.command(name="echo", description="Prints the given message", guild=GUILD_ID)
async def slash_echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="help", description="Shows help menu", guild=GUILD_ID)
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_TEXT)


# =========================
# ▶️ RUN BOT
# =========================

bot.run(TOKEN)
