import random
import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS
from database import (
    get_player, get_connection, update_cultivation,
    get_player_combat_stats, add_quest_progress
)
from cogs.equipment import create_random_equipment

# Kho danh xưng và ngoại hiệu Boss Ngoại Vực theo 5 phân tầng cảnh giới
NGOAIVUC_POOLS = {
    # 0-1: Luyện Khí – Trúc Cơ
    "low": [
        {"name": "Hư Không Oán Linh", "icon": "👻", "desc": "Oán khí kết tụ nơi khe nứt hư không phàm giới."},
        {"name": "Bạch Cốt Dạ Xoa", "icon": "💀", "desc": "Ma tướng tuần tra ranh giới thế tục."},
        {"name": "U Minh Quỷ Vương", "icon": "👹", "desc": "Chủ nhân quỷ vực, thống lĩnh trăm quỷ."}
    ],
    # 2-3: Kết Đan – Nguyên Anh
    "mid": [
        {"name": "Cửu U Ma Xà", "icon": "🐍", "desc": "Hắc xà ngàn năm hút linh khí cửu u, da dày vảy cứng."},
        {"name": "Huyết Ngục Cuồng Ma", "icon": "🐺", "desc": "Ma thú cuồng bạo thoát ra từ tầng sâu huyết ngục."},
        {"name": "Hắc Ám Ma Quân", "icon": "🦇", "desc": "Ma tu kết đan sa đọa, công pháp âm độc quỷ dị."}
    ],
    # 4-5: Hóa Thần – Luyện Hư
    "high": [
        {"name": "Ma Diễm Cự Tích", "icon": "🔥", "desc": "Thần thú viễn cổ đọa ma, ma hỏa thiêu rụi sơn hà."},
        {"name": "Vô Tướng Cổ Ma", "icon": "🌪️", "desc": "Cổ ma vô hình vô tướng, tâm ma khó lường."},
        {"name": "Thôn Thiên Ma Tôn", "icon": "👑", "desc": "Ma Tôn ngạo thị cấm địa, một hơi thở nuốt chửng thiên địa."}
    ],
    # 6-8: Hợp Thể – Đại Thừa – Độ Kiếp
    "peak": [
        {"name": "Cửu U Ma Long", "icon": "🐉", "desc": "Thái cổ ma long phá toái hư không hạ giới."},
        {"name": "Hỗn Độn Ma Thần", "icon": "⚡", "desc": "Ma thần sinh ra giữa sấm sét hỗn độn."},
        {"name": "Vực Ngoại Minh Hoàng", "icon": "🪐", "desc": "Chúa tể minh giới vực ngoại, uy áp chư thiên."}
    ],
    # 9+: Phi Thăng – Tiên Nhân
    "immortal": [
        {"name": "Thái Sơ Ma Tướng", "icon": "🌌", "desc": "Chiến tướng từ thời thái sơ hồng hoang."},
        {"name": "La Hầu Phân Thân", "icon": "🩸", "desc": "Một tia ý chí của Ma Tổ La Hầu giáng lâm tam giới."},
        {"name": "Vạn Ma Chí Tôn", "icon": "👑", "desc": "Đứng đầu ma giới hồng hoang, sát phạt vô thượng."}
    ]
}

# Backward compatibility
BOSSES = [
    {"name": "Hư Không Oán Linh", "req_realm": 0, "hp": 1500, "atk": 120, "def": 50, "reward_exp": 1200, "reward_stone": 300, "icon": "👻"},
    {"name": "Cửu U Ma Xà", "req_realm": 2, "hp": 5000, "atk": 400, "def": 200, "reward_exp": 3500, "reward_stone": 800, "icon": "🐍"},
    {"name": "Thôn Thiên Ma Tôn", "req_realm": 4, "hp": 25000, "atk": 2000, "def": 1000, "reward_exp": 15000, "reward_stone": 3000, "icon": "👹"},
]

def get_ngoaivuc_boss_list(user_id: int):
    """Tạo danh sách 3 Boss Ngoại Vực tự động tương thích cảnh giới và chiến lực người chơi"""
    stats = get_player_combat_stats(user_id)
    if not stats:
        return []

    r_idx = stats["realm_idx"]
    p_hp = stats["hp"]
    p_atk = stats["atk"]
    p_def = stats["def"]

    if r_idx <= 7:
        pool = NGOAIVUC_POOLS["low"]
    elif r_idx <= 13:
        pool = NGOAIVUC_POOLS["mid"]
    elif r_idx <= 19:
        pool = NGOAIVUC_POOLS["high"]
    elif r_idx <= 25:
        pool = NGOAIVUC_POOLS["peak"]
    else:
        pool = NGOAIVUC_POOLS["immortal"]

    base_exp = max(450, int((r_idx + 1) * 380))
    base_stone = max(150, int((r_idx + 1) * 120))

    configs = [
        {
            "id": 0,
            "tier_label": "🟢 Vừa Sức (Dễ)",
            "style": discord.ButtonStyle.primary,
            "mult_hp": 0.85,
            "mult_atk": 0.75,
            "mult_def": 0.70,
            "exp_mult": 1.0,
            "stone_mult": 1.0,
            "equip_chance": 0.20
        },
        {
            "id": 1,
            "tier_label": "🟡 Ngang Sức (Vừa)",
            "style": discord.ButtonStyle.danger,
            "mult_hp": 1.25,
            "mult_atk": 0.95,
            "mult_def": 0.85,
            "exp_mult": 2.2,
            "stone_mult": 2.0,
            "equip_chance": 0.50
        },
        {
            "id": 2,
            "tier_label": "🔴 Ma Tôn (Thử Thách)",
            "style": discord.ButtonStyle.secondary,
            "mult_hp": 1.75,
            "mult_atk": 1.20,
            "mult_def": 1.05,
            "exp_mult": 4.5,
            "stone_mult": 3.8,
            "equip_chance": 1.00 # 100% chắc chắn rơi pháp bảo trang bị!
        }
    ]

    bosses = []
    for idx, cfg in enumerate(configs):
        tmpl = pool[idx % len(pool)]
        b_hp = max(100, int(p_hp * cfg["mult_hp"]))
        b_atk = max(20, int(p_atk * cfg["mult_atk"]))
        b_def = max(10, int(p_def * cfg["mult_def"]))
        b_power = b_atk * 2 + b_def * 2 + b_hp // 2
        reward_exp = int(base_exp * cfg["exp_mult"])
        reward_stone = int(base_stone * cfg["stone_mult"])

        bosses.append({
            "idx": idx,
            "name": tmpl["name"],
            "icon": tmpl["icon"],
            "desc": tmpl["desc"],
            "difficulty": cfg["tier_label"],
            "hp": b_hp,
            "atk": b_atk,
            "def": b_def,
            "power": b_power,
            "reward_exp": reward_exp,
            "reward_stone": reward_stone,
            "equip_chance": cfg["equip_chance"],
            "style": cfg["style"]
        })

    return bosses

class NgoaiVucView(discord.ui.View):
    def __init__(self, user_id: int, bosses: list = None):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bosses = bosses or get_ngoaivuc_boss_list(user_id)

        # Tạo nút bấm động theo 3 cấp độ Boss
        for b in self.bosses:
            btn = discord.ui.Button(
                label=f"{b['name'][:25]} — {b['difficulty'].split()[0]}",
                emoji=b["icon"],
                style=b["style"],
                custom_id=f"fight_boss_{b['idx']}",
                row=0 if b["idx"] < 2 else 1
            )
            btn.callback = self.make_callback(b["idx"])
            self.add_item(btn)

    def make_callback(self, boss_idx: int):
        async def callback(interaction: discord.Interaction):
            await self.fight_boss(interaction, boss_idx)
        return callback

    async def fight_boss(self, interaction: discord.Interaction, boss_idx: int):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/ngoaivuc` để tự mở chiến trường!", ephemeral=True)

        stats = get_player_combat_stats(self.user_id)
        if not stats:
            return await interaction.response.send_message("❌ Chưa nhập đạo! Dùng `/nhapdao` trước.", ephemeral=True)

        if boss_idx >= len(self.bosses):
            boss_idx = 0
        boss = self.bosses[boss_idx]

        p_hp = stats["hp"]
        p_atk = stats["atk"]
        p_def = stats["def"]

        b_hp = boss["hp"]
        b_atk = boss["atk"]
        b_def = boss["def"]

        combat_log = []
        for rnd in range(1, 8):
            p_dmg = max(1, int(p_atk * random.uniform(0.85, 1.15) - b_def * 0.25))
            b_dmg = max(1, int(b_atk * random.uniform(0.85, 1.15) - p_def * 0.25))
            b_hp -= p_dmg
            p_hp -= b_dmg
            combat_log.append(f"⚔️ **Hiệp {rnd}:** Đạo hữu gây `{p_dmg:,}` ST | {boss['name']} phản `{b_dmg:,}` ST")
            if b_hp <= 0 or p_hp <= 0:
                break

        won = (b_hp <= 0 and p_hp > 0) or (p_hp >= b_hp)

        conn = get_connection()
        c = conn.cursor()

        if won:
            c.execute("UPDATE players SET exp = exp + ?, linh_thach = linh_thach + ? WHERE user_id = ?",
                      (boss["reward_exp"], boss["reward_stone"], self.user_id))
            conn.commit()
            conn.close()

            add_quest_progress(self.user_id, "q_fight")

            item_drop_text = ""
            if random.random() < boss["equip_chance"]:
                item = create_random_equipment(self.user_id, stats["realm_idx"])
                item_drop_text = (
                    f"\n\n🎁 **BẢO VẬT NGOẠI VỰC XUẤT THẾ:**\n"
                    f"**{item['eq_name']}** ({item['eq_type']})\n"
                    f"🗡️ +`{item['atk_bonus']:,}` Công kích | 🛡️ +`{item['def_bonus']:,}` Phòng ngự\n"
                    f"*(Đã cất vào kho trang bị — dùng `/trangbi` để mặc)*"
                )

            embed = discord.Embed(
                title=f"🏆 CHIẾN THẮNG NGOẠI VỰC — TRẢM {boss['icon']} {boss['name'].upper()}!",
                description=(
                    f"Trận chiến chấn động hư không đã kết thúc với thắng lợi thuộc về đạo hữu!\n\n"
                    + "\n".join(combat_log[:5]) +
                    f"\n\n🎁 **Chiến lợi phẩm:** ✨ `+{boss['reward_exp']:,}` Linh Khí | 💎 `+{boss['reward_stone']:,}` Linh Thạch"
                    f"{item_drop_text}"
                ),
                color=0x2ecc71
            )
        else:
            lost = max(50, int(boss["reward_stone"] * 0.2))
            c.execute("UPDATE players SET linh_thach = MAX(0, linh_thach - ?) WHERE user_id = ?", (lost, self.user_id))
            conn.commit()
            conn.close()

            embed = discord.Embed(
                title=f"🩸 THẤT THỦ NGOẠI VỰC — BỊ {boss['icon']} {boss['name'].upper()} ĐÁNH LUI!",
                description=(
                    f"Ma khí quá đỗi hung hiểm và áp đảo, đạo hữu đành thi triển Huyết Độn rút lui!\n\n"
                    + "\n".join(combat_log[:5]) +
                    f"\n\n📉 **Tổn thất:** -`{lost:,}` Linh Thạch để mua linh dược trị thương."
                ),
                color=0xc0392b
            )

        await interaction.response.send_message(embed=embed)

def create_ngoaivuc_embed_and_view(user_id: int):
    stats = get_player_combat_stats(user_id)
    if not stats:
        embed = discord.Embed(title="❌ Chưa nhập đạo! Dùng `/nhapdao` trước.", color=0xe74c3c)
        return embed, None

    bosses = get_ngoaivuc_boss_list(user_id)
    embed = discord.Embed(
        title="🌌 NGOẠI VỰC HƯ KHÔNG — MA TỘC CHIẾN TRƯỜNG",
        description=(
            f"👤 Tu sĩ: **{stats['player'][2]}** | Cảnh giới: {stats['realm_icon']} **{stats['realm_name']}**\n"
            f"⚡ **Chiến Lực Bản Thân:** `❤️ {stats['hp']:,}` | `🗡️ {stats['atk']:,}` | `🛡️ {stats['def']:,}` (Tổng: **`{stats['power']:,}`**)\n"
            "────────────────────────────────────────\n"
            "🔥 **Boss Ngoại Vực tự động thay đổi theo Cảnh Giới và Chiến Lực:**\n"
            "*(Chọn mục tiêu khiêu chiến bên dưới)*"
        ),
        color=0x8e44ad
    )

    for b in bosses:
        drop_txt = " (🎁 Rơi Pháp Bảo)" if b["equip_chance"] >= 0.4 else ""
        embed.add_field(
            name=f"{b['icon']} {b['name']} — [{b['difficulty']}]",
            value=(
                f"*{b['desc']}*\n"
                f"❤️ Máu: `{b['hp']:,}` | 🗡️ Công: `{b['atk']:,}` | 🛡️ Thủ: `{b['def']:,}`\n"
                f"🎁 Thưởng: ✨ `+{b['reward_exp']:,}` LK | 💎 `+{b['reward_stone']:,}` LT{drop_txt}"
            ),
            inline=False
        )

    view = NgoaiVucView(user_id, bosses)
    return embed, view

class NgoaiVucCog(commands.Cog, name="Ngoại Vực"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ngoaivuc", description="Viễn chinh Ngoại Vực — Khiêu chiến Ma Tộc tương ứng cảnh giới và chiến lực")
    async def ngoaivuc(self, interaction: discord.Interaction):
        embed, view = create_ngoaivuc_embed_and_view(interaction.user.id)
        if not view:
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="ngoaivuc", aliases=["nv", "boss", "sanboss"])
    async def prefix_ngoaivuc(self, ctx: commands.Context):
        embed, view = create_ngoaivuc_embed_and_view(ctx.author.id)
        if not view:
            return await ctx.send(embed=embed)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(NgoaiVucCog(bot))
