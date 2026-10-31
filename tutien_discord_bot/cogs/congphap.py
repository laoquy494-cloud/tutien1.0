import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS, CONG_PHAP
from database import get_player, get_connection

class CongPhapCog(commands.Cog, name="Công Pháp"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="congphap", description="Xem và học Công Pháp tu luyện để tăng sức chiến đấu")
    async def congphap(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        current_cp_idx = player[10]
        realm_idx = player[4]
        linh_thach = player[6]

        embed = discord.Embed(
            title="📚 CÔNG PHÁP TU LUYỆN — CHỌN CON ĐƯỜNG",
            description=f"Cảnh giới: **{REALMS[realm_idx]['name']}** | 💎 Linh Thạch: **`{linh_thach:,}`**",
            color=0x8e44ad
        )
        options = []
        for i, cp in enumerate(CONG_PHAP):
            unlocked = realm_idx >= cp["req_realm"]
            is_current = (i == current_cp_idx)
            if is_current:
                status = "✅ Đang Dùng"
            elif unlocked:
                status = "🔓 Có Thể Học"
            else:
                status = f"🔒 Cần {REALMS[cp['req_realm']]['name']}"
            embed.add_field(
                name=f"{cp['icon']} {cp['name']} [{status}]",
                value=f"💰 `{cp['cost']:,}` LT | 🗡️+{int(cp['atk_bonus']*100)}% | 🛡️+{int(cp['def_bonus']*100)}% | ✨+{int(cp['exp_bonus']*100)}%\n*{cp['desc']}*",
                inline=False
            )
            if unlocked and not is_current:
                options.append(discord.SelectOption(
                    label=f"{cp['name']} — {cp['cost']:,} LT",
                    value=str(i),
                    description=f"ATK+{int(cp['atk_bonus']*100)}% DEF+{int(cp['def_bonus']*100)}% EXP+{int(cp['exp_bonus']*100)}%",
                    emoji=cp["icon"]
                ))

        if not options:
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        view = discord.ui.View(timeout=120)
        select = discord.ui.Select(placeholder="Chọn công pháp muốn học...", options=options)

        async def select_callback(sel_interaction: discord.Interaction):
            if sel_interaction.user.id != interaction.user.id:
                return await sel_interaction.response.send_message("❌ Đây không phải ngọc giản của đạo hữu!", ephemeral=True)
            cp_idx = int(sel_interaction.data["values"][0])
            cp = CONG_PHAP[cp_idx]
            p = get_player(interaction.user.id)
            if p[6] < cp["cost"]:
                return await sel_interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần `{cp['cost']:,}`.", ephemeral=True)
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET cong_phap_idx = ?, linh_thach = linh_thach - ? WHERE user_id = ?",
                      (cp_idx, cp["cost"], interaction.user.id))
            conn.commit()
            conn.close()
            await sel_interaction.response.send_message(
                f"📖 Đạo hữu đã lĩnh ngộ **{cp['icon']} {cp['name']}**!\n"
                f"🗡️ ATK +{int(cp['atk_bonus']*100)}% | 🛡️ DEF +{int(cp['def_bonus']*100)}% | ✨ EXP +{int(cp['exp_bonus']*100)}%",
                ephemeral=True
            )

        select.callback = select_callback
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="congphap", aliases=["cp"])
    async def prefix_congphap(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        current_cp_idx = player[10]
        realm_idx = player[4]
        linh_thach = player[6]

        embed = discord.Embed(
            title="📚 CÔNG PHÁP TU LUYỆN — CHỌN CON ĐƯỜNG",
            description=f"Cảnh giới: **{REALMS[realm_idx]['name']}** | 💎 Linh Thạch: **`{linh_thach:,}`**",
            color=0x8e44ad
        )
        options = []
        for i, cp in enumerate(CONG_PHAP):
            unlocked = realm_idx >= cp["req_realm"]
            is_current = (i == current_cp_idx)
            if is_current:
                status = "✅ Đang Dùng"
            elif unlocked:
                status = "🔓 Có Thể Học"
            else:
                status = f"🔒 Cần {REALMS[cp['req_realm']]['name']}"
            embed.add_field(
                name=f"{cp['icon']} {cp['name']} [{status}]",
                value=f"💰 `{cp['cost']:,}` LT | 🗡️+{int(cp['atk_bonus']*100)}% | 🛡️+{int(cp['def_bonus']*100)}% | ✨+{int(cp['exp_bonus']*100)}%\n*{cp['desc']}*",
                inline=False
            )
            if unlocked and not is_current:
                options.append(discord.SelectOption(
                    label=f"{cp['name']} — {cp['cost']:,} LT",
                    value=str(i),
                    description=f"ATK+{int(cp['atk_bonus']*100)}% DEF+{int(cp['def_bonus']*100)}% EXP+{int(cp['exp_bonus']*100)}%",
                    emoji=cp["icon"]
                ))

        if not options:
            return await ctx.send(embed=embed)

        view = discord.ui.View(timeout=120)
        select = discord.ui.Select(placeholder="Chọn công pháp muốn học...", options=options)

        async def select_callback(sel_interaction: discord.Interaction):
            if sel_interaction.user.id != ctx.author.id:
                return await sel_interaction.response.send_message("❌ Đây không phải ngọc giản của đạo hữu!", ephemeral=True)
            cp_idx = int(sel_interaction.data["values"][0])
            cp = CONG_PHAP[cp_idx]
            p = get_player(ctx.author.id)
            if p[6] < cp["cost"]:
                return await sel_interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần `{cp['cost']:,}`.", ephemeral=True)
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE players SET cong_phap_idx = ?, linh_thach = linh_thach - ? WHERE user_id = ?",
                      (cp_idx, cp["cost"], ctx.author.id))
            conn.commit()
            conn.close()
            await sel_interaction.response.send_message(
                f"📖 Đạo hữu đã lĩnh ngộ **{cp['icon']} {cp['name']}**!\n"
                f"🗡️ ATK +{int(cp['atk_bonus']*100)}% | 🛡️ DEF +{int(cp['def_bonus']*100)}% | ✨ EXP +{int(cp['exp_bonus']*100)}%",
                ephemeral=True
            )

        select.callback = select_callback
        view.add_item(select)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(CongPhapCog(bot))
