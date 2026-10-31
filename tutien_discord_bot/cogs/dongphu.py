import time
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection, get_or_create_dongphu

def create_dongphu_embed(user_id: int, user_name: str):
    player = get_player(user_id)
    dp = get_or_create_dongphu(user_id)
    # dp: (user_id, level_tran, level_vuon, last_harvest, last_spring)
    now = int(time.time())
    
    tran_lvl = dp[1]
    vuon_lvl = dp[2]
    last_h = dp[3]
    last_s = dp[4]

    spring_ready = (now - last_s) >= 3600
    harvest_ready = (now - last_h) >= 7200

    s_status = "✅ Có thể múc nước" if spring_ready else f"⏳ Đang ngưng tụ ({max(1, (3600 - (now - last_s)) // 60)} phút)"
    h_status = "✅ Dược thảo đã chín" if harvest_ready else f"⏳ Đang sinh trưởng ({max(1, (7200 - (now - last_h)) // 60)} phút)"

    embed = discord.Embed(
        title=f"🌌 ĐỘNG PHỦ TIÊN GIA — {user_name}",
        description=(
            "Nơi bế quan tu luyện, linh khí nồng đậm u tịch, cách biệt hồng trần cuồn cuộn.\n"
            "Chăm sóc các công trình để nhận thêm linh khí và tài nguyên mỗi ngày!"
        ),
        color=0x1abc9c
    )
    embed.add_field(name="🌀 Tụ Linh Đại Trận", value=f"Cấp độ: **Cấp {tran_lvl}**\nBuff tốc độ hấp thụ: `+{tran_lvl * 5}%` LK", inline=True)
    embed.add_field(name="💧 Cổ Linh Tuyền", value=f"Trạng thái: **{s_status}**\n*Mỗi giờ ngưng tụ 1 bình Linh Dịch*", inline=True)
    embed.add_field(name="🌿 Dược Điền Linh Thảo", value=f"Cấp độ: **Cấp {vuon_lvl}**\nTrạng thái: **{h_status}**", inline=False)
    embed.set_footer(text="Dùng các nút bên dưới để thu hoạch hoặc nâng cấp Động Phủ")
    return embed

class DongPhuView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây là động phủ của đạo hữu khác!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="💧 Múc Linh Tuyền", style=discord.ButtonStyle.primary, row=0)
    async def btn_spring(self, interaction: discord.Interaction, button: discord.ui.Button):
        dp = get_or_create_dongphu(self.user_id)
        now = int(time.time())
        if now - dp[4] < 3600:
            rem = (3600 - (now - dp[4])) // 60
            return await interaction.response.send_message(f"⏳ Cổ Linh Tuyền còn cần ngưng tụ thêm **{rem} phút**!", ephemeral=True)

        exp_gain = 400 * dp[1]
        stone_gain = 100 * dp[1]

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE dong_phu SET last_spring = ? WHERE user_id = ?", (now, self.user_id))
        c.execute("UPDATE players SET exp = exp + ?, linh_thach = linh_thach + ? WHERE user_id = ?",
                  (exp_gain, stone_gain, self.user_id))
        conn.commit()
        conn.close()

        embed = create_dongphu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"💧 Uống một ngụm Linh Tuyền tinh khiết! Nhận **+{exp_gain:,} Linh Khí** & **+{stone_gain:,} Linh Thạch**!", ephemeral=True)

    @discord.ui.button(label="🌿 Thu Hoạch Dược Điền", style=discord.ButtonStyle.success, row=0)
    async def btn_harvest(self, interaction: discord.Interaction, button: discord.ui.Button):
        dp = get_or_create_dongphu(self.user_id)
        now = int(time.time())
        if now - dp[3] < 7200:
            rem = (7200 - (now - dp[3])) // 60
            return await interaction.response.send_message(f"⏳ Dược thảo chưa chín! Cần thêm **{rem} phút**!", ephemeral=True)

        stone_gain = 350 * dp[2]
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE dong_phu SET last_harvest = ? WHERE user_id = ?", (now, self.user_id))
        c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (stone_gain, self.user_id))
        conn.commit()
        conn.close()

        embed = create_dongphu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🌿 Thu hoạch một mẻ Cổ Linh Chi! Bán thu được **+{stone_gain:,} Linh Thạch**!", ephemeral=True)

    @discord.ui.button(label="🌀 Nâng Cấp Tụ Linh Trận", style=discord.ButtonStyle.secondary, row=1)
    async def btn_upgrade_tran(self, interaction: discord.Interaction, button: discord.ui.Button):
        dp = get_or_create_dongphu(self.user_id)
        player = get_player(self.user_id)
        cost = dp[1] * 800
        if player[6] < cost:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần **{cost:,} Linh Thạch** để nâng cấp trận pháp.", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (cost, self.user_id))
        c.execute("UPDATE dong_phu SET level_tran = level_tran + 1 WHERE user_id = ?", (self.user_id,))
        conn.commit()
        conn.close()

        embed = create_dongphu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🌀 Tụ Linh Trận đã thăng lên **Cấp {dp[1] + 1}**! Linh khí bế quan tăng thêm!", ephemeral=True)

class DongPhuCog(commands.Cog, name="Động Phủ"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dongphu", description="Mở Động Phủ tu tiên — Linh Tuyền, Dược Điền, Tụ Linh Trận")
    async def slash_dongphu(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = create_dongphu_embed(interaction.user.id, interaction.user.display_name)
        view = DongPhuView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="dongphu", aliases=["dp"])
    async def prefix_dongphu(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send("❌ Hãy dùng `t nhapdao` trước!")

        embed = create_dongphu_embed(ctx.author.id, ctx.author.display_name)
        view = DongPhuView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(DongPhuCog(bot))
