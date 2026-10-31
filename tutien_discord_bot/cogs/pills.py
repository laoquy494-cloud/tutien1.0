import time
import discord
from discord import app_commands
from discord.ext import commands
from config import DAN_DUOC, SPIRIT_ROOTS
from database import get_player, get_connection, add_quest_progress

def create_pills_shop_embed(player):
    embed = discord.Embed(
        title="🏪 TIỆM ĐAN DƯỢC — THIÊN PHONG DƯỢC ĐIẾM",
        description=(
            f"💎 Túi trữ vật: **`{player[6]:,}` Linh Thạch**\n"
            f"🧬 Linh căn hiện tại: **{player[2]}** (`{player[3]}x`)\n\n"
            "Chọn đan dược muốn mua bên dưới:"
        ),
        color=0x2ecc71
    )
    for i, d in enumerate(DAN_DUOC):
        embed.add_field(
            name=f"{d['icon']} {i+1}. {d['name']} — `{d['cost']:,}` Linh Thạch",
            value=d["desc"],
            inline=False
        )
    return embed

class DanDuocShopView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        options = [
            discord.SelectOption(
                label=f"{d['icon']} {d['name']} — {d['cost']} Linh Thạch",
                value=str(i),
                description=d["desc"][:100]
            )
            for i, d in enumerate(DAN_DUOC)
        ]
        select = discord.ui.Select(placeholder="Chọn Đan Dược muốn mua...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Không phải túi trữ vật của đạo hữu!", ephemeral=True)
        idx = int(interaction.data["values"][0])
        dan = DAN_DUOC[idx]
        player = get_player(self.user_id)
        if not player:
            return await interaction.response.send_message("❌ Nhân vật chưa khởi tạo! Dùng `/nhapdao`.", ephemeral=True)
        if player[6] < dan["cost"]:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần `{dan['cost']:,}`.", ephemeral=True)

        if dan["effect"] == "upgrade_root":
            cur_idx = -1
            for idx_r, r in enumerate(SPIRIT_ROOTS):
                if r["name"] == player[2] or abs(r["speed"] - player[3]) < 0.05:
                    cur_idx = idx_r
                    break
            if cur_idx == -1:
                cur_idx = 0

            if cur_idx >= len(SPIRIT_ROOTS) - 1:
                return await interaction.response.send_message(
                    f"⚠️ Linh căn của đạo hữu đã đạt cảnh giới tối cao **{player[2]}** (`{player[3]}x`), không thể tẩy tủy thăng cấp thêm!",
                    ephemeral=True
                )

            next_root = SPIRIT_ROOTS[cur_idx + 1]
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET linh_can = ?, speed = ?, linh_thach = linh_thach - ? WHERE user_id = ?",
                      (next_root["name"], next_root["speed"], dan["cost"], self.user_id))
            conn.commit()
            conn.close()
            add_quest_progress(self.user_id, "q_pills")
            return await interaction.response.send_message(
                f"{dan['icon']} Đạo hữu đã phục dụng **{dan['name']}**!\n"
                f"🎉 **TẨY KINH PHẠT TỦY — LINH CĂN THĂNG CẤP THÀNH CÔNG!**\n"
                f"🧬 Phẩm giai mới: **{next_root['name']}**\n"
                f"⚡ Tốc độ tu vi bế quan vĩnh viễn: `{player[3]}x` ➔ **`{next_root['speed']}x`**!",
                ephemeral=True
            )

        elif dan["effect"] == "max_root":
            max_root = SPIRIT_ROOTS[-1]
            if player[2] == max_root["name"] or player[3] >= max_root["speed"]:
                return await interaction.response.send_message(
                    f"⚠️ Đạo hữu đã sở hữu **{max_root['name']}** (`{max_root['speed']}x`) tối cao, không cần dùng Bổ Thiên Đan!",
                    ephemeral=True
                )

            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET linh_can = ?, speed = ?, linh_thach = linh_thach - ? WHERE user_id = ?",
                      (max_root["name"], max_root["speed"], dan["cost"], self.user_id))
            conn.commit()
            conn.close()
            add_quest_progress(self.user_id, "q_pills")
            return await interaction.response.send_message(
                f"{dan['icon']} Đạo hữu đã phục dụng **{dan['name']}**!\n"
                f"✨ **NGHỊCH THIÊN CẢI MỆNH THÀNH CÔNG!**\n"
                f"🔮 Hào quang vạn trượng! Đạo căn thăng hoa thành **{max_root['name']}**!\n"
                f"⚡ Tốc độ tu vi bế quan vĩnh viễn: `{player[3]}x` ➔ **`{max_root['speed']}x`**!",
                ephemeral=True
            )

        elif dan["effect"] == "bonus_rate":
            current_bonus = player[7]
            if dan.get("max_stack") and current_bonus >= dan["max_stack"]:
                return await interaction.response.send_message("⚠️ Đã đạt tối đa hiệu lực đan dược cho cảnh giới này!", ephemeral=True)
            new_bonus = min(dan["max_stack"], current_bonus + dan["value"])
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET bonus_rate = ?, linh_thach = linh_thach - ? WHERE user_id = ?",
                      (new_bonus, dan["cost"], self.user_id))
            conn.commit()
            conn.close()
            add_quest_progress(self.user_id, "q_pills")
            return await interaction.response.send_message(
                f"{dan['icon']} Đạo hữu đã phục dụng **{dan['name']}**!\n✅ Tỷ lệ Độ Kiếp tăng thêm **+{int(dan['value']*100)}%**!",
                ephemeral=True
            )

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (dan["cost"], self.user_id))
        msg = f"{dan['icon']} Đạo hữu đã phục dụng **{dan['name']}**!\n"

        if dan["effect"] == "exp_boost":
            c.execute("UPDATE players SET exp = exp + ? WHERE user_id = ?", (int(dan["value"]), self.user_id))
            msg += f"✅ Thu ngay **+{int(dan['value']):,} Linh Khí**!"
        elif dan["effect"] == "linh_thach":
            c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (int(dan["value"]), self.user_id))
            msg += f"✅ Thu ngay **+{int(dan['value']):,} Linh Thạch**!"
        elif dan["effect"] == "speed_temp":
            boost_end = int(time.time()) + 3600
            c.execute("UPDATE players SET speed_boost = speed_boost + ?, speed_boost_end = ? WHERE user_id = ?",
                      (dan["value"], boost_end, self.user_id))
            msg += f"✅ Tốc độ tu luyện tăng **+{dan['value']}x** trong 1 giờ!"

        conn.commit()
        conn.close()
        add_quest_progress(self.user_id, "q_pills")
        await interaction.response.send_message(msg, ephemeral=True)

class PillsCog(commands.Cog, name="Đan Dược"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="danduoc", description="Mở Thiên Phong Dược Điếm — mua đan dược hỗ trợ tu hành")
    async def danduoc(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = create_pills_shop_embed(player)
        view = DanDuocShopView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="danduoc", aliases=["thuoc", "shopdan", "duocdiem", "dan"])
    async def prefix_danduoc(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = create_pills_shop_embed(player)
        view = DanDuocShopView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(PillsCog(bot))
