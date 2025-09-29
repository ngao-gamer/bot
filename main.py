import discord
from discord.ext import commands
from discord import app_commands 
import asyncio
import datetime
import os
import typing
import time
import requests
from flask import Flask
from threading import Thread, Timer

# ----------------------------------------------------------------------------------
# THIẾT LẬP TOKEN BẰNG CÁCH LẤY TỪ BIẾN MÔI TRƯỜNG (CHO RENDER)
# ----------------------------------------------------------------------------------
BOT_TOKEN = os.environ.get('DISCORD_TOKEN')

if not BOT_TOKEN:
    raise ValueError("""
    ❌ DISCORD_TOKEN environment variable is required!
    
    To fix this:
    1. Get your bot token from Discord Developer Portal
    2. For Render: Set DISCORD_TOKEN in environment variables  
    3. For local development: Create .env file with DISCORD_TOKEN=your_token_here
    
    Never hardcode tokens in your code for security!
    """)

# Thiết lập Intents (BẮT BUỘC)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Khởi tạo bot (Bot tự động tạo command tree)
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
        print(f"❌ Lỗi khi khởi tạo bot: {e}")

# ----------------------------------------------------------------------------------
# CÁC LỆNH SLASH CHÍNH THỨC (SLASH COMMANDS)
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
        # Tạo Embed
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
# CÁC CHỨC NĂNG CHẠY 24/7 (KEEP ALIVE) CHO RENDER.COM
# ----------------------------------------------------------------------------------
app = Flask(__name__)
start_time = time.time()

@app.route('/')
def home():
    try:
        uptime = int(time.time() - start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        bot_status = "🟢 ONLINE" if client.is_ready() else "🔴 OFFLINE"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Purium Bot Status</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .status {{ font-size: 24px; margin: 10px 0; }}
                .online {{ color: #28a745; }}
                .offline {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Purium Bot Status Dashboard</h1>
                <div class="status">Bot Status: <span class="{'online' if client.is_ready() else 'offline'}">{bot_status}</span></div>
                <p><strong>⏰ Uptime:</strong> {hours}h {minutes}m {seconds}s</p>
                <p><strong>🕐 Last Check:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>🖥️ Server:</strong> Render.com Always Running ✅</p>
                <p><strong>🔄 Auto-Refresh:</strong> Every 30 seconds</p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/ping')
def ping():
    return {
        "status": "alive",
        "bot_ready": client.is_ready() if client else False,
        "uptime": int(time.time() - start_time),
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "discord-bot",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime": int(time.time() - start_time)
    }

# Lấy PORT từ environment variable (Render tự động cung cấp)
PORT = int(os.environ.get('PORT', 8080))

def run_flask():
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Flask server error: {e}")

def keep_alive():  
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print(f"✅ Flask server started on port {PORT}")

# Auto-ping system để giữ server luôn hoạt động trên Render
def auto_ping():
    try:
        if PORT != 80 and PORT != 443:
            url = f"http://localhost:{PORT}/ping"
        else:
            url = "http://localhost/ping"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Auto-ping successful - Server is alive")
        else:
            print(f"⚠️ Auto-ping returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Auto-ping failed: {e}")
    
    # Lặp lại mỗi 5 phút
    Timer(300, auto_ping).start()

def start_auto_ping():
    # Đợi 30 giây rồi bắt đầu auto-ping
    Timer(30, auto_ping).start()
    print("✅ Auto-ping system activated")

# ----------------------------------------------------------------------------------
# KHỞI CHẠY BOT CHO RENDER.COM
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        print("🚀 Starting Purium Bot for Render.com...")
        print(f"🔧 Using PORT: {PORT}")
        
        # Khởi động Flask server
        keep_alive()
        
        # Khởi động auto-ping system
        start_auto_ping()
        
        print("✅ All systems ready!")
        
        # Chạy Discord bot
        client.run(BOT_TOKEN)
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        raise