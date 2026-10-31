import time
import random
import discord
from discord import app_commands
from discord.ext import commands
from config import REALMS, SPIRIT_ROOTS, FAIL_MESSAGES, CONG_PHAP, EXPLORE_EVENTS
from database import (
    get_player, get_connection, update_cultivation,
    get_equipment_bonus, get_tong_mon, add_quest_progress,
    reset_daily_if_needed, DAILY_QUESTS, get_player_combat_stats
)
from cogs.pills import DanDuocShopView, create_pills_shop_embed
from cogs.equipment import perform_forge, create_random_equipment
from cogs.dongphu import create_dongphu_embed, DongPhuView
from cogs.tiencu import create_tiencu_embed, TienCuView
from cogs.phucloi import create_phucloi_embed, PhucLoiView
from cogs.dophuong import DoPhuongView
from cogs.tambao import TamBaoView
from cogs.vanthu import create_vanthu_embed, VanThuView
from cogs.nokhu import create_nokhu_embed, NoKhuView
from cogs.vanbaolau import get_market_items, VanBaoLauView
from cogs.ngoaivuc import NgoaiVucView, BOSSES, create_ngoaivuc_embed_and_view
from cogs.lichluyen import get_lichluyen_data, LichLuyenView, MAPS
from cogs.vandinh import VanDinhView
from cogs.help import create_overview_embed, HelpView

def perform_breakthrough(user_id: int):
    player, _ = update_cultivation(user_id)
    if not player:
        return False, "❌ Đạo hữu chưa nhập đạo! Hãy dùng `/nhapdao` trước."

    uid, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate = player[:8]
    current_realm = REALMS[realm_idx]

    if realm_idx >= len(REALMS) - 1:
        return False, "⚠️ Đạo hữu đã đạt đến cảnh giới tối cao — Đại Thừa Hậu Kỳ, không thể đột phá thêm!"

    if exp < current_realm["max_exp"]:
        return False, f"⚠️ Tu vi chưa viên mãn! Cần thêm `{current_realm['max_exp'] - exp:,}` Linh Khí nữa để xung quan."

    total_rate = min(1.0, current_realm["rate"] + bonus_rate)
    roll = random.random()
    conn = get_connection()
    c = conn.cursor()

    if roll <= total_rate:
        new_idx = realm_idx + 1
        new_exp = exp - current_realm["max_exp"]
        c.execute("UPDATE players SET realm_idx = ?, exp = ?, bonus_rate = 0.0 WHERE user_id = ?",
                  (new_idx, new_exp, user_id))
        conn.commit()
        conn.close()
        next_r = REALMS[new_idx]
        embed = discord.Embed(
            title="🌩️ ĐỘ KIẾP THÀNH CÔNG — ĐẠO CƠ THĂNG HOA!",
            description=(
                f"Chúc mừng đạo hữu **{name}** đã nghịch thiên cải mệnh!\n\n"
                f"## {next_r['icon']} {next_r['name']} {next_r['icon']}\n"
                f"❤️ Máu: `{next_r['hp']:,}` | 🗡️ Công: `{next_r['atk']:,}` | 🛡️ Thủ: `{next_r['def']:,}`"
            ),
            color=0xf1c40f
        )
        return True, embed
    else:
        lost_exp = int(current_realm["max_exp"] * 0.25)
        new_exp = max(0, exp - lost_exp)
        c.execute("UPDATE players SET exp = ? WHERE user_id = ?", (new_exp, user_id))
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="🩸 XUNG QUAN THẤT BẠI — TẨU HỎA NHẬP MA!",
            description=(
                f"Đạo hữu **{name}** {random.choice(FAIL_MESSAGES)}\n\n"
                f"📉 Tổn thất: **-{lost_exp:,} Linh Khí**\n"
                f"*Dùng Đan Dược (`/danduoc`) để tăng tỷ lệ độ kiếp lần sau!*"
            ),
            color=0xc0392b
        )
        return False, embed

BICANH_BOSS_POOLS = {
    # 0-1: Luyện Khí – Trúc Cơ
    "low": [
        ("🐅 Hỏa Diễm Cuồng Hổ", "Yêu thú hộ sơn hung hãn, toàn thân bốc cháy ngọn lửa hừng hực."),
        ("🐍 Bạch Ngọc Xà Vương", "Cự mãng ngàn năm uốn lượn bò ra từ đầm lầy bí cảnh."),
        ("🐻 Thiết Bì Cự Hùng", "Gấu sắt mình đồng da sắt canh giữ lối vào động phủ thượng cổ.")
    ],
    # 2-3: Kết Đan – Nguyên Anh
    "mid": [
        ("🦊 Cửu Vĩ Yêu Hồ", "Hồ ly chín đuôi mị hoặc lòng người, yêu khí ngập tràn sơn cốc."),
        ("🦂 U Minh Độc Hạt", "Bọ cạp khổng lồ mang nọc độc hủ cốt thực hồn."),
        ("🐆 Hắc Lôi Báo Vương", "Báo đen ngự lôi điện với tốc độ xé toạc cuồng phong.")
    ],
    # 4-5: Hóa Thần – Luyện Hư
    "high": [
        ("🦅 Thanh Loan Thần Điểu", "Thần điểu mang huyết mạch phượng hoàng canh giữ cây báu bí cảnh."),
        ("🐉 Thôn Thiên Cự Mãng", "Đại xà hóa giao long, nuốt chửng linh lực nhật nguyệt."),
        ("⚡ Tử Lôi Kim Bằng", "Đại bàng kim sí vỗ cánh dấy lên lôi kiếp vạn trượng.")
    ],
    # 6-8: Hợp Thể – Đại Thừa – Độ Kiếp
    "peak": [
        ("🐲 Thái Cổ Chân Long", "Chân long thượng cổ trấn thủ hạch tâm bí cảnh, long uy ngập trời."),
        ("🦚 Bất Tử Hỏa Phượng", "Phượng hoàng dục hỏa niết bàn, ngọn lửa thái sơ thiêu đốt hư không."),
        ("👹 Hỗn Độn Thao Thiết", "Hung thú hồng hoang đói khát, gầm vang chấn toái linh hồn tu sĩ.")
    ],
    # 9+: Phi Thăng – Tiên Nhân
    "immortal": [
        ("🌌 Hồng Hoang Cổ Thần", "Tàn hồn cổ thần ngự trị bí cảnh từ thuở khai thiên lập địa."),
        ("⚔️ Chân Tiên Bí Cảnh Trấn Giả", "Khôi lỗi chiến binh do Đại La Kim Tiên lưu lại khảo nghiệm hậu nhân."),
        ("👑 Thái Sơ Thần Thú", "Vật báu hộ giới nắm giữ pháp tắc đại đạo sơ khai.")
    ]
}

def perform_explore(user_id: int):
    player = get_player(user_id)
    if not player:
        return False, "❌ Đạo hữu chưa nhập đạo! Hãy dùng `/nhapdao` trước."

    now = int(time.time())
    cooldown = 300
    last_exp = player[9]
    if now - last_exp < cooldown:
        rem = cooldown - (now - last_exp)
        m, s = divmod(rem, 60)
        return False, f"⏳ Thần thức cần nghỉ ngơi tĩnh dưỡng thêm **{m}p {s}s** nữa!"

    stats = get_player_combat_stats(user_id)
    realm_idx = player[4]
    realm_mult = realm_idx + 1

    # 60% Đụng độ Boss Thủ Hộ Bí Cảnh tương thích Cảnh Giới & Chiến Lực
    # 40% Gặp Cơ Duyên Bí Cảnh thông thường
    is_boss_encounter = random.random() < 0.60

    if is_boss_encounter and stats:
        if realm_idx <= 7:
            pool = BICANH_BOSS_POOLS["low"]
        elif realm_idx <= 13:
            pool = BICANH_BOSS_POOLS["mid"]
        elif realm_idx <= 19:
            pool = BICANH_BOSS_POOLS["high"]
        elif realm_idx <= 25:
            pool = BICANH_BOSS_POOLS["peak"]
        else:
            pool = BICANH_BOSS_POOLS["immortal"]

        boss_name, boss_desc = random.choice(pool)

        # Scale chỉ số Boss Bí Cảnh theo chiến lực thực tế của người chơi
        p_hp = stats["hp"]
        p_atk = stats["atk"]
        p_def = stats["def"]

        b_hp = max(80, int(p_hp * random.uniform(1.0, 1.30)))
        b_atk = max(15, int(p_atk * random.uniform(0.85, 1.05)))
        b_def = max(10, int(p_def * random.uniform(0.75, 0.95)))

        combat_log = []
        for rnd in range(1, 7):
            p_dmg = max(1, int(p_atk * random.uniform(0.85, 1.15) - b_def * 0.25))
            b_dmg = max(1, int(b_atk * random.uniform(0.85, 1.15) - p_def * 0.25))
            b_hp -= p_dmg
            p_hp -= b_dmg
            combat_log.append(f"⚔️ **Hiệp {rnd}:** Đạo hữu đánh `{p_dmg:,}` ST | {boss_name.split()[1]} phản `{b_dmg:,}` ST")
            if b_hp <= 0 or p_hp <= 0:
                break

        won = (b_hp <= 0 and p_hp > 0) or (p_hp >= b_hp)

        conn = get_connection()
        c = conn.cursor()

        if won:
            exp_gain = int(random.randint(320, 550) * realm_mult)
            stone_gain = int(random.randint(90, 180) * realm_mult)
            c.execute("""UPDATE players
                         SET exp = exp + ?, linh_thach = linh_thach + ?, last_explore = ?
                         WHERE user_id = ?""",
                      (exp_gain, stone_gain, now, user_id))
            conn.commit()
            conn.close()

            add_quest_progress(user_id, "q_explore")
            item = create_random_equipment(user_id, realm_idx)

            embed = discord.Embed(
                title=f"⚔️ BÍ CẢNH TRẢM THÚ — ĐẠI PHÁ {boss_name.upper()}!",
                description=(
                    f"Bước vào hạch tâm bí cảnh, đạo hữu kinh động **{boss_name}**!\n"
                    f"📜 *\"{boss_desc}\"*\n\n"
                    + "\n".join(combat_log[:4]) +
                    f"\n\n🏆 **Chém rụng thủ hộ thú, mở toang cổ điện:**\n"
                    f"✨ Linh khí: **`+{exp_gain:,}`** | 💎 Linh thạch: **`+{stone_gain:,}`**"
                ),
                color=0x2ecc71
            )
            embed.add_field(
                name="🎁 Pháp Bảo Khai Quật Từ Cổ Điện",
                value=(
                    f"**{item['eq_name']}** ({item['eq_type']})\n"
                    f"🗡️ +`{item['atk_bonus']:,}` Công kích | 🛡️ +`{item['def_bonus']:,}` Phòng ngự\n"
                    f"*(Đã lưu vào kho trang bị — dùng `/trangbi` hoặc `t trangbi` để mặc)*"
                ),
                inline=False
            )
            return True, embed

        else:
            exp_gain = int(120 * realm_mult)
            lost_stone = max(20, int(40 * realm_mult))
            c.execute("""UPDATE players
                         SET exp = exp + ?, linh_thach = MAX(0, linh_thach - ?), last_explore = ?
                         WHERE user_id = ?""",
                      (exp_gain, lost_stone, now, user_id))
            conn.commit()
            conn.close()

            add_quest_progress(user_id, "q_explore")

            embed = discord.Embed(
                title=f"🩸 BÍ CẢNH NGUY HIỂM — BỊ {boss_name.upper()} ĐÁNH LUI!",
                description=(
                    f"Đụng độ thủ hộ thú **{boss_name}** uy năng cái thế!\n"
                    f"📜 *\"{boss_desc}\"*\n\n"
                    + "\n".join(combat_log[:4]) +
                    f"\n\nThế trận bất lợi, đạo hữu đành thi triển Ngự Kiếm Phi Hành phá vòng vây tẩu thoát!\n"
                    f"✨ Thu hoạch thực chiến: **`+{exp_gain:,}`** Linh Khí\n"
                    f"📉 Tổn thất: -`{lost_stone:,}` Linh Thạch để trị thương."
                ),
                color=0xe74c3c
            )
            return True, embed

    else:
        # Cơ Duyên Bí Cảnh thông thường
        weights = [e["weight"] for e in EXPLORE_EVENTS]
        event = random.choices(EXPLORE_EVENTS, weights=weights, k=1)[0]
        exp_gain = int(event["exp_mult"] * realm_mult)
        stone_gain = int(event["stone_mult"] * realm_mult)

        conn = get_connection()
        c = conn.cursor()
        c.execute("""UPDATE players
                     SET exp = MAX(0, exp + ?), linh_thach = MAX(0, linh_thach + ?), last_explore = ?
                     WHERE user_id = ?""",
                  (exp_gain, stone_gain, now, user_id))
        conn.commit()
        conn.close()

        add_quest_progress(user_id, "q_explore")

        item = None
        if random.random() < 0.40:
            item = create_random_equipment(user_id, realm_idx)

        embed = discord.Embed(
            title="⛰️ THÁM HIỂM BÍ CẢNH — THU HOẠCH CƠ DUYÊN",
            description=f"*{event['desc']}*\n\n✨ Linh khí: **`+{exp_gain:,}`** | 💎 Linh thạch: **`+{stone_gain:,}`**",
            color=0x27ae60
        )

        if item:
            embed.add_field(
                name="🎁 Cơ Duyên Bảo Vật",
                value=(
                    f"**{item['eq_name']}** ({item['eq_type']})\n"
                    f"🗡️ +`{item['atk_bonus']:,}` Công kích | 🛡️ +`{item['def_bonus']:,}` Phòng ngự\n"
                    f"*(Đã lưu vào kho trang bị — dùng `/trangbi` hoặc `t trangbi` để mặc)*"
                ),
                inline=False
            )

        return True, embed

def build_profile_embed(user: discord.User | discord.Member, player, gained_exp: int = 0):
    uid, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate = player[:8]
    cong_phap_idx = player[10]
    speed_boost = player[11]
    speed_boost_end = player[12]
    tong_id = player[13]
    spouse_id = player[14]
    pvp_wins = player[20]
    pvp_losses = player[21]

    r = REALMS[realm_idx]
    cp = CONG_PHAP[cong_phap_idx]

    pct = min(1.0, exp / r["max_exp"])
    filled = int(pct * 20)
    bar = "🟦" * filled + "⬛" * (20 - filled)
    total_rate = min(100, int((r["rate"] + bonus_rate) * 100))

    eq_atk, eq_def = get_equipment_bonus(uid)
    effective_atk = int(r["atk"] * (1 + cp["atk_bonus"])) + eq_atk
    effective_def = int(r["def"] * (1 + cp["def_bonus"])) + eq_def

    extra_lines = []
    if spouse_id:
        sp = get_player(spouse_id)
        if sp:
            extra_lines.append(f"💑 Đạo Lữ: **{sp[1]}** (+5% LK)")
    now = int(time.time())
    if speed_boost > 0 and now < speed_boost_end:
        rem = speed_boost_end - now
        m, s = divmod(rem, 60)
        extra_lines.append(f"⚡ Boost: +`{speed_boost}x` (còn `{m}p{s}s`)")
    if tong_id:
        tm = get_tong_mon(tong_id)
        if tm:
            extra_lines.append(f"🏯 Tông: **{tm[1]}**")
    extra_str = ("\n" + " | ".join(extra_lines)) if extra_lines else ""

    embed = discord.Embed(
        title=f"📜 Ngọc Giản Mệnh Cách — {name}",
        description=f"> *🧘 Bế quan vừa rồi thu được: **`+{gained_exp:,}`** Linh Khí*{extra_str}",
        color=0x3498db
    )
    if hasattr(user, "display_avatar"):
        embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name=f"{r['icon']} Cảnh Giới", value=f"**{r['name']}**", inline=True)
    embed.add_field(name="🧬 Linh Căn", value=f"{linh_can}\n(`{speed}x`)", inline=True)
    embed.add_field(name="💎 Linh Thạch", value=f"`{linh_thach:,}` viên", inline=True)
    embed.add_field(name=f"{cp['icon']} Công Pháp", value=f"**{cp['name']}**\n🗡️+{int(cp['atk_bonus']*100)}% | 🛡️+{int(cp['def_bonus']*100)}% | ✨+{int(cp['exp_bonus']*100)}%", inline=True)
    embed.add_field(name="🗡️ Chiến Lực", value=f"❤️ `{r['hp']:,}` | 🗡️ `{effective_atk:,}` | 🛡️ `{effective_def:,}`", inline=True)
    embed.add_field(name="⚔️ PvP", value=f"🏆 `{pvp_wins}` thắng | 💀 `{pvp_losses}` thua", inline=True)
    embed.add_field(
        name=f"✨ Tu Vi ({int(pct*100)}%) — Độ Kiếp: `{total_rate}%`",
        value=f"{bar}\n`{exp:,}` / `{r['max_exp']:,}` LK *(Đan dược: +{int(bonus_rate*100)}%)*",
        inline=False
    )
    embed.set_footer(text="Chọn các tính năng bên dưới theo từng phân hệ: Thông Tin, Tu Luyện, Tài Sản")
    return embed

class TuTienDashboardView(discord.ui.View):
    def __init__(self, user_id: int, user_obj: discord.User | discord.Member, current_tab: str = "thong_tin"):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.user_obj = user_obj
        self.current_tab = current_tab
        self.build_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ngọc giản của đạo hữu khác, xin chớ tự ý chạm vào!", ephemeral=True)
            return False
        return True

    def build_buttons(self):
        self.clear_items()

        # Hiển thị chính xác 2 HÀNG NGANG, MỖI HÀNG 5 NÚT
        if self.current_tab == "thong_tin":
            # Hàng 1 (5 nút): [👤 Hồ Sơ] [🌌 Động Phủ] [🏯 Tông Môn] [📖 Hướng Dẫn] [🎖️ Tiên Bảng]
            b_hoso = discord.ui.Button(label="Hồ Sơ", emoji="👤", style=discord.ButtonStyle.primary, row=0, custom_id="act_hoso")
            b_dongphu = discord.ui.Button(label="Động Phủ", emoji="🌌", style=discord.ButtonStyle.secondary, row=0, custom_id="act_dongphu")
            b_tongmon = discord.ui.Button(label="Tông Môn", emoji="🏯", style=discord.ButtonStyle.secondary, row=0, custom_id="act_tongmon")
            b_huongdan = discord.ui.Button(label="Hướng Dẫn", emoji="📖", style=discord.ButtonStyle.secondary, row=0, custom_id="act_huongdan")
            b_tienbang = discord.ui.Button(label="Tiên Bảng", emoji="🎖️", style=discord.ButtonStyle.secondary, row=0, custom_id="act_tienbang")

            # Hàng 2 (5 nút): [✨ Tiên Cư] [⚙️ Hệ Thống] [⚡ Độ Kiếp] [🧘 Tu Luyện] [💰 Tài Sản]
            b_tiencu = discord.ui.Button(label="Tiên Cư", emoji="✨", style=discord.ButtonStyle.secondary, row=1, custom_id="act_tiencu")
            b_hethong = discord.ui.Button(label="Hệ Thống", emoji="⚙️", style=discord.ButtonStyle.secondary, row=1, custom_id="act_hethong")
            b_dokiep = discord.ui.Button(label="Độ Kiếp", emoji="⚡", style=discord.ButtonStyle.danger, row=1, custom_id="act_dokiep")
            b_switch_tuluyen = discord.ui.Button(label="Tu Luyện", emoji="🧘", style=discord.ButtonStyle.success, row=1, custom_id="tab_tu_luyen")
            b_switch_taisan = discord.ui.Button(label="Tài Sản", emoji="💰", style=discord.ButtonStyle.success, row=1, custom_id="tab_tai_san")

            for b in [b_hoso, b_dongphu, b_tongmon, b_huongdan, b_tienbang, b_tiencu, b_hethong, b_dokiep]:
                b.callback = self.on_action_click
                self.add_item(b)
            for b in [b_switch_tuluyen, b_switch_taisan]:
                b.callback = self.on_tab_click
                self.add_item(b)

        elif self.current_tab == "tu_luyen":
            # Hàng 1 (5 nút): [🧭 Lịch Luyện] [🥥 Hoạt Động] [🔮 Bí Cảnh] [📜 Nhiệm Vụ] [🧙‍♂️ Chế Tạo]
            b_lichluyen = discord.ui.Button(label="Lịch Luyện", emoji="🧭", style=discord.ButtonStyle.secondary, row=0, custom_id="act_lichluyen")
            b_hoatdong = discord.ui.Button(label="Hoạt Động", emoji="🥥", style=discord.ButtonStyle.secondary, row=0, custom_id="act_hoatdong")
            b_bicanh = discord.ui.Button(label="Bí Cảnh", emoji="🔮", style=discord.ButtonStyle.primary, row=0, custom_id="act_bicanh")
            b_nhiemvu = discord.ui.Button(label="Nhiệm Vụ", emoji="📜", style=discord.ButtonStyle.secondary, row=0, custom_id="act_nhiemvu")
            b_chetao = discord.ui.Button(label="Chế Tạo", emoji="🧙‍♂️", style=discord.ButtonStyle.secondary, row=0, custom_id="act_chetao")

            # Hàng 2 (5 nút): [🌌 Ngoại Vực] [⚔️ Vấn Đỉnh] [⚡ Độ Kiếp] [👤 Thông Tin] [💰 Tài Sản]
            b_ngoaivuc = discord.ui.Button(label="Ngoại Vực", emoji="🌌", style=discord.ButtonStyle.secondary, row=1, custom_id="act_ngoaivuc")
            b_vandinh = discord.ui.Button(label="Vấn Đỉnh", emoji="⚔️", style=discord.ButtonStyle.secondary, row=1, custom_id="act_vandinh")
            b_dokiep = discord.ui.Button(label="Độ Kiếp", emoji="⚡", style=discord.ButtonStyle.danger, row=1, custom_id="act_dokiep")
            b_switch_thongtin = discord.ui.Button(label="Thông Tin", emoji="👤", style=discord.ButtonStyle.success, row=1, custom_id="tab_thong_tin")
            b_switch_taisan = discord.ui.Button(label="Tài Sản", emoji="💰", style=discord.ButtonStyle.success, row=1, custom_id="tab_tai_san")

            for b in [b_lichluyen, b_hoatdong, b_bicanh, b_nhiemvu, b_chetao, b_ngoaivuc, b_vandinh, b_dokiep]:
                b.callback = self.on_action_click
                self.add_item(b)
            for b in [b_switch_thongtin, b_switch_taisan]:
                b.callback = self.on_tab_click
                self.add_item(b)

        elif self.current_tab == "tai_san":
            # Hàng 1 (5 nút): [💰 Hành Trang] [🏛️ Vạn Bảo Lâu] [🎁 Phúc Lợi] [🛒 Cửa Hàng] [🌀 Tầm Bảo]
            b_hanhtrang = discord.ui.Button(label="Hành Trang", emoji="💰", style=discord.ButtonStyle.primary, row=0, custom_id="act_hanhtrang")
            b_vanbaolau = discord.ui.Button(label="Vạn Bảo Lâu", emoji="🏛️", style=discord.ButtonStyle.secondary, row=0, custom_id="act_vanbaolau")
            b_phucloi = discord.ui.Button(label="Phúc Lợi", emoji="🎁", style=discord.ButtonStyle.secondary, row=0, custom_id="act_phucloi")
            b_cuahang = discord.ui.Button(label="Cửa Hàng", emoji="🛒", style=discord.ButtonStyle.secondary, row=0, custom_id="act_cuahang")
            b_tambao = discord.ui.Button(label="Tầm Bảo", emoji="🌀", style=discord.ButtonStyle.secondary, row=0, custom_id="act_tambao")

            # Hàng 2 (5 nút): [🎲 Đổ Phường] [🦊 Vạn Thú Các] [⛓️ Nô Khu] [👤 Thông Tin] [🧘 Tu Luyện]
            b_dophuong = discord.ui.Button(label="Đổ Phường", emoji="🎲", style=discord.ButtonStyle.secondary, row=1, custom_id="act_dophuong")
            b_vanthu = discord.ui.Button(label="Vạn Thú Các", emoji="🦊", style=discord.ButtonStyle.secondary, row=1, custom_id="act_vanthu")
            b_nokhu = discord.ui.Button(label="Nô Khu", emoji="⛓️", style=discord.ButtonStyle.secondary, row=1, custom_id="act_nokhu")
            b_switch_thongtin = discord.ui.Button(label="Thông Tin", emoji="👤", style=discord.ButtonStyle.success, row=1, custom_id="tab_thong_tin")
            b_switch_tuluyen = discord.ui.Button(label="Tu Luyện", emoji="🧘", style=discord.ButtonStyle.success, row=1, custom_id="tab_tu_luyen")

            for b in [b_hanhtrang, b_vanbaolau, b_phucloi, b_cuahang, b_tambao, b_dophuong, b_vanthu, b_nokhu]:
                b.callback = self.on_action_click
                self.add_item(b)
            for b in [b_switch_thongtin, b_switch_tuluyen]:
                b.callback = self.on_tab_click
                self.add_item(b)

    async def on_tab_click(self, interaction: discord.Interaction):
        cid = interaction.data["custom_id"]
        if cid == "tab_thong_tin":
            self.current_tab = "thong_tin"
        elif cid == "tab_tu_luyen":
            self.current_tab = "tu_luyen"
        elif cid == "tab_tai_san":
            self.current_tab = "tai_san"

        self.build_buttons()
        player = get_player(self.user_id)
        embed = build_profile_embed(self.user_obj, player, 0)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_action_click(self, interaction: discord.Interaction):
        cid = interaction.data["custom_id"]
        player = get_player(self.user_id)
        if not player:
            return await interaction.response.send_message("❌ Chưa nhập đạo!", ephemeral=True)

        if cid == "act_hoso":
            embed = build_profile_embed(self.user_obj, player, 0)
            await interaction.response.edit_message(embed=embed, view=self)

        elif cid == "act_dongphu":
            embed = create_dongphu_embed(self.user_id, interaction.user.display_name)
            view = DongPhuView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_tongmon":
            if not player[13]:
                return await interaction.response.send_message("❌ Chưa gia nhập tông môn nào! Dùng `/giamon` hoặc `/lapmon`.", ephemeral=True)
            tm = get_tong_mon(player[13])
            if not tm:
                return await interaction.response.send_message("❌ Tông môn không tồn tại!", ephemeral=True)
            leader = get_player(tm[2])
            embed = discord.Embed(title=f"🏯 {tm[1]}", description=tm[3] or "*Tông môn chưa có miêu tả.*", color=0xe74c3c)
            embed.add_field(name="👑 Chưởng Môn", value=leader[1] if leader else "Không rõ", inline=True)
            embed.add_field(name="💎 Ngân Khố", value=f"`{tm[4]:,}` Linh Thạch", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_huongdan":
            embed = create_overview_embed("t")
            view = HelpView("t")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_tienbang":
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT name, realm_idx, exp, linh_can, pvp_wins, total_exp_gained FROM players ORDER BY realm_idx DESC, exp DESC LIMIT 10")
            rows = c.fetchall()
            conn.close()
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            lines = []
            for idx, (name, realm_idx, exp, linh_can, pvp_wins, total_exp) in enumerate(rows):
                realm = REALMS[realm_idx]
                lines.append(f"{medals[idx]} **{name}** — {realm['icon']} `{realm['name']}` | `{exp:,}` LK")
            embed = discord.Embed(title="🏆 THIÊN ĐẠO KIM BẢNG", description="\n".join(lines) or "Trống", color=0xe67e22)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_tiencu":
            embed = create_tiencu_embed(self.user_id, interaction.user.display_name)
            view = TienCuView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_hethong":
            r = REALMS[player[4]]
            cp = CONG_PHAP[player[10]]
            eq_atk, eq_def = get_equipment_bonus(self.user_id)
            total_pvp = player[20] + player[21]
            winrate = int(player[20] / total_pvp * 100) if total_pvp > 0 else 0
            embed = discord.Embed(title=f"📊 HỆ THỐNG THỐNG KÊ — {player[1]}", color=0x2c3e50)
            embed.add_field(name="🏔️ Cảnh Giới", value=f"{r['icon']} **{r['name']}**", inline=True)
            embed.add_field(name="🧬 Linh Căn", value=f"`{player[3]}x` — *{player[2]}*", inline=True)
            embed.add_field(name="📖 Công Pháp", value=f"{cp['icon']} **{cp['name']}**", inline=True)
            embed.add_field(name="⚔️ PvP", value=f"🏆 `{player[20]}` thắng / 💀 `{player[21]}` thua (`{winrate}%`)", inline=True)
            embed.add_field(name="💎 Tài Sản", value=f"`{player[6]:,}` Linh Thạch", inline=True)
            embed.add_field(name="✨ Tổng Tu Vi Đã Đạt", value=f"`{player[22]:,}` LK", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_dokiep":
            success, res = perform_breakthrough(self.user_id)
            if isinstance(res, str):
                await interaction.response.send_message(res, ephemeral=True)
            else:
                await interaction.response.send_message(embed=res, ephemeral=True)

        elif cid == "act_lichluyen":
            map_id, start_time = get_lichluyen_data(self.user_id)
            cur_map = next((m for m in MAPS if m["id"] == map_id), MAPS[0])
            now = int(time.time())
            mins = (now - start_time) // 60
            embed = discord.Embed(
                title="🧭 LỊCH LUYỆN GIANG HỒ — TREO MÁY TU CHÂN",
                description=(
                    f"Đang vân du tại: **{cur_map['icon']} {cur_map['name']}**\n"
                    f"⏱️ Đã tích lũy: **`{mins}` phút** (Tối đa 480 phút)\n"
                    f"📈 Tốc độ: **`{cur_map['rate'] * 3}` Linh Khí / phút**"
                ),
                color=0x34495e
            )
            view = LichLuyenView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_hoatdong":
            embed = discord.Embed(
                title="🥥 HOẠT ĐỘNG THỜI HẠN",
                description="Các hoạt động tu chân đang mở:\n• 🐲 Ma Thú Triều Xâm Lăng (20:00)\n• ⚡ Vấn Đỉnh Thí Luyện (`/vandinh`)\n• 📜 Trả Lời Vấn Đáp (`/hoatdong`)",
                color=0xe67e22
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_bicanh":
            success, res = perform_explore(self.user_id)
            if not success:
                await interaction.response.send_message(res, ephemeral=True)
            else:
                await interaction.response.send_message(embed=res, ephemeral=True)

        elif cid == "act_nhiemvu":
            reset_daily_if_needed(self.user_id)
            p = get_player(self.user_id)
            cols = {"q_cultivate": p[16], "q_explore": p[17], "q_fight": p[18], "q_pills": p[19]}
            embed = discord.Embed(title="📋 NHIỆM VỤ HÀNG NGÀY", color=0xf39c12)
            for q in DAILY_QUESTS:
                prog = cols[q["id"]]
                q_target = q["target"]
                done = prog >= q_target
                q_stat = "✅" if done else f"({prog}/{q_target})"
                embed.add_field(
                    name=f"{q['icon']} {q['name']} {q_stat}",
                    value=f"*{q['desc']}*\nThưởng: ✨+{q['reward_exp']} LK | 💎+{q['reward_stone']} LT",
                    inline=False
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_chetao":
            success, res = perform_forge(self.user_id)
            if not success:
                await interaction.response.send_message(res, ephemeral=True)
            else:
                await interaction.response.send_message(embed=res, ephemeral=True)

        elif cid == "act_ngoaivuc":
            embed, view = create_ngoaivuc_embed_and_view(self.user_id)
            if not view:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_vandinh":
            view = VanDinhView(self.user_id)
            embed = discord.Embed(title="⚔️ VẤN ĐỈNH PHONG — CỬU TRÙNG THIÊN THÁP", description="Leo tháp 100 tầng thử thách chiến lực!", color=0x9b59b6)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_hanhtrang":
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT eq_type, eq_name, grade, atk_bonus, def_bonus, is_equipped FROM equipment WHERE user_id = ? ORDER BY is_equipped DESC", (self.user_id,))
            items = c.fetchall()
            conn.close()
            embed = discord.Embed(title="🎒 HÀNH TRANG PHÁP BẢO", color=0xe67e22)
            if not items:
                embed.description = "Kho đồ đang trống! Hãy dùng nút **Chế Tạo** hoặc `/ren`."
            else:
                lines = []
                for it in items[:10]:
                    eq_stat = "✅ [ĐANG MANG] " if it[5] else ""
                    lines.append(f"{eq_stat}**{it[1]}** ({it[0]}) — 🗡️+{it[3]} 🛡️+{it[4]}")
                embed.description = "\n".join(lines)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif cid == "act_vanbaolau":
            items = get_market_items()
            embed = discord.Embed(title="🏛️ VẠN BẢO LÂU — CHỢ ĐẤU GIÁ", color=0x16a085)
            embed.description = f"💎 Linh thạch của bạn: `{player[6]:,}`\nHiện có `{len(items)}` bảo vật đang rao bán."
            view = VanBaoLauView(self.user_id, items)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_phucloi":
            embed = create_phucloi_embed(self.user_id, interaction.user.display_name)
            view = PhucLoiView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_cuahang":
            embed = create_pills_shop_embed(player)
            view = DanDuocShopView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_tambao":
            embed = discord.Embed(title="🌀 VÒNG QUAY TẦM BẢO", description="Tiêu tốn Linh Thạch để săn tìm Thần Phẩm Cổ Bảo!", color=0x3498db)
            view = TamBaoView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_dophuong":
            embed = discord.Embed(title="🎲 THIÊN PHONG ĐỔ PHƯỜNG — TÀI XỈU", description=f"💎 Túi linh thạch: `{player[6]:,}`\nChọn cửa đặt cược Tài hoặc Xỉu!", color=0x9b59b6)
            view = DoPhuongView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_vanthu":
            embed = create_vanthu_embed(self.user_id, interaction.user.display_name)
            view = VanThuView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif cid == "act_nokhu":
            embed, _ = create_nokhu_embed(self.user_id, interaction.user.display_name)
            view = NoKhuView(self.user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

def create_canhgioi_embed(user_id: int = None):
    player = get_player(user_id) if user_id else None
    cur_realm = player[4] if player else -1

    lines = []
    for idx, r in enumerate(REALMS):
        is_cur = " 📍 **[HIỆN TẠI]**" if idx == cur_realm else ""
        lines.append(
            f"{r['icon']} **Cấp {idx+1}: {r['name']}**{is_cur}\n"
            f"   └ 💖 HP: `{r['hp']:,}` | 🗡️ ATK: `{r['atk']:,}` | 🛡️ DEF: `{r['def']:,}` | ⚡ Tỉ lệ: `{int(r['rate']*100)}%`"
        )

    embed = discord.Embed(
        title="🌌 BẢNG CẢNH GIỚI TU TIÊN CHÍNH TÔNG",
        description=(
            "Con đường nghịch thiên tu hành trải qua các tầng cảnh giới trùng trùng thiên kiếp:\n\n"
            + "\n".join(lines) + "\n\n"
            "*(Dùng lệnh `/dotpha` hoặc `t dotpha` khi đủ tu vi để xung kích cảnh giới kế tiếp)*"
        ),
        color=0x9b59b6
    )
    return embed

class CultivationCog(commands.Cog, name="Tu Luyện"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="canhgioi", description="Xem toàn bộ thứ bậc các cảnh giới tu tiên và chỉ số cơ bản")
    async def canhgioi(self, interaction: discord.Interaction):
        embed = create_canhgioi_embed(interaction.user.id)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="canhgioi", aliases=["cg", "bangcanhgioi"])
    async def prefix_canhgioi(self, ctx: commands.Context):
        embed = create_canhgioi_embed(ctx.author.id)
        await ctx.send(embed=embed)

    @app_commands.command(name="nhapdao", description="Cảm ứng thiên địa, kiểm tra Linh Căn và bước vào con đường tu tiên")
    async def nhapdao(self, interaction: discord.Interaction):
        if get_player(interaction.user.id):
            return await interaction.response.send_message("⚠️ Đạo hữu đã có tên trên Tiên Tịch! Dữ liệu tu vi của đạo hữu đã được liên thông toàn bộ các server. Hãy dùng `/thongtin`.", ephemeral=True)

        weights = [r["weight"] for r in SPIRIT_ROOTS]
        chosen_root = random.choices(SPIRIT_ROOTS, weights=weights, k=1)[0]
        now = int(time.time())

        conn = get_connection()
        c = conn.cursor()
        c.execute("""INSERT INTO players (user_id, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate,
                     last_cultivate, last_explore, cong_phap_idx, speed_boost, speed_boost_end, tong_mon_id,
                     spouse_id, daily_quest_date, q_cultivate, q_explore, q_fight, q_pills,
                     pvp_wins, pvp_losses, total_exp_gained)
                  VALUES (?,?,?,?,0,0,150,0.0,?,0,0,0.0,0,0,0,'',0,0,0,0,0,0,0)""",
                  (interaction.user.id, interaction.user.display_name, chosen_root["name"], chosen_root["speed"], now))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="⛩️ KHAI MỞ TIÊN DUYÊN — TRẮC NGHIỆM LINH CĂN",
            description=f"Đạo hữu **{interaction.user.display_name}** đặt tay lên Trắc Linh Bi, hào quang vạn trượng phóng thẳng lên trời!",
            color=chosen_root["color"]
        )
        embed.add_field(name="🧬 Tư Chất Linh Căn", value=f"**{chosen_root['name']}**\n*{chosen_root['desc']}*", inline=False)
        embed.add_field(name="🌊 Tốc Độ Hấp Thụ", value=f"`{chosen_root['speed']}x` Linh khí/phút", inline=True)
        embed.add_field(name="📖 Công Pháp", value="Luyện Khí Quyết (Cơ Bản)", inline=True)
        embed.add_field(name="💎 Túi Trữ Vật", value="`150` Hạ Phẩm Linh Thạch", inline=True)
        embed.set_footer(text="Dùng /thongtin để bắt đầu tu luyện • Dữ liệu tự động đồng bộ trên mọi server Discord")
        await interaction.response.send_message(embed=embed)

    @commands.command(name="nhapdao", aliases=["start", "batdau"])
    async def prefix_nhapdao(self, ctx: commands.Context):
        if get_player(ctx.author.id):
            return await ctx.send(f"⚠️ Đạo hữu đã có tên trên Tiên Tịch! Dữ liệu tu vi của đạo hữu đã được liên thông toàn bộ các server. Hãy dùng `{ctx.prefix}thongtin`.")

        weights = [r["weight"] for r in SPIRIT_ROOTS]
        chosen_root = random.choices(SPIRIT_ROOTS, weights=weights, k=1)[0]
        now = int(time.time())

        conn = get_connection()
        c = conn.cursor()
        c.execute("""INSERT INTO players (user_id, name, linh_can, speed, realm_idx, exp, linh_thach, bonus_rate,
                     last_cultivate, last_explore, cong_phap_idx, speed_boost, speed_boost_end, tong_mon_id,
                     spouse_id, daily_quest_date, q_cultivate, q_explore, q_fight, q_pills,
                     pvp_wins, pvp_losses, total_exp_gained)
                  VALUES (?,?,?,?,0,0,150,0.0,?,0,0,0.0,0,0,0,'',0,0,0,0,0,0,0)""",
                  (ctx.author.id, ctx.author.display_name, chosen_root["name"], chosen_root["speed"], now))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="⛩️ KHAI MỞ TIÊN DUYÊN — TRẮC NGHIỆM LINH CĂN",
            description=f"Đạo hữu **{ctx.author.display_name}** đặt tay lên Trắc Linh Bi, hào quang vạn trượng phóng thẳng lên trời!",
            color=chosen_root["color"]
        )
        embed.add_field(name="🧬 Tư Chất Linh Căn", value=f"**{chosen_root['name']}**\n*{chosen_root['desc']}*", inline=False)
        embed.add_field(name="🌊 Tốc Độ Hấp Thụ", value=f"`{chosen_root['speed']}x` Linh khí/phút", inline=True)
        embed.add_field(name="📖 Công Pháp", value="Luyện Khí Quyết (Cơ Bản)", inline=True)
        embed.add_field(name="💎 Túi Trữ Vật", value="`150` Hạ Phẩm Linh Thạch", inline=True)
        embed.set_footer(text=f"Dùng {ctx.prefix}thongtin để bắt đầu tu luyện • Dữ liệu tự động đồng bộ trên mọi server Discord")
        await ctx.send(embed=embed)

    @app_commands.command(name="thongtin", description="Xem Ngọc Giản Mệnh Cách, thu hoạch tu vi bế quan và bảng điều khiển tu tiên")
    async def thongtin(self, interaction: discord.Interaction):
        player, gained_exp = update_cultivation(interaction.user.id, interaction.user.display_name)
        if not player:
            return await interaction.response.send_message("❌ Đạo hữu vẫn là phàm nhân! Hãy dùng `/nhapdao` trước.", ephemeral=True)

        add_quest_progress(interaction.user.id, "q_cultivate")
        embed = build_profile_embed(interaction.user, player, gained_exp)
        view = TuTienDashboardView(interaction.user.id, interaction.user, "thong_tin")
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="thongtin", aliases=["tt", "hoso", "thongin"])
    async def prefix_thongtin(self, ctx: commands.Context):
        player, gained_exp = update_cultivation(ctx.author.id, ctx.author.display_name)
        if not player:
            return await ctx.send("❌ Đạo hữu vẫn là phàm nhân! Hãy dùng `t nhapdao` trước.")

        add_quest_progress(ctx.author.id, "q_cultivate")
        embed = build_profile_embed(ctx.author, player, gained_exp)
        view = TuTienDashboardView(ctx.author.id, ctx.author, "thong_tin")
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="dotpha", description="Xung Quan Độ Kiếp — Nghịch thiên cải mệnh, đột phá cảnh giới")
    async def dotpha(self, interaction: discord.Interaction):
        success, res = perform_breakthrough(interaction.user.id)
        if isinstance(res, str):
            await interaction.response.send_message(res, ephemeral=True)
        else:
            await interaction.response.send_message(embed=res)

    @commands.command(name="dotpha", aliases=["dokiep", "xungquan", "dpk"])
    async def prefix_dotpha(self, ctx: commands.Context):
        success, res = perform_breakthrough(ctx.author.id)
        if isinstance(res, str):
            await ctx.send(res)
        else:
            await ctx.send(embed=res)

    @app_commands.command(name="thamhiem", description="Thám hiểm bí cảnh — Tìm kiếm cơ duyên, chém yêu thú (5 phút/lần)")
    async def thamhiem(self, interaction: discord.Interaction):
        success, res = perform_explore(interaction.user.id)
        if not success:
            await interaction.response.send_message(res, ephemeral=True)
        else:
            await interaction.response.send_message(embed=res)

    @commands.command(name="thamhiem", aliases=["bicanh", "th"])
    async def prefix_thamhiem(self, ctx: commands.Context):
        success, res = perform_explore(ctx.author.id)
        if not success:
            await ctx.send(res)
        else:
            await ctx.send(embed=res)

async def setup(bot: commands.Bot):
    await bot.add_cog(CultivationCog(bot))
