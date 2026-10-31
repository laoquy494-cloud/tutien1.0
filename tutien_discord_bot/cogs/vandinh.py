import random
import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS
from database import get_player, get_connection, get_or_create_vandinh, get_equipment_bonus

class VanDinhView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="⚔️ Khiêu Chiến Vượt Tháp", style=discord.ButtonStyle.danger)
    async def btn_climb(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/vandinh`!", ephemeral=True)

        vd = get_or_create_vandinh(self.user_id)
        current_floor = vd[1]
        player = get_player(self.user_id)

        r = REALMS[player[4]]
        eq_atk, eq_def = get_equipment_bonus(self.user_id)
        p_hp = r["hp"]
        p_atk = r["atk"] + eq_atk
        p_def = r["def"] + eq_def

        # Thủ vệ tháp
        e_hp = 300 + current_floor * 250
        e_atk = 20 + current_floor * 25
        e_def = 10 + current_floor * 15

        for _ in range(6):
            dmg_to_e = max(1, int(p_atk * random.uniform(0.9, 1.1) - e_def * 0.2))
            dmg_to_p = max(1, int(e_atk * random.uniform(0.8, 1.1) - p_def * 0.2))
            e_hp -= dmg_to_e
            p_hp -= dmg_to_p
            if e_hp <= 0 or p_hp <= 0:
                break

        won = (e_hp <= 0 and p_hp > 0) or (p_hp >= e_hp)

        conn = get_connection()
        c = conn.cursor()
        if won:
            reward_stone = 150 + current_floor * 50
            reward_exp = 300 + current_floor * 100
            new_floor = current_floor + 1
            c.execute("UPDATE vandinh_tower SET floor = ?, max_floor = MAX(max_floor, ?) WHERE user_id = ?",
                      (new_floor, new_floor, self.user_id))
            c.execute("UPDATE players SET exp = exp + ?, linh_thach = linh_thach + ? WHERE user_id = ?",
                      (reward_exp, reward_stone, self.user_id))
            embed = discord.Embed(
                title=f"🏆 VƯỢT THÀNH CÔNG TẦNG {current_floor} VẤN ĐỈNH PHONG!",
                description=(
                    f"Đạo hữu đã chém ngã Thủ Hộ Giả Tầng {current_floor}!\n\n"
                    f"🎁 **Phần thưởng:** 💎 `+{reward_stone:,}` Linh Thạch | ✨ `+{reward_exp:,}` Linh Khí\n"
                    f"🚀 Cánh cổng bước lên **Tầng {new_floor}** đã mở ra!"
                ),
                color=0xf1c40f
            )
        else:
            embed = discord.Embed(
                title=f"💀 KHIÊU CHIẾN THẤT BẠI TẦNG {current_floor}!",
                description=(
                    f"Thủ Hộ Giả Tầng {current_floor} thực lực quá hung mãnh!\n"
                    f"Hãy tăng cấp Cảnh Giới, học Công Pháp hoặc Rèn Thần Binh rồi quay lại tái chiến!"
                ),
                color=0xc0392b
            )

        conn.commit()
        conn.close()
        await interaction.response.send_message(embed=embed)

class VanDinhCog(commands.Cog, name="Vấn Đỉnh"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vandinh", description="Tháp Vấn Đỉnh — Leo tháp 100 tầng thử thách chiến lực")
    async def vandinh(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        vd = get_or_create_vandinh(interaction.user.id)
        current_floor = vd[1]
        max_floor = vd[2]

        embed = discord.Embed(
            title="⚔️ VẤN ĐỈNH PHONG — CỬU TRÙNG THIÊN THÁP",
            description=(
                "Tháp Cổ Thông Thiên ngự trị giữa biển mây vạn trượng.\n"
                "Mỗi tầng là một trận huyết chiến thử thách đạo tâm và tu vi!\n\n"
                f"🪜 **Tầng hiện tại:** `Tầng {current_floor}`\n"
                f"👑 **Kỷ lục cao nhất:** `Tầng {max_floor}`\n\n"
                "Nhấp nút bên dưới để bắt đầu khiêu chiến tầng tiếp theo!"
            ),
            color=0x9b59b6
        )
        embed.set_footer(text="Vấn đỉnh thiên hạ — duy ngã độc tôn!")
        view = VanDinhView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="vandinh", aliases=["vd", "leothap", "thap"])
    async def prefix_vandinh(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        vd = get_or_create_vandinh(ctx.author.id)
        current_floor = vd[1]
        max_floor = vd[2]

        embed = discord.Embed(
            title="⚔️ VẤN ĐỈNH PHONG — CỬU TRÙNG THIÊN THÁP",
            description=(
                "Tháp Cổ Thông Thiên ngự trị giữa biển mây vạn trượng.\n"
                "Mỗi tầng là một trận huyết chiến thử thách đạo tâm và tu vi!\n\n"
                f"🪜 **Tầng hiện tại:** `Tầng {current_floor}`\n"
                f"👑 **Kỷ lục cao nhất:** `Tầng {max_floor}`\n\n"
                "Nhấp nút bên dưới để bắt đầu khiêu chiến tầng tiếp theo!"
            ),
            color=0x9b59b6
        )
        embed.set_footer(text="Vấn đỉnh thiên hạ — duy ngã độc tôn!")
        view = VanDinhView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(VanDinhCog(bot))
