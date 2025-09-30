import discord
from discord.ext import commands
from discord import app_commands 
import asyncio
import datetime
import os
import typing 

# ----------------------------------------------------------------------------------
# THIẾT LẬP TOKEN BẰNG CÁCH LẤY TỪ BIẾN MÔI TRƯỜNG (CHO RENDER WORKER)
# ----------------------------------------------------------------------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN') 
# Đảm bảo Key bạn đặt trên Render là BOT_TOKEN

# Thiết lập Intents (BẮT BUỘC)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Khởi tạo bot và Cây lệnh Slash
client = commands.Bot(command_prefix='!', intents=intents) 
tree = client.tree 

# ----------------------------------------------------------------------------------
# SỰ KIỆN KHI BOT SẴN SÀNG (Đăng ký Slash Commands)
# ----------------------------------------------------------------------------------
@client.event
async def on_ready():
    try:
        # Đồng bộ hóa (Sync) các lệnh Slash lên Discord
        await tree.sync()
        print(f'✅ Bot đã đăng nhập với tên: {client.user}') 
        await client.change_presence(activity=discord.Game(name="Quản lý với Slash /"))
        print("✅ Bot đã sẵn sàng để nhận lệnh!")
    except Exception as e:
        print(f"❌ Lỗi khi đồng bộ lệnh: {e}")

# ----------------------------------------------------------------------------------
# CÁC LỆNH SLASH CHÍNH THỨC
# ----------------------------------------------------------------------------------

# Lệnh KICK: /kick member: @thành_viên reason: lý_do
@tree.command(name="kick", description="Kick thành viên khỏi server.")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = None):
    try:
        if member.guild_permissions.administrator:
            await interaction.response.send_message(f"❌ Không thể kick {member.display_name} vì họ là Quản trị viên.", ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(f'✅ {member.display_name} đã bị kick.\nLý do: {reason or "Không có"}')
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)

# Lệnh BAN: /ban member: @thành_viên reason: lý_do
@tree.command(name="ban", description="Ban thành viên khỏi server.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = None):
    try:
        if member.guild_permissions.administrator:
            await interaction.response.send_message(f"❌ Không thể ban {member.display_name} vì họ là Quản trị viên.", ephemeral=True)
            return
        await member.ban(reason=reason)
        await interaction.response.send_message(f'✅ {member.display_name} đã bị ban.\nLý do: {reason or "Không có"}')
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)

# Lệnh SEND (Gửi thông báo Embed): /send channel: #kênh title: Tiêu đề content: Nội dung
@tree.command(name="send", description="Gửi thông báo Embed đến một kênh.")
@app_commands.checks.has_permissions(manage_messages=True)
async def send_slash(interaction: discord.Interaction, channel: discord.TextChannel, title: str, content: str):
    try:
        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Thông báo từ Mod: {interaction.user.display_name}", 
                        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Đã gửi thông báo đến {channel.mention}!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)

# ----------------------------------------------------------------------------------
# XỬ LÝ LỖI (ERROR HANDLING)
# ----------------------------------------------------------------------------------
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Bạn không có đủ quyền hạn để thực hiện lệnh này!", ephemeral=True)
        else:
            print(f"❌ Lỗi lệnh Slash: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Có lỗi xảy ra khi thực hiện lệnh.", ephemeral=True)
    except Exception as e:
        print(f"❌ Lỗi trong error handler: {e}")

# ----------------------------------------------------------------------------------
# KHỞI CHẠY BOT (CHO BACKGROUND WORKER)
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    if BOT_TOKEN:
        print("🚀 Starting Purium Bot for Render Worker...")
        client.run(BOT_TOKEN)
    else:
        print("❌ LỖI: Không tìm thấy BOT_TOKEN. Vui lòng kiểm tra Biến môi trường trên Render.")
