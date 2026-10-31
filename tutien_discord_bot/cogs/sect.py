import time
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS
from database import get_player, get_connection, get_tong_mon

class SectCog(commands.Cog, name="Tông Môn"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lapmon", description="Lập Tông Môn — cần Trúc Cơ Sơ Kỳ và 2,000 Linh Thạch")
    @app_commands.describe(ten_mon="Tên tông môn muốn thành lập")
    async def lapmon(self, interaction: discord.Interaction, ten_mon: str):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        if player[4] < 5:
            return await interaction.response.send_message("❌ Phải đạt **Trúc Cơ - Sơ Kỳ** mới được lập tông môn!", ephemeral=True)
        if player[13]:
            return await interaction.response.send_message("❌ Đạo hữu đã thuộc một tông môn! Dùng `/roimon` trước.", ephemeral=True)
        if player[6] < 2000:
            return await interaction.response.send_message("❌ Lập tông cần **2,000 Linh Thạch**!", ephemeral=True)
        if len(ten_mon) > 30:
            return await interaction.response.send_message("❌ Tên tông môn quá dài (tối đa 30 ký tự)!", ephemeral=True)

        try:
            conn = get_connection()
            c = conn.cursor()
            now = int(time.time())
            c.execute("INSERT INTO tong_mon (name, leader_id, linh_thach, created_at) VALUES (?, ?, 0, ?)",
                      (ten_mon, interaction.user.id, now))
            tong_id = c.lastrowid
            c.execute("UPDATE players SET tong_mon_id = ?, linh_thach = linh_thach - 2000 WHERE user_id = ?",
                      (tong_id, interaction.user.id))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            return await interaction.response.send_message("❌ Tên tông môn này đã được sử dụng!", ephemeral=True)

        embed = discord.Embed(
            title="🏯 TÔNG MÔN ĐÃ THÀNH LẬP!",
            description=(
                f"**Chưởng Môn {player[1]}** đã khai môn lập phái — **{ten_mon}** chào đời!\n\n"
                f"Chiêu mộ đệ tử bằng cách chia sẻ lệnh `/giamon {ten_mon}`.\n"
                f"Quản lý tông môn qua `/tongmon`."
            ),
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="giamon", description="Gia nhập một Tông Môn")
    @app_commands.describe(ten_mon="Tên tông môn muốn gia nhập")
    async def giamon(self, interaction: discord.Interaction, ten_mon: str):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        if player[13]:
            return await interaction.response.send_message("❌ Đạo hữu đã thuộc tông môn! Dùng `/roimon` để rời đi trước.", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tong_mon WHERE name = ?", (ten_mon,))
        tm = c.fetchone()
        if not tm:
            conn.close()
            return await interaction.response.send_message(f"❌ Không tìm thấy tông môn **{ten_mon}**!", ephemeral=True)

        c.execute("UPDATE players SET tong_mon_id = ? WHERE user_id = ?", (tm[0], interaction.user.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🏯 GIA NHẬP TÔNG MÔN THÀNH CÔNG!",
            description=f"Đạo hữu **{player[1]}** đã chính thức gia nhập **{tm[1]}**!\nCùng sư môn chinh phục đỉnh cao thiên đạo!",
            color=0xe74c3c
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tongmon", description="Xem thông tin Tông Môn của bạn")
    async def tongmon(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        if not player[13]:
            return await interaction.response.send_message("❌ Chưa gia nhập tông môn nào! Dùng `/giamon` hoặc `/lapmon`.", ephemeral=True)

        tm = get_tong_mon(player[13])
        if not tm:
            return await interaction.response.send_message("❌ Tông môn không tồn tại!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name, realm_idx, pvp_wins FROM players WHERE tong_mon_id = ? ORDER BY realm_idx DESC, exp DESC", (tm[0],))
        members = c.fetchall()
        conn.close()

        leader = get_player(tm[2])
        member_lines = []
        for i, (mname, mrealm, mwins) in enumerate(members[:15]):
            prefix = "👑 " if leader and leader[1] == mname else f"{i+1}. "
            member_lines.append(f"{prefix}**{mname}** — `{REALMS[mrealm]['name']}` | 🏆 `{mwins}`")

        embed = discord.Embed(title=f"🏯 {tm[1]}", description=tm[3] or "*Tông môn chưa có miêu tả.*", color=0xe74c3c)
        embed.add_field(name="👑 Chưởng Môn", value=leader[1] if leader else "Không rõ", inline=True)
        embed.add_field(name="👥 Số Đệ Tử", value=f"`{len(members)}` người", inline=True)
        embed.add_field(name="📋 Thành Viên", value="\n".join(member_lines) or "Chưa có thành viên.", inline=False)
        embed.set_footer(text=f"Tông Môn #{tm[0]}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roimon", description="Rời khỏi Tông Môn hiện tại hoặc giải tán tông môn (nếu là Chưởng Môn)")
    async def roimon(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player or not player[13]:
            return await interaction.response.send_message("❌ Chưa gia nhập tông môn nào!", ephemeral=True)

        tm = get_tong_mon(player[13])
        if tm and tm[2] == interaction.user.id:
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET tong_mon_id = 0 WHERE tong_mon_id = ?", (tm[0],))
            c.execute("DELETE FROM tong_mon WHERE id = ?", (tm[0],))
            conn.commit()
            conn.close()
            return await interaction.response.send_message(
                f"🏯 Chưởng Môn đã giải tán **{tm[1]}**. Toàn bộ đệ tử đã được thả ra.", ephemeral=True
            )

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET tong_mon_id = 0 WHERE user_id = ?", (interaction.user.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message(
            f"🚪 Đạo hữu đã rời khỏi **{tm[1] if tm else 'tông môn'}**.", ephemeral=True
        )

    @commands.command(name="lapmon")
    async def prefix_lapmon(self, ctx: commands.Context, *, ten_mon: str = None):
        if not ten_mon:
            return await ctx.send(f"⚠️ Cách dùng: `{ctx.prefix}lapmon <tên_tông_môn>` (VD: `{ctx.prefix}lapmon Tiêu Dao Phái`)")

        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        if player[4] < 5:
            return await ctx.send("❌ Phải đạt **Trúc Cơ - Sơ Kỳ** mới được lập tông môn!")
        if player[13]:
            return await ctx.send(f"❌ Đạo hữu đã thuộc một tông môn! Dùng `{ctx.prefix}roimon` trước.")
        if player[6] < 2000:
            return await ctx.send("❌ Lập tông cần **2,000 Linh Thạch**!")
        if len(ten_mon) > 30:
            return await ctx.send("❌ Tên tông môn quá dài (tối đa 30 ký tự)!")

        try:
            conn = get_connection()
            c = conn.cursor()
            now = int(time.time())
            c.execute("INSERT INTO tong_mon (name, leader_id, linh_thach, created_at) VALUES (?, ?, 0, ?)",
                      (ten_mon, ctx.author.id, now))
            tong_id = c.lastrowid
            c.execute("UPDATE players SET tong_mon_id = ?, linh_thach = linh_thach - 2000 WHERE user_id = ?",
                      (tong_id, ctx.author.id))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            return await ctx.send("❌ Tên tông môn này đã được sử dụng!")

        embed = discord.Embed(
            title="🏯 TÔNG MÔN ĐÃ THÀNH LẬP!",
            description=(
                f"**Chưởng Môn {player[1]}** đã khai môn lập phái — **{ten_mon}** chào đời!\n\n"
                f"Chiêu mộ đệ tử bằng cách chia sẻ lệnh `{ctx.prefix}giamon {ten_mon}`.\n"
                f"Quản lý tông môn qua `{ctx.prefix}tongmon`."
            ),
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

    @commands.command(name="giamon")
    async def prefix_giamon(self, ctx: commands.Context, *, ten_mon: str = None):
        if not ten_mon:
            return await ctx.send(f"⚠️ Cách dùng: `{ctx.prefix}giamon <tên_tông_môn>`")

        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        if player[13]:
            return await ctx.send(f"❌ Đạo hữu đã thuộc tông môn! Dùng `{ctx.prefix}roimon` để rời đi trước.")

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM tong_mon WHERE name = ?", (ten_mon,))
        tm = c.fetchone()
        if not tm:
            conn.close()
            return await ctx.send(f"❌ Không tìm thấy tông môn **{ten_mon}**!")

        c.execute("UPDATE players SET tong_mon_id = ? WHERE user_id = ?", (tm[0], ctx.author.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🏯 GIA NHẬP TÔNG MÔN THÀNH CÔNG!",
            description=f"Đạo hữu **{player[1]}** đã chính thức gia nhập **{tm[1]}**!\nCùng sư môn chinh phục đỉnh cao thiên đạo!",
            color=0xe74c3c
        )
        await ctx.send(embed=embed)

    @commands.command(name="tongmon", aliases=["tm", "bangphai"])
    async def prefix_tongmon(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        if not player[13]:
            return await ctx.send(f"❌ Chưa gia nhập tông môn nào! Dùng `{ctx.prefix}giamon` hoặc `{ctx.prefix}lapmon`.")

        tm = get_tong_mon(player[13])
        if not tm:
            return await ctx.send("❌ Tông môn không tồn tại!")

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name, realm_idx, pvp_wins FROM players WHERE tong_mon_id = ? ORDER BY realm_idx DESC, exp DESC", (tm[0],))
        members = c.fetchall()
        conn.close()

        leader = get_player(tm[2])
        member_lines = []
        for i, (mname, mrealm, mwins) in enumerate(members[:15]):
            prefix = "👑 " if leader and leader[1] == mname else f"{i+1}. "
            member_lines.append(f"{prefix}**{mname}** — `{REALMS[mrealm]['name']}` | 🏆 `{mwins}`")

        embed = discord.Embed(title=f"🏯 {tm[1]}", description=tm[3] or "*Tông môn chưa có miêu tả.*", color=0xe74c3c)
        embed.add_field(name="👑 Chưởng Môn", value=leader[1] if leader else "Không rõ", inline=True)
        embed.add_field(name="👥 Số Đệ Tử", value=f"`{len(members)}` người", inline=True)
        embed.add_field(name="📋 Thành Viên", value="\n".join(member_lines) or "Chưa có thành viên.", inline=False)
        embed.set_footer(text=f"Tông Môn #{tm[0]}")
        await ctx.send(embed=embed)

    @commands.command(name="roimon")
    async def prefix_roimon(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player or not player[13]:
            return await ctx.send("❌ Chưa gia nhập tông môn nào!")

        tm = get_tong_mon(player[13])
        if tm and tm[2] == ctx.author.id:
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET tong_mon_id = 0 WHERE tong_mon_id = ?", (tm[0],))
            c.execute("DELETE FROM tong_mon WHERE id = ?", (tm[0],))
            conn.commit()
            conn.close()
            return await ctx.send(f"🏯 Chưởng Môn đã giải tán **{tm[1]}**. Toàn bộ đệ tử đã được thả ra.")

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET tong_mon_id = 0 WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        conn.close()
        await ctx.send(f"🚪 Đạo hữu đã rời khỏi **{tm[1] if tm else 'tông môn'}**.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SectCog(bot))
