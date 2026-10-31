import os
import sys
import atexit
import datetime
import logging
import logging.handlers
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import init_db

# Đảm bảo sys.stdout và sys.stderr không phải None khi chạy ngầm bằng pythonw
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# Đảm bảo mã hóa UTF-8 cho console trên Windows
if sys.platform.startswith("win"):
    try:
        if sys.stdout is not None:
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr is not None:
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Nạp cấu hình từ file .env
load_dotenv()

# Thiết lập logging (ghi đồng thời ra console và file bot.log xoay vòng 10MB)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "bot.log")
PID_FILE = os.path.join(BASE_DIR, "bot.pid")

log_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=3,
    encoding="utf-8"
)
file_handler.setFormatter(log_formatter)

handlers = [file_handler]
try:
    if sys.stdout is not None and hasattr(sys.stdout, "write"):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        handlers.append(console_handler)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    handlers=handlers
)
logger = logging.getLogger("TuTienBot")

def save_pid():
    """Lưu Process ID vào file bot.pid để quản lý chạy ngầm"""
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception as e:
        logger.warning(f"Không thể ghi file bot.pid: {e}")

def cleanup_pid():
    """Xóa file bot.pid khi bot dừng"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass

atexit.register(cleanup_pid)

class TuTienBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        prefix = os.getenv("COMMAND_PREFIX", "t").strip()
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix, f"{prefix} "),
            intents=intents,
            help_command=None
        )
        self.start_time = datetime.datetime.now()

    async def close(self):
        logger.info("🛑 Bot đang tiến hành hạ máy chủ / đóng kết nối an toàn...")
        cleanup_pid()
        await super().close()

    async def setup_hook(self):
        # Khởi tạo cơ sở dữ liệu SQLite
        init_db()
        logger.info(" Cơ sở dữ liệu SQLite đã được khởi tạo thành công.")

        # Tự động nạp tất cả các Cogs trong thư mục cogs/
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        loaded_cogs = 0
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    cog_name = f"cogs.{filename[:-3]}"
                    try:
                        await self.load_extension(cog_name)
                        logger.info(f"📦 Đã nạp thành công Cog: {cog_name}")
                        loaded_cogs += 1
                    except Exception as e:
                        logger.error(f"❌ Lỗi khi nạp Cog {cog_name}: {e}", exc_info=True)

        logger.info(f"🎯 Tổng cộng {loaded_cogs} cogs đã được nạp.")

        # Đồng bộ Slash Commands với Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"✨ Đã đồng bộ {len(synced)} lệnh Slash Commands với Discord.")
        except Exception as e:
            logger.error(f"❌ Lỗi khi đồng bộ Slash Commands: {e}")

        # Nạp trước thông tin Application Owner để tối ưu tốc độ lệnh Admin
        try:
            app_info = await self.application_info()
            if app_info.team:
                self.owner_ids = {m.id for m in app_info.team.members}
            elif app_info.owner:
                self.owner_id = app_info.owner.id
        except Exception:
            pass

    async def on_ready(self):
        logger.info("=" * 50)
        logger.info(f"⚡ Thiên Đạo đã vận hành — Bot [{self.user}] đã online!")
        logger.info(f"🆔 ID: {self.user.id}")
        logger.info(f"🌐 Đang phục vụ: {len(self.guilds)} máy chủ")
        logger.info("=" * 50)
        
        # Đặt trạng thái hoạt động cho Bot
        activity = discord.Activity(
            type=discord.ActivityType.competing,
            name="Đỉnh Phong Tu Tiên | /thongtin"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

def main():
    save_pid()
    token = os.getenv("DISCORD_TOKEN")
    if not token or token.strip() == "YOUR_BOT_TOKEN_HERE" or token.strip() == "YOUR_BOT_TOKEN":
        msg = (
            "\n" + "!" * 60 + "\n"
            "❌ LỖI: Chưa cấu hình DISCORD_TOKEN!\n"
            "👉 Vui lòng mở file `.env` và điền Bot Token của bạn:\n"
            "   DISCORD_TOKEN=your_actual_bot_token_here\n"
            + "!" * 60 + "\n"
        )
        logger.error(msg)
        try:
            print(msg)
        except Exception:
            pass
        cleanup_pid()
        sys.exit(1)

    logger.info("⛩️ Bắt đầu khởi chạy Tu Tiên Discord Bot...")
    bot = TuTienBot()
    try:
        bot.run(token)
    except BaseException as e:
        logger.error(f"❌ Bot bị dừng hoặc gặp lỗi: {e}", exc_info=True)
    finally:
        cleanup_pid()

if __name__ == "__main__":
    main()
