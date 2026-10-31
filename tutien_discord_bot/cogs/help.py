import os
import discord
from discord import app_commands
from discord.ext import commands

HELP_CATEGORIES = {
    "cultivation": {
        "label": "Tu Luyện & Cảnh Giới",
        "emoji": "🧘",
        "description": "Nhập đạo, bế quan, độ kiếp & thám hiểm",
        "commands": [
            ("`/nhapdao` | `t nhapdao`", "Cảm ứng thiên địa, kiểm tra Linh Căn và bắt đầu tu tiên."),
            ("`/thongtin` | `t thongtin`", "Xem Ngọc Giản Mệnh Cách, thu hoạch Linh Khí bế quan (kèm 4 nút bấm tương tác)."),
            ("`/dotpha` | `t dotpha`", "⚡ Xung quan độ kiếp vượt cảnh giới (yêu cầu viên mãn Linh Khí)."),
            ("`/thamhiem` | `t thamhiem`", "🗺️ Lịch luyện bí cảnh săn tìm linh dược, yêu đan (hồi chiêu 5 phút)."),
            ("`/canhgioi` | `t canhgioi`", "🌌 Xem chi tiết toàn bộ các cấp bậc cảnh giới tu tiên, chỉ số cơ bản và tỷ lệ độ kiếp.")
        ]
    },
    "technique": {
        "label": "Công Pháp Tu Luyện",
        "emoji": "📖",
        "description": "Lĩnh ngộ công pháp gia tăng ATK, DEF, EXP",
        "commands": [
            ("`/congphap` | `t congphap`", "Xem danh sách công pháp, mua & lĩnh ngộ công pháp mạnh hơn.")
        ]
    },
    "equipment": {
        "label": "Trang Bị & Luyện Khí",
        "emoji": "⚒️",
        "description": "Rèn đúc pháp bảo và quản lý kho trang bị",
        "commands": [
            ("`/trangbi` | `t trangbi`", "Xem các pháp bảo đang đeo trên người (Vũ Khí, Giáp, Giày, Nhẫn), chọn đeo / tháo."),
            ("`/trangbinhanh` | `t tbnhanh`", "⚡ Tự động tìm và mặc bộ pháp bảo tối ưu nhất cho từng vị trí."),
            ("`/ren` | `t ren`", "Lò Luyện Khí — Tiêu hao 25,000 Linh Thạch để rèn trang bị mới phẩm cấp ngẫu nhiên."),
            ("`/capbactrangbi` | `t capbac`", "📜 Xem chi tiết 5 Đại Cấp Bậc pháp bảo, 23 phẩm cấp và tỷ lệ xuất hiện (Phàm Khí 70%).")
        ]
    },
    "pills": {
        "label": "Đan Dược & Tiệm Thuốc",
        "emoji": "💊",
        "description": "Thiên Phong Dược Điếm bán đan dược tu hành",
        "commands": [
            ("`/danduoc` | `t danduoc`", "Mở Thiên Phong Dược Điếm — mua Tẩy Tủy Đan (tăng cấp linh căn), Phá Cảnh Đan, Bổ Thiên Đan, v.v.")
        ]
    },
    "sect": {
        "label": "Tông Môn Bang Phái",
        "emoji": "🏯",
        "description": "Khai môn lập phái, chiêu mộ đệ tử",
        "commands": [
            ("`/lapmon [tên]`", "Khai môn lập phái (Yêu cầu: Trúc Cơ Sơ Kỳ + 2,000 Linh Thạch)."),
            ("`/giamon [tên]`", "Gia nhập một Tông Môn đã thành lập."),
            ("`/tongmon`", "Xem thông tin Tông Môn, Chưởng Môn và danh sách đệ tử."),
            ("`/roimon`", "Rời khỏi tông môn hiện tại (hoặc giải tán nếu là Chưởng Môn).")
        ]
    },
    "pvp": {
        "label": "Luận Kiếm Đài (PvP)",
        "emoji": "⚔️",
        "description": "Tỷ thí võ công đoạt Linh Thạch",
        "commands": [
            ("`/tythi [@đạo_hữu]`", "Gửi chiến thư khiêu chiến đạo hữu trong server (giao tranh 10 hiệp dựa trên chỉ số).")
        ]
    },
    "dongphu": {
        "label": "Động Phủ Tiên Gia",
        "emoji": "🌌",
        "description": "Tụ Linh Trận, Dược Điền, Cổ Linh Tuyền",
        "commands": [
            ("`/dongphu`", "Mở Động Phủ — Thu hoạch Cổ Linh Tuyền, Dược Điền và nâng cấp Tụ Linh Trận.")
        ]
    },
    "tiencu": {
        "label": "Tiên Cư Phủ Đệ",
        "emoji": "✨",
        "description": "Biệt viện tiên phủ cư ngụ và song tu",
        "commands": [
            ("`/tiencu`", "Xem Tiên Cư — Nâng cấp gia viên tăng độ tiện nghi và buff song tu.")
        ]
    },
    "lichluyen": {
        "label": "Lịch Luyện Treo Máy",
        "emoji": "🧭",
        "description": "Treo máy thế giới tu chân thu hoạch Linh Khí",
        "commands": [
            ("`/lichluyen`", "Xem tiến trình lịch luyện, thu hoạch Linh Khí và Linh Thạch thụ động.")
        ]
    },
    "hoatdong": {
        "label": "Hoạt Động Sự Kiện",
        "emoji": "🥥",
        "description": "Tham gia sự kiện tiên giới, vấn đáp tu chân",
        "commands": [
            ("`/hoatdong` | `t hd`", "Xem các sự kiện tiên giới, Ma Thú triều và nhận thưởng."),
            ("`/vandap` | `t vandap`", "Tham gia Vấn Đáp Tiên Cơ liên tục với hàng chục câu hỏi tu chân nhận Linh Thạch & Linh Khí.")
        ]
    },
    "ngoaivuc": {
        "label": "Ngoại Vực Hư Không",
        "emoji": "🌌",
        "description": "Viễn chinh Hư Không Ma Tộc săn Boss",
        "commands": [
            ("`/ngoaivuc`", "Khiêu chiến Boss Hư Không U Hồn, Cửu U Ma Xà, Thôn Thiên Ma Tôn.")
        ]
    },
    "vandinh": {
        "label": "Vấn Đỉnh Thiên Tháp",
        "emoji": "⚔️",
        "description": "Leo tháp 100 tầng thử thách chiến lực",
        "commands": [
            ("`/vandinh`", "Thử thách tháp Vấn Đỉnh Phong, chém thủ hộ giả đoạt kho báu.")
        ]
    },
    "vanbaolau": {
        "label": "Vạn Bảo Lâu Chợ Đấu Giá",
        "emoji": "🏛️",
        "description": "Chợ giao dịch pháp bảo giữa các tu sĩ",
        "commands": [
            ("`/vanbaolau`", "Xem chợ đấu giá Vạn Bảo Lâu, mua pháp bảo từ người chơi khác."),
            ("`/banphapbao [id] [giá]` | `t ban [tên]`", "Chọn bán hoặc treo trang bị lên chợ Vạn Bảo Lâu (Phí 10%)."),
            ("`/sellall` | `t sellall` | `t sell all`", "💰 Bán toàn bộ trang bị chưa đeo trên người lấy Linh Thạch ngay lập tức.")
        ]
    },
    "phucloi": {
        "label": "Phúc Lợi Thiên Đạo",
        "emoji": "🎁",
        "description": "Điểm danh hàng ngày & Quà tân thủ",
        "commands": [
            ("`/phucloi` | `t diemdanh`", "Điểm danh hàng ngày nhận Linh Thạch & Quà tân thủ.")
        ]
    },
    "tambao": {
        "label": "Vòng Quay Tầm Bảo",
        "emoji": "🌀",
        "description": "Săn tìm bảo vật cổ đại và tiên tủy",
        "commands": [
            ("`/tambao` | `t tambao`", "Quay tầm bảo 1 lần (10,000 LT) hoặc 10 lần (90,000 LT) săn tìm Tiên Khí và cổ bảo cực phẩm.")
        ]
    },
    "dophuong": {
        "label": "Đổ Phường Tài Xỉu",
        "emoji": "🎲",
        "description": "Lắc xúc xắc cá cược Linh Thạch",
        "commands": [
            ("`/dophuong`", "Mở sòng bạc Đổ Phường, chọn cược Tài hoặc Xỉu tỷ lệ 1:2.")
        ]
    },
    "vanthu": {
        "label": "Vạn Thú Các Linh Thú",
        "emoji": "🦊",
        "description": "Ấp trứng, nuôi dưỡng Linh Thú hộ thể",
        "commands": [
            ("`/vanthu`", "Ấp trứng thú, cho ăn bồi bổ tăng cấp, xuất chiến trợ trận.")
        ]
    },
    "nokhu": {
        "label": "Nô Khu Khai Thác Mỏ",
        "emoji": "⛓️",
        "description": "Quản thúc nô bộc đào mỏ Linh Thạch",
        "commands": [
            ("`/nokhu`", "Mua nô bộc, khai thác mỏ quặng linh thạch tích lũy tự động.")
        ]
    },
    "marriage": {
        "label": "Đạo Lữ & Hôn Nhân",
        "emoji": "💍",
        "description": "Kết bái đạo lữ cùng song tu",
        "commands": [
            ("`/cauhon [@đạo_hữu]`", "Cầu hôn một đạo hữu kết bái Đạo Lữ (nhận vĩnh viễn +5% Linh Khí bế quan)."),
            ("`/lyhon`", "Cắt đứt duyên phận, ly hôn với Đạo Lữ hiện tại.")
        ]
    },
    "quests": {
        "label": "Nhiệm Vụ Hàng Ngày",
        "emoji": "📋",
        "description": "Nhiệm vụ tu hành nhận thưởng EXP & Linh Thạch",
        "commands": [
            ("`/nhiemvu` | `t nhiemvu`", "Xem tiến độ 4 nhiệm vụ hàng ngày (tự động làm mới lúc 00:00 GMT+7).")
        ]
    },
    "ranking": {
        "label": "Kim Bảng & Thống Kê",
        "emoji": "🏆",
        "description": "Bảng xếp hạng cường giả và hồ sơ tu tiên",
        "commands": [
            ("`/thienbang` | `t thienbang`", "Xem Thiên Đạo Kim Bảng — Top 10 Cường Giả Tu Tiên Giới."),
            ("`/thongke` | `t thongke`", "Xem chi tiết toàn bộ hồ sơ tu vi, chiến tích PvP, tài sản cá nhân.")
        ]
    },
    "admin": {
        "label": "Quyền Hạn Thiên Đạo (Owner)",
        "emoji": "⚡",
        "description": "Lệnh quản trị chỉ dành cho Owner Bot",
        "commands": [
            ("`/addlinhthach [@đạo_hữu] [số_lượng]`", "Ban thưởng hoặc khấu trừ Linh Thạch của người chơi."),
            ("`/setlinhthach [@đạo_hữu] [số_lượng]`", "Đặt số dư Linh Thạch cố định cho người chơi."),
            ("`/addtuvi [@đạo_hữu] [số_lượng]`", "Quán đỉnh truyền thụ tu vi (Linh Khí) trực tiếp."),
            ("`/resetplayer [@đạo_hữu]` | `t resetplayer`", "Reset toàn bộ dữ liệu 1 người chơi về Phàm Nhân ban đầu (kèm xác nhận an toàn)."),
            ("`/resetall` | `t resetall`", "Wipe / Reset toàn bộ cơ sở dữ liệu người chơi về ban đầu (chỉ Owner, kèm xác nhận).")
        ]
    }
}

def create_overview_embed(prefix: str):
    embed = discord.Embed(
        title="⛩️ CẨM NANG TU TIÊN — TOÀN BỘ LỆNH BOT",
        description=(
            "Chào mừng đạo hữu bước chân vào **Thế Giới Tu Tiên Cổ Phong**!\n\n"
            f"🔹 **Prefix lệnh:** `{prefix}` *(Ví dụ: `{prefix} help`, `{prefix}help`, `{prefix} thongtin`)*\n"
            "🔹 **Slash Command:** Gõ dấu `/` để dùng các lệnh tương tác nhanh.\n\n"
            "📜 **Danh sách các phân hệ tu tiên bên dưới:**"
        ),
        color=0xf39c12
    )

    for cat_key, cat_data in HELP_CATEGORIES.items():
        cmd_names = [c[0].split()[0] for c in cat_data["commands"]]
        cmd_preview = " • ".join(cmd_names)
        embed.add_field(
            name=f"{cat_data['emoji']} {cat_data['label']}",
            value=f"*{cat_data['description']}*\n╰┈➤ {cmd_preview}",
            inline=False
        )

    embed.set_footer(text="💡 Chọn danh mục bên dưới menu để xem hướng dẫn chi tiết từng lệnh!")
    return embed

def create_category_embed(cat_key: str, prefix: str):
    cat_data = HELP_CATEGORIES.get(cat_key)
    if not cat_data:
        return create_overview_embed(prefix)

    embed = discord.Embed(
        title=f"{cat_data['emoji']} PHÂN HỆ: {cat_data['label'].upper()}",
        description=f"*{cat_data['description']}*\n\nCác lệnh trong phân hệ này:",
        color=0x3498db
    )

    for cmd_syntax, cmd_desc in cat_data["commands"]:
        embed.add_field(
            name=f"📌 {cmd_syntax}",
            value=f"╰┈➤ {cmd_desc}",
            inline=False
        )

    embed.set_footer(text=f"Prefix hiện tại: {prefix} • Dùng menu bên dưới để chuyển danh mục khác")
    return embed

class HelpSelect(discord.ui.Select):
    def __init__(self, prefix: str):
        self.prefix = prefix
        options = [
            discord.SelectOption(
                label="📜 Tất Cả Phân Hệ (Tổng quan)",
                value="all",
                description="Xem trang chủ danh sách tất cả các lệnh"
            )
        ]
        for key, data in HELP_CATEGORIES.items():
            options.append(
                discord.SelectOption(
                    label=data["label"],
                    value=key,
                    description=data["description"][:100],
                    emoji=data["emoji"]
                )
            )
        super().__init__(placeholder="Chọn phân hệ lệnh muốn xem chi tiết...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if selected == "all":
            embed = create_overview_embed(self.prefix)
        else:
            embed = create_category_embed(selected, self.prefix)
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, prefix: str):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(prefix))

class HelpCog(commands.Cog, name="Hướng Dẫn"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_prefix(self) -> str:
        return os.getenv("COMMAND_PREFIX", "t").strip()

    @app_commands.command(name="help", description="Xem toàn bộ danh sách lệnh và cẩm nang tu tiên")
    async def slash_help(self, interaction: discord.Interaction):
        prefix = self.get_prefix()
        embed = create_overview_embed(prefix)
        view = HelpView(prefix)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="help", aliases=["lenh", "trogiup", "commands"])
    async def prefix_help(self, ctx: commands.Context):
        prefix = self.get_prefix()
        embed = create_overview_embed(prefix)
        view = HelpView(prefix)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
