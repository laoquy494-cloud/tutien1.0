import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS
from database import get_connection

class LeaderboardCog(commands.Cog, name="Bảng Xếp Hạng"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="thienbang", description="Xem Bảng Xếp Hạng Thiên Bảng — Top 10 Cường Giả Tu Tiên Giới")
    async def thienbang(self, interaction: discord.Interaction):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""SELECT name, realm_idx, exp, linh_can, pvp_wins, total_exp_gained
                     FROM players
                     ORDER BY realm_idx DESC, exp DESC
                     LIMIT 10""")
        rows = c.fetchall()
        conn.close()

        if not rows:
            return await interaction.response.send_message("📜 Thiên Bảng hiện tại vẫn còn trống!", ephemeral=True)

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        lines = []
        for idx, (name, realm_idx, exp, linh_can, pvp_wins, total_exp) in enumerate(rows):
            realm = REALMS[realm_idx]
            lines.append(
                f"{medals[idx]} **{name}** — {realm['icon']} `{realm['name']}`\n"
                f"╰┈➤ Tu vi: `{exp:,}` LK | 🏆 PvP: `{pvp_wins}` thắng | *{linh_can}*"
            )

        embed = discord.Embed(
            title="🏆 THIÊN ĐẠO KIM BẢNG — TOP 10 CƯỜNG GIẢ 🏆",
            description="\n\n".join(lines),
            color=0xe67e22
        )
        embed.set_footer(text="Kim Bảng đề danh — danh chấn thiên hạ, vạn người kính ngưỡng!")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="thienbang", aliases=["bxh", "top", "bangxephang"])
    async def prefix_thienbang(self, ctx: commands.Context):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""SELECT name, realm_idx, exp, linh_can, pvp_wins, total_exp_gained
                     FROM players
                     ORDER BY realm_idx DESC, exp DESC
                     LIMIT 10""")
        rows = c.fetchall()
        conn.close()

        if not rows:
            return await ctx.send("📜 Thiên Bảng hiện tại vẫn còn trống!")

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        lines = []
        for idx, (name, realm_idx, exp, linh_can, pvp_wins, total_exp) in enumerate(rows):
            realm = REALMS[realm_idx]
            lines.append(
                f"{medals[idx]} **{name}** — {realm['icon']} `{realm['name']}`\n"
                f"╰┈➤ Tu vi: `{exp:,}` LK | 🏆 PvP: `{pvp_wins}` thắng | *{linh_can}*"
            )

        embed = discord.Embed(
            title="🏆 THIÊN ĐẠO KIM BẢNG — TOP 10 CƯỜNG GIẢ 🏆",
            description="\n\n".join(lines),
            color=0xe67e22
        )
        embed.set_footer(text="Kim Bảng đề danh — danh chấn thiên hạ, vạn người kính ngưỡng!")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardCog(bot))
