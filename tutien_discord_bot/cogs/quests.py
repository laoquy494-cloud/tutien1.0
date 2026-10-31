import discord
from discord import app_commands
from discord.ext import commands
from config import DAILY_QUESTS
from database import get_player, reset_daily_if_needed, get_today_str

class QuestsCog(commands.Cog, name="Nhiệm Vụ"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="nhiemvu", description="Xem các Nhiệm Vụ Hàng Ngày và nhận thưởng Linh Khí, Linh Thạch")
    async def nhiemvu(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        reset_daily_if_needed(interaction.user.id)
        player = get_player(interaction.user.id)

        quest_cols = {
            "q_cultivate": player[16],
            "q_explore": player[17],
            "q_fight": player[18],
            "q_pills": player[19],
        }

        embed = discord.Embed(
            title="📋 NHIỆM VỤ HÀNG NGÀY",
            description=f"📅 Ngày: **{get_today_str()}** | Hoàn thành để nhận phần thưởng!",
            color=0xf39c12
        )
        for q in DAILY_QUESTS:
            progress = quest_cols[q["id"]]
            target = q["target"]
            done = progress >= target
            pct_blocks = min(progress, target)
            bar = "🟩" * pct_blocks + "⬜" * (target - pct_blocks)
            status = "✅ **HOÀN THÀNH**" if done else f"{bar} `{progress}/{target}`"
            embed.add_field(
                name=f"{q['icon']} {q['name']}",
                value=f"*{q['desc']}*\n{status}\n💰 Thưởng: ✨ `+{q['reward_exp']:,}` LK | 💎 `+{q['reward_stone']:,}` LT",
                inline=False
            )
        completed = sum(1 for q in DAILY_QUESTS if quest_cols[q["id"]] >= q["target"])
        embed.set_footer(text=f"Đã hoàn thành: {completed}/{len(DAILY_QUESTS)} | Tự động làm mới lúc 00:00 (GMT+7)")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="nhiemvu", aliases=["nvh", "daily", "quest"])
    async def prefix_nhiemvu(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        reset_daily_if_needed(ctx.author.id)
        player = get_player(ctx.author.id)

        quest_cols = {
            "q_cultivate": player[16],
            "q_explore": player[17],
            "q_fight": player[18],
            "q_pills": player[19],
        }

        embed = discord.Embed(
            title="📋 NHIỆM VỤ HÀNG NGÀY",
            description=f"📅 Ngày: **{get_today_str()}** | Hoàn thành để nhận phần thưởng!",
            color=0xf39c12
        )
        for q in DAILY_QUESTS:
            progress = quest_cols[q["id"]]
            target = q["target"]
            done = progress >= target
            pct_blocks = min(progress, target)
            bar = "🟩" * pct_blocks + "⬜" * (target - pct_blocks)
            status = "✅ **HOÀN THÀNH**" if done else f"{bar} `{progress}/{target}`"
            embed.add_field(
                name=f"{q['icon']} {q['name']}",
                value=f"*{q['desc']}*\n{status}\n💰 Thưởng: ✨ `+{q['reward_exp']:,}` LK | 💎 `+{q['reward_stone']:,}` LT",
                inline=False
            )
        completed = sum(1 for q in DAILY_QUESTS if quest_cols[q["id"]] >= q["target"])
        embed.set_footer(text=f"Đã hoàn thành: {completed}/{len(DAILY_QUESTS)} | Tự động làm mới lúc 00:00 (GMT+7)")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(QuestsCog(bot))
