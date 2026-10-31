import random
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection

DICE_EMOJIS = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

def roll_dice():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    d3 = random.randint(1, 6)
    total = d1 + d2 + d3
    is_triple = (d1 == d2 == d3)
    result_type = "Tài" if total >= 11 else "Xỉu"
    return d1, d2, d3, total, is_triple, result_type

class TaiXiuModal(discord.ui.Modal, title="🎲 Đổ Phường — Đặt Cược Tài Xỉu"):
    def __init__(self, choice: str):
        super().__init__()
        self.choice = choice # "Tài" hoặc "Xỉu"
        self.bet_amount = discord.ui.TextInput(
            label=f"Nhập số Linh Thạch cược ({choice})",
            placeholder="Ví dụ: 100",
            min_length=1,
            max_length=8
        )
        self.add_item(self.bet_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.bet_amount.value.strip())
            if amount < 50:
                return await interaction.response.send_message("❌ Mức cược tối thiểu là **50 Linh Thạch**!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Vui lòng nhập số nguyên hợp lệ!", ephemeral=True)

        player = get_player(interaction.user.id)
        if not player or player[6] < amount:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Hiện có: `{player[6] if player else 0:,}`.", ephemeral=True)

        d1, d2, d3, total, is_triple, outcome = roll_dice()
        won = (self.choice == outcome) and not is_triple

        conn = get_connection()
        c = conn.cursor()

        if won:
            gain = amount
            c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (gain, interaction.user.id))
            title = "🎉 CHIẾN THẮNG — TIỀN VÀO NHƯ NƯỚC!"
            color = 0x2ecc71
            result_msg = f"🏆 Đạo hữu đoán đúng **{outcome}**! Thắng được **+{gain:,} Linh Thạch**!"
        elif is_triple:
            c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (amount, interaction.user.id))
            title = "💥 BÃO XUẤT HIỆN — NHÀ CÁI ĂN HẾT!"
            color = 0xe74c3c
            result_msg = f"⚡ Xuất hiện Tam Hoa Tụ Đỉnh ({d1}-{d2}-{d3})! Thua trắng **-{amount:,} Linh Thạch**!"
        else:
            c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (amount, interaction.user.id))
            title = "💸 THUA CƯỢC — VẬN MAY CHƯA TỚI!"
            color = 0x95a5a6
            result_msg = f"📉 Kết quả là **{outcome}** ({total} điểm). Mất **-{amount:,} Linh Thạch**!"

        conn.commit()
        conn.close()

        dice_display = f"{DICE_EMOJIS[d1]} `{d1}` + {DICE_EMOJIS[d2]} `{d2}` + {DICE_EMOJIS[d3]} `{d3}` = **{total} điểm**"
        new_player = get_player(interaction.user.id)

        embed = discord.Embed(title=title, description=result_msg, color=color)
        embed.add_field(name="🎲 Xúc Xắc", value=dice_display, inline=False)
        embed.add_field(name="🎯 Lựa chọn của bạn", value=f"**{self.choice}**", inline=True)
        embed.add_field(name="💰 Số Dư Mới", value=f"`{new_player[6]:,}` Linh Thạch", inline=True)
        embed.set_footer(text="Đổ Phường mua vui — chớ nên tham lam sa đà!")
        await interaction.response.send_message(embed=embed)

class DoPhuongView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="🔴 Cược TÀI (11 - 17)", style=discord.ButtonStyle.danger)
    async def btn_tai(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/dophuong` để tự mở bàn của mình!", ephemeral=True)
        await interaction.response.send_modal(TaiXiuModal("Tài"))

    @discord.ui.button(label="⚪ Cược XỈU (4 - 10)", style=discord.ButtonStyle.secondary)
    async def btn_xiu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/dophuong` để tự mở bàn của mình!", ephemeral=True)
        await interaction.response.send_modal(TaiXiuModal("Xỉu"))

class DoPhuongCog(commands.Cog, name="Đổ Phường"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dophuong", description="Vào Đổ Phường — Lắc xúc xắc Tài Xỉu cược Linh Thạch")
    async def dophuong(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = discord.Embed(
            title="🎲 THIÊN PHONG ĐỔ PHƯỜNG — TÀI XỈU TIÊN GIA",
            description=(
                f"💎 Túi trữ vật của đạo hữu: **`{player[6]:,}` Linh Thạch**\n\n"
                "**Luật chơi:**\n"
                "• 🔴 **TÀI:** Tổng điểm từ **11 đến 17**\n"
                "• ⚪ **XỈU:** Tổng điểm từ **4 đến 10**\n"
                "• 💥 **Bão (3 xúc xắc giống nhau):** Nhà cái ăn trọn\n"
                "• Tỷ lệ trả thưởng: **1 ăn 2** (Thắng nhận lại vốn + thưởng bằng vốn)\n\n"
                "*Nhấp nút bên dưới để chọn cửa cược!*"
            ),
            color=0x9b59b6
        )
        embed.set_footer(text="Cờ bạc dưỡng thần — vui vẻ là chính, chớ dốc hết gia tài!")
        view = DoPhuongView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="dophuong", aliases=["taixiu", "tx", "cuoc"])
    async def prefix_dophuong(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = discord.Embed(
            title="🎲 THIÊN PHONG ĐỔ PHƯỜNG — TÀI XỈU TIÊN GIA",
            description=(
                f"💎 Túi trữ vật của đạo hữu: **`{player[6]:,}` Linh Thạch**\n\n"
                "**Luật chơi:**\n"
                "• 🔴 **TÀI:** Tổng điểm từ **11 đến 17**\n"
                "• ⚪ **XỈU:** Tổng điểm từ **4 đến 10**\n"
                "• 💥 **Bão (3 xúc xắc giống nhau):** Nhà cái ăn trọn\n"
                "• Tỷ lệ trả thưởng: **1 ăn 2** (Thắng nhận lại vốn + thưởng bằng vốn)\n\n"
                "*Nhấp nút bên dưới để chọn cửa cược!*"
            ),
            color=0x9b59b6
        )
        embed.set_footer(text="Cờ bạc dưỡng thần — vui vẻ là chính, chớ dốc hết gia tài!")
        view = DoPhuongView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(DoPhuongCog(bot))
