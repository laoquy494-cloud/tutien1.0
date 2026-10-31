import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection, get_or_create_tiencu

TIENCU_LEVELS = [
    {"name": "Tranh Xá Thảo Ốc (Nhà Tranh)", "cost": 0,     "comfort": 10,  "bonus_rate": 0.02, "icon": "🛖"},
    {"name": "Thanh Trúc Tiểu Viện",         "cost": 2500,  "comfort": 35,  "bonus_rate": 0.05, "icon": "🎋"},
    {"name": "Bạch Ngọc U Cư",               "cost": 8000,  "comfort": 80,  "bonus_rate": 0.08, "icon": "🏡"},
    {"name": "Tử Tiêu Tiên Phủ",             "cost": 25000, "comfort": 150, "bonus_rate": 0.12, "icon": "🏯"},
    {"name": "Cửu Trọng Thiên Khuyết",       "cost": 80000, "comfort": 300, "bonus_rate": 0.20, "icon": "✨"}
]

def create_tiencu_embed(user_id: int, user_name: str):
    tc = get_or_create_tiencu(user_id)
    player = get_player(user_id)
    lvl_idx = min(tc[1] - 1, len(TIENCU_LEVELS) - 1)
    cur_house = TIENCU_LEVELS[lvl_idx]
    spouse = get_player(player[14]) if player[14] else None

    next_house = TIENCU_LEVELS[lvl_idx + 1] if lvl_idx < len(TIENCU_LEVELS) - 1 else None

    embed = discord.Embed(
        title=f"✨ TIÊN CƯ PHỦ ĐỆ — {user_name}",
        description=(
            f"Tư gia tọa lạc tại Tiên Thành sầm uất, nơi tu thân dưỡng tính và song tu cùng Đạo Lữ.\n\n"
            f"**{cur_house['icon']} Phẩm cấp:** `{cur_house['name']}`\n"
            f"🛋️ **Độ Tiện Nghi:** `{tc[2]}` điểm\n"
            f"💖 **Buff Song Tu:** `+{int(cur_house['bonus_rate'] * 100)}%` Linh Khí\n"
            f"💑 **Chủ nhân:** {user_name} & {spouse[1] if spouse else '*(Chưa có Đạo Lữ)*'}"
        ),
        color=0xff7979
    )
    if next_house:
        embed.add_field(
            name="🔨 Nâng Cấp Kế Tiếp",
            value=f"**{next_house['icon']} {next_house['name']}**\nChi phí: `{next_house['cost']:,}` Linh Thạch | Buff: `+{int(next_house['bonus_rate']*100)}%`",
            inline=False
        )
    else:
        embed.add_field(name="👑 Tiên Phủ Cực Phẩm", value="Tiên Cư đã đạt cấp độ tráng lệ tối cao!", inline=False)

    return embed

class TienCuView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="🔨 Nâng Cấp Tiên Cư", style=discord.ButtonStyle.primary)
    async def btn_upgrade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Tiên Cư của đạo hữu khác!", ephemeral=True)

        tc = get_or_create_tiencu(self.user_id)
        lvl_idx = tc[1] - 1
        if lvl_idx >= len(TIENCU_LEVELS) - 1:
            return await interaction.response.send_message("👑 Tiên Cư đã đạt cấp tối đa!", ephemeral=True)

        next_h = TIENCU_LEVELS[lvl_idx + 1]
        player = get_player(self.user_id)
        if player[6] < next_h["cost"]:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần **`{next_h['cost']:,}` Linh Thạch**.", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (next_h["cost"], self.user_id))
        c.execute("UPDATE tiencu SET home_level = home_level + 1, comfort = comfort + ? WHERE user_id = ?",
                  (next_h["comfort"], self.user_id))
        conn.commit()
        conn.close()

        embed = create_tiencu_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🎉 Chúc mừng! Tiên Cư đã được thăng cấp lên **{next_h['icon']} {next_h['name']}**!", ephemeral=True)

class TienCuCog(commands.Cog, name="Tiên Cư"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tiencu", description="Xem Tiên Cư — Biệt viện phủ đệ tu tiên và nâng cấp phòng ốc")
    async def tiencu(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = create_tiencu_embed(interaction.user.id, interaction.user.display_name)
        view = TienCuView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="tiencu", aliases=["tc", "nhacua", "phude"])
    async def prefix_tiencu(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = create_tiencu_embed(ctx.author.id, ctx.author.display_name)
        view = TienCuView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(TienCuCog(bot))
