import time
import discord
from discord import app_commands
from discord.ext import commands
from config import get_equipment_grade
from database import get_player, get_connection

INSTANT_SELL_BASE = [
    # Tier 1: Phàm Khí / Pháp Khí
    50, 90, 150, 260, 450,
    # Tier 2: Linh Bảo
    800, 1400, 2400, 4000,
    # Tier 3: Thông Linh Bảo
    7000, 12000, 20000, 35000,
    # Tier 4: Tiên Khí
    60000, 100000, 180000, 300000,
    # Tier 5: Hỗn Độn / Hồng Mông
    600000, 1200000, 2500000, 5000000, 10000000, 30000000
]

def calc_instant_price(grade_idx: int, atk_b: int = 0, def_b: int = 0) -> int:
    idx = max(0, min(grade_idx, len(INSTANT_SELL_BASE) - 1))
    base = INSTANT_SELL_BASE[idx]
    bonus = int((atk_b + def_b) * 0.15)
    return base + bonus

def get_market_items():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, seller_id, seller_name, item_name, item_type, atk_bonus, def_bonus, price FROM market ORDER BY id DESC LIMIT 15")
    rows = c.fetchall()
    conn.close()
    return rows

def get_unequipped_items(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus
                 FROM equipment
                 WHERE user_id = ? AND is_equipped = 0
                 ORDER BY grade DESC, id DESC LIMIT 25""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def perform_sell_all(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus
                 FROM equipment
                 WHERE user_id = ? AND is_equipped = 0
                 ORDER BY grade DESC, id DESC""", (user_id,))
    unequipped_items = c.fetchall()

    if not unequipped_items:
        conn.close()
        return False, "📦 Kho đồ của đạo hữu không có pháp bảo nào chưa trang bị để bán!\n*(Các món đang đeo trên nhân vật được bảo vệ an toàn tuyệt đối)*"

    total_price = 0
    tier_summary = {}

    for it in unequipped_items:
        iid, itype, iname, igrade, iatk, idef = it
        price = calc_instant_price(igrade, iatk, idef)
        total_price += price

        grade = get_equipment_grade(igrade)
        tier_key = f"{grade['icon']} Tier {grade['tier']} ({grade['tier_name']})"
        if tier_key not in tier_summary:
            tier_summary[tier_key] = {"count": 0, "price": 0}
        tier_summary[tier_key]["count"] += 1
        tier_summary[tier_key]["price"] += price

    # Xóa các món chưa trang bị
    c.execute("DELETE FROM equipment WHERE user_id = ? AND is_equipped = 0", (user_id,))
    # Cộng linh thạch
    c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (total_price, user_id))
    conn.commit()

    c.execute("SELECT linh_thach FROM players WHERE user_id = ?", (user_id,))
    p_row = c.fetchone()
    current_lt = p_row[0] if p_row else 0
    conn.close()

    summary_lines = []
    for t_key, data in tier_summary.items():
        summary_lines.append(f"• **{t_key}:** `{data['count']}` món → `+{data['price']:,}` LT")

    embed = discord.Embed(
        title="💰 THU MUA TOÀN BỘ PHÁP BẢO — VẠN BẢO LÂU",
        description=(
            f"Chưởng quầy Vạn Bảo Lâu đã thẩm định và thu mua toàn bộ trang bị dự trữ trong túi đồ:\n\n"
            f"📦 **Tổng số lượng bán:** `{len(unequipped_items)}` món\n"
            + "\n".join(summary_lines) + "\n\n"
            f"────────────────────────────────────────\n"
            f"💎 **Tổng Linh Thạch thu về:** `+{total_price:,}` Linh Thạch\n"
            f"💰 **Số dư Linh Thạch hiện có:** `{current_lt:,}` Linh Thạch\n\n"
            f"🛡️ *Toàn bộ trang bị đang đeo trên nhân vật được bảo lưu an toàn 100%!*"
        ),
        color=0x2ecc71
    )
    embed.set_footer(text="Giao dịch thành công • Vạn Bảo Lâu hân hạnh phục vụ đạo hữu!")
    return True, embed

class TreoBanModal(discord.ui.Modal, title="Treo Bán Lên Vạn Bảo Lâu"):
    def __init__(self, item_id: int, item_name: str, item_type: str, atk_bonus: int, def_bonus: int):
        super().__init__()
        self.item_id = item_id
        self.item_name = item_name
        self.item_type = item_type
        self.atk_bonus = atk_bonus
        self.def_bonus = def_bonus

        self.price_input = discord.ui.TextInput(
            label="Giá bán mong muốn (Linh Thạch)",
            placeholder="Ví dụ: 1000 (Tối thiểu 100 LT - Phí sàn 10%)",
            min_length=3,
            max_length=10,
            required=True
        )
        self.add_item(self.price_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price_input.value.strip())
        except ValueError:
            return await interaction.response.send_message("❌ Giá bán phải là số nguyên hợp lệ!", ephemeral=True)

        if price < 100:
            return await interaction.response.send_message("❌ Giá bán tối thiểu trên Vạn Bảo Lâu là 100 Linh Thạch!", ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, eq_type, eq_name, atk_bonus, def_bonus, is_equipped, grade FROM equipment WHERE id = ? AND user_id = ?",
                  (self.item_id, interaction.user.id))
        row = c.fetchone()
        if not row:
            conn.close()
            return await interaction.response.send_message("❌ Không tìm thấy trang bị này trong kho của đạo hữu!", ephemeral=True)
        if row[5]:
            conn.close()
            return await interaction.response.send_message("❌ Vui lòng tháo trang bị ra trước khi treo bán!", ephemeral=True)

        item_grade = row[6] if len(row) > 6 and row[6] is not None else 0
        c.execute("DELETE FROM equipment WHERE id = ?", (self.item_id,))
        now = int(time.time())
        c.execute("""INSERT INTO market (seller_id, seller_name, item_name, item_type, atk_bonus, def_bonus, price, created_at, grade)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (interaction.user.id, interaction.user.display_name, row[2], row[1], row[3], row[4], price, now, item_grade))
        conn.commit()
        conn.close()

        seller_receive = int(price * 0.90)
        fee = price - seller_receive

        embed = discord.Embed(
            title="🏛️ NIÊM YẾT VẠN BẢO LÂU THÀNH CÔNG!",
            description=(
                f"Đạo hữu đã treo bán thành công **{row[2]}** lên sàn giao dịch!\n\n"
                f"🏷️ **Loại:** {row[1]} | 🗡️ +`{row[3]:,}` 🛡️ +`{row[4]:,}`\n"
                f"💎 **Giá niêm yết:** `{price:,}` Linh Thạch\n"
                f"💼 **Phí sàn Vạn Bảo Lâu (10%):** `{fee:,}` Linh Thạch\n"
                f"💰 **Thực nhận khi có người mua:** `{seller_receive:,}` Linh Thạch\n\n"
                f"*Các tu sĩ khác có thể tìm mua món đồ này qua `/vanbaolau` hoặc `t vanbaolau`.*"
            ),
            color=0x16a085
        )
        await interaction.response.send_message(embed=embed)

class BanPhapBaoActionView(discord.ui.View):
    def __init__(self, user_id: int, item_data, instant_price: int, items_map: dict):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.item_data = item_data
        self.instant_price = instant_price
        self.items_map = items_map

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây không phải kho đồ của đạo hữu!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Treo Bán Lên Sàn (Phí 10%)", emoji="🏪", style=discord.ButtonStyle.primary)
    async def btn_treo_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoBanModal(
            self.item_data[0],
            self.item_data[2],
            self.item_data[1],
            self.item_data[4],
            self.item_data[5]
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Bán Luôn Cho Tiệm", emoji="⚡", style=discord.ButtonStyle.success)
    async def btn_ban_ngay(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, eq_type, eq_name, is_equipped FROM equipment WHERE id = ? AND user_id = ?",
                  (self.item_data[0], self.user_id))
        row = c.fetchone()
        if not row:
            conn.close()
            return await interaction.response.send_message("❌ Món đồ này không còn trong kho!", ephemeral=True)
        if row[3]:
            conn.close()
            return await interaction.response.send_message("❌ Trang bị đang mang trên người, hãy tháo ra trước!", ephemeral=True)

        c.execute("DELETE FROM equipment WHERE id = ?", (self.item_data[0],))
        c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?",
                  (self.instant_price, self.user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="💰 THU MUA THÀNH CÔNG — VẠN BẢO LÂU",
            description=(
                f"Chưởng quầy Vạn Bảo Lâu đã thẩm định và thu mua đứt đoạn:\n\n"
                f"📦 **{row[2]}** ({row[1]})\n"
                f"💎 Đạo hữu đã nhận ngay **+{self.instant_price:,} Linh Thạch** vào túi trữ vật!"
            ),
            color=0x2ecc71
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Chọn Món Khác", emoji="🔙", style=discord.ButtonStyle.secondary)
    async def btn_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        items = get_unequipped_items(self.user_id)
        if not items:
            return await interaction.response.edit_message(
                content="📦 Kho đồ không còn pháp bảo nào chưa trang bị để bán!",
                embed=None,
                view=None
            )
        embed, view = create_banphapbao_embed_and_view(self.user_id, items)
        await interaction.response.edit_message(embed=embed, view=view)

class BanPhapBaoView(discord.ui.View):
    def __init__(self, user_id: int, items):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.items_map = {it[0]: it for it in items}

        options = []
        for it in items[:25]:
            iid, itype, iname, igrade, iatk, idef = it[:6]
            instant_p = calc_instant_price(igrade, iatk, idef)
            grade = get_equipment_grade(igrade)
            options.append(discord.SelectOption(
                label=f"{iname[:40]} ({itype})",
                value=str(iid),
                description=f"{grade['name']} | 🗡️+{iatk:,} 🛡️+{idef:,} | Tiệm: ~{instant_p:,} LT",
                emoji=grade["icon"]
            ))

        select = discord.ui.Select(placeholder="Chọn trang bị muốn bán...", options=options)
        select.callback = self.on_select_item
        self.add_item(select)

    @discord.ui.button(label="Bán Toàn Bộ (Sell All)", emoji="💰", style=discord.ButtonStyle.danger, row=1)
    async def btn_sell_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, res = perform_sell_all(self.user_id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        await interaction.response.edit_message(embed=res, view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Đây không phải kho đồ của đạo hữu!", ephemeral=True)
            return False
        return True

    async def on_select_item(self, interaction: discord.Interaction):
        item_id = int(interaction.data["values"][0])
        it = self.items_map.get(item_id)
        if not it:
            return await interaction.response.send_message("❌ Không tìm thấy trang bị!", ephemeral=True)

        iid, itype, iname, igrade, iatk, idef = it[:6]
        instant_p = calc_instant_price(igrade, iatk, idef)
        grade = get_equipment_grade(igrade)

        embed = discord.Embed(
            title="🏛️ XÁC NHẬN PHƯƠNG THỨC BÁN PHÁP BẢO",
            description=(
                f"Đạo hữu đã chọn: **{iname}** ({itype})\n"
                f"🏷️ Cấp bậc: Tier {grade['tier']} — **{grade['tier_name']}** ({grade['icon']} **{grade['name']}**)\n"
                f"📜 *\"{grade['desc']}\"*\n"
                f"🗡️ Công kích: +`{iatk:,}` | 🛡️ Phòng ngự: +`{idef:,}`\n\n"
                f"**Chọn một trong hai phương thức bán bên dưới:**\n\n"
                f"1. 🏪 **Treo Bán Tại Sàn Vạn Bảo Lâu:**\n"
                f"   • Tự do định giá bán cho các tu sĩ khác mua.\n"
                f"   • Phí sàn: **10%** tổng Linh Thạch bán (thực nhận 90% khi có người mua).\n\n"
                f"2. ⚡ **Bán Luôn Cho Vạn Bảo Lâu:**\n"
                f"   • Chưởng quầy Vạn Bảo Lâu thu mua đứt đoạn ngay lập tức!\n"
                f"   • Giá thu mua: **`+{instant_p:,}` Linh Thạch** (Cộng thẳng vào túi)."
            ),
            color=grade["color"]
        )
        action_view = BanPhapBaoActionView(self.user_id, it, instant_p, self.items_map)
        action_view.btn_ban_ngay.label = f"Bán Cho Tiệm (+{instant_p:,} LT)"
        await interaction.response.edit_message(embed=embed, view=action_view)

def create_banphapbao_embed_and_view(user_id: int, items):
    player = get_player(user_id)
    embed = discord.Embed(
        title="🏛️ VẠN BẢO LÂU — BÁN PHÁP BẢO",
        description=(
            f"💎 Linh thạch hiện có: **`{player[6]:,}` LT**\n"
            f"📦 Số pháp bảo chưa trang bị: **`{len(items)}` món**\n\n"
            "📜 **Chọn trang bị cần bán từ danh mục bên dưới:**\n"
            "• 🏪 **Treo bán tại sàn:** Tự đặt giá, phí sàn 10% (Nhận 90% khi có người mua).\n"
            "• ⚡ **Bán luôn cho Vạn Bảo Lâu:** Thu mua ngay lập tức lấy Linh Thạch!\n"
            "• 💰 **Bán toàn bộ (Sell All):** Bấm nút đỏ bên dưới hoặc gõ `sellall`."
        ),
        color=0x16a085
    )
    view = BanPhapBaoView(user_id, items)
    return embed, view

class VanBaoLauView(discord.ui.View):
    def __init__(self, user_id: int, items):
        super().__init__(timeout=120)
        self.user_id = user_id

        if items:
            options = [
                discord.SelectOption(
                    label=f"{it[3][:45]} — {it[7]:,} LT",
                    value=str(it[0]),
                    description=f"Bán bởi {it[2]} | ATK+{it[5]} DEF+{it[6]}"
                )
                for it in items[:15]
            ]
            select = discord.ui.Select(placeholder="Chọn bảo vật muốn mua từ chợ...", options=options, row=0)
            select.callback = self.select_buy
            self.add_item(select)

    @discord.ui.button(label="Bán Pháp Bảo", emoji="📦", style=discord.ButtonStyle.secondary, row=1)
    async def btn_ban_phapbao(self, interaction: discord.Interaction, button: discord.ui.Button):
        items = get_unequipped_items(self.user_id)
        if not items:
            return await interaction.response.send_message(
                "📦 Kho đồ không có pháp bảo nào chưa trang bị để bán! (Nếu đang mang, hãy tháo ra trong `/trangbi` trước).",
                ephemeral=True
            )
        embed, view = create_banphapbao_embed_and_view(self.user_id, items)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def select_buy(self, interaction: discord.Interaction):
        item_id = int(interaction.data["values"][0])
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, seller_id, seller_name, item_name, item_type, atk_bonus, def_bonus, price, grade FROM market WHERE id = ?", (item_id,))
        item = c.fetchone()

        if not item:
            conn.close()
            return await interaction.response.send_message("❌ Bảo vật này đã có người khác mua mất rồi!", ephemeral=True)

        if item[1] == interaction.user.id:
            conn.close()
            return await interaction.response.send_message("❌ Không thể tự mua bảo vật do chính mình rao bán!", ephemeral=True)

        buyer = get_player(interaction.user.id)
        if not buyer or buyer[6] < item[7]:
            conn.close()
            return await interaction.response.send_message(f"❌ Không đủ Linh Thạch! Cần **{item[7]:,} Linh Thạch**.", ephemeral=True)

        # Chuyển tiền & nhận đồ (Phí sàn 10%: người bán nhận 90%)
        seller_receive = int(item[7] * 0.90)
        fee = item[7] - seller_receive
        item_grade = item[8] if len(item) > 8 and item[8] is not None else 0
        c.execute("UPDATE players SET linh_thach = linh_thach - ? WHERE user_id = ?", (item[7], interaction.user.id))
        c.execute("UPDATE players SET linh_thach = linh_thach + ? WHERE user_id = ?", (seller_receive, item[1]))
        c.execute("""INSERT INTO equipment (user_id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped)
                     VALUES (?, ?, ?, ?, ?, ?, 0)""", (interaction.user.id, item[4], item[3], item_grade, item[5], item[6]))
        c.execute("DELETE FROM market WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🎉 Giao dịch thành công! Đạo hữu đã mua **{item[3]}** với giá **{item[7]:,} Linh Thạch**!\n"
            f"*(Chủ tiệm thực nhận **{seller_receive:,} LT**, Vạn Bảo Lâu thu phí sàn 10%: **{fee:,} LT**)*\n"
            f"Vật phẩm đã được chuyển vào `/trangbi` của bạn.",
            ephemeral=True
        )

class VanBaoLauCog(commands.Cog, name="Vạn Bảo Lâu"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vanbaolau", description="Mở Vạn Bảo Lâu — Sàn đấu giá & chợ giao dịch giữa các tu sĩ")
    async def vanbaolau(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        items = get_market_items()
        embed = discord.Embed(
            title="🏛️ VẠN BẢO LÂU — CHỢ ĐẤU GIÁ TIÊN GIA",
            description=(
                f"💎 Linh thạch của bạn: **`{player[6]:,}`**\n"
                "Nơi giao thương sầm uất bậc nhất tam giới. Các tu sĩ có thể tự do trao đổi pháp bảo!\n"
                "*(Dùng lệnh `/banphapbao` hoặc bấm nút bên dưới để bán đồ)*"
            ),
            color=0x16a085
        )

        if not items:
            embed.add_field(name="📦 Chợ Đang Trống", value="Hiện chưa có ai treo bán bảo vật. Hãy là người đầu tiên!", inline=False)
        else:
            for it in items[:6]:
                embed.add_field(
                    name=f"⚔️ {it[3]} ({it[4]}) — Giá: `{it[7]:,}` LT",
                    value=f"👤 Bán bởi: **{it[2]}** | 🗡️+{it[5]} 🛡️+{it[6]}",
                    inline=False
                )

        view = VanBaoLauView(interaction.user.id, items)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="banphapbao", description="Bán hoặc treo bán trang bị lên Vạn Bảo Lâu (Phí sàn 10% hoặc bán ngay)")
    @app_commands.describe(
        id_trang_bi="ID trang bị (để trống để mở danh sách chọn)",
        gia_ban="Giá bán bằng Linh Thạch (để trống nếu muốn bán nhanh cho tiệm)"
    )
    async def banphapbao(self, interaction: discord.Interaction, id_trang_bi: int = None, gia_ban: int = None):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Chưa nhập đạo!", ephemeral=True)

        if id_trang_bi is None:
            items = get_unequipped_items(interaction.user.id)
            if not items:
                return await interaction.response.send_message(
                    "📦 Kho đồ không có pháp bảo nào chưa trang bị để bán!\n*(Lưu ý: Nếu trang bị đang mang trên người, hãy vào `/trangbi` để tháo ra trước)*",
                    ephemeral=True
                )
            embed, view = create_banphapbao_embed_and_view(interaction.user.id, items)
            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped FROM equipment WHERE id = ? AND user_id = ?",
                  (id_trang_bi, interaction.user.id))
        row = c.fetchone()
        conn.close()
        if not row:
            return await interaction.response.send_message("❌ Không tìm thấy trang bị này trong kho của đạo hữu!", ephemeral=True)
        if row[6]:
            return await interaction.response.send_message("❌ Vui lòng tháo trang bị ra trước khi treo bán!", ephemeral=True)

        grade = get_equipment_grade(row[3])

        if gia_ban is not None:
            if gia_ban < 100:
                return await interaction.response.send_message("❌ Giá bán tối thiểu là 100 Linh Thạch!", ephemeral=True)

            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM equipment WHERE id = ?", (id_trang_bi,))
            now = int(time.time())
            c.execute("""INSERT INTO market (seller_id, seller_name, item_name, item_type, atk_bonus, def_bonus, price, created_at, grade)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (interaction.user.id, interaction.user.display_name, row[2], row[1], row[4], row[5], gia_ban, now, row[3]))
            conn.commit()
            conn.close()

            seller_receive = int(gia_ban * 0.90)
            fee = gia_ban - seller_receive
            embed = discord.Embed(
                title="🏛️ NIÊM YẾT VẠN BẢO LÂU THÀNH CÔNG!",
                description=(
                    f"Đạo hữu đã treo bán thành công **{row[2]}** lên sàn giao dịch!\n\n"
                    f"🏷️ **Cấp bậc:** Tier {grade['tier']} — **{grade['tier_name']}** ({grade['icon']} {grade['name']})\n"
                    f"🏷️ **Loại:** {row[1]} | 🗡️ +`{row[4]:,}` 🛡️ +`{row[5]:,}`\n"
                    f"💎 **Giá niêm yết:** `{gia_ban:,}` Linh Thạch\n"
                    f"💼 **Phí sàn Vạn Bảo Lâu (10%):** `{fee:,}` Linh Thạch\n"
                    f"💰 **Thực nhận khi có người mua:** `{seller_receive:,}` Linh Thạch"
                ),
                color=grade["color"]
            )
            return await interaction.response.send_message(embed=embed)

        instant_p = calc_instant_price(row[3], row[4], row[5])
        embed = discord.Embed(
            title="🏛️ XÁC NHẬN PHƯƠNG THỨC BÁN PHÁP BẢO",
            description=(
                f"Đạo hữu đã chọn: **{row[2]}** ({row[1]})\n"
                f"🏷️ **Cấp bậc:** Tier {grade['tier']} — **{grade['tier_name']}** ({grade['icon']} {grade['name']})\n"
                f"📜 *\"{grade['desc']}\"*\n"
                f"🗡️ Công kích: +`{row[4]:,}` | 🛡️ Phòng ngự: +`{row[5]:,}`\n\n"
                f"**Chọn một trong hai phương thức bán bên dưới:**\n\n"
                f"1. 🏪 **Treo Bán Tại Sàn Vạn Bảo Lâu:**\n"
                f"   • Tự do định giá bán cho các tu sĩ khác mua.\n"
                f"   • Phí sàn: **10%** tổng Linh Thạch bán (thực nhận 90% khi có người mua).\n\n"
                f"2. ⚡ **Bán Luôn Cho Vạn Bảo Lâu:**\n"
                f"   • Chưởng quầy Vạn Bảo Lâu thu mua đứt đoạn ngay lập tức!\n"
                f"   • Giá thu mua: **`+{instant_p:,}` Linh Thạch** (Cộng thẳng vào túi)."
            ),
            color=grade["color"]
        )
        action_view = BanPhapBaoActionView(interaction.user.id, row[:6], instant_p, {})
        action_view.btn_ban_ngay.label = f"Bán Cho Tiệm (+{instant_p:,} LT)"
        return await interaction.response.send_message(embed=embed, view=action_view, ephemeral=True)

    @commands.command(name="vanbaolau", aliases=["vbl", "market", "chodaugia"])
    async def prefix_vanbaolau(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        items = get_market_items()
        embed = discord.Embed(
            title="🏛️ VẠN BẢO LÂU — CHỢ ĐẤU GIÁ TIÊN GIA",
            description=(
                f"💎 Linh thạch của bạn: **`{player[6]:,}`**\n"
                "Nơi giao thương sầm uất bậc nhất tam giới. Các tu sĩ có thể tự do trao đổi pháp bảo!\n"
                f"*(Dùng lệnh `{ctx.prefix}banphapbao` hoặc bấm nút bên dưới để bán đồ)*"
            ),
            color=0x16a085
        )

        if not items:
            embed.add_field(name="📦 Chợ Đang Trống", value="Hiện chưa có ai treo bán bảo vật. Hãy là người đầu tiên!", inline=False)
        else:
            for it in items[:6]:
                embed.add_field(
                    name=f"⚔️ {it[3]} ({it[4]}) — Giá: `{it[7]:,}` LT",
                    value=f"👤 Bán bởi: **{it[2]}** | 🗡️+{it[5]} 🛡️+{it[6]}",
                    inline=False
                )

        view = VanBaoLauView(ctx.author.id, items)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="banphapbao", aliases=["ban", "sell"])
    async def prefix_banphapbao(self, ctx: commands.Context, *, args: str = None):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Chưa nhập đạo! Dùng `{ctx.prefix}nhapdao` trước.")

        id_trang_bi = None
        gia_ban = None

        if args:
            clean_arg = args.strip().lower()
            if clean_arg in ["all", "het", "toanbo", "tatca", "allitems"]:
                success, res = perform_sell_all(ctx.author.id)
                if not success:
                    return await ctx.send(res)
                return await ctx.send(embed=res)

            parts = args.strip().split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                id_trang_bi = int(parts[0])
                gia_ban = int(parts[1])
            elif len(parts) == 1 and parts[0].isdigit():
                id_trang_bi = int(parts[0])
            else:
                search_term = args.strip()
                items = get_unequipped_items(ctx.author.id)
                import unicodedata
                def remove_accents(s):
                    nfkd = unicodedata.normalize('NFKD', s)
                    return "".join([c for c in nfkd if not unicodedata.combining(c)])

                term_clean = remove_accents(search_term).lower().replace(" ", "")
                matched = [it for it in items if term_clean in remove_accents(it[2]).lower().replace(" ", "")]

                if not matched:
                    return await ctx.send(f"❌ Không tìm thấy trang bị nào chưa trang bị có tên khớp `{search_term}`!")
                elif len(matched) == 1:
                    id_trang_bi = matched[0][0]
                else:
                    embed, view = create_banphapbao_embed_and_view(ctx.author.id, matched)
                    embed.title = f"🏛️ CHỌN TRANG BỊ CẦN BÁN (Khớp: {search_term})"
                    return await ctx.send(embed=embed, view=view)

        if id_trang_bi is None:
            items = get_unequipped_items(ctx.author.id)
            if not items:
                return await ctx.send(
                    f"📦 Kho đồ không có pháp bảo nào chưa trang bị để bán!\n*(Lưu ý: Nếu trang bị đang mang trên người, hãy vào `{ctx.prefix}trangbi` để tháo ra trước)*"
                )
            embed, view = create_banphapbao_embed_and_view(ctx.author.id, items)
            return await ctx.send(embed=embed, view=view)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped FROM equipment WHERE id = ? AND user_id = ?",
                  (id_trang_bi, ctx.author.id))
        row = c.fetchone()
        conn.close()
        if not row:
            return await ctx.send("❌ Không tìm thấy trang bị này trong kho của đạo hữu!")
        if row[6]:
            return await ctx.send("❌ Vui lòng tháo trang bị ra trước khi treo bán!")

        grade = get_equipment_grade(row[3])

        if gia_ban is not None:
            if gia_ban < 100:
                return await ctx.send("❌ Giá bán tối thiểu là 100 Linh Thạch!")

            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM equipment WHERE id = ?", (id_trang_bi,))
            now = int(time.time())
            c.execute("""INSERT INTO market (seller_id, seller_name, item_name, item_type, atk_bonus, def_bonus, price, created_at, grade)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (ctx.author.id, ctx.author.display_name, row[2], row[1], row[4], row[5], gia_ban, now, row[3]))
            conn.commit()
            conn.close()

            seller_receive = int(gia_ban * 0.90)
            fee = gia_ban - seller_receive
            embed = discord.Embed(
                title="🏛️ NIÊM YẾT VẠN BẢO LÂU THÀNH CÔNG!",
                description=(
                    f"Đạo hữu đã treo bán thành công **{row[2]}** lên sàn giao dịch!\n\n"
                    f"🏷️ **Cấp bậc:** Tier {grade['tier']} — **{grade['tier_name']}** ({grade['icon']} {grade['name']})\n"
                    f"🏷️ **Loại:** {row[1]} | 🗡️ +`{row[4]:,}` 🛡️ +`{row[5]:,}`\n"
                    f"💎 **Giá niêm yết:** `{gia_ban:,}` Linh Thạch\n"
                    f"💼 **Phí sàn Vạn Bảo Lâu (10%):** `{fee:,}` Linh Thạch\n"
                    f"💰 **Thực nhận khi có người mua:** `{seller_receive:,}` Linh Thạch"
                ),
                color=grade["color"]
            )
            return await ctx.send(embed=embed)

        instant_p = calc_instant_price(row[3], row[4], row[5])
        embed = discord.Embed(
            title="🏛️ XÁC NHẬN PHƯƠNG THỨC BÁN PHÁP BẢO",
            description=(
                f"Đạo hữu đã chọn: **{row[2]}** ({row[1]})\n"
                f"🏷️ **Cấp bậc:** Tier {grade['tier']} — **{grade['tier_name']}** ({grade['icon']} {grade['name']})\n"
                f"📜 *\"{grade['desc']}\"*\n"
                f"🗡️ Công kích: +`{row[4]:,}` | 🛡️ Phòng ngự: +`{row[5]:,}`\n\n"
                f"**Chọn một trong hai phương thức bán bên dưới:**\n\n"
                f"1. 🏪 **Treo Bán Tại Sàn Vạn Bảo Lâu:**\n"
                f"   • Tự do định giá bán cho các tu sĩ khác mua.\n"
                f"   • Phí sàn: **10%** tổng Linh Thạch bán (thực nhận 90% khi có người mua).\n\n"
                f"2. ⚡ **Bán Luôn Cho Vạn Bảo Lâu:**\n"
                f"   • Chưởng quầy Vạn Bảo Lâu thu mua đứt đoạn ngay lập tức!\n"
                f"   • Giá thu mua: **`+{instant_p:,}` Linh Thạch** (Cộng thẳng vào túi)."
            ),
            color=grade["color"]
        )
        action_view = BanPhapBaoActionView(ctx.author.id, row[:6], instant_p, {})
        action_view.btn_ban_ngay.label = f"Bán Cho Tiệm (+{instant_p:,} LT)"
        return await ctx.send(embed=embed, view=action_view)

    @app_commands.command(name="sellall", description="Bán toàn bộ trang bị chưa đeo trên nhân vật cho Vạn Bảo Lâu")
    async def sellall(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)
        success, res = perform_sell_all(interaction.user.id)
        if not success:
            return await interaction.response.send_message(res, ephemeral=True)
        await interaction.response.send_message(embed=res)

    @commands.command(name="sellall", aliases=["banall", "banhet", "bantoanbo", "bantatca", "sell_all"])
    async def prefix_sellall(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")
        success, res = perform_sell_all(ctx.author.id)
        if not success:
            return await ctx.send(res)
        await ctx.send(embed=res)

async def setup(bot: commands.Bot):
    await bot.add_cog(VanBaoLauCog(bot))
