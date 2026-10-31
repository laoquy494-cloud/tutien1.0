import discord
from discord import app_commands
from discord.ext import commands
from database import (
    get_player, get_connection,
    get_today_str, get_or_create_attendance
)

def create_phucloi_embed(user_id: int, user_name: str):
    att = get_or_create_attendance(user_id)
    # att: (user_id, last_claim_date, streak, claimed_starter)
    today = get_today_str()
    has_claimed_today = (att[1] == today)
    streak = att[2]
    claimed_starter = att[3]

    embed = discord.Embed(
        title="🎁 PHÚC LỢI THIÊN ĐẠO — NHẬN THƯỞNG MỖI NGÀY",
        description=(
            f"Chào mừng đạo hữu **{user_name}** đến với sảnh đường Phúc Lợi!\n"
            f"Điểm danh mỗi ngày để nhận tài nguyên tu luyện và quà tân thủ."
        ),
        color=0xf1c40f
    )
    embed.add_field(
        name="📅 Điểm Danh Hàng Ngày",
        value=f"Trạng thái: {'✅ **Đã nhận hôm nay**' if has_claimed_today else '🔴 **Chưa điểm danh**'}\nChuỗi điểm danh: `🔥 {streak} ngày liên tục`\nPhần thưởng: `+{500 + streak * 100:,}` Linh Thạch + `+800` Linh Khí",
        inline=False
    )
    embed.add_field(
        name="🎉 Quà Tân Thủ Nhập Đạo",
        value=f"Trạng thái: {'✅ Đã nhận' if claimed_starter else '🎁 **Sẵn sàng nhận** (`1,000` Linh Thạch + `1,500` Linh Khí)'}",
        inline=False
    )
    embed.set_footer(text="Reset lúc 00:00 (GMT+7) mỗi ngày")
    return embed

class PhucLoiView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="📅 Điểm Danh Ngay", style=discord.ButtonStyle.success)
    async def btn_claim_daily(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải phúc lợi của đạo hữu!", ephemeral=True)

        att = get_or_create_attendance(self.user_id)
        today = get_today_str()
        if att[1] == today:
            return await interaction.response.send_message("⚠️ Hôm nay đạo hữu đã điểm danh rồi! Hãy quay lại vào ngày mai.", ephemeral=True)

        new_streak = att[2] + 1
        stone_reward = 500 + new_streak * 100
        exp_reward = 800

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE attendance SET last_claim_date = ?, streak = ? WHERE user_id = ?", (today, new_streak, self.user_id))
        c.execute("UPDATE players SET linh_thach = linh_thach + ?, exp = exp + ? WHERE user_id = ?",
                  (stone_reward, exp_reward, self.user_id))
        conn.commit()
        conn.close()

        embed = create_phucloi_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(
            f"🎉 **Điểm danh thành công (Chuỗi {new_streak} ngày)!**\n"
            f"💰 Nhận: **+{stone_reward:,} Linh Thạch** | ✨ **+{exp_reward:,} Linh Khí**",
            ephemeral=True
        )

    @discord.ui.button(label="🎁 Quà Tân Thủ", style=discord.ButtonStyle.primary)
    async def btn_claim_starter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải phúc lợi của đạo hữu!", ephemeral=True)

        att = get_or_create_attendance(self.user_id)
        if att[3]:
            return await interaction.response.send_message("⚠️ Đạo hữu đã nhận Quà Tân Thủ rồi!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE attendance SET claimed_starter = 1 WHERE user_id = ?", (self.user_id,))
        c.execute("UPDATE players SET linh_thach = linh_thach + 1000, exp = exp + 1500 WHERE user_id = ?", (self.user_id,))
        conn.commit()
        conn.close()

        embed = create_phucloi_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(
            "🎁 **Nhận Quà Tân Thủ thành công!**\n💰 **+1,000 Linh Thạch** | ✨ **+1,500 Linh Khí**!\nChúc đạo hữu sớm đắc đạo phi thăng!",
            ephemeral=True
        )

class PhucLoiCog(commands.Cog, name="Phúc Lợi"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="phucloi", description="Nhận phúc lợi Thiên Đạo — Điểm danh mỗi ngày & Quà tân thủ")
    async def slash_phucloi(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = create_phucloi_embed(interaction.user.id, interaction.user.display_name)
        view = PhucLoiView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="diemdanh", aliases=["phucloi"])
    async def prefix_diemdanh(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send("❌ Hãy dùng `t nhapdao` trước!")

        embed = create_phucloi_embed(ctx.author.id, ctx.author.display_name)
        view = PhucLoiView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(PhucLoiCog(bot))
