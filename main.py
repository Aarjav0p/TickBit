import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
# from dotenv import load_dotenv
# load_dotenv()

TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("TOKEN is not set in environment variables")

intents = discord.Intents.default()
intents.message_content = True

HELP_TEXT=(
    "** TickBit help menu **\n\n"
    "Prefix : !\n\n"
    "/ping → Check if bot is alive\n"
    "/echo <message> → Echo your message\n"
    "/mute <user> → Mute a user\n"
    "/unmute <user> → Unmute a user\n"
    "/kick <user> → Kick a user\n"
    "/ban <user> → Ban a user\n"
    "/help → Show this help message\n\n"
)

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# =========================
#    Auxilary functions
# =========================

MAX_TIMEOUT = datetime.timedelta(days=28)
def parse_duration(duration_str: str | None):
    if not duration_str:
        return MAX_TIMEOUT
    
    try:
        unit = duration_str[-1]
        value = int(duration_str[:-1])
        
        if unit == "s":
            duration = datetime.timedelta(seconds=value)
        elif unit == "m":
            duration = datetime.timedelta(minutes=value)
        elif unit == "h":
            duration = datetime.timedelta(hours=value)
        elif unit == "d":
            duration = datetime.timedelta(days=value)
        else:
            duration = MAX_TIMEOUT

        if duration > MAX_TIMEOUT:
            return MAX_TIMEOUT
        
        return duration
        
    except:
        return MAX_TIMEOUT

def hierarchy_check(author: discord.Member, target: discord.Member, bot_member: discord.Member):
    # Server owner bypass
    if author.id == author.guild.owner_id:
        return True, None

    # Cannot act on yourself
    if author == target:
        return False, "!!! You cannot moderate yourself."
    
    # Cannot act on owner
    if target == author.guild.owner:
        return False, "!!! You cannot moderate the server owner."

    # User hierarchy check
    if target.top_role >= author.top_role:
        return False, "!!! You cannot moderate This user (role heirarchy)"

    # Bot hierarchy check
    if target.top_role >= bot_member.top_role:
        return False, "!!! I cannot moderate this user (my role is too low)."

    return True, None


# ===================
#        BODY
# ===================

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")

    try:
        synced = await bot.tree.sync()
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

# ==== MODERATION =====

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason: str = None):
    allowed, error = hierarchy_check(ctx.author, member, ctx.guild.me)
    if not allowed:
        return await ctx.send(error)
    duration_td = parse_duration(duration)
    until = discord.utils.utcnow() + duration_td
    await member.timeout(until, reason=reason)
    await ctx.send(f"{member.mention} muted for {duration_td}\nReason : {reason}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason: str = None):
    allowed, error = hierarchy_check(ctx.author, member, ctx.guild.me)
    if not allowed:
        return await ctx.send(error)
    if member.timed_out_until is None:
        return await ctx.send("This user is not muted.")
    await member.timeout(None, reason=reason)
    await ctx.send(f"{member.mention} has been unmuted\nReason: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    allowed, error = hierarchy_check(ctx.author, member, ctx.guild.me)
    if not allowed:
        return await ctx.send(error)
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked\nReason : {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    allowed, error = hierarchy_check(ctx.author, member, ctx.guild.me)
    if not allowed:
        return await ctx.send(error)
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned\nReason : {reason}")


# =========================
#     SLASH COMMANDS (/)
# =========================

@bot.tree.command(name="ping", description="Replies with pong!")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.tree.command(name="echo", description="Prints the given message")
async def slash_echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name="help", description="Shows help menu")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_TEXT)

# ==== MODERATION ====

@bot.tree.command(name="mute", description="Mute a user")
@app_commands.describe(
    member="User to mute",
    duration="e.g. 10m, 2h, 3d",
    reason="Reason for mute"
)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, duration: str = None, reason: str = None):
    allowed, error = hierarchy_check(interaction.user, member, interaction.guild.me)
    if not allowed:
        return await interaction.response.send_message(error, ephemeral=True)
    duration_td = parse_duration(duration)
    until = discord.utils.utcnow() + duration_td
    await member.timeout(until, reason=reason)
    await interaction.response.send_message(f"{member.mention} has been muted for {duration_td}\nReason: {reason}")

@bot.tree.command(name="unmute", description="Unmute a user")
async def slash_unmute(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    allowed, error = hierarchy_check(interaction.user, member, interaction.guild.me)
    if not allowed:
        return await interaction.response.send_message(error, ephemeral=True)
    if member.timed_out_until is None:
        return await interaction.response.send_message("This user is not muted.", ephemeral=True)
    await member.timeout(None, reason=reason)
    await interaction.response.send_message(f"{member.mention} has been unmuted\nReason: {reason or 'No reason provided'}")

@bot.tree.command(name="kick", description="Kick a user")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    allowed, error = hierarchy_check(interaction.user, member, interaction.guild.me)
    if not allowed:
        return await interaction.response.send_message(error, ephemeral=True)
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been kicked\nReason: {reason}")

@bot.tree.command(name="ban", description="Ban a user")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    allowed, error = hierarchy_check(interaction.user, member, interaction.guild.me)
    if not allowed:
        return await interaction.response.send_message(error, ephemeral=True)
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been banned\nReason: {reason}")


# =========================
# ▶️ RUN BOT
# =========================

bot.run(TOKEN)
