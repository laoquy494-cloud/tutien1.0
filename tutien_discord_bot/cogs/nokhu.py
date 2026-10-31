import time
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection, get_or_create_slaves

def create_nokhu_embed(user_id: int, user_name: str):
    slaves = get_or_create_slaves(user_id)
    # slaves: (user_id, slave_count, last_mine)
    now = int(time.time())
    count = slaves[1]
    elapsed = max(0, now - slaves[2])
    hours = elapsed / 3600.0

    # Mỗi nô bộc đào 60 LT/giờ, tối đa tích lũy 12 giờ
    effective_hours = min(12.0, hours)
    mined_stones = int(effective_hours * 60 * count)

    embed = discord.Embed(
        title=f"⛓️ NÔ KHU KHAI THÁC MỎ — {user_name}",
        description=(
            "Lãnh địa mỏ quặng linh thạch thuộc quyền sở hữu của đạo hữu.\n"
            "Các nô bộc ngày đêm đào bới mỏ sâu để cống nạp Linh Thạch thô!"
        ),
        color=0x7f8c8d
    )
    embed.add_field(name="👥 Số Lượng Nô Bộc", value=f"**`{count}`** người (Tối đa 20)", inline=True)
    embed.add_field(name="⛏️ Tốc Độ Khai Thác", value=f"`{count * 60:,}` Linh Thạch / Giờ", inline=True)
    embed.add_field(
        name="📦 Kho Quặng Tích Lũy",
        value=f"💎 Đã đào được: **`{mined_stones:,}` Linh Thạch**\n*(Tích lũy tối đa 12 giờ)*",
        inline=False
    )
    embed.set_footer(text="Nhớ thường xuyên thu hoạch để kho không bị đầy!")
    return embed, mined_stones

class NoKhuView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="⛏️ Thu Hoạch Linh Thạch", style=discord.ButtonStyle.success)
    async def btn_harvest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải Nô Khu của đạo hữu!", ephemeral=True)

        _, mined_stones = create_nokhu_embed(self.user_id, interaction.user.display_name)
        if mined_stones < 10:
            return await interaction.response.send_message("⏳ Nô bộc mới bắt đầu đào, chưa đủ lượng khoáng để thu gom!", ephemeral=True)

        now = int(time.time())
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE slaves SET last_mine = ? WHERE user_id = ?", (now, self.user_id))
        c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (mined_stones, self.user_id))
        conn.commit()
        conn.close()

        embed, _ = create_nokhu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"⛏️ Thu gom thành công **+{mined_stones:,} Linh Thạch** từ mỏ quặng!", ephemeral=True)

    @discord.ui.button(label="⛓️ Mua Thêm Nô Bộc (500 LT)", style=discord.ButtonStyle.secondary)
    async def btn_buy_slave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Không thể thao tác!", ephemeral=True)

        slaves = get_or_create_slaves(self.user_id)
        if slaves[1] >= 20:
            return await interaction.response.send_message("⚠️ Mỏ quặng đã đầy chỗ, không thể chứa quá 20 nô bộc!", ephemeral=True)

        player = get_player(self.user_id)
        if player[6] < 500:
            return await interaction.response.send_message("❌ Cần **500 Linh Thạch** để chuộc thêm 1 nô bộc!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - 500 WHERE user_id = ?", (self.user_id,))
        c.execute("UPDATE slaves SET slave_count = slave_count + 1 WHERE user_id = ?", (self.user_id,))
        conn.commit()
        conn.close()

        embed, _ = create_nokhu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"⛓️ Đã đưa thêm 1 nô bộc vào mỏ! Hiện có **{slaves[1] + 1}** người làm việc.", ephemeral=True)

class NoKhuCog(commands.Cog, name="Nô Khu"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nokhu", description="Mở Nô Khu — Quản lý nô bộc khai thác mỏ quặng Linh Thạch")
    async def nokhu(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed, _ = create_nokhu_embed(interaction.user.id, interaction.user.display_name)
        view = NoKhuView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="nokhu", aliases=["nk", "noboc"])
    async def prefix_nokhu(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed, _ = create_nokhu_embed(ctx.author.id, ctx.author.display_name)
        view = NoKhuView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(NoKhuCog(bot))
