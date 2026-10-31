import random
import discord
from discord import app_commands
from discord.ext import commands
from database import get_player, get_connection

# ================= KHO CÂU HỎI VẤN ĐÁP TIÊN CƠ =================
QUIZ_QUESTIONS = [
    {
        "q": "Cảnh giới đầu tiên của người phàm sau khi trắc nghiệm linh căn là gì?",
        "options": ["Luyện Khí", "Trúc Cơ", "Kết Đan", "Nguyên Anh"],
        "ans": 0,
        "explain": "Luyện Khí là bước khởi đầu dẫn khí nhập thể, gột rửa phàm thai của tu sĩ."
    },
    {
        "q": "Linh căn nào được tôn vinh là vạn năm có một, tốc độ tu luyện cực hạn (4.0x)?",
        "options": ["Hỗn Độn Tiên Thiên Linh Căn", "Thiên Linh Căn", "Dị Linh Căn", "Ngụy Linh Căn"],
        "ans": 0,
        "explain": "Hỗn Độn Tiên Thiên Linh Căn dung nạp hồng mông tử khí, đứng đầu vạn linh căn."
    },
    {
        "q": "Đan dược nào dùng để gia tăng tỷ lệ Độ Kiếp xung quan thành công?",
        "options": ["Phá Cảnh Đan", "Hồi Xuân Đan", "Tụ Linh Đan", "Tẩy Tủy Đan"],
        "ans": 0,
        "explain": "Phá Cảnh Đan giúp ổn định đan điền, gia tăng xác suất phá vỡ bình cảnh."
    },
    {
        "q": "Cảnh giới nào nằm ngay trước Nguyên Anh Kỳ?",
        "options": ["Kết Đan", "Trúc Cơ", "Hóa Thần", "Luyện Hư"],
        "ans": 0,
        "explain": "Tu sĩ ngưng tụ Kim Đan viên mãn ở Kết Đan kỳ rồi mới toái đan thành anh."
    },
    {
        "q": "Sau khi Nguyên Anh đại thành, tu sĩ sẽ đột phá lên cảnh giới nào?",
        "options": ["Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa"],
        "ans": 0,
        "explain": "Hóa Thần kỳ là khi Nguyên Anh hóa thần, câu thông thiên địa nguyên lực."
    },
    {
        "q": "Đan dược nào dùng để tẩy kinh phạt tủy, nâng 1 bậc Linh Căn vĩnh viễn?",
        "options": ["Tẩy Tủy Đan", "Bổ Thiên Đan", "Thăng Tốc Đan", "Hồi Xuân Đan"],
        "ans": 0,
        "explain": "Tẩy Tủy Đan thanh lọc tạp chất kinh mạch, nâng phẩm cấp linh căn vĩnh viễn."
    },
    {
        "q": "Đan dược quý giá nhất có thể thăng thẳng lên Hỗn Độn Tiên Thiên Linh Căn là gì?",
        "options": ["Bổ Thiên Đan", "Tẩy Tủy Đan", "Ngũ Hành Đan", "Phá Cảnh Đan"],
        "ans": 0,
        "explain": "Bổ Thiên Đan có thể nghịch thiên cải mệnh, tái tạo tiên thiên bản nguyên."
    },
    {
        "q": "Cấp bậc pháp bảo nào đã sinh ra Khí Linh, tự động nhận chủ và hộ vệ?",
        "options": ["Thông Linh Bảo", "Linh Bảo", "Pháp Khí", "Phàm Khí"],
        "ans": 0,
        "explain": "Thông Linh Bảo đã ngưng tụ khí linh có ý thức độc lập, biến hóa tùy tâm."
    },
    {
        "q": "Lò Luyện Khí cần tiêu hao bao nhiêu Linh Thạch cho một lần rèn trang bị mới?",
        "options": ["25,000 Linh Thạch", "300 Linh Thạch", "5,000 Linh Thạch", "50,000 Linh Thạch"],
        "ans": 0,
        "explain": "Chi phí lò rèn thần binh tiêu hao đúng 25,000 Linh Thạch mỗi lần rèn."
    },
    {
        "q": "Trên thân thể tu sĩ có thể trang bị tối đa bao nhiêu món pháp bảo cùng lúc?",
        "options": ["5 món (Vũ Khí, Áo, Quần, Giày, Nhẫn)", "3 món", "4 món", "6 món"],
        "ans": 0,
        "explain": "Bộ trang bị hoàn chỉnh gồm 5 vị trí: Vũ Khí, Áo, Quần, Giày và Nhẫn."
    },
    {
        "q": "Cảnh giới tối thiểu để đạo hữu có thể Khai Môn Lập Phái (tạo Tông Môn) là gì?",
        "options": ["Trúc Cơ - Sơ Kỳ", "Luyện Khí - Đỉnh Phong", "Kết Đan - Sơ Kỳ", "Nguyên Anh - Sơ Kỳ"],
        "ans": 0,
        "explain": "Tu sĩ cần đạt tối thiểu Trúc Cơ - Sơ Kỳ và 2,000 Linh Thạch để lập Tông Môn."
    },
    {
        "q": "Khi hai đạo hữu kết bái Đạo Lữ với nhau, cả hai sẽ nhận được bổng lộc gì?",
        "options": ["Gia tăng +5% tốc độ tu luyện", "Gia tăng +20% công kích", "Nhận 1,000 LT mỗi ngày", "Tăng 10% tỉ lệ độ kiếp"],
        "ans": 0,
        "explain": "Đạo Lữ song tu đồng tâm hiệp lực, cùng nhau bế quan tăng 5% tốc độ tích lũy tu vi."
    },
    {
        "q": "Tháp thí luyện leo tầng ma luyện ý chí trong game có tên là gì?",
        "options": ["Tháp Vấn Đỉnh", "Tháp Thông Thiên", "Cửu Trọng Tháp", "Vạn Yêu Tháp"],
        "ans": 0,
        "explain": "Tháp Vấn Đỉnh là nơi khảo nghiệm chiến lực và cảnh giới của các tu sĩ."
    },
    {
        "q": "Nơi tu sĩ bước qua khe nứt hư không để săn lùng Ma Tôn dị tộc gọi là gì?",
        "options": ["Ngoại Vực", "Bí Cảnh", "Động Phủ", "Nô Khu"],
        "ans": 0,
        "explain": "Ngoại Vực là chiến trường ranh giới chống lại ma thú và ma vương hư không."
    },
    {
        "q": "Khi xung quan độ kiếp thất bại, tu sĩ sẽ chịu tổn thất tu vi như thế nào?",
        "options": ["Mất 25% Linh Khí của cảnh giới hiện tại", "Mất toàn bộ tu vi về 0", "Rớt 1 cấp cảnh giới", "Mất toàn bộ Linh Thạch"],
        "ans": 0,
        "explain": "Tâm ma quấy nhiễu khi xung quan thất bại làm tổn hao 25% tiến độ linh khí."
    },
    {
        "q": "Trong tiểu thuyết 'Phàm Nhân Tu Tiên', bảo vật nghịch thiên của Hàn Lập tên là gì?",
        "options": ["Chưởng Thiên Bình", "Cửu Châu Đỉnh", "Hỗn Độn Chung", "Thái Hư Kính"],
        "ans": 0,
        "explain": "Chưởng Thiên Bình hấp thu ánh trăng ngưng tụ lục dịch giúp linh dược tăng trưởng vạn năm."
    },
    {
        "q": "Hàn Lập trong 'Phàm Nhân Tu Tiên' thường được đạo hữu gọi bằng biệt danh hài hước nào?",
        "options": ["Hàn Chạy Nhanh", "Hàn Liều Mạng", "Hàn Vô Địch", "Hàn Hảo Hán"],
        "ans": 0,
        "explain": "Hàn Lập hành sự cẩn trọng, thấy nguy hiểm là thi triển thần pháp tẩu thoát vi thượng."
    },
    {
        "q": "Trong tác phẩm 'Tiên Nghịch', nhân vật chính Vương Lâm lĩnh ngộ ý cảnh nào chấn động giới tu chân?",
        "options": ["Sinh Tử Ý Cảnh", "Ngũ Hành Ý Cảnh", "Thời Gian Ý Cảnh", "Hư Vô Ý Cảnh"],
        "ans": 0,
        "explain": "Vương Lâm trải qua hồng trần hóa phàm, ngộ ra quy luật Sinh - Tử luân hồi."
    },
    {
        "q": "Nhân vật Tiêu Viêm trong 'Đấu Phá Thương Khung' tu luyện công pháp tiến hóa nhờ điều gì?",
        "options": ["Thôn phệ Dị Hỏa", "Hấp thụ Lôi Kiếp", "Luyện hóa Ma Hạch", "Uống Tiên Tửu"],
        "ans": 0,
        "explain": "Phần Quyết là công pháp kỳ dị có thể tiến hóa khi dung nạp các loại Dị Hỏa thiên địa."
    },
    {
        "q": "Câu nói trứ danh: 'Ta vì Thiên Đế, đương trấn áp hết thảy địch nhân thế gian' là của ai?",
        "options": ["Diệp Phàm (Già Thiên)", "Thạch Hạo", "Bạch Tiểu Thuần", "Lâm Động"],
        "ans": 0,
        "explain": "Diệp Thiên Đế trong Già Thiên quét ngang cấm khu, bình định hắc ám động loạn."
    },
    {
        "q": "Ai là người sáng lập Thiên Đình trong 'Thế Giới Hoàn Mỹ', một mình độc đoán vạn cổ?",
        "options": ["Hoang Thiên Đế (Thạch Hạo)", "Liễu Thần", "Diệp Phàm", "Ngoan Nhân Đại Đế"],
        "ans": 0,
        "explain": "Thạch Hạo xưng Hoang Thiên Đế, một mình ngăn chặn đầu nguồn hắc ám nơi biên giới thượng thương."
    },
    {
        "q": "Trong điển tịch tiên hiệp, Cửu Cửu Thiên Kiếp có tổng cộng bao nhiêu đạo sấm sét giáng xuống?",
        "options": ["81 đạo lôi kiếp", "9 đạo lôi kiếp", "49 đạo lôi kiếp", "99 đạo lôi kiếp"],
        "ans": 0,
        "explain": "Cửu Cửu là 9 x 9 = 81 đạo thiên lôi khảo nghiệm chí tôn độ kiếp phi thăng."
    },
    {
        "q": "Câu thành ngữ tu chân 'Thuận vi phàm, nghịch tắc tiên' mang hàm nghĩa gì?",
        "options": ["Tu tiên là con đường nghịch thiên cải mệnh, đoạt tạo hóa của vũ trụ", "Người phàm sống thuận theo tự nhiên", "Cần phải tuân phục thiên đạo", "Chỉ cần siêng năng ắt thành tiên"],
        "ans": 0,
        "explain": "Người thuận thiên thì sinh lão bệnh tử, tu sĩ muốn trường sinh phải nghịch chuyển thiên mệnh."
    },
    {
        "q": "Dị Linh Căn nổi tiếng với khả năng sát phạt sấm sét khắc chế ma đạo là hệ nào?",
        "options": ["Dị Linh Căn - Lôi Hệ", "Dị Linh Căn - Phong Hệ", "Chân Linh Căn", "Ngụy Linh Căn"],
        "ans": 0,
        "explain": "Lôi hệ mang sức mạnh thiên kiếp chính khí, là khắc tinh số một của ma tu và tà túy."
    },
    {
        "q": "Đan dược nào giúp tăng tốc độ tu luyện thêm +0.5x trong thời hạn 1 giờ?",
        "options": ["Thăng Tốc Đan", "Tụ Linh Đan", "Hồi Xuân Đan", "Phá Cảnh Đan"],
        "ans": 0,
        "explain": "Thăng Tốc Đan kích phát kinh mạch, đẩy nhanh tốc độ hấp thụ linh khí."
    },
    {
        "q": "Kim Đan có phẩm chất cao nhất trong Kết Đan kỳ thường được gọi là gì?",
        "options": ["Cửu Chuyển Kim Đan", "Tam Hoa Đan", "Thiên Huyết Đan", "Nguyên Anh Đan"],
        "ans": 0,
        "explain": "Cửu Chuyển Kim Đan là đỉnh phong ngưng kết, đạo cơ vững như bàn thạch."
    },
    {
        "q": "Khái niệm 'Đoạt Xá' trong giới tu tiên có nghĩa là gì?",
        "options": ["Cướp đoạt nhục thân người khác để tái sinh", "Cướp pháp bảo của tông môn", "Đánh cắp đan dược", "Phá hủy đan điền địch nhân"],
        "ans": 0,
        "explain": "Khi thân xác bị hủy, thần hồn tu sĩ có thể đoạt lấy thể xác kẻ khác để tiếp tục sống."
    },
    {
        "q": "Thần thông 'Súc Địa Thành Thốn' có hiệu quả gì đặc trưng?",
        "options": ["Thu hẹp không gian, bước một bước đi xa vạn dặm", "Phóng to kích thước vũ khí", "Tàng hình tuyệt đối", "Độn thổ ẩn thân"],
        "ans": 0,
        "explain": "Súc Địa Thành Thốn là đại thần thông không gian giúp di chuyển chớp mắt qua ngàn sông núi."
    },
    {
        "q": "Vật phẩm mà các tu sĩ dùng để lưu giữ công pháp, bản đồ và truyền thừa gọi là gì?",
        "options": ["Ngọc Giản", "Chỉ Phù", "Bạch Tranh", "Kim Bài"],
        "ans": 0,
        "explain": "Ngọc Giản được khắc thần thức lên, chỉ cần chạm thần niệm vào là thấu suốt nội dung."
    },
    {
        "q": "Hiện tượng tu sĩ bị thiên đạo hòa tan ý thức và thân xác khi ngộ đạo thất bại gọi là gì?",
        "options": ["Đạo Hóa", "Tẩu Hỏa", "Nhập Ma", "Trọng Sinh"],
        "ans": 0,
        "explain": "Đạo Hóa là cái chết đáng sợ nhất của đại năng, tan biến vào thiên địa không còn luân hồi."
    },
    {
        "q": "Trận pháp bảo vệ bao bọc toàn bộ lãnh địa của một phái tu tiên được gọi là gì?",
        "options": ["Hộ Sơn Trận Pháp", "Tru Tiên Kiếm Trận", "Tụ Linh Trận", "Mê Hồn Trận"],
        "ans": 0,
        "explain": "Hộ Sơn Đại Trận là bình phong bảo vệ môn phái trước xâm lăng của ngoại địch."
    },
    {
        "q": "Loại đá chứa linh khí tinh thuần vừa làm tiền tệ vừa hỗ trợ tu luyện trong giới tu chân là gì?",
        "options": ["Linh Thạch", "Kim Thạch", "Phù Thạch", "Ma Tinh"],
        "ans": 0,
        "explain": "Linh Thạch là huyết mạch kinh tế của tam giới, dùng mua bán và bố trí trận pháp."
    },
    {
        "q": "Cảnh giới nằm giữa Luyện Hư Kỳ và Đại Thừa Kỳ trong bảng cảnh giới là gì?",
        "options": ["Hợp Thể", "Nguyên Anh", "Hóa Thần", "Trúc Cơ"],
        "ans": 0,
        "explain": "Hợp Thể Kỳ là giai đoạn Nguyên Thần và Nhục Thân dung hợp hoàn mỹ thành một thể."
    },
    {
        "q": "Yêu thú tu luyện ngàn năm trải qua lôi kiếp biến thành hình dáng con người gọi là gì?",
        "options": ["Hóa Hình", "Dục Hỏa", "Biến Dị", "Niết Bàn"],
        "ans": 0,
        "explain": "Hóa Hình là bước ngoặt của yêu tộc để có được thể chất đạo thể tu luyện của loài người."
    },
    {
        "q": "Khi tu sĩ khai thác quặng tại Nô Khu, họ sẽ thu về tài nguyên gì?",
        "options": ["Linh Thạch", "Đan Dược", "Linh Thú", "Công Pháp"],
        "ans": 0,
        "explain": "Nô Khu là mỏ khoáng sản linh thạch dồi dào, mỗi ngày đều có thể thu hoạch."
    },
    {
        "q": "Linh thú đứng đầu tứ linh thần thú thượng cổ trấn giữ phương Đông là thần thú nào?",
        "options": ["Thanh Long", "Bạch Hổ", "Chu Tước", "Huyền Vũ"],
        "ans": 0,
        "explain": "Thanh Long chưởng quản phương Đông và mộc khí trong tứ tượng thiên chi linh thú."
    },
    {
        "q": "Thần thú nào trong tứ linh trấn giữ phương Bắc, biểu trưng cho sự trường thọ và thủ ngự?",
        "options": ["Huyền Vũ", "Chu Tước", "Bạch Hổ", "Kỳ Lân"],
        "ans": 0,
        "explain": "Huyền Vũ là linh thú kết hợp giữa rùa đen và rắn, phòng ngự vững như thiên thành."
    },
    {
        "q": "Tu sĩ Trúc Cơ Kỳ thường sử dụng loại vũ khí nào phổ biến và tối ưu nhất?",
        "options": ["Pháp Khí Cực Phẩm", "Tiên Khí", "Thông Linh Bảo", "Hỗn Độn Bảo"],
        "ans": 0,
        "explain": "Tu vi Trúc Cơ thích hợp nhất để ngự khống các Pháp Khí thượng phẩm và cực phẩm."
    },
    {
        "q": "Nguyên Anh của tu sĩ có hình dáng đặc trưng như thế nào?",
        "options": ["Một tiểu hài tử thu nhỏ tỏa hào quang trong đan điền", "Một viên ngọc tròn", "Một đám sương mù", "Một ngọn lửa"],
        "ans": 0,
        "explain": "Nguyên Anh là bản thể linh hồn hóa thành hình hài hài nhi ngũ quan đầy đủ."
    },
    {
        "q": "Để tăng cấp Linh Thú tại Vạn Thú Các, chủ nhân cần cho linh thú ăn gì?",
        "options": ["Thú Đan bồi bổ (300 LT)", "Linh Thảo ngàn năm", "Tiên Đan", "Nước Ôn Tuyền"],
        "ans": 0,
        "explain": "Thú Đan chứa tinh hoa yêu thú giúp linh thú thăng cấp và tăng chỉ số chiến đấu."
    },
    {
        "q": "Khu vườn thảo dược tại Động Phủ của tu sĩ dùng để làm gì?",
        "options": ["Trồng và thu hoạch Linh Thảo", "Khai mỏ quặng", "Luyện chế Tiên Khí", "Bắt yêu thú"],
        "ans": 0,
        "explain": "Linh Dược Viên tại động phủ giúp tu sĩ bồi dục các loại linh thảo quý báu."
    },
    {
        "q": "Khái niệm 'Bình Cảnh' trong tu tiên chỉ điều gì?",
        "options": ["Ngưỡng cửa tu vi bị kẹt lại không thể tăng thêm nếu chưa ngộ đạo hoặc độ kiếp", "Bình rượu tiên", "Chai đựng đan dược", "Trận pháp giam cầm"],
        "ans": 0,
        "explain": "Bình Cảnh là ranh giới giữa các tầng cảnh giới, đòi hỏi cơ duyên để xung kích vượt qua."
    },
    {
        "q": "Khi tắm mình trong Linh Tuyền (Ôn Tuyền) tại Động Phủ, tu sĩ sẽ nhận được lợi ích gì?",
        "options": ["Tăng tốc độ tích lũy tu vi", "Tăng Linh Thạch", "Nhận trang bị ngẫu nhiên", "Tăng điểm PvP"],
        "ans": 0,
        "explain": "Linh Tuyền đượm khí tiên gia, giúp thư giãn thần kinh và kích phát hấp thụ linh khí."
    },
    {
        "q": "Vật phẩm nào trong game có thể tăng trực tiếp +500 Linh Khí ngay sau khi dùng?",
        "options": ["Tụ Linh Đan", "Hồi Xuân Đan", "Phá Cảnh Đan", "Tẩy Tủy Đan"],
        "ans": 0,
        "explain": "Tụ Linh Đan cô đọng linh khí thiên địa, nuốt vào lập tức tăng 500 tu vi."
    },
    {
        "q": "Trong hệ thống Công Pháp, 'Thái Cực Hỗn Độn Quyết' yêu cầu tu sĩ đạt cảnh giới nào?",
        "options": ["Nguyên Anh - Sơ Kỳ", "Kết Đan - Hậu Kỳ", "Trúc Cơ - Sơ Kỳ", "Phàm Nhân"],
        "ans": 0,
        "explain": "Thái Cực Hỗn Độn Quyết là công pháp cao cấp đòi hỏi tu vi Nguyên Anh để vận hành kinh mạch."
    },
    {
        "q": "Công pháp 'Cửu Thiên Vạn Kiếp Quy Chân' yêu cầu cảnh giới tối thiểu là gì?",
        "options": ["Đại Thừa - Sơ Kỳ", "Hợp Thể - Hậu Kỳ", "Hóa Thần - Sơ Kỳ", "Trúc Cơ - Đỉnh Phong"],
        "ans": 0,
        "explain": "Đây là công pháp chí tôn tối cao dành cho bậc đại năng Đại Thừa cảnh giới."
    },
    {
        "q": "Phẩm cấp cao nhất của hệ thống trang bị thế tục sơ khai trước Linh Bảo là gì?",
        "options": ["Cực Phẩm Pháp Khí", "Phàm Khí", "Trung Phẩm", "Hạ Phẩm"],
        "ans": 0,
        "explain": "Cực Phẩm Pháp Khí là đỉnh cao trang bị giai đoạn Luyện Khí – Trúc Cơ."
    },
    {
        "q": "Tỷ lệ xuất hiện cơ bản của Phàm Khí khi rèn đồ là khoảng bao nhiêu phần trăm?",
        "options": ["Khoảng 70%", "Khoảng 10%", "Khoảng 30%", "Khoảng 99%"],
        "ans": 0,
        "explain": "Đồ phàm tục chiếm khoảng 70% tỷ lệ, tu sĩ cảnh giới càng cao mới dễ rèn ra bảo vật quý."
    },
    {
        "q": "Công pháp 'Vạn Kiếm Quy Tông Quyết' nổi bật nhất ở chỉ số nào?",
        "options": ["Công kích cực mạnh (ATK +40%)", "Phòng thủ siêu đẳng (DEF +100%)", "Tăng tốc độ chạy", "Hồi máu liên tục"],
        "ans": 0,
        "explain": "Vạn Kiếm Quy Tông tập hợp muôn vàn kiếm ý, tăng mạnh sức sát thương công kích."
    },
    {
        "q": "Trong 'Thế Giới Hoàn Mỹ', bảo thuật nào gắn liền với thời niên thiếu của Thạch Hạo?",
        "options": ["Côn Bằng Bảo Thuật", "Hư Không Thuật", "Đại Đạo Bảo Bình", "Thái Dương Quyền"],
        "ans": 0,
        "explain": "Thạch Hạo đạt được Côn Bằng Bảo Thuật tại Côn Bằng Sào, làm rạng danh thiên hạ."
    }
]

# ================= QUẢN LÝ XOAY VÒNG CÂU HỎI LIÊN TỤC =================
class QuizManager:
    """Quản lý câu hỏi chống lặp lại và theo dõi chuỗi trả lời đúng liên tục"""
    def __init__(self):
        self.recent_questions = {}   # user_id -> list of question indices
        self.streaks = {}            # user_id -> int
        self.total_correct = {}      # user_id -> int

    def get_next_question(self, user_id: int):
        seen = self.recent_questions.setdefault(user_id, [])
        available = [i for i in range(len(QUIZ_QUESTIONS)) if i not in seen]
        if not available:
            seen.clear()
            available = list(range(len(QUIZ_QUESTIONS)))

        q_idx = random.choice(available)
        seen.append(q_idx)
        if len(seen) > 35:
            seen.pop(0)

        raw = QUIZ_QUESTIONS[q_idx]
        correct_text = raw["options"][raw["ans"]]

        # Xáo trộn các phương án để vị trí đáp án luôn thay đổi
        shuffled = list(raw["options"])
        random.shuffle(shuffled)
        new_correct_idx = shuffled.index(correct_text)

        return {
            "q_idx": q_idx,
            "q": raw["q"],
            "options": shuffled,
            "ans": new_correct_idx,
            "explain": raw["explain"]
        }

    def add_correct(self, user_id: int) -> int:
        self.streaks[user_id] = self.streaks.get(user_id, 0) + 1
        self.total_correct[user_id] = self.total_correct.get(user_id, 0) + 1
        return self.streaks[user_id]

    def reset_streak(self, user_id: int):
        self.streaks[user_id] = 0

    def get_streak(self, user_id: int) -> int:
        return self.streaks.get(user_id, 0)

    def get_total_correct(self, user_id: int) -> int:
        return self.total_correct.get(user_id, 0)

global_quiz_mgr = QuizManager()

# ================= VIEW VẤN ĐÁP TIÊN CƠ TƯƠNG TÁC LIÊN TỤC =================
class QuizPlayView(discord.ui.View):
    def __init__(self, user_id: int, user_name: str, quiz_mgr: QuizManager):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.user_name = user_name
        self.quiz_mgr = quiz_mgr
        self.current_q = self.quiz_mgr.get_next_question(user_id)
        self.answered = False
        self._build_buttons()

    def _build_buttons(self):
        self.clear_items()
        opt_labels = ["A", "B", "C", "D"]
        for i, opt in enumerate(self.current_q["options"]):
            btn = discord.ui.Button(
                label=f"{opt_labels[i]}. {opt[:70]}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"opt_{i}",
                row=i // 2
            )
            btn.callback = self.make_answer_callback(i)
            self.add_item(btn)

    def make_answer_callback(self, chosen_idx: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("❌ Đây không phải ngọc giản vấn đáp của đạo hữu!", ephemeral=True)
            if self.answered:
                return await interaction.response.send_message("⚠️ Đạo hữu đã chọn đáp án cho câu này rồi!", ephemeral=True)

            self.answered = True
            correct_idx = self.current_q["ans"]
            is_correct = (chosen_idx == correct_idx)

            reward_str = ""
            if is_correct:
                streak = self.quiz_mgr.add_correct(self.user_id)
                base_lt = 300
                base_exp = 500
                bonus_lt = 100 if (streak > 0 and streak % 5 == 0) else 0
                total_lt = base_lt + bonus_lt

                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "UPDATE players SET linh_thach = linh_thach + ?, exp = exp + ? WHERE user_id = ?",
                    (total_lt, base_exp, self.user_id)
                )
                conn.commit()
                conn.close()

                reward_str = f"💎 **+{total_lt:,} Linh Thạch** | ✨ **+{base_exp:,} Linh Khí**"
                if bonus_lt > 0:
                    reward_str += f"\n🔥 **KÍCH HOẠT THƯỞNG CHUỖI STREAK {streak}!** (+{bonus_lt} LT)"
            else:
                self.quiz_mgr.reset_streak(self.user_id)

            opt_labels = ["A", "B", "C", "D"]
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id and item.custom_id.startswith("opt_"):
                    idx = int(item.custom_id.split("_")[1])
                    item.disabled = True
                    if idx == correct_idx:
                        item.style = discord.ButtonStyle.success
                        item.label = f"✅ {opt_labels[idx]}. {self.current_q['options'][idx][:65]}"
                    elif idx == chosen_idx:
                        item.style = discord.ButtonStyle.danger
                        item.label = f"❌ {opt_labels[idx]}. {self.current_q['options'][idx][:65]}"

            btn_next = discord.ui.Button(
                label="➡️ Câu Tiếp Theo",
                style=discord.ButtonStyle.primary,
                custom_id="btn_next_q",
                row=2
            )
            btn_next.callback = self.next_question_callback
            self.add_item(btn_next)

            btn_stop = discord.ui.Button(
                label="🚪 Dừng Lại",
                style=discord.ButtonStyle.secondary,
                custom_id="btn_stop_q",
                row=2
            )
            btn_stop.callback = self.stop_callback
            self.add_item(btn_stop)

            embed = self.create_result_embed(is_correct, chosen_idx, reward_str)
            await interaction.response.edit_message(embed=embed, view=self)

        return callback

    def create_result_embed(self, is_correct: bool, chosen_idx: int, reward_str: str) -> discord.Embed:
        streak = self.quiz_mgr.get_streak(self.user_id)
        total_c = self.quiz_mgr.get_total_correct(self.user_id)
        correct_idx = self.current_q["ans"]
        opt_labels = ["A", "B", "C", "D"]

        if is_correct:
            title = "🎉 CHÍNH XÁC — ĐẠO TÂM THÔNG TRIỆT!"
            color = 0x2ecc71
            status_desc = f"✅ Đáp án: **{opt_labels[correct_idx]}. {self.current_q['options'][correct_idx]}**\n{reward_str}"
        else:
            title = "❌ CHƯA CHÍNH XÁC — CẦN NGỘ ĐẠO THÊM!"
            color = 0xe74c3c
            status_desc = (
                f"Lựa chọn của đạo hữu: ~~{opt_labels[chosen_idx]}. {self.current_q['options'][chosen_idx]}~~\n"
                f"✅ Đáp án chuẩn xác: **{opt_labels[correct_idx]}. {self.current_q['options'][correct_idx]}**"
            )

        embed = discord.Embed(
            title=title,
            description=(
                f"❓ **Câu hỏi:** {self.current_q['q']}\n\n"
                f"{status_desc}\n\n"
                f"📖 **Điển tích ghi chép:** *{self.current_q['explain']}*"
            ),
            color=color
        )
        embed.set_footer(text=f"👤 {self.user_name} | 🔥 Chuỗi đúng liên tiếp: {streak} | 🏆 Tổng câu đúng: {total_c}")
        return embed

    async def next_question_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải ngọc giản vấn đáp của đạo hữu!", ephemeral=True)

        self.current_q = self.quiz_mgr.get_next_question(self.user_id)
        self.answered = False
        self._build_buttons()
        embed = self.create_question_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def stop_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ Đây không phải ngọc giản vấn đáp của đạo hữu!", ephemeral=True)

        streak = self.quiz_mgr.get_streak(self.user_id)
        total_c = self.quiz_mgr.get_total_correct(self.user_id)

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="📜 KẾT THÚC BUỔI VẤN ĐÁP TIÊN CƠ",
            description=(
                f"Đạo hữu **{self.user_name}** đã hoàn thành phiên vấn đáp đạo học!\n\n"
                f"🏆 **Tổng câu trả lời đúng:** `{total_c}` câu\n"
                f"🔥 **Chuỗi đúng cao nhất:** `{streak}` câu liên tiếp\n\n"
                "*(Đạo hữu có thể dùng lệnh `/vandap` hoặc `/hoatdong` bất cứ lúc nào để tiếp tục thử tài)*"
            ),
            color=0x9b59b6
        )
        await interaction.response.edit_message(embed=embed, view=self)

    def create_question_embed(self) -> discord.Embed:
        streak = self.quiz_mgr.get_streak(self.user_id)
        total_c = self.quiz_mgr.get_total_correct(self.user_id)
        opt_labels = ["A", "B", "C", "D"]

        opts_formatted = "\n".join(
            f"**{opt_labels[i]}.** {opt}"
            for i, opt in enumerate(self.current_q["options"])
        )

        embed = discord.Embed(
            title="📜 VẤN ĐÁP TIÊN CƠ — THỬ TÀI ĐẠO HỌC",
            description=(
                f"❓ **Câu hỏi:**\n### {self.current_q['q']}\n\n"
                f"{opts_formatted}\n\n"
                "────────────────────────────────────────\n"
                "*(Chọn một phương án A, B, C, D bên dưới)*"
            ),
            color=0x3498db
        )
        embed.set_footer(text=f"👤 {self.user_name} | 🔥 Chuỗi đúng: {streak} | 🏆 Tổng câu đúng: {total_c}")
        return embed

# ================= COG HOẠT ĐỘNG =================
class HoatDongCog(commands.Cog, name="Hoạt Động"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vandap", description="Tham gia Vấn Đáp Tiên Cơ liên tục với hàng chục câu hỏi tu tiên nhận thưởng")
    async def vandap(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước để gia nhập giới tu chân!", ephemeral=True)

        view = QuizPlayView(interaction.user.id, interaction.user.display_name, global_quiz_mgr)
        embed = view.create_question_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="vandap", aliases=["vd", "quiz", "dovui"])
    async def prefix_vandap(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        view = QuizPlayView(ctx.author.id, ctx.author.display_name, global_quiz_mgr)
        embed = view.create_question_embed()
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="hoatdong", description="Xem các Hoạt Động sự kiện tu tiên đang diễn ra")
    async def hoatdong(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("❌ Hãy dùng `/nhapdao` trước!", ephemeral=True)

        embed = discord.Embed(
            title="🥥 HOẠT ĐỘNG THỜI HẠN — TIÊN GIỚI ĐẠI HỘI",
            description=(
                "Các hoạt động quy tụ vạn tiên trong tam giới:\n\n"
                "1. 🐲 **Ma Thú Triều Xâm Lăng:** Toàn server chung tay đẩy lùi yêu ma (Diễn ra lúc 20:00 hàng ngày).\n"
                "2. ⚡ **Thiên Kiếp Thí Luyện:** Leo Tháp Vấn Đỉnh (`/vandinh`) nhận x2 phần thưởng.\n"
                "3. 📜 **Vấn Đáp Tu Tiên:** Vấn đáp đạo học liên tục nhận thưởng miễn phí (`/vandap`).\n\n"
                "Nhấp nút bên dưới để bắt đầu thử tài vấn đáp tu chân liên tục!"
            ),
            color=0xe67e22
        )

        view = discord.ui.View(timeout=120)
        btn_quiz = discord.ui.Button(label="📜 Trả Lời Vấn Đáp Liên Tục", style=discord.ButtonStyle.success)

        async def quiz_callback(btn_interaction: discord.Interaction):
            if btn_interaction.user.id != interaction.user.id:
                return await btn_interaction.response.send_message("❌ Không thể thao tác!", ephemeral=True)

            q_view = QuizPlayView(interaction.user.id, interaction.user.display_name, global_quiz_mgr)
            q_embed = q_view.create_question_embed()
            await btn_interaction.response.send_message(embed=q_embed, view=q_view, ephemeral=True)

        btn_quiz.callback = quiz_callback
        view.add_item(btn_quiz)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="hoatdong", aliases=["hd", "sukien"])
    async def prefix_hoatdong(self, ctx: commands.Context):
        player = get_player(ctx.author.id)
        if not player:
            return await ctx.send(f"❌ Hãy dùng `{ctx.prefix}nhapdao` trước!")

        embed = discord.Embed(
            title="🥥 HOẠT ĐỘNG THỜI HẠN — TIÊN GIỚI ĐẠI HỘI",
            description=(
                "Các hoạt động quy tụ vạn tiên trong tam giới:\n\n"
                "1. 🐲 **Ma Thú Triều Xâm Lăng:** Toàn server chung tay đẩy lùi yêu ma (Diễn ra lúc 20:00 hàng ngày).\n"
                "2. ⚡ **Thiên Kiếp Thí Luyện:** Leo Tháp Vấn Đỉnh (`t vandinh`) nhận x2 phần thưởng.\n"
                "3. 📜 **Vấn Đáp Tu Tiên:** Vấn đáp đạo học liên tục nhận thưởng miễn phí (`t vandap`).\n\n"
                "Nhấp nút bên dưới để bắt đầu thử tài vấn đáp tu chân liên tục!"
            ),
            color=0xe67e22
        )

        view = discord.ui.View(timeout=120)
        btn_quiz = discord.ui.Button(label="📜 Trả Lời Vấn Đáp Liên Tục", style=discord.ButtonStyle.success)

        async def quiz_callback(btn_interaction: discord.Interaction):
            if btn_interaction.user.id != ctx.author.id:
                return await btn_interaction.response.send_message("❌ Không thể thao tác!", ephemeral=True)

            q_view = QuizPlayView(ctx.author.id, ctx.author.display_name, global_quiz_mgr)
            q_embed = q_view.create_question_embed()
            await btn_interaction.response.send_message(embed=q_embed, view=q_view, ephemeral=True)

        btn_quiz.callback = quiz_callback
        view.add_item(btn_quiz)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(HoatDongCog(bot))
