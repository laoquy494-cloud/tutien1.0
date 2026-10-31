import random
import discord
from discord import app_commands
from discord.ext import commands
from config import (
    REALMS, EQUIPMENT_GRADES, EQUIPMENT_NAMES, EQUIPMENT_TYPES,
    EQUIPMENT_NAMES_BY_TIER, get_equipment_grade
)
from database import get_player, get_connection

TAMBAO_COST_1 = 10000
TAMBAO_COST_10 = 90000

TAMBAO_REWARDS = [
    {"type": "exp", "value": 25000, "name": "Bình Linh Khí Tinh Thuần", "icon": "✨", "weight": 33},
    {"type": "exp", "value": 80000, "name": "Đoàn Thiên Địa Nguyên Khí", "icon": "🌟", "weight": 18},
    {"type": "stone", "value": 8000, "name": "Túi Lớn Linh Thạch", "icon": "💰", "weight": 24},
    {"type": "stone", "value": 30000, "name": "Rương Cực Phẩm Linh Thạch", "icon": "💎", "weight": 10},
    {"type": "pill", "value": 0.20, "name": "Thượng Cổ Phá Cảnh Đan (+20% ĐK)", "icon": "💊", "weight": 7},
    {"type": "equip", "value": 7, "name": "Thượng Phẩm Linh Bảo Cổ Xưa", "icon": "🟣", "weight": 5},
    {"type": "tien_khi", "value": 13, "name": "🏮 Tiên Khí Thượng Cổ Giáng Thế", "icon": "🏮", "weight": 2},
    {"type": "jackpot", "value": 100000, "name": "Hồng Mông Tiên Tủy (Đại Phúc Duyên)", "icon": "👑", "weight": 1},
]

def draw_tambao(user_id: int):
    weights = [r["weight"] for r in TAMBAO_REWARDS]
    reward = random.choices(TAMBAO_REWARDS, weights=weights, k=1)[0]
    conn = get_connection()
    c = conn.cursor()

    desc = ""
    if reward["type"] == "exp":
        c.execute("UPDATE players SET exp = exp + ? WHERE user_id = ?", (reward["value"], user_id))
        desc = f"✨ Nhận được **+{reward['value']:,} Linh Khí**!"
    elif reward["type"] == "stone":
        c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (reward["value"], user_id))
        desc = f"💎 Thu hoạch **+{reward['value']:,} Linh Thạch**!"
    elif reward["type"] == "pill":
        c.execute("UPDATE players SET bonus_rate = MIN(0.75, bonus_rate + ?) WHERE user_id = ?", (reward["value"], user_id))
        desc = f"💊 Nuốt đan dược: Tỷ lệ Độ Kiếp tăng vĩnh viễn **+{int(reward['value']*100)}%**!"
    elif reward["type"] == "equip":
        eq_type = random.choice(EQUIPMENT_TYPES)
        grade_idx = 7  # Thượng Phẩm Linh Bảo (Tier 2)
        grade = get_equipment_grade(grade_idx)
        tier_names = EQUIPMENT_NAMES_BY_TIER.get(grade["tier"], EQUIPMENT_NAMES_BY_TIER[1])
        base_name = random.choice(tier_names.get(eq_type, EQUIPMENT_NAMES[eq_type]))
        eq_name = f"{grade['icon']} {grade['name']} {base_name}"
        atk_b = random.randint(1200, 3000)
        def_b = random.randint(500, 1500)
        c.execute("""INSERT INTO equipment (user_id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped)
                     VALUES (?, ?, ?, ?, ?, ?, 0)""", (user_id, eq_type, eq_name, grade_idx, atk_b, def_b))
        desc = f"⚔️ Rơi ra bảo vật: **{eq_name}** (🗡️+{atk_b:,} 🛡️+{def_b:,})!"
    elif reward["type"] == "tien_khi":
        # Tier 4: Tiên Khí (Grade 13 -> 16: Hạ Phẩm, Trung Phẩm, Thượng Phẩm, Cực Phẩm Tiên Khí)
        tier_4_grades = [13, 14, 15, 16]
        tier_4_weights = [55, 28, 12, 5]
        grade_idx = random.choices(tier_4_grades, weights=tier_4_weights, k=1)[0]
        grade = get_equipment_grade(grade_idx)

        eq_type = random.choice(EQUIPMENT_TYPES)
        tier_names = EQUIPMENT_NAMES_BY_TIER.get(4, {})
        names_pool = tier_names.get(eq_type, EQUIPMENT_NAMES.get(eq_type, ["Tiên Khí"]))
        base_name = random.choice(names_pool)
        eq_name = f"{grade['icon']} {grade['name']} {base_name}"

        # Tính toán chỉ số khủng xứng tầm Tiên Khí
        p_row = c.execute("SELECT realm_idx FROM players WHERE user_id = ?", (user_id,)).fetchone()
        p_realm = p_row[0] if p_row and p_row[0] is not None else 0
        calc_realm = min(len(REALMS) - 1, max(p_realm, 8))
        r_stat = REALMS[calc_realm]
        base_atk = max(1000, r_stat["atk"])
        base_def = max(500, r_stat["def"])

        mult_atk = grade.get("atk_mult", 85.0)
        mult_def = grade.get("def_mult", 85.0)

        if eq_type == "Vũ Khí":
            atk_b = int(base_atk * mult_atk * random.uniform(0.9, 1.15))
            def_b = int(base_def * mult_def * 0.15 * random.uniform(0.9, 1.15))
        elif eq_type in ["Áo", "Giáp"]:
            atk_b = int(base_atk * mult_atk * 0.15 * random.uniform(0.9, 1.15))
            def_b = int(base_def * mult_def * random.uniform(0.9, 1.15))
        elif eq_type == "Quần":
            atk_b = int(base_atk * mult_atk * 0.15 * random.uniform(0.9, 1.15))
            def_b = int(base_def * mult_def * 0.85 * random.uniform(0.9, 1.15))
        elif eq_type == "Giày":
            atk_b = int(base_atk * mult_atk * 0.35 * random.uniform(0.9, 1.15))
            def_b = int(base_def * mult_def * 0.45 * random.uniform(0.9, 1.15))
        else:  # Nhẫn
            atk_b = int(base_atk * mult_atk * 0.65 * random.uniform(0.9, 1.15))
            def_b = int(base_def * mult_def * 0.35 * random.uniform(0.9, 1.15))

        c.execute("""INSERT INTO equipment (user_id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped)
                     VALUES (?, ?, ?, ?, ?, ?, 0)""", (user_id, eq_type, eq_name, grade_idx, atk_b, def_b))
        desc = f"🏮✨ **TIÊN QUANG DIỆU THẾ!** Thu được Tiên Khí Thượng Cổ: **{eq_name}** (🗡️+{atk_b:,} 🛡️+{def_b:,})!"
    elif reward["type"] == "jackpot":
        c.execute("UPDATE players SET exp = exp + 200000, linh_thach = linh_thach + 100000 WHERE user_id = ?", (user_id,))
        desc = "👑 **ĐẠI CƠ DUYÊN THIÊN ĐỊA!** Nhận ngay **+200,000 Linh Khí** & **+100,000 Linh Thạch**!"

    conn.commit()
    conn.close()
    return reward, desc

class TamBaoView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="🌀 Tầm Bảo 1 Lần (10,000 LT)", style=discord.ButtonStyle.primary)
    async def btn_draw_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/tambao` để mở bàn quay của mình!", ephemeral=True)

        player = get_player(self.user_id)
        if player[6] < TAMBAO_COST_1:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần **{TAMBAO_COST_1:,} Linh Thạch**.", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (TAMBAO_COST_1, self.user_id))
        conn.commit()
        conn.close()

        reward, desc = draw_tambao(self.user_id)
        if reward["type"] == "tien_khi":
            color = 0xe67e22
            title = "🏮✨ DỊ TƯỢNG XUẤT THẾ — THU ĐƯỢC TIÊN KHÍ!"
        elif reward["type"] == "jackpot":
            color = 0xf1c40f
            title = "👑 ĐẠI PHÚC DUYÊN — HỒNG MÔNG TIÊN TỦY!"
        else:
            color = 0x9b59b6
            title = "🌀 TẦM BẢO KẾT QUẢ"

        embed = discord.Embed(
            title=title,
            description=f"Thiên Đạo Vận Chuyển — Cơ Duyên Giáng Lâm!\n\n{reward['icon']} **{reward['name']}**\n{desc}",
            color=color
        )
        if reward["type"] == "tien_khi":
            embed.set_footer(text="🏮 Tiên quang chiếu rọi cửu thiên bát hoang!")
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="🌟 Tầm Bảo 10 Lần (90,000 LT)", style=discord.ButtonStyle.success)
    async def btn_draw_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Hãy dùng `/tambao` để mở bàn quay của mình!", ephemeral=True)

        player = get_player(self.user_id)
        if player[6] < TAMBAO_COST_10:
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần **{TAMBAO_COST_10:,} Linh Thạch**.", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (TAMBAO_COST_10, self.user_id))
        conn.commit()
        conn.close()

        results = []
        has_tien_khi = False
        has_jackpot = False
        for _ in range(10):
            reward, desc = draw_tambao(self.user_id)
            if reward["type"] == "tien_khi":
                has_tien_khi = True
            elif reward["type"] == "jackpot":
                has_jackpot = True
            results.append(f"{reward['icon']} **{reward['name']}** — {desc}")

        if has_tien_khi:
            color = 0xe67e22
            title = "🏮✨ TẬP HỢP TẦM BẢO 10 LẦN — PHÚC DUYÊN TIÊN KHÍ!"
        elif has_jackpot:
            color = 0xf1c40f
            title = "👑 TẬP HỢP TẦM BẢO 10 LẦN — ĐẠI CƠ DUYÊN THIÊN ĐỊA!"
        else:
            color = 0xf1c40f
            title = "🌟 TẬP HỢP TẦM BẢO 10 LẦN THÀNH CÔNG!"

        embed = discord.Embed(
            title=title,
            description="\n".join(results),
            color=color
        )
        if has_tien_khi:
            embed.set_footer(text="🏮 Chúc mừng đạo hữu đã hữu duyên thu phục Tiên Khí Thượng Cổ trấn áp chư thiên!")
        await interaction.response.send_message(embed=embed)

class TamBaoCog(commands.Cog, name="Tầm Bảo"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tambao", description="Mở Vòng Quay Tầm Bảo — Săn tìm Tiên Khí và cổ bảo thượng cổ")
    async def tambao(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = discord.Embed(
            title="🌀 VÒNG QUAY TẦM BẢO — THIÊN ĐẠO CƠ DUYÊN",
            description=(
                f"💎 Linh Thạch trong túi: **`{player[6]:,}` LT**\n"
                f"🎟️ Chi phí: **`10,000` LT / 1 lần** (Quay 10 lần: **`90,000` LT** — Tiết kiệm 10,000 LT)\n\n"
                "**Bảo vật có thể nhận được:**\n"
                "• 🏮 **Tiên Khí Thượng Cổ (Tier 4):** Vũ Khí, Áo, Quần, Giày, Nhẫn cấp Tiên Khí (Uy năng hủy thiên diệt địa)\n"
                "• 👑 **Hồng Mông Tiên Tủy:** 200,000 Linh Khí + 100,000 Linh Thạch (Đại Phúc Duyên)\n"
                "• 🟣 **Thượng Phẩm Linh Bảo Cổ Xưa:** Pháp bảo uy áp mạnh mẽ\n"
                "• 💊 **Thượng Cổ Phá Cảnh Đan:** +20% tỷ lệ Độ Kiếp vĩnh viễn\n"
                "• 💎 **Rương Cực Phẩm Linh Thạch (30,000 LT) / Đoàn Thiên Địa Nguyên Khí (80,000 LK)**\n\n"
                "Chọn số lần tầm bảo bên dưới:"
            ),
            color=0x3498db
        )
        view = TamBaoView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="tambao", aliases=["tbquaysan", "gacha", "quay"])
    async def prefix_tambao(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = discord.Embed(
            title="🌀 VÒNG QUAY TẦM BẢO — THIÊN ĐẠO CƠ DUYÊN",
            description=(
                f"💎 Linh Thạch trong túi: **`{player[6]:,}` LT**\n"
                f"🎟️ Chi phí: **`10,000` LT / 1 lần** (Quay 10 lần: **`90,000` LT** — Tiết kiệm 10,000 LT)\n\n"
                "**Bảo vật có thể nhận được:**\n"
                "• 🏮 **Tiên Khí Thượng Cổ (Tier 4):** Vũ Khí, Áo, Quần, Giày, Nhẫn cấp Tiên Khí (Uy năng hủy thiên diệt địa)\n"
                "• 👑 **Hồng Mông Tiên Tủy:** 200,000 Linh Khí + 100,000 Linh Thạch (Đại Phúc Duyên)\n"
                "• 🟣 **Thượng Phẩm Linh Bảo Cổ Xưa:** Pháp bảo uy áp mạnh mẽ\n"
                "• 💊 **Thượng Cổ Phá Cảnh Đan:** +20% tỷ lệ Độ Kiếp vĩnh viễn\n"
                "• 💎 **Rương Cực Phẩm Linh Thạch (30,000 LT) / Đoàn Thiên Địa Nguyên Khí (80,000 LK)**\n\n"
                "Chọn số lần tầm bảo bên dưới:"
            ),
            color=0x3498db
        )
        view = TamBaoView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(TamBaoCog(bot))
