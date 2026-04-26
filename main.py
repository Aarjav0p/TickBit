import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = discord.Object(id=1236902125406257192)

HELP_TEXT=(
    "** TickBit help menu **\n"
    "/ping → Check if bot is alive\n"
    "/echo <message> → Echo your message\n"
    "/help → Show this help message\n\n"
    "You can also mention me with `help`!"
)

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        
        try:
            synced = await tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith("Hello"):
            await message.channel.send(f"Hi there {message.author}")
        
        if self.user in message.mentions:
            if "help" in message.content.lower():
                await message.channel.send(HELP_TEXT)

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

tree = app_commands.CommandTree(client)

@tree.command(name="ping", description="Replies with pong!", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    
@tree.command(name="echo", description="Prints the given message", guild=GUILD_ID)
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@tree.command(name="help", description="Tells status and all commands", guild=GUILD_ID)
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_TEXT)

client.run(TOKEN)