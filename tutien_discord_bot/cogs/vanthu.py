import random
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection, get_active_pet

PET_SPECIES = [
    {"name": "Cửu Vĩ Linh Hồ",   "atk": 120, "def": 80,  "icon": "🦊", "desc": "Linh hồ cửu vĩ, trí tuệ vô song, mị lực vô biên."},
    {"name": "Hỏa Lân Ấu Thú",   "atk": 180, "def": 90,  "icon": "🔥", "desc": "Kỳ Lân chi tử, toàn thân rực lửa tam muội chân hỏa."},
    {"name": "Thanh Loan Tiên Điểu", "atk": 140, "def": 110, "icon": "🦅", "desc": "Điềm lành hạ phàm, tốc độ tựa phong lôi chớp giật."},
    {"name": "Huyền Quy Cổ Thú",  "atk": 80,  "def": 250, "icon": "🐢", "desc": "Mai rùa hóa thạch, phòng ngự vững chắc như sơn nhạc."},
    {"name": "Thái Cổ Chân Long", "atk": 300, "def": 200, "icon": "🐉", "desc": "Đứng đầu thần thú, long uy uy áp vạn linh phủ phục!"}
]

def create_vanthu_embed(user_id: int, user_name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, species, level, atk_bonus, def_bonus, is_active FROM pets WHERE user_id = ?", (user_id,))
    pets = c.fetchall()
    conn.close()

    embed = discord.Embed(
        title=f"🦊 VẠN THÚ CÁC — {user_name}",
        description=(
            "Nơi thu phục và dưỡng dục các loài Linh Thú, Dị Thú thượng cổ.\n"
            "Linh Thú xuất chiến sẽ cộng trực tiếp thuộc tính Chiến Lực cho chủ nhân!"
        ),
        color=0xe67e22
    )

    if not pets:
        embed.add_field(
            name="🐾 Trống Rỗng",
            value="Đạo hữu chưa sở hữu Linh Thú nào! Nhấp nút **🥚 Ấp Trứng Linh Thú (800 LT)** bên dưới để triệu hoán.",
            inline=False
        )
    else:
        for p in pets[:6]:
            pid, pname, pspecies, plevel, patk, pdef, pactive = p
            status = "⚔️ **[ĐANG XUẤT CHIẾN]**" if pactive else "💤 Đang nghỉ"
            embed.add_field(
                name=f"{pname} ({pspecies}) — Cấp {plevel} {status}",
                value=f"🗡️ ATK: `+{patk * plevel:,}` | 🛡️ DEF: `+{pdef * plevel:,}`",
                inline=False
            )

    embed.set_footer(text="Nuôi dưỡng Linh Thú sẽ giúp đạo hữu gia tăng sức mạnh khi Luận Kiếm và Lịch Luyện!")
    return embed

class VanThuView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="🥚 Ấp Trứng Thú (800 LT)", style=discord.ButtonStyle.success)
    async def btn_hatch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/vanthu` để tự mở Vạn Thú Các!", ephemeral=True)

        player = get_player(self.user_id)
        if player[6] < 800:
            return await interaction.response.send_message("❌ Cần **800 Linh Thạch** để mua Trứng Thú quý hiếm!", ephemeral=True)

        spec = random.choice(PET_SPECIES)
        pname = f"{spec['icon']} {spec['name']}"

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - 800 WHERE user_id = ?", (self.user_id,))
        c.execute("""INSERT INTO pets (user_id, name, species, level, atk_bonus, def_bonus, is_active)
                     VALUES (?, ?, ?, 1, ?, ?, 1)""", (self.user_id, pname, spec["name"], spec["atk"], spec["def"]))
        # Đặt các thú khác về nghỉ
        new_pet_id = c.lastrowid
        c.execute("UPDATE pets SET is_active = 0 WHERE user_id = ? AND id != ?", (self.user_id, new_pet_id))
        conn.commit()
        conn.close()

        embed = create_vanthu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(
            f"🎉 Trứng thú nứt ra! Đạo hữu đã ấp thành công **{pname}**!\n"
            f"*{spec['desc']}*\n🗡️ ATK: +{spec['atk']} | 🛡️ DEF: +{spec['def']} (Đã tự động xuất chiến!)",
            ephemeral=True
        )

    @discord.ui.button(label="🥩 Cho Ăn (Tăng Cấp 300 LT)", style=discord.ButtonStyle.primary)
    async def btn_feed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải linh thú của đạo hữu!", ephemeral=True)

        pet = get_active_pet(self.user_id)
        if not pet:
            return await interaction.response.send_message("❌ Đạo hữu chưa có Linh Thú nào xuất chiến!", ephemeral=True)

        player = get_player(self.user_id)
        if player[6] < 300:
            return await interaction.response.send_message("❌ Cần **300 Linh Thạch** để mua Thú Đan bồi bổ!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - 300 WHERE user_id = ?", (self.user_id,))
        c.execute("UPDATE pets SET level = level + 1 WHERE id = ?", (pet[0],))
        conn.commit()
        conn.close()

        embed = create_vanthu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🥩 Linh Thú **{pet[1]}** đã ăn no nê và thăng lên **Cấp {pet[4] + 1}**!", ephemeral=True)

class VanThuCog(commands.Cog, name="Vạn Thú Các"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vanthu", description="Mở Vạn Thú Các — Thu phục, ấp trứng và bồi dưỡng Linh Thú hộ thể")
    async def vanthu(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = create_vanthu_embed(interaction.user.id, interaction.user.display_name)
        view = VanThuView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="vanthu", aliases=["vt", "linhthu", "pet"])
    async def prefix_vanthu(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = create_vanthu_embed(ctx.author.id, ctx.author.display_name)
        view = VanThuView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(VanThuCog(bot))
