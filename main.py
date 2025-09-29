import discord
from discord.ext import commands
from discord import app_commands 
import asyncio
import datetime
import os # Bắt buộc: Để lấy BOT_TOKEN từ Render
import typing # Dùng cho Optional[str] để fix cảnh báo None

# ----------------------------------------------------------------------------------
# THIẾT LẬP TOKEN BẰNG CÁCH LẤY TỪ BIẾN MÔI TRƯỜNG (CHO RENDER)
# ----------------------------------------------------------------------------------
BOT_TOKEN = os.environ.get('MTQyMjE1MDYwOTg4ODQ3NzE4NA.GDetWd.-1Li9dhDVdE1WCZnCQ4QY87PqdA9oiwyysQkrc') 

# Thiết lập Intents (BẮT BUỘC)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Khởi tạo bot và Cây lệnh Slash (CHỈ MỘT LẦN DUY NHẤT)
client = commands.Bot(command_prefix='!', intents=intents) 
tree = app_commands.CommandTree(client) 

# ----------------------------------------------------------------------------------
# SỰ KIỆN KHI BOT SẴN SÀNG (Đăng ký Slash Commands)
# ----------------------------------------------------------------------------------
@client.event
async def on_ready():
    # Đồng bộ hóa (Sync) các lệnh Slash lên Discord
    await tree.sync()

    print(f'Bot đã đăng nhập với tên: {"Purium Bot"}') 
    await client.change_presence(activity=discord.Game(name=f"Quản lý với Slash /"))
    print("Bot đã sẵn sàng để nhận lệnh!")

# ----------------------------------------------------------------------------------
# CÁC LỆNH SLASH CHÍNH THỨC (SLASH COMMANDS)
# ----------------------------------------------------------------------------------

# Lệnh KICK: /kick member: @thành_viên reason: lý_do
@tree.command(name="kick", description="Kick thành viên khỏi server.")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = None):
    # Dùng Optional[str] để fix cảnh báo Pylint

    if member.guild_permissions.administrator:
        await interaction.response.send_message(f"Không thể kick {member.display_name} vì họ là Quản trị viên.", ephemeral=True)
        return

    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member.display_name} đã bị kick.\nLý do: {reason or "Không có"}')

# Lệnh BAN: /ban member: @thành_viên reason: lý_do
@tree.command(name="ban", description="Ban thành viên khỏi server.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = None):
    # Dùng Optional[str] để fix cảnh báo Pylint

    if member.guild_permissions.administrator:
        await interaction.response.send_message(f"Không thể ban {member.display_name} vì họ là Quản trị viên.", ephemeral=True)
        return

    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member.display_name} đã bị ban.\nLý do: {reason or "Không có"}')

# Lệnh SEND (Gửi thông báo Embed): /send channel: #kênh title: Tiêu đề content: Nội dung
@tree.command(name="send", description="Gửi thông báo Embed đến một kênh.")
@app_commands.checks.has_permissions(manage_messages=True)
async def send_slash(interaction: discord.Interaction, channel: discord.TextChannel, title: str, content: str):

    # Tạo Embed
    embed = discord.Embed(
        title=title,
        description=content,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    # Dùng display_avatar.url để tránh lỗi/cảnh báo 'None'
    embed.set_footer(text=f"Thông báo từ Mod: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    await channel.send(embed=embed)
    await interaction.response.send_message(f"Đã gửi thông báo đến {channel.mention}!", ephemeral=True)

# ----------------------------------------------------------------------------------
# XỬ LÝ LỖI (ERROR HANDLING)
# ----------------------------------------------------------------------------------
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Bạn không có đủ quyền hạn để thực hiện lệnh này!", ephemeral=True)
    else:
        # Nếu có lỗi khác, in ra console để debug
        print(f"Lỗi lệnh Slash: {error}")
        await interaction.response.send_message("Có lỗi xảy ra khi thực hiện lệnh.", ephemeral=True)

# ----------------------------------------------------------------------------------
# KHỞI CHẠY BOT (KHÔNG CÓ KEEP-ALIVE CHO RENDER)
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# KHỞI CHẠY BOT (Đã sửa lỗi None)
# ----------------------------------------------------------------------------------
if BOT_TOKEN:
    client.run(BOT_TOKEN)
else:
    print("LỖI: Không tìm thấy BOT_TOKEN. Vui lòng kiểm tra biến môi trường trên Render.")