import os

# ================= CƠ SỞ DỮ LIỆU =================
DB_NAME = os.getenv("DB_NAME", "tutien_chinh_thong.db")

# ================= CẤU HÌNH OWNER BOT =================
def get_owner_ids():
    raw_owners = os.getenv("OWNER_ID", "")
    owner_set = set()
    for part in raw_owners.replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            owner_set.add(int(part))
    return owner_set

def is_owner_id(user_id: int) -> bool:
    return user_id in get_owner_ids()

# ================= CẤU HÌNH CẢNH GIỚI & LINH CĂN =================
REALMS = [
    # Phàm Nhân
    {"name": "Phàm Nhân",            "max_exp": 100,      "rate": 1.00, "hp": 100,        "atk": 10,       "def": 5,        "icon": "🪨"},
    # Luyện Khí
    {"name": "Luyện Khí - Sơ Kỳ",   "max_exp": 300,      "rate": 0.90, "hp": 250,        "atk": 25,       "def": 12,       "icon": "🌱"},
    {"name": "Luyện Khí - Trung Kỳ", "max_exp": 700,      "rate": 0.80, "hp": 500,        "atk": 50,       "def": 25,       "icon": "🌿"},
    {"name": "Luyện Khí - Hậu Kỳ",  "max_exp": 1500,     "rate": 0.70, "hp": 900,        "atk": 90,       "def": 45,       "icon": "🍃"},
    {"name": "Luyện Khí - Đỉnh Phong","max_exp": 3000,    "rate": 0.60, "hp": 1500,       "atk": 150,      "def": 80,       "icon": "🌲"},
    # Trúc Cơ
    {"name": "Trúc Cơ - Sơ Kỳ",     "max_exp": 6500,     "rate": 0.45, "hp": 3500,       "atk": 350,      "def": 180,      "icon": "💧"},
    {"name": "Trúc Cơ - Trung Kỳ",  "max_exp": 14000,    "rate": 0.40, "hp": 6000,       "atk": 600,      "def": 300,      "icon": "🌊"},
    {"name": "Trúc Cơ - Hậu Kỳ",   "max_exp": 28000,    "rate": 0.35, "hp": 10000,      "atk": 1000,     "def": 500,      "icon": "🌀"},
    # Kết Đan
    {"name": "Kết Đan - Sơ Kỳ",     "max_exp": 60000,    "rate": 0.25, "hp": 25000,      "atk": 2500,     "def": 1200,     "icon": "💠"},
    {"name": "Kết Đan - Trung Kỳ",  "max_exp": 85000,    "rate": 0.22, "hp": 38000,      "atk": 3800,     "def": 1800,     "icon": "💠"},
    {"name": "Kết Đan - Hậu Kỳ",   "max_exp": 115000,   "rate": 0.18, "hp": 52000,      "atk": 5200,     "def": 2500,     "icon": "💠"},
    # Nguyên Anh
    {"name": "Nguyên Anh - Sơ Kỳ",  "max_exp": 150000,   "rate": 0.15, "hp": 70000,      "atk": 7500,     "def": 3500,     "icon": "🔮"},
    {"name": "Nguyên Anh - Trung Kỳ","max_exp": 220000,  "rate": 0.13, "hp": 105000,     "atk": 11500,    "def": 5500,     "icon": "🔮"},
    {"name": "Nguyên Anh - Hậu Kỳ", "max_exp": 300000,   "rate": 0.11, "hp": 150000,     "atk": 16000,    "def": 7500,     "icon": "🔮"},
    # Hóa Thần
    {"name": "Hóa Thần - Sơ Kỳ",    "max_exp": 400000,   "rate": 0.10, "hp": 200000,     "atk": 22000,    "def": 10000,    "icon": "⭐"},
    {"name": "Hóa Thần - Trung Kỳ", "max_exp": 580000,   "rate": 0.09, "hp": 300000,     "atk": 35000,    "def": 16000,    "icon": "⭐"},
    {"name": "Hóa Thần - Hậu Kỳ",  "max_exp": 780000,   "rate": 0.08, "hp": 440000,     "atk": 50000,    "def": 22000,    "icon": "⭐"},
    # Luyện Hư
    {"name": "Luyện Hư - Sơ Kỳ",    "max_exp": 1000000,  "rate": 0.07, "hp": 600000,     "atk": 70000,    "def": 30000,    "icon": "🌟"},
    {"name": "Luyện Hư - Trung Kỳ", "max_exp": 1500000,  "rate": 0.065,"hp": 950000,     "atk": 115000,   "def": 48000,    "icon": "🌟"},
    {"name": "Luyện Hư - Hậu Kỳ",  "max_exp": 2200000,  "rate": 0.06, "hp": 1400000,   "atk": 175000,   "def": 72000,    "icon": "🌟"},
    # Hợp Thể
    {"name": "Hợp Thể - Sơ Kỳ",     "max_exp": 3000000,  "rate": 0.05, "hp": 2000000,    "atk": 250000,   "def": 100000,   "icon": "✨"},
    {"name": "Hợp Thể - Trung Kỳ",  "max_exp": 4800000,  "rate": 0.045,"hp": 3500000,    "atk": 450000,   "def": 180000,   "icon": "✨"},
    {"name": "Hợp Thể - Hậu Kỳ",   "max_exp": 7000000,  "rate": 0.04, "hp": 5500000,    "atk": 700000,   "def": 280000,   "icon": "✨"},
    # Đại Thừa
    {"name": "Đại Thừa - Sơ Kỳ",    "max_exp": 10000000, "rate": 0.03, "hp": 8000000,    "atk": 1000000,  "def": 400000,   "icon": "☀️"},
    {"name": "Đại Thừa - Trung Kỳ", "max_exp": 16000000, "rate": 0.025,"hp": 14000000,   "atk": 1800000,  "def": 700000,   "icon": "☀️"},
    {"name": "Đại Thừa - Hậu Kỳ",  "max_exp": 25000000, "rate": 0.02, "hp": 22000000,   "atk": 3000000,  "def": 1200000,  "icon": "☀️"},
]

SPIRIT_ROOTS = [
    {"name": "Ngụy Linh Căn (Ngũ Hành Khuyết)", "speed": 0.8,  "weight": 40, "desc": "Linh khí tạp loạn, con đường tu đạo gian nan gấp bội.", "color": 0x95a5a6},
    {"name": "Chân Linh Căn (Hỏa - Mộc)",       "speed": 1.2,  "weight": 30, "desc": "Tư chất trung đẳng, thích hợp luyện đan và tu luyện chính thống.", "color": 0x27ae60},
    {"name": "Dị Linh Căn - Phong Hệ",           "speed": 1.7,  "weight": 12, "desc": "Biến dị linh căn hiếm gặp, thân pháp và tốc độ hấp thụ linh khí cực nhanh.", "color": 0x3498db},
    {"name": "Dị Linh Căn - Lôi Hệ",             "speed": 1.9,  "weight": 11, "desc": "Chưởng quản sấm sét, sát phạt quả đoán, khắc chế tà ma.", "color": 0xf39c12},
    {"name": "Thiên Linh Căn (Cực Phẩm Thủy)",   "speed": 2.5,  "weight": 5,  "desc": "Thiên đạo sủng nhi, trước Kết Đan cơ hồ không có bình cảnh.", "color": 0x1abc9c},
    {"name": "Hỗn Độn Tiên Thiên Linh Căn",      "speed": 4.0,  "weight": 2,  "desc": "Vạn năm có một, dung nạp hồng mông tử khí, kinh thiên động địa!", "color": 0x9b59b6},
]

FAIL_MESSAGES = [
    "tâm ma quấy nhiễu lúc xung quan, kinh mạch nghịch chuyển mà thổ huyết!",
    "không chịu nổi uy áp của Cửu Cửu Thiên Kiếp, đạo cơ bị tổn hại!",
    "linh khí trong đan điền bạo động, suýt chút nữa thân tử đạo tiêu!",
    "ngộ đạo chưa thông, vội vàng cưỡng ép đột phá dẫn đến tẩu hỏa nhập ma!"
]

# ================= CÔNG PHÁP =================
CONG_PHAP = [
    {"name": "Luyện Khí Quyết (Cơ Bản)",   "cost": 0,      "atk_bonus": 0.05, "def_bonus": 0.05, "exp_bonus": 0.05, "req_realm": 0,  "desc": "Công pháp cơ bản, miễn phí cho người mới nhập đạo.", "icon": "📖"},
    {"name": "Hỏa Linh Kiếm Quyết",         "cost": 500,    "atk_bonus": 0.15, "def_bonus": 0.05, "exp_bonus": 0.08, "req_realm": 1,  "desc": "Kiếm quyết hóa hỏa, luyện chưởng như kiếm khí thiêu đốt.", "icon": "🔥"},
    {"name": "Huyền Băng Linh Quyết",       "cost": 800,    "atk_bonus": 0.08, "def_bonus": 0.20, "exp_bonus": 0.10, "req_realm": 2,  "desc": "Luyện thân băng giá, phòng thủ vững như thành đá.", "icon": "❄️"},
    {"name": "Lôi Đình Bát Quái Quyết",     "cost": 2000,   "atk_bonus": 0.25, "def_bonus": 0.10, "exp_bonus": 0.12, "req_realm": 4,  "desc": "Cưỡng ép thiên lôi, mỗi chiêu đánh đều như sấm trời nổ vang.", "icon": "⚡"},
    {"name": "Cửu Chuyển Kim Đan Quyết",    "cost": 6000,   "atk_bonus": 0.20, "def_bonus": 0.20, "exp_bonus": 0.25, "req_realm": 5,  "desc": "Đan đạo tôn công pháp, cân bằng tấn thủ, tốc độ tu luyện thần tốc.", "icon": "💊"},
    {"name": "Vạn Kiếm Quy Tông Quyết",    "cost": 15000,  "atk_bonus": 0.40, "def_bonus": 0.15, "exp_bonus": 0.20, "req_realm": 7,  "desc": "Vô số kiếm khí quy về một điểm, sát thương cực cao.", "icon": "⚔️"},
    {"name": "Thái Cực Hỗn Độn Quyết",     "cost": 50000,  "atk_bonus": 0.35, "def_bonus": 0.35, "exp_bonus": 0.40, "req_realm": 11, "desc": "Công pháp đỉnh cao của Hỗn Độn Linh Căn, toàn năng vô địch.", "icon": "☯️"},
    {"name": "Phong Thần Thiên Địa Chuyển", "cost": 200000, "atk_bonus": 0.60, "def_bonus": 0.50, "exp_bonus": 0.60, "req_realm": 17, "desc": "Công pháp cổ tiên, dung hợp phong hệ với thiên địa nguyên lực.", "icon": "🌪️"},
    {"name": "Hư Vô Thần Quyết",           "cost": 500000, "atk_bonus": 0.85, "def_bonus": 0.70, "exp_bonus": 0.80, "req_realm": 20, "desc": "Dung hợp hư không bản nguyên, cử chỉ dời non lấp bể.", "icon": "🌌"},
    {"name": "Cửu Thiên Vạn Kiếp Quy Chân", "cost": 1500000,"atk_bonus": 1.20, "def_bonus": 1.00, "exp_bonus": 1.00, "req_realm": 23, "desc": "Công pháp chí tôn của cảnh giới Đại Thừa, ngộ thấu thiên đạo luân hồi.", "icon": "☀️"},
]

# ================= TRANG BỊ & PHÁP BẢO =================
EQUIPMENT_TYPES = ["Vũ Khí", "Áo", "Quần", "Giày", "Nhẫn"]

# 5 ĐẠI CẤP BẬC TRANG BỊ
EQUIPMENT_TIERS = [
    {
        "tier": 1,
        "name": "Phàm Khí / Pháp Khí",
        "stage": "Luyện Khí – Trúc Cơ",
        "icon": "⚔️",
        "desc": "Vũ khí thế tục hoặc pháp khí khắc trận pháp cơ bản, dùng bởi tu sĩ cấp thấp."
    },
    {
        "tier": 2,
        "name": "Linh Bảo",
        "stage": "Kết Đan – Nguyên Anh",
        "icon": "✨",
        "desc": "Có uy áp linh khí mạnh mẽ, phá hủy núi non, có linh tính sơ khai."
    },
    {
        "tier": 3,
        "name": "Thông Linh Bảo",
        "stage": "Hóa Thần – Luyện Hư",
        "icon": "🔮",
        "desc": "Pháp bảo bản mệnh đã sinh khí linh, tự động hộ chủ, biến hóa kích thước tùy ý."
    },
    {
        "tier": 4,
        "name": "Tiên Khí",
        "stage": "Hợp Thể – Đại Thừa – Độ Kiếp",
        "icon": "🏮",
        "desc": "Tích chứa Tiên Linh Khí thuần khiết, xé rách không gian, ẩn chứa quy tắc thiên địa."
    },
    {
        "tier": 5,
        "name": "Hỗn Độn / Hồng Mông",
        "stage": "Hồng Hoang Đỉnh Cao",
        "icon": "👑",
        "desc": "Sinh ra từ hỗn độn sơ khai, mang đại đạo bản nguyên, đứng đầu trật tự vũ trụ."
    }
]

# 23 PHẨM CẤP CHI TIẾT
EQUIPMENT_GRADES = [
    # Tier 1: Phàm Khí / Pháp Khí (Giai đoạn Luyện Khí – Trúc Cơ)
    {
        "id": 0, "tier": 1, "tier_name": "Phàm Khí / Pháp Khí", "stage": "Luyện Khí – Trúc Cơ",
        "name": "Phàm Khí", "icon": "⚪", "color": 0x95a5a6,
        "atk_mult": 1.0, "def_mult": 1.0,
        "desc": "Vũ khí bình thường do thợ rèn làm từ kim loại thế tục, không có linh lực."
    },
    {
        "id": 1, "tier": 1, "tier_name": "Phàm Khí / Pháp Khí", "stage": "Luyện Khí – Trúc Cơ",
        "name": "Hạ Phẩm Pháp Khí", "icon": "⚪", "color": 0xbdc3c7,
        "atk_mult": 1.3, "def_mult": 1.3,
        "desc": "Đã khắc trận pháp đơn giản, có thể dẫn truyền linh lực sơ khai."
    },
    {
        "id": 2, "tier": 1, "tier_name": "Phàm Khí / Pháp Khí", "stage": "Luyện Khí – Trúc Cơ",
        "name": "Trung Phẩm Pháp Khí", "icon": "🟢", "color": 0x2ecc71,
        "atk_mult": 1.7, "def_mult": 1.7,
        "desc": "Trận pháp kiên cố, linh lực lưu chuyển mượt mà thông suốt."
    },
    {
        "id": 3, "tier": 1, "tier_name": "Phàm Khí / Pháp Khí", "stage": "Luyện Khí – Trúc Cơ",
        "name": "Thượng Phẩm Pháp Khí", "icon": "🟢", "color": 0x27ae60,
        "atk_mult": 2.2, "def_mult": 2.2,
        "desc": "Rèn từ khoáng thạch trăm năm, sát thương và thủ ngự vững chắc."
    },
    {
        "id": 4, "tier": 1, "tier_name": "Phàm Khí / Pháp Khí", "stage": "Luyện Khí – Trúc Cơ",
        "name": "Cực Phẩm Pháp Khí", "icon": "🔵", "color": 0x3498db,
        "atk_mult": 3.0, "def_mult": 3.0,
        "desc": "Đỉnh cao pháp khí tu sĩ Trúc Cơ tranh đoạt, uy lực vô song ở hạ giới."
    },

    # Tier 2: Linh Bảo (Giai đoạn Kết Đan – Nguyên Anh)
    {
        "id": 5, "tier": 2, "tier_name": "Linh Bảo", "stage": "Kết Đan – Nguyên Anh",
        "name": "Hạ Phẩm Linh Bảo", "icon": "🔵", "color": 0x2980b9,
        "atk_mult": 4.5, "def_mult": 4.5,
        "desc": "Uy lực bắt đầu có uy áp linh khí mạnh mẽ."
    },
    {
        "id": 6, "tier": 2, "tier_name": "Linh Bảo", "stage": "Kết Đan – Nguyên Anh",
        "name": "Trung Phẩm Linh Bảo", "icon": "🔷", "color": 0x1abc9c,
        "atk_mult": 6.5, "def_mult": 6.5,
        "desc": "Phá hủy được núi non, có chút linh tính cơ bản."
    },
    {
        "id": 7, "tier": 2, "tier_name": "Linh Bảo", "stage": "Kết Đan – Nguyên Anh",
        "name": "Thượng Phẩm Linh Bảo", "icon": "🟣", "color": 0x9b59b6,
        "atk_mult": 9.5, "def_mult": 9.5,
        "desc": "Công kích uyển chuyển, có thể thu phóng theo ý niệm."
    },
    {
        "id": 8, "tier": 2, "tier_name": "Linh Bảo", "stage": "Kết Đan – Nguyên Anh",
        "name": "Cực Phẩm Linh Bảo", "icon": "🟣", "color": 0x8e44ad,
        "atk_mult": 14.0, "def_mult": 14.0,
        "desc": "Đỉnh cao của linh bảo thông thường, gần chạm ngưỡng thông linh sâu sắc."
    },

    # Tier 3: Thông Linh Bảo / Pháp Bảo Bản Mệnh (Giai đoạn Hóa Thần – Luyện Hư)
    {
        "id": 9, "tier": 3, "tier_name": "Thông Linh Bảo", "stage": "Hóa Thần – Luyện Hư",
        "name": "Hạ Phẩm Thông Linh Bảo", "icon": "🪞", "color": 0xe056fd,
        "atk_mult": 20.0, "def_mult": 20.0,
        "desc": "Đã có ý thức sơ khai, có thể tự động hộ chủ khi gặp hiểm nguy."
    },
    {
        "id": 10, "tier": 3, "tier_name": "Thông Linh Bảo", "stage": "Hóa Thần – Luyện Hư",
        "name": "Trung Phẩm Thông Linh Bảo", "icon": "🔮", "color": 0xbe2edd,
        "atk_mult": 28.0, "def_mult": 28.0,
        "desc": "Khí linh ngưng tụ thành hình tiểu hài tử, biến hóa kích thước tùy ý."
    },
    {
        "id": 11, "tier": 3, "tier_name": "Thông Linh Bảo", "stage": "Hóa Thần – Luyện Hư",
        "name": "Thượng Phẩm Thông Linh Bảo", "icon": "🌸", "color": 0xf0932b,
        "atk_mult": 40.0, "def_mult": 40.0,
        "desc": "Khí linh thông tuệ, cùng chủ nhân hòa làm một thể, uy chấn thiên hạ."
    },
    {
        "id": 12, "tier": 3, "tier_name": "Thông Linh Bảo", "stage": "Hóa Thần – Luyện Hư",
        "name": "Chí Bảo Thông Linh", "icon": "🏵️", "color": 0xff7979,
        "atk_mult": 60.0, "def_mult": 60.0,
        "desc": "Sinh ra từ thiên địa nguyên khí, uy lực vượt xa linh bảo bình thường."
    },

    # Tier 4: Tiên Khí (Giai đoạn Hợp Thể – Đại Thừa – Độ Kiếp / Phi Thăng)
    {
        "id": 13, "tier": 4, "tier_name": "Tiên Khí", "stage": "Hợp Thể – Đại Thừa – Độ Kiếp",
        "name": "Hạ Phẩm Tiên Khí", "icon": "🟡", "color": 0xf1c40f,
        "atk_mult": 85.0, "def_mult": 85.0,
        "desc": "Vũ khí của tu sĩ mới phi thăng hoặc Chân Tiên cấp thấp, tích chứa Tiên Linh Khí."
    },
    {
        "id": 14, "tier": 4, "tier_name": "Tiên Khí", "stage": "Hợp Thể – Đại Thừa – Độ Kiếp",
        "name": "Trung Phẩm Tiên Khí", "icon": "🌟", "color": 0xf39c12,
        "atk_mult": 120.0, "def_mult": 120.0,
        "desc": "Uy lực có thể xé rách không gian hạ giới một cách dễ dàng."
    },
    {
        "id": 15, "tier": 4, "tier_name": "Tiên Khí", "stage": "Hợp Thể – Đại Thừa – Độ Kiếp",
        "name": "Thượng Phẩm Tiên Khí", "icon": "✨", "color": 0xe67e22,
        "atk_mult": 170.0, "def_mult": 170.0,
        "desc": "Có uy năng quy tắc nhỏ của thiên địa, nhất kích toái tinh thần."
    },
    {
        "id": 16, "tier": 4, "tier_name": "Tiên Khí", "stage": "Hợp Thể – Đại Thừa – Độ Kiếp",
        "name": "Cực Phẩm Tiên Khí", "icon": "🏮", "color": 0xd35400,
        "atk_mult": 250.0, "def_mult": 250.0,
        "desc": "Bảo vật của Tiên Vương / Tiên Tôn cấp cao trấn áp chư thiên vạn giới."
    },

    # Tier 5: Hỗn Độn Linh Bảo / Hồng Mông Chí Bảo (Cấp bậc Hồng Hoang / Đỉnh cao Tiên Hiệp)
    {
        "id": 17, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Hạ Phẩm Tiên Thiên Linh Bảo", "icon": "🔴", "color": 0xe74c3c,
        "atk_mult": 360.0, "def_mult": 360.0,
        "desc": "Sinh ra từ hỗn độn sơ khai, mang theo một tia đại đạo bản nguyên."
    },
    {
        "id": 18, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Trung Phẩm Tiên Thiên Linh Bảo", "icon": "🩸", "color": 0xc0392b,
        "atk_mult": 520.0, "def_mult": 520.0,
        "desc": "Khai thiên tích địa sinh ra, ẩn chứa pháp tắc đại đạo nguyên thủy."
    },
    {
        "id": 19, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Thượng Phẩm Tiên Thiên Linh Bảo", "icon": "🌌", "color": 0x6c5ce7,
        "atk_mult": 750.0, "def_mult": 750.0,
        "desc": "Mang quy tắc đại đạo hoàn chỉnh, có thể tự diễn sinh một phương đại thế giới."
    },
    {
        "id": 20, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Cực Phẩm Tiên Thiên Linh Bảo", "icon": "🪐", "color": 0x575fcf,
        "atk_mult": 1100.0, "def_mult": 1100.0,
        "desc": "Đỉnh cao tiên thiên (như Thập Nhị Phẩm Liên Hoa), chứa 48 đạo cấm chế vô thượng."
    },
    {
        "id": 21, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Hỗn Độn Chí Bảo", "icon": "☯️", "color": 0x2d3436,
        "atk_mult": 1600.0, "def_mult": 1600.0,
        "desc": "Sinh ra từ trước khi hỗn độn phân khai (Bàn Cổ Phủ, Hỗn Độn Châu, Thái Cực Đồ)."
    },
    {
        "id": 22, "tier": 5, "tier_name": "Hỗn Độn / Hồng Mông", "stage": "Hồng Hoang Đỉnh Cao",
        "name": "Hồng Mông Chí Bảo", "icon": "👑", "color": 0xffd700,
        "atk_mult": 2500.0, "def_mult": 2500.0,
        "desc": "Đứng đầu toàn bộ hệ thống trang bị tu tiên, nắm giữ trật tự tối thượng của vũ trụ!"
    }
]

# Kho tên trang bị theo cấp bậc (Tier 1 -> Tier 5)
EQUIPMENT_NAMES_BY_TIER = {
    1: {  # Phàm Khí / Pháp Khí
        "Vũ Khí": ["Thiết Kiếm", "Thanh Phong Kiếm", "Trảm Mã Đao", "Xích Hỏa Đao", "Thiết Thương", "Huyền Thiết Bổng", "Lạc Nhật Cung", "Phi Kiếm"],
        "Áo":     ["Áo Vải Thô", "Hộ Thân Áo Vải", "Thanh Bố Y", "Linh Tơ Bào", "Bát Quái Đạo Y", "Huyền Thiết Y"],
        "Quần":   ["Quần Vải Thô", "Thô Bố Khố", "Thú Bì Khố", "Linh Tơ Quần", "Huyền Thiết Giáp Khố", "Thanh Vân Quần"],
        "Giày":   ["Giày Rơm", "Hài Vải Thô", "Ủng Da Bò", "Thanh Vân Hài", "Thần Hành Hài", "Ngự Phong Lý"],
        "Nhẫn":   ["Nhẫn Đồng", "Nhẫn Thiết Thô", "Nhẫn Bạc", "Tụ Khí Nhẫn", "Uẩn Linh Nhẫn", "Thanh Tâm Nhẫn"],
        "Giáp":   ["Áo Vải Thô", "Hộ Thân Áo Vải", "Thanh Bố Y", "Linh Tơ Bào", "Bát Quái Đạo Y", "Huyền Thiết Y"]
    },
    2: {  # Linh Bảo
        "Vũ Khí": ["Trảm Long Kiếm", "Phá Thiên Đao", "Băng Phách Thần Thương", "Cửu Tiêu Lôi Trượng", "Bách Phách Kiếm", "Vô Ảnh Thần Đao"],
        "Áo":     ["Thiên Tàm Bảo Y", "Ngũ Hành Hộ Thân Bào", "Thất Tinh Đạo Bào", "Huyền Lân Chiến Y", "Kim Ty Khải Bào"],
        "Quần":   ["Thiên Tàm Khố", "Ngũ Hành Hộ Thân Quần", "Huyền Lân Giáp Khố", "Kim Ty Tiên Khố", "Bát Hoang Chiến Quần"],
        "Giày":   ["Đạp Lôi Hài", "Bát Hoang Du Hài", "Xích Lôi Lý", "Vân Tiêu Hài", "Phi Vân Bộ Giày"],
        "Nhẫn":   ["Hư Không Nhẫn", "Linh Hồn Giới", "Tu Di Bảo Giới", "Càn Khôn Linh Nhẫn", "Băng Tâm Nhẫn"],
        "Giáp":   ["Thiên Tàm Bảo Y", "Ngũ Hành Hộ Thân Bào", "Thất Tinh Đạo Bào", "Huyền Lân Chiến Y", "Kim Ty Khải Bào"]
    },
    3: {  # Thông Linh Bảo
        "Vũ Khí": ["Tử Dĩnh Kiếm", "Thanh Tác Kiếm", "Phược Long Tác", "Cửu Long Thần Hỏa Tráo", "Hám Thiên Đao", "Diệt Hồn Thần Thương"],
        "Áo":     ["Thái Ất Thiên Y", "Bất Diệt Linh Bào", "Huyền Quy Bảo Khải", "Chân Linh Hộ Thân Bào", "Vô Cực Tiên Y"],
        "Quần":   ["Thái Ất Linh Khố", "Bất Diệt Chiến Quần", "Huyền Quy Giáp Khố", "Chân Linh Hộ Mệnh Khố", "Vô Cực Thần Quần"],
        "Giày":   ["Lục Hợp Đạp Vân Hài", "Thuấn Di Linh Hài", "Thiên Tinh Hài", "Hư Bộ Hài", "Lôi Đình Phi Hài"],
        "Nhẫn":   ["Tạo Hóa Linh Nhẫn", "Thông Thiên Giới", "Vạn Hóa Thần Nhẫn", "Hóa Thần Linh Giới", "Thái Hư Nhẫn"],
        "Giáp":   ["Thái Ất Thiên Y", "Bất Diệt Linh Bào", "Huyền Quy Bảo Khải", "Chân Linh Hộ Thân Bào", "Vô Cực Tiên Y"]
    },
    4: {  # Tiên Khí
        "Vũ Khí": ["Thần Kiếm Ngự Lôi", "Trảm Tiên Phi Đao", "Hỗn Nguyên Kim Đấu", "Cửu Châu Thần Kiếm", "Bát Hoang Thần Thương", "Đại Diệt Tuyệt Đao"],
        "Áo":     ["Chân Tiên Hộ Mệnh Khải", "Vạn Kiếp Bất Diệt Bào", "Cửu Thiên Huyền Nữ Y", "Tiên Tôn Kim Giáp", "Đại Thừa Tiên Y"],
        "Quần":   ["Chân Tiên Càn Khôn Khố", "Vạn Kiếp Bất Diệt Quần", "Cửu Thiên Huyền Khố", "Tiên Tôn Hộ Thể Khố", "Đại Thừa Tiên Khố"],
        "Giày":   ["Thiên Ngoại Phi Tiên Hài", "Thái Hư Độn Giày", "Phá Hư Lý", "Cửu Tiêu Tiên Hài", "Đạp Hư Thần Giày"],
        "Nhẫn":   ["Chân Tiên Càn Khôn Giới", "Đại La Giới Chỉ", "Niết Bàn Tiên Nhẫn", "Vạn Giới Tiên Nhẫn", "Cực Lạc Giới"],
        "Giáp":   ["Chân Tiên Hộ Mệnh Khải", "Vạn Kiếp Bất Diệt Bào", "Cửu Thiên Huyền Nữ Y", "Tiên Tôn Kim Giáp", "Đại Thừa Tiên Y"]
    },
    5: {  # Hỗn Độn / Hồng Mông
        "Vũ Khí": ["Bàn Cổ Phủ", "Tru Tiên Kiếm", "Thí Thần Thương", "Hỗn Độn Thương", "Hiên Viên Kiếm", "Đông Hoàng Chung", "Khai Thiên Kiếm"],
        "Áo":     ["Thái Cực Đồ", "Huyền Hoàng Linh Lung Tháp", "Chư Thiên Khánh Vân", "Sơn Hà Xã Tắc Đồ", "Hỗn Độn Bất Diệt Khải"],
        "Quần":   ["Thái Cực Bản Nguyên Khố", "Huyền Hoàng Hộ Thể Khố", "Chư Thiên Tạo Hóa Quần", "Hỗn Độn Thần Khố", "Hồng Mông Bất Diệt Khố"],
        "Giày":   ["Hỗn Độn Đạp Hư Hài", "Thái Hư Vân Du Hài", "Cửu U Độn Quang Lý", "Hồng Mông Tiên Bộ Hài"],
        "Nhẫn":   ["Hỗn Độn Châu", "Càn Khôn Giới", "Hồng Mông Tạo Hóa Giới", "Định Hải Thần Châu", "Thái Sơ Chi Giới"],
        "Giáp":   ["Thái Cực Đồ", "Huyền Hoàng Linh Lung Tháp", "Chư Thiên Khánh Vân", "Sơn Hà Xã Tắc Đồ", "Hỗn Độn Bất Diệt Khải"]
    }
}

EQUIPMENT_NAMES = {
    "Vũ Khí": ["Kiếm", "Đao", "Thương", "Xử", "Quyền", "Trượng", "Cung", "Pháp Khí"],
    "Áo":     ["Chiến Bào", "Hộ Thân Y", "Linh Y", "Thiên Bào", "Đạo Y"],
    "Quần":   ["Chiến Khố", "Hộ Thể Quần", "Linh Khố", "Thiên Khố", "Đạo Khố"],
    "Giày":   ["Vân Ly", "Phi Thiên Hài", "Cấp Thủy Giày", "Linh Túc", "Ngự Phong Hài"],
    "Nhẫn":   ["Linh Nhẫn", "Hỏa Nhẫn", "Băng Nhẫn", "Lôi Nhẫn", "Càn Khôn Nhẫn"],
    "Giáp":   ["Chiến Bào", "Hộ Thân Y", "Linh Y", "Thiên Bào", "Đạo Y"]
}

def get_equipment_grade(grade_idx: int):
    if grade_idx is None or grade_idx < 0:
        return EQUIPMENT_GRADES[0]
    if grade_idx >= len(EQUIPMENT_GRADES):
        return EQUIPMENT_GRADES[-1]
    return EQUIPMENT_GRADES[grade_idx]

def get_equipment_tier(tier_idx: int):
    for t in EQUIPMENT_TIERS:
        if t["tier"] == tier_idx:
            return t
    return EQUIPMENT_TIERS[0]

FORGE_COST = 25000

# ================= ĐAN DƯỢC =================
DAN_DUOC = [
    {"name": "Phá Cảnh Đan",  "cost": 200,  "effect": "bonus_rate", "value": 0.15, "max_stack": 0.45, "desc": "+15% tỷ lệ Độ Kiếp", "icon": "💊"},
    {"name": "Tụ Linh Đan",   "cost": 150,  "effect": "exp_boost",  "value": 500,  "max_stack": None, "desc": "+500 Linh Khí ngay lập tức", "icon": "💠"},
    {"name": "Hồi Xuân Đan",  "cost": 100,  "effect": "linh_thach", "value": 150,  "max_stack": None, "desc": "+150 Linh Thạch", "icon": "💎"},
    {"name": "Thăng Tốc Đan", "cost": 350,  "effect": "speed_temp", "value": 0.5,  "max_stack": None, "desc": "+0.5x Tốc Độ tu luyện trong 1 giờ", "icon": "⚡"},
    {"name": "Ngũ Hành Đan",  "cost": 800,  "effect": "bonus_rate", "value": 0.30, "max_stack": 0.75, "desc": "+30% tỷ lệ Độ Kiếp (Cao cấp)", "icon": "🌟"},
    {"name": "Tẩy Tủy Đan",   "cost": 1500, "effect": "upgrade_root", "value": 1,    "max_stack": None, "desc": "Tẩy kinh phạt tủy, thăng 1 bậc Linh Căn kế tiếp (Vĩnh viễn)", "icon": "🧬"},
    {"name": "Bổ Thiên Đan",  "cost": 5000, "effect": "max_root",     "value": 1,    "max_stack": None, "desc": "Nghịch thiên cải mệnh, thăng thẳng lên Hỗn Độn Tiên Thiên (4.0x)", "icon": "🔮"},
]

# ================= NHIỆM VỤ HÀNG NGÀY =================
DAILY_QUESTS = [
    {"id": "q_cultivate", "name": "Bế Quan Tịnh Tâm",  "desc": "Thu hoạch linh khí bằng /thongtin 3 lần", "target": 3, "reward_exp": 500,  "reward_stone": 100, "icon": "🧘"},
    {"id": "q_explore",   "name": "Thám Hiểm Bí Cảnh", "desc": "Thám hiểm bí cảnh 2 lần",                "target": 2, "reward_exp": 800,  "reward_stone": 200, "icon": "🗺️"},
    {"id": "q_fight",     "name": "Lịch Luyện Tỷ Thí", "desc": "Tỷ thí với đạo hữu 1 lần",              "target": 1, "reward_exp": 300,  "reward_stone": 150, "icon": "⚔️"},
    {"id": "q_pills",     "name": "Luyện Đan Khai Lò",  "desc": "Mua/dùng đan dược 1 lần",              "target": 1, "reward_exp": 200,  "reward_stone": 50,  "icon": "🔥"},
]

# ================= BÍ CẢNH MỞ RỘNG =================
EXPLORE_EVENTS = [
    {"desc": "Vào sâu Vạn Yêu Sơn Mạch, chém giết Yêu Thú thu được yêu đan!", "exp_mult": 120, "stone_mult": 40, "weight": 30},
    {"desc": "Phát hiện động phủ bậc tiền bối tọa hóa, lĩnh ngộ tàn quyển công pháp!", "exp_mult": 250, "stone_mult": 20, "weight": 20},
    {"desc": "Hái được cây Thiên Niên Linh Chi bên vách đá dựng đứng!", "exp_mult": 180, "stone_mult": 60, "weight": 25},
    {"desc": "Tìm thấy Linh Mạch ẩn giấu, hút linh khí như điên!", "exp_mult": 200, "stone_mult": 80, "weight": 15},
    {"desc": "Giải cứu tiểu tu sĩ bị yêu thú truy đuổi, được tạ ơn hậu hĩnh!", "exp_mult": 100, "stone_mult": 120, "weight": 20},
    {"desc": "Khai quật di tích thượng cổ dưới đáy vực sâu, hào quang pháp bảo phóng thẳng lên trời!", "exp_mult": 220, "stone_mult": 90, "weight": 20},
    {"desc": "Tình cờ bước vào Thần Binh Các cổ xưa, rút bảo vật khỏi phong ấn ngàn năm!", "exp_mult": 260, "stone_mult": 100, "weight": 20},
    {"desc": "Chạm trán hung thú thượng cổ, phải đốt cháy tinh huyết để độn thổ thoát thân!", "exp_mult": -80, "stone_mult": 0, "weight": 10},
    {"desc": "Rơi vào trận pháp cổ đại, phải tiêu hao linh khí để phá trận!", "exp_mult": -50, "stone_mult": -30, "weight": 8},
    {"desc": "Phát hiện Linh Thú con còn sống sót, quyết định mang về nuôi dưỡng!", "exp_mult": 0, "stone_mult": 200, "weight": 12},
]
