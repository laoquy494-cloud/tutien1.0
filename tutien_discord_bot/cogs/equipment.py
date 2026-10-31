import random
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from config import (
    REALMS, EQUIPMENT_TYPES, EQUIPMENT_TIERS, EQUIPMENT_GRADES,
    EQUIPMENT_NAMES, EQUIPMENT_NAMES_BY_TIER, FORGE_COST,
    get_equipment_grade, get_equipment_tier
)
from database import get_player, get_connection, get_equipment_bonus

def create_capbac_embed():
    """Tạo Embed hiển thị 5 Đại Cấp Bậc và 23 Phẩm Cấp cùng tỉ lệ rơi"""
    embed = discord.Embed(
        title="🏛️ HỆ THỐNG CẤP BẬC PHÁP BẢO & TỶ LỆ XUẤT HIỆN",
        description=(
            "Toàn bộ vũ khí, pháp bảo trong thiên địa được chia thành **5 Đại Cấp Bậc (23 Phẩm Cấp)**.\n"
            "Tỉ lệ rèn xuất hiện **Phàm Khí cơ bản là 70%**, cấp bậc càng cao tỉ lệ rơi sẽ **càng cực kỳ thấp**!\n"
            "────────────────────────────────────────"
        ),
        color=0xf1c40f
    )
    embed.add_field(
        name="1. ⚔️ Phàm Khí / Pháp Khí (Luyện Khí – Trúc Cơ) [Tỷ lệ: ~70% - 94.6%]",
        value=(
            "• ⚪ **Phàm Khí** (~70%): Vũ khí bình thường do thợ rèn làm từ kim loại thế tục, không có linh lực.\n"
            "• ⚪ **Hạ / 🟢 Trung / 🟢 Thượng / 🔵 Cực Phẩm Pháp Khí**: Đã khắc trận pháp, có thể dẫn truyền linh lực tu sĩ sơ cấp."
        ),
        inline=False
    )
    embed.add_field(
        name="2. ✨ Linh Bảo (Kết Đan – Nguyên Anh) [Tỷ lệ: ~4.8%]",
        value=(
            "• 🔵 **Hạ Phẩm Linh Bảo**: Bắt đầu có uy áp linh khí mạnh mẽ.\n"
            "• 🔷 **Trung Phẩm Linh Bảo**: Phá hủy được núi non, có chút linh tính cơ bản.\n"
            "• 🟣 **Thượng Phẩm Linh Bảo**: Công kích uyển chuyển, thu phóng theo ý niệm.\n"
            "• 🟣 **Cực Phẩm Linh Bảo**: Đỉnh cao linh bảo thông thường, gần chạm ngưỡng thông linh sâu sắc."
        ),
        inline=False
    )
    embed.add_field(
        name="3. 🔮 Thông Linh Bảo / Pháp Bảo Bản Mệnh (Hóa Thần – Luyện Hư) [Tỷ lệ: ~0.51%]",
        value=(
            "• 🪞 **Hạ / 🔮 Trung / 🌸 Thượng Phẩm Thông Linh Bảo**: Đã sinh khí linh (ý thức sơ khai hoặc hóa hình tiểu hài tử), tự động hộ chủ, biến hóa tùy ý.\n"
            "• 🏵️ **Chí Bảo Thông Linh**: Sinh ra từ thiên địa nguyên khí, uy lực vượt xa linh bảo thường."
        ),
        inline=False
    )
    embed.add_field(
        name="4. 🏮 Tiên Khí (Hợp Thể – Đại Thừa – Độ Kiếp / Phi Thăng) [Tỷ lệ: ~0.058%]",
        value=(
            "• 🟡 **Hạ Phẩm Tiên Khí**: Bắt đầu tích chứa Tiên Linh Khí thuần khiết của Chân Tiên.\n"
            "• 🌟 **Trung Phẩm Tiên Khí**: Uy lực có thể xé rách không gian hạ giới dễ dàng.\n"
            "• ✨ **Thượng Phẩm Tiên Khí**: Ẩn chứa quy tắc nhỏ của thiên địa đại đạo.\n"
            "• 🏮 **Cực Phẩm Tiên Khí**: Bảo vật Tiên Vương / Tiên Tôn cấp cao trấn áp chư thiên vạn giới."
        ),
        inline=False
    )
    embed.add_field(
        name="5. 👑 Hỗn Độn / Hồng Mông Chí Bảo (Hồng Hoang Đỉnh Cao) [Tỷ lệ: ~0.012%]",
        value=(
            "• 🔴 **Tiên Thiên Linh Bảo (Hạ, Trung, Thượng, Cực)**: Sinh ra từ hỗn độn khai thiên lập địa, mang theo đại đạo bản nguyên.\n"
            "• ☯️ **Hỗn Độn Chí Bảo**: Bàn Cổ Phủ, Thái Cực Đồ, Hỗn Độn Châu... sinh từ lúc hỗn độn chưa phân.\n"
            "• 👑 **Hồng Mông Chí Bảo**: Đứng đầu toàn bộ hệ thống trang bị tu tiên, nắm giữ trật tự tối thượng của vũ trụ!"
        ),
        inline=False
    )
    return embed

def create_random_equipment(user_id: int, realm_idx: int):
    """Tạo ngẫu nhiên một trang bị: Phàm Khí 70% giảm dần đến Hỗn Độn / Hồng Mông"""
    eq_type = random.choice(EQUIPMENT_TYPES)

    # Trọng số chuẩn trên 100,000 (100%):
    # Phàm Khí chuẩn 70% (70,000) giảm dần từng bậc đến 0.0004%
    base_weights = [
        # Tier 1: Phàm Khí / Pháp Khí
        70000,   # 0: Phàm Khí (Đúng 70.0%)
        12500,   # 1: Hạ Phẩm Pháp Khí (12.5%)
        6800,    # 2: Trung Phẩm Pháp Khí (6.8%)
        3700,    # 3: Thượng Phẩm Pháp Khí (3.7%)
        1600,    # 4: Cực Phẩm Pháp Khí (1.6%)

        # Tier 2: Linh Bảo
        2400,    # 5: Hạ Phẩm Linh Bảo (2.4%)
        1300,    # 6: Trung Phẩm Linh Bảo (1.3%)
        750,     # 7: Thượng Phẩm Linh Bảo (0.75%)
        370,     # 8: Cực Phẩm Linh Bảo (0.37%)

        # Tier 3: Thông Linh Bảo
        240,     # 9: Hạ Phẩm Thông Linh Bảo (0.24%)
        140,     # 10: Trung Phẩm Thông Linh Bảo (0.14%)
        80,      # 11: Thượng Phẩm Thông Linh Bảo (0.08%)
        50,      # 12: Chí Bảo Thông Linh (0.05%)

        # Tier 4: Tiên Khí
        30,      # 13: Hạ Phẩm Tiên Khí (0.03%)
        16,      # 14: Trung Phẩm Tiên Khí (0.016%)
        8,       # 15: Thượng Phẩm Tiên Khí (0.008%)
        4,       # 16: Cực Phẩm Tiên Khí (0.004%)

        # Tier 5: Hỗn Độn & Hồng Mông
        5,       # 17: Hạ Phẩm Tiên Thiên Linh Bảo (0.005%)
        3,       # 18: Trung Phẩm Tiên Thiên Linh Bảo (0.003%)
        2,       # 19: Thượng Phẩm Tiên Thiên Linh Bảo (0.002%)
        1,       # 20: Cực Phẩm Tiên Thiên Linh Bảo (0.001%)
        0.6,     # 21: Hỗn Độn Chí Bảo (0.0006%)
        0.4      # 22: Hồng Mông Chí Bảo (0.0004%)
    ]

    weights = list(base_weights)
    # Tu sĩ có cảnh giới cao hơn giảm nhẹ Phàm Khí chuyển sang các bậc phù hợp cảnh giới
    if realm_idx > 0:
        shift = min(realm_idx * 1200, 30000)
        weights[0] -= shift
        if realm_idx <= 7:
            target_tier = 1
        elif realm_idx <= 13:
            target_tier = 2
        elif realm_idx <= 19:
            target_tier = 3
        elif realm_idx <= 25:
            target_tier = 4
        else:
            target_tier = 5
        for i in range(1, len(weights)):
            g_tier = EQUIPMENT_GRADES[i]["tier"]
            if g_tier <= target_tier:
                weights[i] += (shift // (len(weights) - 1))

    grade_idx = random.choices(range(len(EQUIPMENT_GRADES)), weights=weights, k=1)[0]
    grade = get_equipment_grade(grade_idx)
    tier = grade["tier"]

    tier_names = EQUIPMENT_NAMES_BY_TIER.get(tier, EQUIPMENT_NAMES_BY_TIER[1])
    names_pool = tier_names.get(eq_type, EQUIPMENT_NAMES.get(eq_type, ["Bảo Vật"]))
    base_name = random.choice(names_pool)

    if tier == 5:
        eq_name = f"{grade['icon']} [{grade['name']}] {base_name}"
    else:
        eq_name = f"{grade['icon']} {grade['name']} {base_name}"

    r = REALMS[min(realm_idx, len(REALMS) - 1)]
    base_atk = max(50, r["atk"])
    base_def = max(30, r["def"])

    if eq_type == "Vũ Khí":
        atk_b = int(base_atk * grade["atk_mult"] * random.uniform(0.85, 1.15))
        def_b = int(base_def * grade["def_mult"] * 0.15 * random.uniform(0.85, 1.15))
    elif eq_type in ["Áo", "Giáp"]:
        atk_b = int(base_atk * grade["atk_mult"] * 0.15 * random.uniform(0.85, 1.15))
        def_b = int(base_def * grade["def_mult"] * random.uniform(0.85, 1.15))
    elif eq_type == "Quần":
        atk_b = int(base_atk * grade["atk_mult"] * 0.15 * random.uniform(0.85, 1.15))
        def_b = int(base_def * grade["def_mult"] * 0.85 * random.uniform(0.85, 1.15))
    elif eq_type == "Giày":
        atk_b = int(base_atk * grade["atk_mult"] * 0.35 * random.uniform(0.85, 1.15))
        def_b = int(base_def * grade["def_mult"] * 0.45 * random.uniform(0.85, 1.15))
    else:  # Nhẫn
        atk_b = int(base_atk * grade["atk_mult"] * 0.65 * random.uniform(0.85, 1.15))
        def_b = int(base_def * grade["def_mult"] * 0.35 * random.uniform(0.85, 1.15))

    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO equipment (user_id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped)
                 VALUES (?, ?, ?, ?, ?, ?, 0)""",
              (user_id, eq_type, eq_name, grade_idx, atk_b, def_b))
    conn.commit()
    conn.close()

    return {
        "eq_type": eq_type,
        "eq_name": eq_name,
        "grade": grade,
        "atk_bonus": atk_b,
        "def_bonus": def_b
    }

def perform_forge(user_id: int):
    player = get_player(user_id)
    if not player:
        return False, "❌ Hãy dùng `/nhapdao` trước để bắt đầu con đường tu tiên!"
    if player[6] < FORGE_COST:
        return False, f"❌ Không đủ Linh Thạch! Cần **{FORGE_COST:,} Linh Thạch** để rèn trang bị."

    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (FORGE_COST, user_id))
    conn.commit()
    conn.close()

    item = create_random_equipment(user_id, player[4])
    grade = item["grade"]

    rare_notice = ""
    if grade["tier"] == 5:
        rare_notice = "\n\n🌟🌌 **THIÊN ĐỊA DỊ TƯỢNG — HỒNG HOANG CHÍ BẢO XUẤT THẾ!**\n*Khí tức hỗn độn chấn động Cửu Châu, tam giới quỳ lạy kính sợ!*"
    elif grade["tier"] == 4:
        rare_notice = "\n\n🏮✨ **TIÊN QUANG HÀO PHÓNG — TIÊN KHÍ XUẤT LÒ!**\n*Tiên linh khí thuần khiết chiếu rọi vạn dặm, thiên kiếp né tránh!*"
    elif grade["tier"] == 3:
        rare_notice = "\n\n🔮🌸 **THÔNG LINH BẢO SINH KHÍ LINH!**\n*Pháp bảo có linh trí, biến hóa khôn lường tự động nhận chủ hộ vệ!*"

    embed = discord.Embed(
        title="⚒️ RÈN TẠO THÀNH CÔNG!",
        description=(
            f"**Cấp bậc:** Tier {grade['tier']} — **{grade['tier_name']}** ({grade['stage']})\n"
            f"**Phẩm cấp:** {grade['icon']} **{grade['name']}**\n"
            f"📜 *\"{grade['desc']}\"*\n\n"
            f"📦 **{item['eq_name']}** ({item['eq_type']})\n"
            f"🗡️ Công kích: +`{item['atk_bonus']:,}` | 🛡️ Phòng ngự: +`{item['def_bonus']:,}`"
            f"{rare_notice}\n\n"
            f"*Dùng lệnh `/trangbi` hoặc `t trangbi` để xem và đeo pháp bảo.*"
        ),
        color=grade["color"]
    )
    return True, embed

def perform_auto_equip(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped
                 FROM equipment WHERE user_id = ?""", (user_id,))
    items = c.fetchall()
    if not items:
        conn.close()
        return False, "❌ Đạo hữu chưa có bất kỳ trang bị nào trong kho! Hãy rèn đồ bằng `/ren` hoặc đi thám hiểm."

    # Gom nhóm theo từng loại trang bị (Vũ Khí, Giáp, Giày, Nhẫn)
    type_items = {}
    for it in items:
        eq_t = it[1]
        if eq_t not in type_items:
            type_items[eq_t] = []
        type_items[eq_t].append(it)

    best_item_ids = []
    equipped_details = []

    for eq_t, list_it in type_items.items():
        def item_score(x):
            iid, itype, iname, igrade, iatk, idef, iequip = x
            if itype == "Vũ Khí":
                return iatk * 2.5 + idef * 0.5 + igrade * 1000
            elif itype in ["Áo", "Giáp"]:
                return idef * 2.5 + iatk * 0.5 + igrade * 1000
            elif itype == "Quần":
                return idef * 2.2 + iatk * 0.6 + igrade * 1000
            elif itype == "Giày":
                return idef * 1.8 + iatk * 1.2 + igrade * 1000
            elif itype == "Nhẫn":
                return iatk * 1.8 + idef * 1.2 + igrade * 1000
            return (iatk + idef) + igrade * 1000

        list_it.sort(key=item_score, reverse=True)
        best = list_it[0]
        best_item_ids.append(best[0])
        equipped_details.append(best)

    # Tháo toàn bộ và trang bị các món tối ưu
    c.execute("UPDATE equipment SET is_equipped = 0 WHERE user_id = ?", (user_id,))
    for bid in best_item_ids:
        c.execute("UPDATE equipment SET is_equipped = 1 WHERE id = ?", (bid,))
    conn.commit()
    conn.close()

    new_atk = sum(it[4] for it in equipped_details)
    new_def = sum(it[5] for it in equipped_details)

    lines = []
    slot_icons = {"Vũ Khí": "🗡️", "Áo": "🥋", "Quần": "👖", "Giày": "👟", "Nhẫn": "💍", "Giáp": "🥋"}
    slot_order = {"Vũ Khí": 1, "Áo": 2, "Giáp": 2, "Quần": 3, "Giày": 4, "Nhẫn": 5}
    equipped_details.sort(key=lambda x: slot_order.get(x[1], 99))

    for it in equipped_details:
        iid, itype, iname, igrade, iatk, idef, iequip = it
        grade = get_equipment_grade(igrade)
        icon = slot_icons.get(itype, "✨")
        lines.append(f"{icon} **{itype}:** {iname} (`{grade['tier_name']}`)\n   └ 🗡️ +`{iatk:,}` | 🛡️ +`{idef:,}`")

    embed = discord.Embed(
        title="⚡ TỰ ĐỘNG TRANG BỊ TỐI ƯU THÀNH CÔNG!",
        description=(
            f"Thiên Đạo Vận Chuyển — Đã tự động trang bị bộ 5 pháp bảo mạnh nhất:\n\n"
            + "\n\n".join(lines) + "\n\n"
            f"────────────────────────────────────────\n"
            f"✨ **Tổng Uy Năng Sau Tối Ưu:** 🗡️ +`{new_atk:,}` Công | 🛡️ +`{new_def:,}` Thủ"
        ),
        color=0x2ecc71
    )
    embed.set_footer(text="Bộ ngũ đại pháp bảo tối ưu đã sẵn sàng nghênh chiến!")
    return True, embed

class TrangBiView(discord.ui.View):
    def __init__(self, user_id: int, items, prefix: str = "/"):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.prefix = prefix

        if items:
            options = []
            for item in items[:25]:
                iid, itype, iname, igrade, iatk, idef, iequip = item
                grade = get_equipment_grade(igrade)
                options.append(discord.SelectOption(
                    label=f"{'[ĐM] ' if iequip else ''}{iname[:45]}",
                    value=str(iid),
                    description=f"[{itype}] {grade['name']} | ATK+{iatk:,} DEF+{idef:,}"[:100],
                    emoji=grade["icon"]
                ))
            select = discord.ui.Select(placeholder="Chọn trang bị để đeo vào hoặc tháo ra...", options=options, row=0)
            select.callback = self.on_select_item
            self.add_item(select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Kho trang bị không phải của đạo hữu!", ephemeral=True)
            return False
        return True

    async def on_select_item(self, interaction: discord.Interaction):
        item_id = int(interaction.data["values"][0])
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT eq_type, eq_name, is_equipped FROM equipment WHERE id = ? AND user_id = ?",
                  (item_id, self.user_id))
        row = c.fetchone()
        if not row:
            conn.close()
            return await interaction.response.send_message("❌ Không tìm thấy trang bị!", ephemeral=True)
        eq_type, eq_name, is_equipped = row
        if is_equipped:
            c.execute("UPDATE equipment SET is_equipped = 0 WHERE id = ?", (item_id,))
            msg = f"🔓 Đã tháo **{eq_name}**."
        else:
            c.execute("UPDATE equipment SET is_equipped = 0 WHERE user_id = ? AND eq_type = ?",
                      (self.user_id, eq_type))
            c.execute("UPDATE equipment SET is_equipped = 1 WHERE id = ?", (item_id,))
            msg = f"✅ Đã trang bị **{eq_name}**!"
        conn.commit()
        conn.close()

        embed, view = create_trangbi_embed_and_view(self.user_id, self.prefix)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Trang Bị Nhanh (Tối Ưu)", emoji="⚡", style=discord.ButtonStyle.success, row=1)
    async def btn_auto_equip(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, res = perform_auto_equip(self.user_id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        embed, view = create_trangbi_embed_and_view(self.user_id, self.prefix)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(embed=res, ephemeral=True)

    @discord.ui.button(label="Bán Đồ Thừa (Sell All)", emoji="💰", style=discord.ButtonStyle.danger, row=1)
    async def btn_sell_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        from cogs.vanbaolau import perform_sell_all
        success, res = perform_sell_all(self.user_id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        embed, view = create_trangbi_embed_and_view(self.user_id, self.prefix)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(embed=res, ephemeral=True)

    @discord.ui.button(label=f"Rèn Trang Bị ({FORGE_COST:,} LT)", emoji="⚒️", style=discord.ButtonStyle.primary, row=1)
    async def btn_ren(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, res = perform_forge(self.user_id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        embed, view = create_trangbi_embed_and_view(self.user_id, self.prefix)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(embed=res, ephemeral=True)

    @discord.ui.button(label="Bảng Cấp Bậc & Tỉ Lệ", emoji="📜", style=discord.ButtonStyle.secondary, row=1)
    async def btn_capbac(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_capbac_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

def create_trangbi_embed_and_view(user_id: int, prefix: str = "/"):
    player = get_player(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped
                 FROM equipment WHERE user_id = ?
                 ORDER BY is_equipped DESC, grade DESC, id DESC""",
              (user_id,))
    items = c.fetchall()
    conn.close()

    equipped_items = [it for it in items if it[6] == 1]
    eq_atk, eq_def = get_equipment_bonus(user_id)

    embed = discord.Embed(
        title="⚔️ THÂN THỂ PHÁP BẢO & TRANG BỊ",
        description=(
            f"👤 Đạo hữu: **{player[1]}** ({player[2]})\n"
            f"💎 Linh Thạch: **`{player[6]:,}` LT** | 📦 Tổng kho: **`{len(items)}` món**\n"
            f"🥋 Đang trang bị: **`{len(equipped_items)}/5` món**\n"
            f"✨ Tổng Uy Năng Thần Binh: 🗡️ +`{eq_atk:,}` | 🛡️ +`{eq_def:,}`\n"
            "────────────────────────────────────────\n"
            "*(Dùng menu bên dưới để Đeo/Tháo, hoặc bấm **[⚡ Trang Bị Nhanh]** để tối ưu)*"
        ),
        color=0xe67e22
    )

    slot_icons = {"Vũ Khí": "🗡️", "Áo": "🥋", "Quần": "👖", "Giày": "👟", "Nhẫn": "💍", "Giáp": "🥋"}

    if not items:
        embed.description += "\n\n📦 *Kho trang bị đang trống! Hãy bấm nút **[⚒️ Rèn Trang Bị]** bên dưới để rèn.*"
    elif not equipped_items:
        embed.add_field(
            name="🥋 Thân Thể Trống Không",
            value="*Chưa mang trang bị nào trên người! Hãy bấm nút **[⚡ Trang Bị Nhanh]** để tự động mặc các món tốt nhất.*",
            inline=False
        )
    else:
        # CHỈ HIỂN THỊ CÁC MÓN ĐỒ ĐANG ĐEO TRÊN NGƯỜI (Sắp xếp theo thứ tự 5 slot: Vũ Khí, Áo, Quần, Giày, Nhẫn)
        slot_order = {"Vũ Khí": 1, "Áo": 2, "Giáp": 2, "Quần": 3, "Giày": 4, "Nhẫn": 5}
        equipped_sorted = sorted(equipped_items, key=lambda x: slot_order.get(x[1], 99))
        for item in equipped_sorted:
            iid, itype, iname, igrade, iatk, idef, iequip = item
            grade = get_equipment_grade(igrade)
            icon = slot_icons.get(itype, "✨")
            embed.add_field(
                name=f"{icon} [{itype}] {iname}",
                value=f"🏷️ `{grade['tier_name']}` ({grade['name']})\n🗡️ +`{iatk:,}` | 🛡️ +`{idef:,}`",
                inline=False
            )

    view = TrangBiView(user_id, items, prefix)
    return embed, view

class EquipmentCog(commands.Cog, name="Trang Bị"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trangbi", description="Xem các pháp bảo đang trang bị trên người và quản lý kho đồ")
    async def trangbi(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed, view = create_trangbi_embed_and_view(interaction.user.id, "/")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="trangbi", aliases=["tb", "hanhtrang", "ruong", "i", "inv", "inventory", "tuido"])
    async def prefix_trangbi(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed, view = create_trangbi_embed_and_view(ctx.author.id, ctx.prefix)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="trangbinhanh", description="Tự động trang bị những món pháp bảo tối ưu nhất cho từng vị trí")
    async def trangbinhanh(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        success, res = perform_auto_equip(interaction.user.id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        await interaction.response.send_message(embed=res)

    @commands.command(name="trangbinhanh", aliases=["tbnhanh", "toiuu", "autoequip", "aeq", "tbopt", "quickequip"])
    async def prefix_trangbinhanh(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        success, res = perform_auto_equip(ctx.author.id)
        if not success:
            return await ctx.send(res)
        await ctx.send(embed=res)

    @app_commands.command(name="ren", description=f"Luyện Khí Lô — Tiêu hao {FORGE_COST:,} Linh Thạch để rèn trang bị mới")
    async def ren(self, interaction: discord.Interaction):
        success, res = perform_forge(interaction.user.id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        await interaction.response.send_message(embed=res)

    @commands.command(name="ren", aliases=["chetao", "luyenkhi", "ri"])
    async def prefix_ren(self, ctx: commands.Context):
        success, res = perform_forge(ctx.author.id)
        if not success:
            return await ctx.send(res)
        await ctx.send(embed=res)

    @app_commands.command(name="capbactrangbi", description="Xem toàn bộ 5 Đại Cấp Bậc pháp bảo, 23 phẩm cấp và tỷ lệ xuất hiện")
    async def capbactrangbi(self, interaction: discord.Interaction):
        embed = create_capbac_embed()
        await interaction.response.send_message(embed=embed)

    @commands.command(name="capbactrangbi", aliases=["capbac", "phapbao", "capbactb"])
    async def prefix_capbactrangbi(self, ctx: commands.Context):
        embed = create_capbac_embed()
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EquipmentCog(bot))
