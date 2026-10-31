import sqlite3
import time
from datetime import datetime, timezone, timedelta
from config import DB_NAME, CONG_PHAP, DAILY_QUESTS

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    linh_can TEXT,
                    speed REAL,
                    realm_idx INTEGER DEFAULT 0,
                    exp INTEGER DEFAULT 0,
                    linh_thach INTEGER DEFAULT 150,
                    bonus_rate REAL DEFAULT 0.0,
                    last_cultivate INTEGER,
                    last_explore INTEGER DEFAULT 0,
                    cong_phap_idx INTEGER DEFAULT 0,
                    speed_boost REAL DEFAULT 0.0,
                    speed_boost_end INTEGER DEFAULT 0,
                    tong_mon_id INTEGER DEFAULT 0,
                    spouse_id INTEGER DEFAULT 0,
                    daily_quest_date TEXT DEFAULT '',
                    q_cultivate INTEGER DEFAULT 0,
                    q_explore INTEGER DEFAULT 0,
                    q_fight INTEGER DEFAULT 0,
                    q_pills INTEGER DEFAULT 0,
                    pvp_wins INTEGER DEFAULT 0,
                    pvp_losses INTEGER DEFAULT 0,
                    total_exp_gained INTEGER DEFAULT 0
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    eq_type TEXT,
                    eq_name TEXT,
                    grade INTEGER,
                    atk_bonus INTEGER DEFAULT 0,
                    def_bonus INTEGER DEFAULT 0,
                    is_equipped INTEGER DEFAULT 0
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tong_mon (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    leader_id INTEGER,
                    description TEXT DEFAULT '',
                    linh_thach INTEGER DEFAULT 0,
                    created_at INTEGER
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS marriage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    married_at INTEGER,
                    UNIQUE(user1_id, user2_id)
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS marriage_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER,
                    to_id INTEGER,
                    created_at INTEGER
                )""")
    # 1. Động Phủ
    c.execute("""CREATE TABLE IF NOT EXISTS dong_phu (
                    user_id INTEGER PRIMARY KEY,
                    level_tran INTEGER DEFAULT 1,
                    level_vuon INTEGER DEFAULT 1,
                    last_harvest INTEGER DEFAULT 0,
                    last_spring INTEGER DEFAULT 0
                )""")
    # 2. Tiên Cư
    c.execute("""CREATE TABLE IF NOT EXISTS tiencu (
                    user_id INTEGER PRIMARY KEY,
                    home_level INTEGER DEFAULT 1,
                    comfort INTEGER DEFAULT 10
                )""")
    # 3. Phúc Lợi / Điểm Danh
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                    user_id INTEGER PRIMARY KEY,
                    last_claim_date TEXT DEFAULT '',
                    streak INTEGER DEFAULT 0,
                    claimed_starter INTEGER DEFAULT 0
                )""")
    # 4. Vạn Thú Các (Linh Thú)
    c.execute("""CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    species TEXT,
                    level INTEGER DEFAULT 1,
                    atk_bonus INTEGER DEFAULT 50,
                    def_bonus INTEGER DEFAULT 30,
                    is_active INTEGER DEFAULT 0
                )""")
    # 5. Nô Khu (Khai mỏ Linh Thạch)
    c.execute("""CREATE TABLE IF NOT EXISTS slaves (
                    user_id INTEGER PRIMARY KEY,
                    slave_count INTEGER DEFAULT 1,
                    last_mine INTEGER DEFAULT 0
                )""")
    # 6. Vạn Bảo Lâu (Chợ Đấu Giá)
    c.execute("""CREATE TABLE IF NOT EXISTS market (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER,
                    seller_name TEXT,
                    item_name TEXT,
                    item_type TEXT,
                    atk_bonus INTEGER DEFAULT 0,
                    def_bonus INTEGER DEFAULT 0,
                    price INTEGER,
                    created_at INTEGER
                )""")
    # 7. Vấn Đỉnh (Leo Tháp)
    c.execute("""CREATE TABLE IF NOT EXISTS vandinh_tower (
                    user_id INTEGER PRIMARY KEY,
                    floor INTEGER DEFAULT 1,
                    max_floor INTEGER DEFAULT 1,
                    last_challenge INTEGER DEFAULT 0
                )""")
    # 8. Lịch Luyện (Treo máy)
    c.execute("""CREATE TABLE IF NOT EXISTS lichluyen (
                    user_id INTEGER PRIMARY KEY,
                    map_id INTEGER DEFAULT 1,
                    start_time INTEGER DEFAULT 0
                )""")
    # 9. Bảng Chọn Vai Trò (Pick Role)
    c.execute("""CREATE TABLE IF NOT EXISTS pickrole_panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER DEFAULT 0,
                    title TEXT,
                    description TEXT,
                    color INTEGER DEFAULT 3447003,
                    mode TEXT DEFAULT 'toggle',
                    ui_style TEXT DEFAULT 'button',
                    created_at INTEGER
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS pickrole_options (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    role_id INTEGER,
                    label TEXT,
                    emoji TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    button_style TEXT DEFAULT 'primary'
                )""")
    try:
        c.execute("ALTER TABLE market ADD COLUMN grade INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Tự động cập nhật chỉ số cảnh giới (realm_idx) khi mở rộng phân bậc cảnh giới
    c.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY
                )""")
    row = c.execute("SELECT version FROM schema_migrations WHERE version = 1").fetchone()
    if not row:
        migration_map = [
            (13, 23),  # Đại Thừa - Sơ Kỳ: 13 -> 23
            (12, 20),  # Hợp Thể - Sơ Kỳ: 12 -> 20
            (11, 17),  # Luyện Hư - Sơ Kỳ: 11 -> 17
            (10, 14),  # Hóa Thần - Sơ Kỳ: 10 -> 14
            (9, 11)    # Nguyên Anh - Sơ Kỳ: 9 -> 11
        ]
        for old_idx, new_idx in migration_map:
            c.execute("UPDATE players SET realm_idx = ? WHERE realm_idx = ?", (new_idx, old_idx))
        c.execute("INSERT INTO schema_migrations (version) VALUES (1)")

    conn.commit()
    conn.close()

def get_player(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_cultivation(user_id: int, new_name: str = None):
    player = get_player(user_id)
    if not player:
        return None, 0

    now = int(time.time())
    last_time = player[8]
    elapsed = max(0, now - last_time)

    speed = player[3]
    realm_idx = player[4]
    speed_boost = player[11]
    speed_boost_end = player[12]
    cong_phap_idx = player[10]
    spouse_id = player[14]

    realm_bonus = 1 + (realm_idx * 0.25)
    cp = CONG_PHAP[cong_phap_idx]
    cp_exp_bonus = 1 + cp["exp_bonus"]

    active_boost = speed_boost if now < speed_boost_end else 0.0
    effective_speed = speed + active_boost

    # Buff hôn nhân +5%
    marriage_mult = 1.05 if spouse_id else 1.0

    gained_exp = int((elapsed / 60) * 12 * effective_speed * realm_bonus * cp_exp_bonus * marriage_mult)
    new_exp = player[5] + gained_exp
    new_total = player[22] + gained_exp

    new_boost_end = speed_boost_end if now < speed_boost_end else 0
    new_boost = speed_boost if now < speed_boost_end else 0.0

    conn = get_connection()
    c = conn.cursor()
    updated = list(player)

    if new_name and new_name.strip() and new_name.strip() != player[1]:
        clean_name = new_name.strip()
        c.execute("""UPDATE players SET exp = ?, last_cultivate = ?, speed_boost = ?, speed_boost_end = ?, total_exp_gained = ?, name = ?
                     WHERE user_id = ?""", (new_exp, now, new_boost, new_boost_end, new_total, clean_name, user_id))
        updated[1] = clean_name
    else:
        c.execute("""UPDATE players SET exp = ?, last_cultivate = ?, speed_boost = ?, speed_boost_end = ?, total_exp_gained = ?
                     WHERE user_id = ?""", (new_exp, now, new_boost, new_boost_end, new_total, user_id))
    conn.commit()
    conn.close()

    updated[5] = new_exp
    updated[8] = now
    updated[11] = new_boost
    updated[12] = new_boost_end
    updated[22] = new_total
    return tuple(updated), gained_exp

def get_equipment_bonus(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT eq_type, atk_bonus, def_bonus FROM equipment WHERE user_id = ? AND is_equipped = 1", (user_id,))
    rows = c.fetchall()
    conn.close()
    total_atk = sum(r[1] for r in rows)
    total_def = sum(r[2] for r in rows)
    return total_atk, total_def

def get_tong_mon(tong_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tong_mon WHERE id = ?", (tong_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_today_str():
    vn_tz = timezone(timedelta(hours=7))
    return datetime.now(vn_tz).strftime("%Y-%m-%d")

def reset_daily_if_needed(user_id: int):
    player = get_player(user_id)
    if not player:
        return
    today = get_today_str()
    if player[15] != today:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""UPDATE players SET daily_quest_date = ?, q_cultivate = 0, q_explore = 0, q_fight = 0, q_pills = 0
                     WHERE user_id = ?""", (today, user_id))
        conn.commit()
        conn.close()

def add_quest_progress(user_id: int, quest_id: str, amount: int = 1):
    reset_daily_if_needed(user_id)
    player = get_player(user_id)
    if not player:
        return False
    col_map = {"q_cultivate": 16, "q_explore": 17, "q_fight": 18, "q_pills": 19}
    col_idx = col_map.get(quest_id)
    if col_idx is None:
        return False
    current = player[col_idx]
    quest_def = next((q for q in DAILY_QUESTS if q["id"] == quest_id), None)
    if quest_def is None:
        return False
    if current >= quest_def["target"]:
        return False
    new_val = min(current + amount, quest_def["target"])
    completed = (new_val >= quest_def["target"] and current < quest_def["target"])
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE players SET {quest_id} = ? WHERE user_id = ?", (new_val, user_id))
    if completed:
        c.execute("UPDATE players SET exp = exp + ?, linh_thach = linh_thach + ? WHERE user_id = ?",
                  (quest_def["reward_exp"], quest_def["reward_stone"], user_id))
    conn.commit()
    conn.close()
    return completed

def get_or_create_dongphu(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM dong_phu WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        now = int(time.time())
        c.execute("INSERT INTO dong_phu (user_id, level_tran, level_vuon, last_harvest, last_spring) VALUES (?, 1, 1, ?, ?)", (user_id, now, now))
        conn.commit()
        c.execute("SELECT * FROM dong_phu WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def get_or_create_tiencu(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tiencu WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO tiencu (user_id, home_level, comfort) VALUES (?, 1, 10)", (user_id,))
        conn.commit()
        c.execute("SELECT * FROM tiencu WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def get_or_create_attendance(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO attendance (user_id, last_claim_date, streak, claimed_starter) VALUES (?, '', 0, 0)", (user_id,))
        conn.commit()
        c.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def get_or_create_slaves(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM slaves WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        now = int(time.time())
        c.execute("INSERT INTO slaves (user_id, slave_count, last_mine) VALUES (?, 1, ?)", (user_id, now))
        conn.commit()
        c.execute("SELECT * FROM slaves WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def get_or_create_vandinh(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vandinh_tower WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO vandinh_tower (user_id, floor, max_floor, last_challenge) VALUES (?, 1, 1, 0)", (user_id,))
        conn.commit()
        c.execute("SELECT * FROM vandinh_tower WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return row

def get_active_pet(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM pets WHERE user_id = ? AND is_active = 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_player_combat_stats(user_id: int):
    """Tính toán toàn diện chỉ số và chiến lực của người chơi (Cảnh giới, Trang bị, Công pháp, Linh thú)"""
    player = get_player(user_id)
    if not player:
        return None
    from config import REALMS
    realm_idx = player[4]
    r = REALMS[min(realm_idx, len(REALMS) - 1)]
    cong_phap_idx = player[10]
    cp = CONG_PHAP[min(cong_phap_idx, len(CONG_PHAP) - 1)]
    eq_atk, eq_def = get_equipment_bonus(user_id)

    pet = get_active_pet(user_id)
    pet_atk = pet[5] if pet else 0
    pet_def = pet[6] if pet else 0

    p_hp = int(r["hp"] * (1 + cp.get("def_bonus", 0)))
    p_atk = int((r["atk"] + eq_atk + pet_atk) * (1 + cp.get("atk_bonus", 0)))
    p_def = int((r["def"] + eq_def + pet_def) * (1 + cp.get("def_bonus", 0)))
    power = p_atk * 2 + p_def * 2 + p_hp // 2

    return {
        "player": player,
        "realm_idx": realm_idx,
        "realm_name": r["name"],
        "realm_icon": r["icon"],
        "hp": p_hp,
        "atk": p_atk,
        "def": p_def,
        "power": power,
        "eq_atk": eq_atk,
        "eq_def": eq_def,
        "pet_atk": pet_atk,
        "pet_def": pet_def,
        "cp_name": cp["name"],
        "cp_icon": cp["icon"]
    }

def reset_player(user_id: int) -> bool:
    """Xóa bỏ hoàn toàn dữ liệu của người chơi để họ trở về trạng thái Phàm Nhân ban đầu"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, tong_mon_id, spouse_id FROM players WHERE user_id = ?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        return False

    # 1. Hôn nhân
    if p[2]:
        spouse_id = p[2]
        c.execute("UPDATE players SET spouse_id = 0 WHERE user_id = ?", (spouse_id,))
    c.execute("DELETE FROM marriage WHERE user1_id = ? OR user2_id = ?", (user_id, user_id))
    c.execute("DELETE FROM marriage_requests WHERE from_id = ? OR to_id = ?", (user_id, user_id))

    # 2. Tông môn (nếu là bang chủ thì giải tán tông môn và cập nhật các thành viên)
    c.execute("SELECT id FROM tong_mon WHERE leader_id = ?", (user_id,))
    tm_rows = c.fetchall()
    for (tm_id,) in tm_rows:
        c.execute("UPDATE players SET tong_mon_id = 0 WHERE tong_mon_id = ?", (tm_id,))
        c.execute("DELETE FROM tong_mon WHERE id = ?", (tm_id,))

    # 3. Xóa các dữ liệu liên quan
    c.execute("DELETE FROM equipment WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM pets WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM dong_phu WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM tiencu WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM attendance WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM slaves WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM vandinh_tower WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM lichluyen WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM market WHERE seller_id = ?", (user_id,))

    # 4. Xóa khỏi bảng players
    c.execute("DELETE FROM players WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()
    return True

def reset_all_players() -> int:
    """Xóa bỏ toàn bộ dữ liệu người chơi trong database về ban đầu"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM players")
    row = c.fetchone()
    count = row[0] if row else 0
    tables = [
        "players", "equipment", "tong_mon", "marriage", "marriage_requests",
        "dong_phu", "tiencu", "attendance", "pets", "slaves", "market",
        "vandinh_tower", "lichluyen"
    ]
    for t in tables:
        c.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
    return count

# ================= PICK ROLE (BẢNG CHỌN VAI TRÒ) =================

def create_pickrole_panel(guild_id: int, channel_id: int, title: str, description: str, color: int, mode: str, ui_style: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    now = int(time.time())
    c.execute("""INSERT INTO pickrole_panels (guild_id, channel_id, message_id, title, description, color, mode, ui_style, created_at)
                 VALUES (?, ?, 0, ?, ?, ?, ?, ?, ?)""",
              (guild_id, channel_id, title, description, color, mode, ui_style, now))
    panel_id = c.lastrowid
    conn.commit()
    conn.close()
    return panel_id

def update_pickrole_message(panel_id: int, message_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE pickrole_panels SET message_id = ? WHERE id = ?", (message_id, panel_id))
    conn.commit()
    conn.close()

def add_pickrole_option(panel_id: int, role_id: int, label: str, emoji: str = "", description: str = "", button_style: str = "primary") -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO pickrole_options (panel_id, role_id, label, emoji, description, button_style)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (panel_id, role_id, label, emoji, description, button_style))
    opt_id = c.lastrowid
    conn.commit()
    conn.close()
    return opt_id

def remove_pickrole_option(panel_id: int, role_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM pickrole_options WHERE panel_id = ? AND role_id = ?", (panel_id, role_id))
    rows = c.rowcount
    conn.commit()
    conn.close()
    return rows > 0

def get_pickrole_panel(panel_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pickrole_panels WHERE id = ?", (panel_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_pickrole_panel_by_message(message_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pickrole_panels WHERE message_id = ?", (message_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_pickrole_options(panel_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pickrole_options WHERE panel_id = ? ORDER BY id ASC", (panel_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_guild_pickrole_panels(guild_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pickrole_panels WHERE guild_id = ? ORDER BY id DESC", (guild_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_active_pickrole_panels():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pickrole_panels WHERE message_id > 0")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_pickrole_panel(panel_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM pickrole_options WHERE panel_id = ?", (panel_id,))
    c.execute("DELETE FROM pickrole_panels WHERE id = ?", (panel_id,))
    rows = c.rowcount
    conn.commit()
    conn.close()
    return rows > 0


