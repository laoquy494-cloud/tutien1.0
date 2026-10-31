import random
import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS, CONG_PHAP
from database import (
    get_player, get_connection, update_cultivation,
    get_equipment_bonus, add_quest_progress
)

def simulate_pvp(p1, p2):
    r1 = REALMS[p1[4]]
    r2 = REALMS[p2[4]]
    cp1 = CONG_PHAP[p1[10]]
    cp2 = CONG_PHAP[p2[10]]

    eq_atk1, eq_def1 = get_equipment_bonus(p1[0])
    eq_atk2, eq_def2 = get_equipment_bonus(p2[0])

    cur_hp1 = int(r1["hp"] * (1 + cp1["def_bonus"]))
    cur_hp2 = int(r2["hp"] * (1 + cp2["def_bonus"]))
    atk1 = int((r1["atk"] + eq_atk1) * (1 + cp1["atk_bonus"]))
    atk2 = int((r2["atk"] + eq_atk2) * (1 + cp2["atk_bonus"]))
    def1 = int((r1["def"] + eq_def1) * (1 + cp1["def_bonus"]))
    def2 = int((r2["def"] + eq_def2) * (1 + cp2["def_bonus"]))

    max_hp1, max_hp2 = cur_hp1, cur_hp2
    log = []

    for rnd in range(1, 11):
        dmg1 = max(1, int(atk1 * random.uniform(0.85, 1.15) - def2 * 0.3))
        dmg2 = max(1, int(atk2 * random.uniform(0.85, 1.15) - def1 * 0.3))
        cur_hp1 -= dmg2
        cur_hp2 -= dmg1
        log.append(f"⚔️ **Hiệp {rnd}:** {p1[1]} gây `{dmg1:,}` | {p2[1]} phản `{dmg2:,}`")
        if cur_hp1 <= 0 or cur_hp2 <= 0:
            break

    if cur_hp1 > cur_hp2:
        winner, loser = p1, p2
    elif cur_hp2 > cur_hp1:
        winner, loser = p2, p1
    else:
        winner, loser = (p1, p2) if max_hp1 >= max_hp2 else (p2, p1)

    return winner, loser, log

class PvPChallengeView(discord.ui.View):
    def __init__(self, challenger_id: int, target_id: int):
        super().__init__(timeout=60)
        self.challenger_id = challenger_id
        self.target_id = target_id

    @discord.ui.button(label="✅ Chấp Nhận Khiêu Chiến", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            return await interaction.response.send_message("❌ Thư khiêu chiến này không gửi cho đạo hữu!", ephemeral=True)

        p1, _ = update_cultivation(self.challenger_id)
        p2, _ = update_cultivation(self.target_id)
        if not p1 or not p2:
            return await interaction.response.send_message("❌ Lỗi dữ liệu nhân vật!", ephemeral=True)

        winner, loser, log = simulate_pvp(p1, p2)
        loot = min(loser[6], max(10, int(loser[6] * 0.10)))

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach + ?, pvp_wins = pvp_wins + 1 WHERE user_id = ?",
                  (loot, winner[0]))
        c.execute("UPDATE players SET linh_thach = MAX(0, linh_thach - ?), pvp_losses = pvp_losses + 1 WHERE user_id = ?",
                  (loot, loser[0]))
        conn.commit()
        conn.close()

        add_quest_progress(self.challenger_id, "q_fight")
        add_quest_progress(self.target_id, "q_fight")

        r1 = REALMS[p1[4]]
        r2 = REALMS[p2[4]]
        embed = discord.Embed(
            title="⚔️ LUẬN KIẾM ĐÀI — KẾT QUẢ TỶ THÍ ⚔️",
            description=(
                f"🗡️ **{p1[1]}** (`{r1['name']}`) VS 🛡️ **{p2[1]}** (`{r2['name']}`)\n"
                f"─────────────────────\n"
                + "\n".join(log[:6]) +
                f"\n─────────────────────\n"
                f"🏆 **{winner[1]}** đã giành chiến thắng!\n"
                f"💎 Chiến lợi phẩm đoạt được: **`{loot:,}` Linh Thạch**"
            ),
            color=0x9b59b6
        )
        for btn in self.children:
            btn.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Từ Chối", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            return await interaction.response.send_message("❌ Thư khiêu chiến này không gửi cho đạo hữu!", ephemeral=True)
        for btn in self.children:
            btn.disabled = True
        await interaction.response.edit_message(
            content=f"❌ **{interaction.user.display_name}** đã từ chối thư khiêu chiến.",
            embed=None,
            view=self
        )

class PvPCog(commands.Cog, name="Tỷ Thí & PvP"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tythi", description="Gửi thư khiêu chiến đến đạo hữu khác — tỷ thí luận kiếm đoạt Linh Thạch")
    @app_commands.describe(doi_thu="Đạo hữu muốn khiêu chiến")
    async def tythi(self, interaction: discord.Interaction, doi_thu: discord.Member):
        if doi_thu.id == interaction.user.id or doi_thu.bot:
            return await interaction.response.send_message("❌ Không thể khiêu chiến bản thân hoặc Bot!", ephemeral=True)

        p1 = get_player(interaction.user.id)
        p2 = get_player(doi_thu.id)
        if not p1:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        if not p2:
            return await interaction.response.send_message(f"❌ **{doi_thu.display_name}** vẫn là phàm nhân!", ephemeral=True)

        r1 = REALMS[p1[4]]
        r2 = REALMS[p2[4]]
        embed = discord.Embed(
            title="⚔️ THƯ KHIÊU CHIẾN — LUẬN KIẾM ĐÀI",
            description=(
                f"⚔️ **{interaction.user.display_name}** (`{r1['name']}`) gửi chiến thư đến **{doi_thu.display_name}** (`{r2['name']}`)!\n\n"
                f"*{doi_thu.mention}, đạo hữu có chấp nhận nghênh chiến không?*\n"
                f"⏳ Chiến thư có hiệu lực trong **60 giây**."
            ),
            color=0x9b59b6
        )
        await interaction.response.send_message(
            content=f"{doi_thu.mention} — thư khiêu chiến từ {interaction.user.mention}!",
            embed=embed,
            view=PvPChallengeView(interaction.user.id, doi_thu.id)
        )

    @commands.command(name="tythi", aliases=["pvp", "dauthu", "solo", "thachdau", "tithi"])
    async def prefix_tythi(self, ctx: commands.Context, doi_thu: discord.Member = None):
        if not doi_thu or doi_thu.id == ctx.author.id or doi_thu.bot:
            return await ctx.send(f"❌ Vui lòng tag đối thủ! Cách dùng: `{ctx.prefix}tythi @User`")

        p1 = get_player(ctx.author.id)
        p2 = get_player(doi_thu.id)
        if not p1:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        if not p2:
            return await ctx.send(f"❌ **{doi_thu.display_name}** vẫn là phàm nhân!")

        r1 = REALMS[p1[4]]
        r2 = REALMS[p2[4]]
        embed = discord.Embed(
            title="⚔️ THƯ KHIÊU CHIẾN — LUẬN KIẾM ĐÀI",
            description=(
                f"⚔️ **{ctx.author.display_name}** (`{r1['name']}`) gửi chiến thư đến **{doi_thu.display_name}** (`{r2['name']}`)!\n\n"
                f"*{doi_thu.mention}, đạo hữu có chấp nhận nghênh chiến không?*\n"
                f"⏳ Chiến thư có hiệu lực trong **60 giây**."
            ),
            color=0x9b59b6
        )
        await ctx.send(
            content=f"{doi_thu.mention} — thư khiêu chiến từ {ctx.author.mention}!",
            embed=embed,
            view=PvPChallengeView(ctx.author.id, doi_thu.id)
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(PvPCog(bot))
