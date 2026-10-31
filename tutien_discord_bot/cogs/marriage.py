import time
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection

class MarriageView(discord.ui.View):
    def __init__(self, from_id: int, to_id: int):
        super().__init__(timeout=120)
        self.from_id = from_id
        self.to_id = to_id

    @discord.ui.button(label="💍 Chấp Nhận Kết Bái", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.to_id:
            return await interaction.response.send_message("❌ Thư kết bái này không gửi cho đạo hữu!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM marriage WHERE user1_id IN (?,?) OR user2_id IN (?,?)",
                  (self.from_id, self.to_id, self.from_id, self.to_id))
        if c.fetchone():
            conn.close()
            return await interaction.response.send_message("❌ Một trong hai đạo hữu đã có Đạo Lữ rồi!", ephemeral=True)

        now = int(time.time())
        c.execute("INSERT OR IGNORE INTO marriage (user1_id, user2_id, married_at) VALUES (?, ?, ?)",
                  (self.from_id, self.to_id, now))
        c.execute("UPDATE players SET spouse_id = ? WHERE user_id = ?", (self.to_id, self.from_id))
        c.execute("UPDATE players SET spouse_id = ? WHERE user_id = ?", (self.from_id, self.to_id))
        c.execute("DELETE FROM marriage_requests WHERE (from_id=? AND to_id=?) OR (from_id=? AND to_id=?)",
                  (self.from_id, self.to_id, self.to_id, self.from_id))
        conn.commit()
        conn.close()

        p1 = get_player(self.from_id)
        p2 = get_player(self.to_id)
        embed = discord.Embed(
            title="💍 KẾT BÁI THÀNH CÔNG — ĐẠO LỮ THIÊN THÀNH!",
            description=(
                f"🌸 **{p1[1]}** và **{p2[1]}** đã chính thức kết thành Đạo Lữ!\n\n"
                f"💑 Buff song tu: **+5% Linh Khí** mỗi lần bế quan!\n"
                f"Xin chúc mừng hai vị đạo hữu trăm năm hạnh phúc, đồng lòng đắc đạo trường sinh!"
            ),
            color=0xff69b4
        )
        for btn in self.children:
            btn.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💔 Từ Chối", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.to_id:
            return await interaction.response.send_message("❌ Thư kết bái này không gửi cho đạo hữu!", ephemeral=True)
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM marriage_requests WHERE from_id = ? AND to_id = ?", (self.from_id, self.to_id))
        conn.commit()
        conn.close()
        for btn in self.children:
            btn.disabled = True
        await interaction.response.edit_message(content="💔 Đề nghị kết bái đã bị từ chối.", embed=None, view=self)

class MarriageCog(commands.Cog, name="Đạo Lữ & Hôn Nhân"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="cauhon", description="Cầu hôn một đạo hữu để kết thành Đạo Lữ (+5% Linh Khí bế quan)")
    @app_commands.describe(doi_tuong="Đạo hữu muốn cầu hôn")
    async def cauhon(self, interaction: discord.Interaction, doi_tuong: discord.Member):
        if doi_tuong.id == interaction.user.id or doi_tuong.bot:
            return await interaction.response.send_message("❌ Không thể cầu hôn bản thân hoặc Bot!", ephemeral=True)

        p1 = get_player(interaction.user.id)
        p2 = get_player(doi_tuong.id)
        if not p1:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        if not p2:
            return await interaction.response.send_message(f"❌ **{doi_tuong.display_name}** chưa nhập đạo!", ephemeral=True)
        if p1[14]:
            return await interaction.response.send_message("❌ Đạo hữu đã có Đạo Lữ! Dùng `/lyhon` nếu muốn thay đổi.", ephemeral=True)
        if p2[14]:
            return await interaction.response.send_message(f"❌ **{doi_tuong.display_name}** đã có Đạo Lữ!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM marriage_requests WHERE from_id = ? AND to_id = ?", (interaction.user.id, doi_tuong.id))
        c.execute("INSERT INTO marriage_requests (from_id, to_id, created_at) VALUES (?, ?, ?)",
                  (interaction.user.id, doi_tuong.id, int(time.time())))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="💍 CẦU HÔN — KẾT BÁI ĐẠO LỮ",
            description=(
                f"🌸 **{p1[1]}** đã quỳ gối dâng lên **{p2[1]}** một viên **Tương Tư Đan** quý giá!\n\n"
                f"*{doi_tuong.mention}, đạo hữu có đồng ý kết thành Đạo Lữ không?*\n"
                f"💑 Buff song tu: +5% Linh Khí mỗi lần bế quan"
            ),
            color=0xff69b4
        )
        await interaction.response.send_message(
            content=f"{doi_tuong.mention} — lời cầu hôn từ {interaction.user.mention}!",
            embed=embed,
            view=MarriageView(interaction.user.id, doi_tuong.id)
        )

    @app_commands.command(name="lyhon", description="Ly hôn với Đạo Lữ hiện tại")
    async def lyhon(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player or not player[14]:
            return await interaction.response.send_message("❌ Đạo hữu chưa có Đạo Lữ!", ephemeral=True)

        spouse = get_player(player[14])
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET spouse_id = 0 WHERE user_id IN (?, ?)", (interaction.user.id, player[14]))
        c.execute("DELETE FROM marriage WHERE (user1_id=? AND user2_id=?) OR (user1_id=? AND user2_id=?)",
                  (interaction.user.id, player[14], player[14], interaction.user.id))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"💔 **{player[1]}** đã ly hôn với **{spouse[1] if spouse else 'đạo lữ'}**.\n"
            f"*Con đường tu tiên từ nay lại cô đơn một mình...*"
        )

    @commands.command(name="cauhon", aliases=["cuoi", "daolu"])
    async def prefix_cauhon(self, ctx: commands.Context, doi_tuong: discord.Member = None):
        if not doi_tuong or doi_tuong.id == ctx.author.id or doi_tuong.bot:
            return await ctx.send(f"❌ Vui lòng tag đạo hữu muốn cầu hôn! Cách dùng: `{ctx.prefix}cauhon @User`")

        p1 = get_player(ctx.author.id)
        p2 = get_player(doi_tuong.id)
        if not p1:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        if not p2:
            return await ctx.send(f"❌ **{doi_tuong.display_name}** chưa nhập đạo!")
        if p1[14]:
            return await ctx.send(f"❌ Đạo hữu đã có Đạo Lữ! Dùng `{ctx.prefix}lyhon` nếu muốn thay đổi.")
        if p2[14]:
            return await ctx.send(f"❌ **{doi_tuong.display_name}** đã có Đạo Lữ!")

        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM marriage_requests WHERE from_id = ? AND to_id = ?", (ctx.author.id, doi_tuong.id))
        c.execute("INSERT INTO marriage_requests (from_id, to_id, created_at) VALUES (?, ?, ?)",
                  (ctx.author.id, doi_tuong.id, int(time.time())))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="💍 CẦU HÔN — KẾT BÁI ĐẠO LỮ",
            description=(
                f"🌸 **{p1[1]}** đã quỳ gối dâng lên **{p2[1]}** một viên **Tương Tư Đan** quý giá!\n\n"
                f"*{doi_tuong.mention}, đạo hữu có đồng ý kết thành Đạo Lữ không?*\n"
                f"💑 Buff song tu: +5% Linh Khí mỗi lần bế quan"
            ),
            color=0xff69b4
        )
        await ctx.send(
            content=f"{doi_tuong.mention} — lời cầu hôn từ {ctx.author.mention}!",
            embed=embed,
            view=MarriageView(ctx.author.id, doi_tuong.id)
        )

    @commands.command(name="lyhon")
    async def prefix_lyhon(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player or not player[14]:
            return await ctx.send("❌ Đạo hữu chưa có Đạo Lữ!")

        spouse = get_player(player[14])
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET spouse_id = 0 WHERE user_id IN (?, ?)", (ctx.author.id, player[14]))
        c.execute("DELETE FROM marriage WHERE (user1_id=? AND user2_id=?) OR (user1_id=? AND user2_id=?)",
                  (ctx.author.id, player[14], player[14], ctx.author.id))
        conn.commit()
        conn.close()

        await ctx.send(
            f"💔 **{player[1]}** đã ly hôn với **{spouse[1] if spouse else 'đạo lữ'}**.\n"
            f"*Con đường tu tiên từ nay lại cô đơn một mình...*"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(MarriageCog(bot))
