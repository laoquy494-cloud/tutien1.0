import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS, CONG_PHAP
from database import (
    get_player, get_connection,
    get_equipment_bonus, get_tong_mon
)

class StatsCog(commands.Cog, name="Thống Kê"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="thongke", description="Xem thống kê tu luyện chi tiết của bản thân")
    async def thongke(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        uid, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate = player[:8]
        cong_phap_idx = player[10]
        tong_id = player[13]
        spouse_id = player[14]
        pvp_wins = player[20]
        pvp_losses = player[21]
        total_exp = player[22]

        cp = CONG_PHAP[cong_phap_idx]
        r = REALMS[realm_idx]
        eq_atk, eq_def = get_equipment_bonus(uid)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM equipment WHERE user_id = ?", (uid,))
        eq_count = c.fetchone()[0]
        conn.close()

        spouse = get_player(spouse_id) if spouse_id else None
        tong = get_tong_mon(tong_id) if tong_id else None
        total_pvp = pvp_wins + pvp_losses
        winrate = int(pvp_wins / total_pvp * 100) if total_pvp > 0 else 0

        embed = discord.Embed(title=f"📊 THỐNG KÊ TU TIÊN — {name}", color=0x2c3e50)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🏔️ Cảnh Giới", value=f"{r['icon']} **{r['name']}**", inline=True)
        embed.add_field(name="🧬 Linh Căn", value=f"`{speed}x` — *{linh_can}*", inline=True)
        embed.add_field(name="📖 Công Pháp", value=f"{cp['icon']} **{cp['name']}**", inline=True)
        embed.add_field(name="⚔️ PvP", value=f"🏆 `{pvp_wins}` thắng / 💀 `{pvp_losses}` thua\nTỷ lệ thắng: `{winrate}%`", inline=True)
        embed.add_field(name="💎 Tài Sản", value=f"`{linh_thach:,}` Linh Thạch", inline=True)
        embed.add_field(name="📦 Trang Bị", value=f"`{eq_count}` món | 🗡️+`{eq_atk:,}` 🛡️+`{eq_def:,}`", inline=True)
        embed.add_field(name="✨ Tổng Tu Vi", value=f"`{total_exp:,}` Linh Khí đã thu thập", inline=True)
        embed.add_field(name="💑 Đạo Lữ", value=f"**{spouse[1]}**" if spouse else "*Chưa kết bái*", inline=True)
        embed.add_field(name="🏯 Tông Môn", value=f"**{tong[1]}**" if tong else "*Chưa gia nhập*", inline=True)
        embed.set_footer(text="Vạn lý tu tiên — bắt đầu từ một bước chân.")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="thongke", aliases=["tk", "hethong"])
    async def prefix_thongke(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        uid, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate = player[:8]
        cong_phap_idx = player[10]
        tong_id = player[13]
        spouse_id = player[14]
        pvp_wins = player[20]
        pvp_losses = player[21]
        total_exp = player[22]

        cp = CONG_PHAP[cong_phap_idx]
        r = REALMS[realm_idx]
        eq_atk, eq_def = get_equipment_bonus(uid)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM equipment WHERE user_id = ?", (uid,))
        eq_count = c.fetchone()[0]
        conn.close()

        spouse = get_player(spouse_id) if spouse_id else None
        tong = get_tong_mon(tong_id) if tong_id else None
        total_pvp = pvp_wins + pvp_losses
        winrate = int(pvp_wins / total_pvp * 100) if total_pvp > 0 else 0

        embed = discord.Embed(title=f"📊 THỐNG KÊ TU TIÊN — {name}", color=0x2c3e50)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="🏔️ Cảnh Giới", value=f"{r['icon']} **{r['name']}**", inline=True)
        embed.add_field(name="🧬 Linh Căn", value=f"`{speed}x` — *{linh_can}*", inline=True)
        embed.add_field(name="📖 Công Pháp", value=f"{cp['icon']} **{cp['name']}**", inline=True)
        embed.add_field(name="⚔️ PvP", value=f"🏆 `{pvp_wins}` thắng / 💀 `{pvp_losses}` thua\nTỷ lệ thắng: `{winrate}%`", inline=True)
        embed.add_field(name="💎 Tài Sản", value=f"`{linh_thach:,}` Linh Thạch", inline=True)
        embed.add_field(name="📦 Trang Bị", value=f"`{eq_count}` món | 🗡️+`{eq_atk:,}` 🛡️+`{eq_def:,}`", inline=True)
        embed.add_field(name="✨ Tổng Tu Vi", value=f"`{total_exp:,}` Linh Khí đã thu thập", inline=True)
        embed.add_field(name="💑 Đạo Lữ", value=f"**{spouse[1]}**" if spouse else "*Chưa kết bái*", inline=True)
        embed.add_field(name="🏯 Tông Môn", value=f"**{tong[1]}**" if tong else "*Chưa gia nhập*", inline=True)
        embed.set_footer(text="Vạn lý tu tiên — bắt đầu từ một bước chân.")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))
