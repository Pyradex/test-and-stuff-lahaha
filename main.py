"""
LCSRC Utilities - Discord Audit Logger Bot
For ER:LC Discord Communications Server
Guild ID: 1289789596238086194
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify

import discord
from discord import app_commands
from discord.ext import commands

# ============== CONFIGURATION ==============
GUILD_ID = 1289789596238086194
AUDIT_CHANNEL_NAME = "「📄」audit-logistics"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Embed Configuration
EMBED_COLOR = 0x43c7c5  # #43c7c5
AUDIT_IMAGE_URL = "https://i.imgur.com/0oNYYxK.png"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== FLASK APP FOR 24/7 HOSTING ==============
app = Flask(__name__)

@app.route('/')
def home():
    """Root route to prevent 404 and show bot is running"""
    return jsonify({
        "status": "online",
        "bot": "LCSRC Utilities",
        "guild": GUILD_ID,
        "audit_logger": "active"
    })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy"})

# Run Flask in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ============== DISCORD BOT SETUP ==============
# Required intents for comprehensive audit logging
intents = discord.Intents.all()
intents.presences = False  # Disable if not needed for privacy

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=None,  # Will be set on ready
    help_command=None
)

# Sync tree for slash commands (use bot's built-in tree)
tree = bot.tree

# ============== UTILITY FUNCTIONS ==============
async def get_audit_channel(guild: discord.Guild) -> discord.TextChannel:
    """Find or create the audit logistics channel"""
    channel = discord.utils.get(guild.text_channels, name=AUDIT_CHANNEL_NAME)
    if not channel:
        # Try to find with similar name (in case of formatting differences)
        for ch in guild.text_channels:
            if "audit" in ch.name.lower() and "logistic" in ch.name.lower():
                channel = ch
                break
    
    if not channel:
        # Create the channel if it doesn't exist
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        channel = await guild.create_text_channel(
            AUDIT_CHANNEL_NAME,
            overwrites=overwrites,
            topic="LCSRC Utilities Audit Logger"
        )
        logger.info(f"Created audit channel: {channel.name}")
    
    return channel

def format_action_details(audit_log_entry, action_type: str) -> str:
    """Format detailed action summary from audit log"""
    details = []
    user = audit_log_entry.user
    target = audit_log_entry.target
    
    # User info
    if user:
        details.append(f"**User:** {user.mention} ({user} | ID: {user.id})")
    
    # Target info
    if target:
        if hasattr(target, 'mention'):
            details.append(f"**Target:** {target.mention} ({target} | ID: {target.id})")
        else:
            details.append(f"**Target:** {target} (ID: {target.id if hasattr(target, 'id') else 'N/A'})")
    
    # Action-specific details
    if action_type == "message_delete":
        if audit_log_entry.extra:
            if isinstance(audit_log_entry.extra, dict):
                count = audit_log_entry.extra.get('count', 1)
                details.append(f"**Messages Deleted:** {count}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "message_edit":
        changes = []
        if audit_log_entry.before:
            changes.append(f"Before: {audit_log_entry.before}")
        if audit_log_entry.after:
            changes.append(f"After: {audit_log_entry.after}")
        if changes:
            details.append(f"**Changes:** {' | '.join(changes)}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type in ["member_ban", "member_unban"]:
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "member_kick":
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "member_timeout":
        # Timeout details
        if audit_log_entry.extra:
            if isinstance(audit_log_entry.extra, dict):
                timeout_until = audit_log_entry.extra.get('timeout_until')
                if timeout_until:
                    details.append(f"**Timeout Until:** <t:{int(timeout_until.timestamp())}>")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type in ["role_create", "role_delete", "role_update"]:
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type in ["channel_create", "channel_delete", "channel_update"]:
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "emoji_create":
        if audit_log_entry.extra:
            details.append(f"**Emoji:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "emoji_delete":
        if audit_log_entry.extra:
            details.append(f"**Deleted Emoji:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "emoji_update":
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "sticker_create":
        if audit_log_entry.extra:
            details.append(f"**Sticker:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "sticker_delete":
        if audit_log_entry.extra:
            details.append(f"**Deleted Sticker:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "sticker_update":
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "invite_create":
        if audit_log_entry.extra:
            invite_data = audit_log_entry.extra
            if isinstance(invite_data, dict):
                details.append(f"**Channel:** {invite_data.get('channel', 'Unknown')}")
                details.append(f"**Max Age:** {invite_data.get('max_age', 'Permanent')}")
                details.append(f"**Max Uses:** {invite_data.get('max_uses', 'Unlimited')}")
                details.append(f"**Temporary:** {invite_data.get('temporary', False)}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "invite_delete":
        if audit_log_entry.extra:
            details.append(f"**Invite:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "webhook_create":
        if audit_log_entry.extra:
            details.append(f"**Webhook:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "webhook_delete":
        if audit_log_entry.extra:
            details.append(f"**Deleted Webhook:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "webhook_update":
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "integration_create":
        if audit_log_entry.extra:
            details.append(f"**Integration:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "integration_delete":
        if audit_log_entry.extra:
            details.append(f"**Deleted Integration:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "integration_update":
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "slash_command_used":
        if audit_log_entry.extra:
            details.append(f"**Command:** {audit_log_entry.extra.get('name', 'Unknown')}")
            details.append(f"**Options:** {audit_log_entry.extra}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    elif action_type == "command_permission_update":
        if audit_log_entry.before:
            details.append(f"**Before:** {audit_log_entry.before}")
        if audit_log_entry.after:
            details.append(f"**After:** {audit_log_entry.after}")
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
            
    else:
        # Generic handling for any other action type
        if audit_log_entry.reason:
            details.append(f"**Reason:** {audit_log_entry.reason}")
    
    return "\n".join(details) if details else "No additional details"

async def send_audit_log(guild: discord.Guild, action_type: str, action_name: str, details: str = None, user: discord.Member = None):
    """Send audit log embed to the audit channel"""
    try:
        channel = await get_audit_channel(guild)
        
        # Get user's nickname in the guild
        member_name = "Unknown"
        if user:
            member_name = user.nick if user.nick else user.name
        
        # Build the text embed
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        action_text = action_name
        if details:
            action_text = f"{action_name}\n{details}"
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        # Create image embed
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        # Send both embeds
        await channel.send(embeds=[image_embed, text_embed])
        logger.info(f"Audit log sent: {action_type} by {member_name}")
        
    except Exception as e:
        logger.error(f"Error sending audit log: {e}")

async def log_audit_entry(guild: discord.Guild, entry: discord.AuditLogEntry):
    """Process and log an audit log entry"""
    action = entry.action
    user = entry.user
    target = entry.target
    
    # Map audit log actions to readable names
    action_mapping = {
        discord.AuditLogAction.message_delete: ("Message Deleted", "message_delete"),
        discord.AuditLogAction.message_edit: ("Message Edited", "message_edit"),
        discord.AuditLogAction.ban: ("Member Banned", "member_ban"),
        discord.AuditLogAction.unban: ("Member Unbanned", "member_unban"),
        discord.AuditLogAction.kick: ("Member Kicked", "member_kick"),
        discord.AuditLogAction.member_update: ("Member Updated", "member_update"),
        discord.AuditLogAction.role_create: ("Role Created", "role_create"),
        discord.AuditLogAction.role_delete: ("Role Deleted", "role_delete"),
        discord.AuditLogAction.role_update: ("Role Updated", "role_update"),
        discord.AuditLogAction.channel_create: ("Channel Created", "channel_create"),
        discord.AuditLogAction.channel_delete: ("Channel Deleted", "channel_delete"),
        discord.AuditLogAction.channel_update: ("Channel Updated", "channel_update"),
        discord.AuditLogAction.emoji_create: ("Emoji Created", "emoji_create"),
        discord.AuditLogAction.emoji_delete: ("Emoji Deleted", "emoji_delete"),
        discord.AuditLogAction.emoji_update: ("Emoji Updated", "emoji_update"),
        discord.AuditLogAction.sticker_create: ("Sticker Created", "sticker_create"),
        discord.AuditLogAction.sticker_delete: ("Sticker Deleted", "sticker_delete"),
        discord.AuditLogAction.sticker_update: ("Sticker Updated", "sticker_update"),
        discord.AuditLogAction.invite_create: ("Invite Created", "invite_create"),
        discord.AuditLogAction.invite_delete: ("Invite Deleted", "invite_delete"),
        discord.AuditLogAction.invite_update: ("Invite Updated", "invite_update"),
        discord.AuditLogAction.webhook_create: ("Webhook Created", "webhook_create"),
        discord.AuditLogAction.webhook_delete: ("Webhook Deleted", "webhook_delete"),
        discord.AuditLogAction.webhook_update: ("Webhook Updated", "webhook_update"),
        discord.AuditLogAction.integration_create: ("Integration Created", "integration_create"),
        discord.AuditLogAction.integration_delete: ("Integration Deleted", "integration_delete"),
        discord.AuditLogAction.integration_update: ("Integration Updated", "integration_update"),
        discord.AuditLogAction.commands_permission_update: ("Command Permissions Updated", "command_permission_update"),
        discord.AuditLogAction.thread_create: ("Thread Created", "thread_create"),
        discord.AuditLogAction.thread_delete: ("Thread Deleted", "thread_delete"),
        discord.AuditLogAction.thread_update: ("Thread Updated", "thread_update"),
        discord.AuditLogAction.automod_rule_create: ("Automod Rule Created", "automod_rule_create"),
        discord.AuditLogAction.automod_rule_delete: ("Automod Rule Deleted", "automod_rule_delete"),
        discord.AuditLogAction.automod_rule_update: ("Automod Rule Updated", "automod_rule_update"),
        discord.AuditLogAction.automod_block_message: ("Automod Blocked Message", "automod_block"),
        discord.AuditLogAction.automod_flag_message: ("Automod Flagged Message", "automod_flag"),
        discord.AuditLogAction.automod_user_timeout: ("Automod Timeout", "automod_timeout"),
        discord.AuditLogAction.soundboard_sound_create: ("Soundboard Sound Created", "soundboard_create"),
        discord.AuditLogAction.soundboard_sound_delete: ("Soundboard Sound Deleted", "soundboard_delete"),
        discord.AuditLogAction.soundboard_sound_update: ("Soundboard Sound Updated", "soundboard_update"),
    }
    
    if action in action_mapping:
        action_name, action_type = action_mapping[action]
        details = format_action_details(entry, action_type)
        await send_audit_log(guild, action_type, action_name, details, user)

# ============== EVENT LISTENERS ==============
@bot.event
async def on_ready():
    """Bot is ready and connected"""
    logger.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    
    # Set application ID
    bot.application_id = bot.user.id
    
    # Get the guild
    guild = bot.get_guild(GUILD_ID)
    if guild:
        logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands for this guild
        try:
            tree.copy_global_to(guild=guild)
            await tree.sync(guild=guild)
            logger.info("Slash commands synced successfully")
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")
    else:
        logger.error(f"Could not find guild with ID: {GUILD_ID}")
    
    # Change bot status
    await bot.change_presence(
        activity=discord.Game(name="LCSRC Utilities | Audit Logger"),
        status=discord.Status.online
    )
    
    logger.info("Bot is ready!")

@bot.event
async def on_guild_join(guild: discord.Guild):
    """When bot joins a new guild - security check"""
    if guild.id != GUILD_ID:
        # Leave any other guild immediately for security
        logger.warning(f"Bot was invited to wrong guild {guild.id}, leaving...")
        await guild.leave()
        return
    
    logger.info(f"Joined correct guild: {guild.name}")

@bot.event
async def on_message(message: discord.Message):
    """Log message sent events"""
    # Only process messages from our target guild
    if message.guild is None or message.guild.id != GUILD_ID:
        return
    
    # Ignore bot messages to prevent feedback loops
    if message.author.bot:
        return
    
    # Log message sent (only for important channels or as needed)
    # Note: Discord doesn't provide audit log for message create, only delete/edit
    # This is handled in the audit log check

@bot.event
async def on_message_delete(message: discord.Message):
    """Log deleted messages"""
    if message.guild is None or message.guild.id != GUILD_ID:
        return
    
    if message.author.bot:
        return
    
    try:
        channel = await get_audit_channel(message.guild)
        
        # Get user's nickname
        member_name = message.author.nick if message.author.nick else message.author.name
        
        # Create detailed action description
        action_text = (
            f"A message was **deleted** in {message.channel.mention}\n"
            f"**Message Content:** {message.content[:500] if message.content else '(No text content)'}\n"
            f"**Message ID:** `{message.id}`\n"
            f"**Channel:** #{message.channel.name}"
        )
        
        # Build embeds
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging message delete: {e}")

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    """Log edited messages"""
    if before.guild is None or before.guild.id != GUILD_ID:
        return
    
    if before.author.bot:
        return
    
    if before.content == after.content:
        return  # No actual edit
    
    try:
        channel = await get_audit_channel(before.guild)
        
        member_name = before.author.nick if before.author.nick else before.author.name
        
        action_text = (
            f"A message was **edited** in {before.channel.mention}\n"
            f"**Before:** {before.content[:500] if before.content else '(No content)'}\n"
            f"**After:** {after.content[:500] if after.content else '(No content)'}\n"
            f"**Message ID:** `{before.id}`\n"
            f"**Channel:** #{before.channel.name}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging message edit: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    """Log member join"""
    if member.guild.id != GUILD_ID:
        return
    
    try:
        channel = await get_audit_channel(member.guild)
        
        member_name = member.nick if member.nick else member.name
        
        action_text = (
            f"A new member **joined** the server\n"
            f"**Account Created:** <t:{int(member.created_at.timestamp())}> ({discord.utils.format_dt(member.created_at, 'R')})\n"
            f"**User ID:** `{member.id}`\n"
            f"**Account Age:** {discord.utils.format_dt(member.created_at, 'R')}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging member join: {e}")

@bot.event
async def on_member_remove(member: discord.Member):
    """Log member leave/kick - try to determine which via audit log"""
    if member.guild.id != GUILD_ID:
        return
    
    try:
        # Give Discord a moment to create the audit log entry
        await discord.utils.sleep_until(datetime.now() + discord.utils.utcnow().timestamp() + 0.5)
        
        # Check audit log for kick
        async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                # It was a kick
                await send_audit_log(
                    member.guild,
                    "member_kick",
                    "Member Kicked",
                    f"**Reason:** {entry.reason if entry.reason else 'No reason provided'}",
                    entry.user
                )
                return
        
        # If no kick found, it's a leave
        channel = await get_audit_channel(member.guild)
        
        member_name = member.nick if member.nick else member.name
        
        action_text = (
            f"A member **left** the server\n"
            f"**User ID:** `{member.id}`"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging member remove: {e}")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Log member updates (nickname, roles, timeout, etc.)"""
    if before.guild.id != GUILD_ID:
        return
    
    changes = []
    
    # Nickname change
    if before.nick != after.nick:
        old_nick = before.nick if before.nick else before.name
        new_nick = after.nick if after.nick else after.name
        changes.append(f"**Nickname:** `{old_nick}` → `{new_nick}`")
    
    # Timeout change
    if before.timeout != after.timeout:
        if after.timeout:
            changes.append(f"**Timeout Set:** Until <t:{int(after.timeout.timestamp())}>")
        else:
            changes.append(f"**Timeout Removed**")
    
    # Role changes
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    
    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles
    
    if added_roles:
        role_names = ", ".join([r.mention for r in added_roles])
        changes.append(f"**Roles Added:** {role_names}")
    
    if removed_roles:
        role_names = ", ".join([r.mention for r in removed_roles])
        changes.append(f"**Roles Removed:** {role_names}")
    
    if not changes:
        return
    
    try:
        channel = await get_audit_channel(before.guild)
        
        member_name = after.nick if after.nick else after.name
        
        action_text = f"Member profile **updated**\n" + "\n".join(changes)
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value=member_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging member update: {e}")

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    """Log guild updates"""
    if before.id != GUILD_ID:
        return
    
    changes = []
    
    if before.name != after.name:
        changes.append(f"**Server Name:** `{before.name}` → `{after.name}`")
    
    if before.icon != after.icon:
        if after.icon:
            changes.append(f"**Server Icon:** Changed to new icon")
        else:
            changes.append(f"**Server Icon:** Removed")
    
    if before.splash != after.splash:
        changes.append(f"**Server Splash:** Updated")
    
    if before.banner != after.banner:
        changes.append(f"**Server Banner:** Updated")
    
    if before.vanity_url_code != after.vanity_url_code:
        changes.append(f"**Vanity URL:** `{before.vanity_url_code}` → `{after.vanity_url_code}`")
    
    if before.verification_level != after.verification_level:
        changes.append(f"**Verification Level:** {before.verification_level} → {after.verification_level}")
    
    if before.explicit_content_filter != after.explicit_content_filter:
        changes.append(f"**Content Filter:** {before.explicit_content_filter} → {after.explicit_content_filter}")
    
    if before.default_notifications != after.default_notifications:
        changes.append(f"**Notifications:** {before.default_notifications} → {after.default_notifications}")
    
    if not changes:
        return
    
    try:
        channel = await get_audit_channel(before)
        
        action_text = "Server settings **updated**\n" + "\n".join(changes)
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging guild update: {e}")

@bot.event
async def on_guild_role_create(role: discord.Role):
    """Log role creation"""
    if role.guild.id != GUILD_ID:
        return
    
    try:
        channel = await get_audit_channel(role.guild)
        
        action_text = (
            f"A new role was **created**\n"
            f"**Role:** {role.mention}\n"
            f"**Color:** {role.color}\n"
            f"**Permissions:** {role.permissions.value}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging role create: {e}")

@bot.event
async def on_guild_role_delete(role: discord.Role):
    """Log role deletion"""
    if role.guild.id != GUILD_ID:
        return
    
    try:
        channel = await get_audit_channel(role.guild)
        
        action_text = (
            f"A role was **deleted**\n"
            f"**Role Name:** {role.name}\n"
            f"**Role ID:** `{role.id}`\n"
            f"**Color:** {role.color}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging role delete: {e}")

@bot.event
async def on_guild_role_update(before: discord.Role, after: discord.Role):
    """Log role updates"""
    if before.guild.id != GUILD_ID:
        return
    
    changes = []
    
    if before.name != after.name:
        changes.append(f"**Name:** `{before.name}` → `{after.name}`")
    
    if before.color != after.color:
        changes.append(f"**Color:** {before.color} → {after.color}")
    
    if before.hoist != after.hoist:
        changes.append(f"**Hoist:** {before.hoist} → {after.hoist}")
    
    if before.mentionable != after.mentionable:
        changes.append(f"**Mentionable:** {before.mentionable} → {after.mentionable}")
    
    if before.permissions != after.permissions:
        changes.append(f"**Permissions:** Updated")
    
    if not changes:
        return
    
    try:
        channel = await get_audit_channel(before.guild)
        
        action_text = f"Role **updated**\n" + "\n".join(changes)
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging role update: {e}")

@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    """Log channel creation"""
    if channel.guild.id != GUILD_ID:
        return
    
    try:
        audit_channel = await get_audit_channel(channel.guild)
        
        action_text = (
            f"A new channel was **created**\n"
            f"**Channel:** {channel.mention}\n"
            f"**Type:** {channel.type}\n"
            f"**Category:** {channel.category.name if channel.category else 'None'}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await audit_channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging channel create: {e}")

@bot.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    """Log channel deletion"""
    if channel.guild.id != GUILD_ID:
        return
    
    try:
        audit_channel = await get_audit_channel(channel.guild)
        
        action_text = (
            f"A channel was **deleted**\n"
            f"**Channel Name:** {channel.name}\n"
            f"**Type:** {channel.type}\n"
            f"**Category:** {channel.category.name if channel.category else 'None'}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await audit_channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging channel delete: {e}")

@bot.event
async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
    """Log channel updates"""
    if before.guild.id != GUILD_ID:
        return
    
    changes = []
    
    if before.name != after.name:
        changes.append(f"**Name:** `{before.name}` → `{after.name}`")
    
    if before.position != after.position:
        changes.append(f"**Position:** {before.position} → {after.position}")
    
    if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
        if before.topic != after.topic:
            changes.append(f"**Topic:** `{before.topic}` → `{after.topic}`")
        if before.slowmode_delay != after.slowmode_delay:
            changes.append(f"**Slowmode:** {before.slowmode_delay}s → {after.slowmode_delay}s")
        if before.nsfw != after.nsfw:
            changes.append(f"**NSFW:** {before.nsfw} → {after.nsfw}")
    
    if isinstance(before, discord.VoiceChannel) and isinstance(after, discord.VoiceChannel):
        if before.bitrate != after.bitrate:
            changes.append(f"**Bitrate:** {before.bitrate} → {after.bitrate}")
        if before.user_limit != after.user_limit:
            changes.append(f"**User Limit:** {before.user_limit} → {after.user_limit}")
    
    if not changes:
        return
    
    try:
        audit_channel = await get_audit_channel(before.guild)
        
        action_text = f"Channel **updated**\n" + "\n".join(changes)
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        text_embed.add_field(
            name="Community Member:",
            value="Server Settings",
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await audit_channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging channel update: {e}")

@bot.event
async def on_invite_create(invite: discord.Invite):
    """Log invite creation"""
    if invite.guild is None or invite.guild.id != GUILD_ID:
        return
    
    try:
        channel = await get_audit_channel(invite.guild)
        
        action_text = (
            f"A new invite was **created**\n"
            f"**Code:** `{invite.code}`\n"
            f"**Channel:** {invite.channel.mention if invite.channel else 'Unknown'}\n"
            f"**Max Age:** {invite.max_age if invite.max_age > 0 else 'Infinite'}\n"
            f"**Max Uses:** {invite.max_uses if invite.max_uses > 0 else 'Infinite'}\n"
            f"**Temporary:** {invite.temporary}"
        )
        
        image_embed = discord.Embed()
        image_embed.set_image(url=AUDIT_IMAGE_URL)
        
        text_embed = discord.Embed(
            color=EMBED_COLOR,
            timestamp=datetime.now()
        )
        
        inviter_name = invite.inviter.nick if invite.inviter.nick else invite.inviter.name if invite.inviter else "Unknown"
        
        text_embed.add_field(
            name="Community Member:",
            value=inviter_name,
            inline=True
        )
        
        text_embed.add_field(
            name="Action:",
            value=action_text,
            inline=True
        )
        
        text_embed.add_field(
            name="Timestamp:",
            value=f"<t:{int(datetime.now().timestamp())}>",
            inline=False
        )
        
        await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging invite create: {e}")

@bot.event
async def on_webhook_update(channel: discord.TextChannel):
    """Log webhook updates"""
    if channel.guild.id != GUILD_ID:
        return
    
    try:
        # Check audit log for webhook changes
        async for entry in channel.guild.audit_logs(limit=5):
            if entry.action in [discord.AuditLogAction.webhook_create, discord.AuditLogAction.webhook_delete, discord.AuditLogAction.webhook_update]:
                await log_audit_entry(channel.guild, entry)
                return
    except Exception as e:
        logger.error(f"Error logging webhook update: {e}")

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before: list, after: list):
    """Log emoji updates"""
    if guild.id != GUILD_ID:
        return
    
    try:
        added = [e for e in after if e not in before]
        removed = [e for e in before if e not in after]
        
        for emoji in added:
            channel = await get_audit_channel(guild)
            
            action_text = (
                f"A new emoji was **added**\n"
                f"**Emoji:** {emoji}\n"
                f"**Name:** {emoji.name}\n"
                f"**Animated:** {emoji.animated}"
            )
            
            image_embed = discord.Embed()
            image_embed.set_image(url=AUDIT_IMAGE_URL)
            
            text_embed = discord.Embed(
                color=EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            text_embed.add_field(
                name="Community Member:",
                value="Server Settings",
                inline=True
            )
            
            text_embed.add_field(
                name="Action:",
                value=action_text,
                inline=True
            )
            
            text_embed.add_field(
                name="Timestamp:",
                value=f"<t:{int(datetime.now().timestamp())}>",
                inline=False
            )
            
            await channel.send(embeds=[image_embed, text_embed])
        
        for emoji in removed:
            channel = await get_audit_channel(guild)
            
            action_text = (
                f"An emoji was **removed**\n"
                f"**Name:** {emoji.name}\n"
                f"**Animated:** {emoji.animated}"
            )
            
            image_embed = discord.Embed()
            image_embed.set_image(url=AUDIT_IMAGE_URL)
            
            text_embed = discord.Embed(
                color=EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            text_embed.add_field(
                name="Community Member:",
                value="Server Settings",
                inline=True
            )
            
            text_embed.add_field(
                name="Action:",
                value=action_text,
                inline=True
            )
            
            text_embed.add_field(
                name="Timestamp:",
                value=f"<t:{int(datetime.now().timestamp())}>",
                inline=False
            )
            
            await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging emoji update: {e}")

@bot.event
async def on_guild_stickers_update(guild: discord.Guild, before: list, after: list):
    """Log sticker updates"""
    if guild.id != GUILD_ID:
        return
    
    try:
        added = [s for s in after if s not in before]
        removed = [s for s in before if s not in after]
        
        for sticker in added:
            channel = await get_audit_channel(guild)
            
            action_text = (
                f"A new sticker was **added**\n"
                f"**Name:** {sticker.name}\n"
                f"**Format:** {sticker.format}"
            )
            
            image_embed = discord.Embed()
            image_embed.set_image(url=AUDIT_IMAGE_URL)
            
            text_embed = discord.Embed(
                color=EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            text_embed.add_field(
                name="Community Member:",
                value="Server Settings",
                inline=True
            )
            
            text_embed.add_field(
                name="Action:",
                value=action_text,
                inline=True
            )
            
            text_embed.add_field(
                name="Timestamp:",
                value=f"<t:{int(datetime.now().timestamp())}>",
                inline=False
            )
            
            await channel.send(embeds=[image_embed, text_embed])
        
        for sticker in removed:
            channel = await get_audit_channel(guild)
            
            action_text = (
                f"A sticker was **removed**\n"
                f"**Name:** {sticker.name}"
            )
            
            image_embed = discord.Embed()
            image_embed.set_image(url=AUDIT_IMAGE_URL)
            
            text_embed = discord.Embed(
                color=EMBED_COLOR,
                timestamp=datetime.now()
            )
            
            text_embed.add_field(
                name="Community Member:",
                value="Server Settings",
                inline=True
            )
            
            text_embed.add_field(
                name="Action:",
                value=action_text,
                inline=True
            )
            
            text_embed.add_field(
                name="Timestamp:",
                value=f"<t:{int(datetime.now().timestamp())}>",
                inline=False
            )
            
            await channel.send(embeds=[image_embed, text_embed])
        
    except Exception as e:
        logger.error(f"Error logging sticker update: {e}")

# ============== BACKGROUND TASK FOR AUDIT LOG CHECKING ==============
async def audit_log_checker():
    """Background task to check for audit log entries that aren't captured by events"""
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        try:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                # Check recent audit log entries
                async for entry in guild.audit_logs(limit=20):
                    # This is a fallback - most actions should be caught by events
                    # Only log if not already handled (you could add tracking here)
                    pass
        except Exception as e:
            logger.error(f"Error in audit log checker: {e}")
        
        await discord.utils.sleep_until(discord.utils.utcnow() + 5)  # Check every 5 seconds

# ============== SLASH COMMANDS ==============
@tree.command(name="auditstatus", description="Check the audit logger status", guild=discord.Object(id=GUILD_ID))
async def audit_status(interaction: discord.Interaction):
    """Check if the audit logger is running"""
    await interaction.response.send_message(
        embed=discord.Embed(
            title="LCSRC Utilities - Audit Logger",
            description=f"✅ Audit Logger is **active** for {interaction.guild.name}",
            color=EMBED_COLOR
        ).add_field(
            name="Guild ID",
            value=str(GUILD_ID),
            inline=True
        ).add_field(
            name="Audit Channel",
            value=AUDIT_CHANNEL_NAME,
            inline=True
        ),
        ephemeral=True
    )

@tree.command(name="ping", description="Check bot latency", guild=discord.Object(id=GUILD_ID))
async def ping_command(interaction: discord.Interaction):
    """Check bot latency"""
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Pong!",
            description=f"Bot latency: **{round(bot.latency * 1000)}ms**",
            color=EMBED_COLOR
        ),
        ephemeral=True
    )

# ============== MAIN ==============
if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("No BOT_TOKEN found in environment variables!")
        logger.error("Please set the BOT_TOKEN environment variable.")
        exit(1)
    
    # Run Flask in background thread
    import threading
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started on port 8080")
    
    # Run Discord bot
    logger.info("Starting Discord bot...")
    bot.run(BOT_TOKEN, reconnect=True)

