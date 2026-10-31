# ⛩️ Bot Discord Game Tu Tiên Cổ Phong (Kiến Trúc Đa Cogs)

Bộ mã nguồn hoàn chỉnh cho Bot Discord Game Tu Tiên Cổ Phong theo kiến trúc module hóa (**Cogs**), tích hợp cấu hình bảo mật qua file `.env`, giao diện nút bấm tương tác (Discord UI Buttons, Select Menus) và cơ sở dữ liệu `SQLite3`.

---

## 📁 Cấu trúc Thư mục Dự án

```text
tutien_discord_bot/
├── .env                  # File chứa cấu hình bí mật (Token bot, DB name)
├── .env.example          # File mẫu hướng dẫn điền cấu hình
├── requirements.txt      # Danh sách thư viện Python cần thiết
├── run.bat               # File chạy nhanh Bot trên Windows (Chỉ cần double-click)
├── run.ps1               # File chạy Bot qua PowerShell
├── config.py             # Cấu hình cân bằng game: Cảnh giới, Linh căn, Công pháp, Đan dược...
├── database.py           # Quản lý cơ sở dữ liệu SQLite và hàm xử lý tu vi, nhiệm vụ
├── main.py               # File khởi chạy Bot chính, tự động nạp tất cả Cogs
└── cogs/                 # Phân hệ Cogs hoàn chỉnh (24 Cogs)
    # --- PHÂN HỆ: THÔNG TIN ---
    ├── cultivation.py    # Bảng điều khiển /thongtin, Nhập Đạo, Bế Quan, Đột Phá
    ├── dongphu.py        # Động Phủ (Linh Tuyền, Dược Điền, Tụ Linh Trận)
    ├── sect.py           # Tông Môn (Lập môn, gia nhập, quản lý đệ tử)
    ├── help.py           # Hướng Dẫn Cẩm Nang (/help và t help)
    ├── leaderboard.py    # Tiên Bảng (Thiên Đạo Kim Bảng Top 10)
    ├── tiencu.py         # Tiên Cư Phủ Đệ (Gia viên & song tu)
    ├── stats.py          # Hệ Thống Thống Kê hồ sơ cá nhân
    # --- PHÂN HỆ: TU LUYỆN ---
    ├── lichluyen.py      # Lịch Luyện Treo Máy thu hoạch Linh Khí thụ động
    ├── hoatdong.py       # Hoạt Động (Vấn đáp tu tiên, Ma Thú Triều)
    ├── quests.py         # Nhiệm Vụ Hàng Ngày nhận EXP & Linh Thạch
    ├── equipment.py      # Chế Tạo & Lò Luyện Khí (Rèn, đeo/tháo trang bị)
    ├── ngoaivuc.py       # Ngoại Vực Hư Không (Viễn chinh săn Boss Ma Tộc)
    ├── vandinh.py        # Vấn Đỉnh Thiên Tháp (Leo tháp 100 tầng thử thách)
    ├── pvp.py            # Luận Kiếm Đài (Tỷ thí giao tranh đoạt Linh Thạch)
    ├── marriage.py       # Đạo Lữ & Hôn Nhân (Cầu hôn, ly hôn, buff song tu)
    # --- PHÂN HỆ: TÀI SẢN ---
    ├── vanbaolau.py      # Vạn Bảo Lâu (Chợ đấu giá, mua bán giữa người chơi)
    ├── phucloi.py        # Phúc Lợi (Điểm danh hàng ngày & Quà tân thủ)
    ├── pills.py          # Cửa Hàng Đan Dược (Thiên Phong Dược Điếm)
    ├── tambao.py         # Vòng Quay Tầm Bảo đoạt Cổ Bảo thượng phẩm
    ├── dophuong.py       # Đổ Phường (Lắc xúc xắc Tài Xỉu cược Linh Thạch)
    ├── vanthu.py         # Vạn Thú Các (Ấp trứng, nuôi dưỡng Linh Thú hộ mệnh)
    ├── nokhu.py          # Nô Khu (Khai thác mỏ khoáng Linh Thạch tự động)
    ├── congphap.py       # Công Pháp Tu Luyện (Lĩnh ngộ công pháp)
    └── admin.py          # Quyền Hạn Thiên Đạo (Dành riêng cho Owner Bot)
```

---

## 🚀 Hướng Dẫn Cài Đặt & Vận Hành

### 1. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Bot Token trong `.env`
Mở file `.env` và thay thế giá trị cấu hình tương ứng:
```env
DISCORD_TOKEN=your_actual_bot_token_here
DB_NAME=tutien_chinh_thong.db
COMMAND_PREFIX=t
OWNER_ID=your_discord_user_id
```
> **Cách lấy Discord User ID:** Bật *Chế độ nhà phát triển (Developer Mode)* trong Cài đặt Discord -> Chuột phải vào Avatar/Tên tài khoản của bạn -> Chọn **Sao chép ID người dùng (Copy User ID)**. Có thể điền nhiều ID phân tách bằng dấu phẩy.


### 3. Khởi chạy & Quản lý Bot

- **Cách 1: Mở Bảng Điều Khiển `run.bat` (Khuyên dùng):**
  Nhấp đúp vào `run.bat` để mở Menu trực quan:
  - `[1]` Chạy trực tiếp (Hiện cửa sổ xem log)
  - `[2]` Khởi động chạy ngầm (Ẩn cửa sổ)
  - `[3]` Dừng bot đang chạy ngầm
  - `[4]` Kiểm tra trạng thái chi tiết & Xem Log
  - `[5]` BẬT tự động Mở/Tắt theo máy tính (Auto-Start PC)
  - `[6]` TẮT tự động Mở/Tắt theo máy tính

- **Cách 2: Chạy ngầm & Mở tắt theo máy tính (PC):**
  - **`cai_dat_khoi_dong_cung_windows.bat`**: Bật tự động khởi động cùng PC. Mỗi khi bật máy tính, bot sẽ tự động chạy ngầm; khi tắt máy tính, bot sẽ tự động tắt theo máy.
  - **`start_chay_ngam.bat`**: Khởi chạy bot ngầm ngay lập tức (không hiện cửa sổ console).
  - **`stop_chay_ngam.bat`**: Tắt bot đang chạy ngầm an toàn.
  - **`check_trang_thai.bat`**: Kiểm tra bot đang Online hay Offline, xem RAM, PID và 15 dòng log mới nhất.
  - **`go_khoi_dong_cung_windows.bat`**: Gỡ bỏ tự khởi động cùng máy tính.

- **Cách 3: Chạy bằng dòng lệnh PowerShell:**
  ```powershell
  .\run.ps1
  ```

- **Cách 4: Chạy trực tiếp qua Python:**
  ```bash
  python main.py
  ```
> Khi bot khởi động thành công, toàn bộ Slash Commands sẽ tự động được đồng bộ với Discord.
> Lệnh quản trị trên Discord: `/botstatus` (kiểm tra trạng thái) và `/shutdown` (tắt bot từ xa).

---

## 🎮 Danh Sách Tính Năng & Lệnh (Slash Commands & Prefix `t`)

### 📜 0. Cẩm Nang Hướng Dẫn (`cogs/help.py`)
- `/help` hoặc `t help` (hoặc `thelp`, `t lenh`): Xem toàn bộ danh sách lệnh kèm giao diện menu dropdown chọn từng phân hệ.

### 🧘 1. Tu Luyện & Cảnh Giới (`cogs/cultivation.py`)
- `/nhapdao`: Cảm ứng thiên địa, trắc nghiệm Linh Căn (Ngụy, Chân, Dị, Thiên, Hỗn Độn) và bước vào con đường tu tiên.
- `/thongtin`: Xem Ngọc Giản Mệnh Cách, tự động thu hoạch Linh Khí bế quan theo thời gian thực kèm 4 nút bấm tương tác:
  - ⚡ **Xung Quan Độ Kiếp**
  - 🗺️ **Thám Hiểm Bí Cảnh**
  - 🏪 **Tiệm Đan Dược**
  - ⚒️ **Rèn Trang Bị**
- `/dotpha`: Thực hiện Xung Quan Độ Kiếp trực tiếp.
- `/thamhiem`: Đi thám hiểm bí cảnh tìm kiếm cơ duyên (thời gian hồi: 5 phút/lần).

### 📖 2. Công Pháp (`cogs/congphap.py`)
- `/congphap`: Xem danh sách công pháp từ sơ cấp đến thần cấp, chọn mua và lĩnh ngộ để gia tăng ATK, DEF và EXP tu luyện.

### ⚔️ 3. Trang Bị & Luyện Khí (`cogs/equipment.py`)
- `/trangbi`: Mở kho trang bị (Vũ Khí, Giáp, Giày, Nhẫn), chọn trang bị hoặc tháo bỏ qua menu chọn tương tác.
- `/ren`: Lò Luyện Khí — tiêu hao 25,000 Linh Thạch để rèn trang bị mới với phẩm cấp ngẫu nhiên (Phàm, Linh, Địa, Thiên, Thánh, Tiên).

### 💊 4. Đan Dược (`cogs/pills.py`)
- `/danduoc`: Mở Thiên Phong Dược Điếm để mua đan dược: Phá Cảnh Đan (+15% tỷ lệ độ kiếp), Tụ Linh Đan, Hồi Xuân Đan, Thăng Tốc Đan...

### 🏯 5. Tông Môn (`cogs/sect.py`)
- `/lapmon [ten_mon]`: Khai môn lập phái (yêu cầu Trúc Cơ Sơ Kỳ và 2,000 Linh Thạch).
- `/giamon [ten_mon]`: Gia nhập một Tông Môn.
- `/tongmon`: Xem thông tin môn phái, Chưởng Môn và danh sách đệ tử.
- `/roimon`: Rời tông môn hoặc giải tán tông môn (nếu là Chưởng Môn).

### ⚔️ 6. Luận Kiếm Đài & PvP (`cogs/pvp.py`)
- `/tythi [doi_thu]`: Gửi chiến thư khiêu chiến đạo hữu trong server. Trận đấu diễn ra tối đa 10 hiệp dựa trên chỉ số thực tế, người thắng đoạt Linh Thạch của đối phương.

### 💍 7. Đạo Lữ & Hôn Nhân (`cogs/marriage.py`)
- `/cauhon [doi_tuong]`: Cầu hôn đạo hữu kết bái thành Đạo Lữ (nhận buff vĩnh viễn +5% Linh Khí mỗi lần bế quan).
- `/lyhon`: Hủy bỏ mối quan hệ Đạo Lữ.

### 📋 8. Nhiệm Vụ Hàng Ngày (`cogs/quests.py`)
- `/nhiemvu`: Kiểm tra tiến độ 4 nhiệm vụ tu hành mỗi ngày (Bế quan, Thám hiểm, Tỷ thí, Dùng đan) để nhận thưởng Linh Khí và Linh Thạch. Tự động làm mới lúc 00:00 (GMT+7).

### 🏆 9. Bảng Xếp Hạng (`cogs/leaderboard.py`)
- `/thienbang`: Xem Thiên Đạo Kim Bảng vinh danh Top 10 Cường Giả có cảnh giới và tu vi cao nhất.

### 📊 10. Thống Kê Cá Nhân (`cogs/stats.py`)
- `/thongke`: Xem toàn bộ hồ sơ tu tiên: Cảnh giới, Linh căn, Công pháp, Tỷ lệ thắng PvP, Tài sản, Trang bị, Đạo Lữ, Tông Môn...

### ⚡ 11. Quyền Hạn Thiên Đạo — Dành Riêng Cho Owner Bot (`cogs/admin.py`)
- `/addlinhthach [dao_huu] [so_luong]`: Ban thưởng hoặc thu hồi Linh Thạch của bất kỳ người chơi nào (nhập số dương để cộng, số âm để trừ).
- `/setlinhthach [dao_huu] [so_luong]`: Đặt trực tiếp số lượng Linh Thạch trong túi trữ vật của một người chơi.
- `/addtuvi [dao_huu] [so_luong]`: Quán đỉnh truyền thụ tu vi (Linh Khí) trực tiếp cho người chơi.
