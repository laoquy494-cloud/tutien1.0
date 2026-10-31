import time
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection

MAPS = [
    {"id": 1, "name": "Vô Danh Thôn (Phàm Giới)", "rate": 5, "icon": "🌾"},
    {"id": 2, "name": "Thanh Vân Sơn Mạch",       "rate": 12, "icon": "🌲"},
    {"id": 3, "name": "Vạn Yêu Cốc Cấm Địa",     "rate": 25, "icon": "🐺"},
    {"id": 4, "name": "Bắc Minh Băng Uyên",       "rate": 50, "icon": "❄️"},
]

def get_lichluyen_data(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT map_id, start_time FROM lichluyen WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        now = int(time.time())
        c.execute("INSERT INTO lichluyen (user_id, map_id, start_time) VALUES (?, 1, ?)", (user_id, now))
        conn.commit()
        row = (1, now)
    conn.close()
    return row

class LichLuyenView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="🌾 Thu Hoạch Lịch Luyện", style=discord.ButtonStyle.success)
    async def btn_harvest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/lichluyen`!", ephemeral=True)

        map_id, start_time = get_lichluyen_data(self.user_id)
        now = int(time.time())
        elapsed_min = max(0, (now - start_time) // 60)
        effective_min = min(480, elapsed_min) # Tối đa 8 giờ

        if effective_min < 5:
            return await interaction.response.send_message(f"⏳ Vừa bắt đầu lịch luyện! Hãy tích lũy ít nhất 5 phút (Hiện tại: {effective_min} phút).", ephemeral=True)

        cur_map = next((m for m in MAPS if m["id"] == map_id), MAPS[0])
        exp_gain = int(effective_min * cur_map["rate"] * 3)
        stone_gain = int(effective_min * cur_map["rate"] * 1.5)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE lichluyen SET start_time = ? WHERE user_id = ?", (now, self.user_id))
        c.execute("UPDATE players SET exp = exp + ?, linh_thach = linh_thach + ? WHERE user_id = ?",
                  (exp_gain, stone_gain, self.user_id))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🧭 **Thu hoạch thành công từ {cur_map['icon']} {cur_map['name']}!**\n"
            f"⏱️ Thời gian treo máy: **{effective_min} phút**\n"
            f"✨ Linh Khí: **+{exp_gain:,}** | 💎 Linh Thạch: **+{stone_gain:,}**",
            ephemeral=True
        )

class LichLuyenCog(commands.Cog, name="Lịch Luyện"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lichluyen", description="Treo máy Lịch Luyện thế giới tu chân — Thu hoạch Linh Khí thụ động")
    async def lichluyen(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        map_id, start_time = get_lichluyen_data(interaction.user.id)
        cur_map = next((m for m in MAPS if m["id"] == map_id), MAPS[0])
        now = int(time.time())
        mins = (now - start_time) // 60

        embed = discord.Embed(
            title="🧭 LỊCH LUYỆN GIANG HỒ — TREO MÁY TU CHÂN",
            description=(
                f"Đạo hữu đang vân du lịch luyện tại: **{cur_map['icon']} {cur_map['name']}**\n\n"
                f"⏱️ Đã tích lũy: **`{mins}` phút** (Tối đa 480 phút / 8 giờ)\n"
                f"📈 Tốc độ sản sinh: **`{cur_map['rate'] * 3}` Linh Khí / phút**\n\n"
                "Nhấp nút bên dưới để thu gom tài nguyên bế quan lịch luyện!"
            ),
            color=0x34495e
        )
        view = LichLuyenView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="lichluyen", aliases=["ll", "treomay"])
    async def prefix_lichluyen(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        map_id, start_time = get_lichluyen_data(ctx.author.id)
        cur_map = next((m for m in MAPS if m["id"] == map_id), MAPS[0])
        now = int(time.time())
        mins = (now - start_time) // 60

        embed = discord.Embed(
            title="🧭 LỊCH LUYỆN GIANG HỒ — TREO MÁY TU CHÂN",
            description=(
                f"Đạo hữu đang vân du lịch luyện tại: **{cur_map['icon']} {cur_map['name']}**\n\n"
                f"⏱️ Đã tích lũy: **`{mins}` phút** (Tối đa 480 phút / 8 giờ)\n"
                f"📈 Tốc độ sản sinh: **`{cur_map['rate'] * 3}` Linh Khí / phút**\n\n"
                "Nhấp nút bên dưới để thu gom tài nguyên bế quan lịch luyện!"
            ),
            color=0x34495e
        )
        view = LichLuyenView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(LichLuyenCog(bot))
