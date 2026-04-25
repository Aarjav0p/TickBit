import discord
from discord import app_commands
import os

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

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents)

tree = app_commands.CommandTree(client)

GUILD_ID = discord.Object(id=1236902125406257192)

@tree.command(name="ping", description="Replies with pong!", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    
@tree.command(name="call", description="Prints the given message", guild=GUILD_ID)
async def call(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

client.run(os.getenv("DISCORD_CLIENT"))