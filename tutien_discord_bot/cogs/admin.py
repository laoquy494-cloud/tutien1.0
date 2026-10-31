import os
import sys
import datetime
import platform
import discord
from discord import app_commands
from discord.ext import commands
from config import is_owner_id
from database import get_player, get_connection, reset_player, reset_all_players

class ConfirmResetPlayerView(discord.ui.View):
    def __init__(self, owner_id: int, target_user: discord.User | discord.Member, target_player):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.target_user = target_user
        self.target_player = target_player

    @discord.ui.button(label="🔴 Xác Nhận Reset", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)

        ok = reset_player(self.target_user.id)
        for child in self.children:
            child.disabled = True

        if ok:
            embed = discord.Embed(
                title="♻️ THIÊN ĐẠO TRÙNG SINH — RESET THÀNH CÔNG",
                description=(
                    f"Chủ Nhân Bot **{interaction.user.display_name}** đã giáng hạ luân hồi thần lôi!\n\n"
                    f"👤 **Đạo hữu:** {self.target_user.mention} (`{self.target_user.id}`)\n"
                    f"🧹 **Trạng thái:** Toàn bộ tu vi, cảnh giới, 5 món pháp bảo, linh thú, động phủ, linh thạch đã bị xóa bỏ.\n\n"
                    f"🌱 Đạo hữu này đã trở về trạng thái **Phàm Nhân** ban đầu (chưa nhập đạo) và có thể bắt đầu lại hành trình bằng lệnh `/nhapdao`!"
                ),
                color=0x2ecc71
            )
        else:
            embed = discord.Embed(
                title="⚠️ KHÔNG TÌM THẤY DỮ LIỆU",
                description=f"Đạo hữu {self.target_user.mention} không tồn tại trong dữ liệu hoặc đã bị reset trước đó.",
                color=0xe74c3c
            )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Hủy Bỏ", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title="🛑 ĐÃ HỦY THAO TÁC",
            description=f"Thao tác reset dữ liệu cho {self.target_user.mention} đã bị hủy bỏ an toàn.",
            color=0x95a5a6
        )
        await interaction.response.edit_message(embed=embed, view=self)

class ConfirmResetAllView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=60)
        self.owner_id = owner_id

    @discord.ui.button(label="☠️ XÁC NHẬN WIPE TOÀN BỘ SERVER", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)

        count = reset_all_players()
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="💥 ĐẠI HỒNG MÔNG TÁI THIẾT — RESET TOÀN BỘ SERVER THÀNH CÔNG",
            description=(
                f"Chủ Nhân Bot **{interaction.user.display_name}** đã mở ra kỷ nguyên mới!\n\n"
                f"🧹 Đã xóa bỏ toàn bộ dữ liệu của **{count:,}** người chơi trong database.\n"
                f"🌱 Tất cả mọi người hiện đã trở về làm **Phàm Nhân**, sẵn sàng khai mở tiên lộ mới bằng `/nhapdao`!"
            ),
            color=0x2ecc71
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Hủy Bỏ", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title="🛑 ĐÃ HỦY THAO TÁC",
            description="Thao tác reset toàn bộ server đã bị hủy bỏ an toàn.",
            color=0x95a5a6
        )
        await interaction.response.edit_message(embed=embed, view=self)


class ConfirmShutdownView(discord.ui.View):
    def __init__(self, owner_id: int, bot: commands.Bot):
        super().__init__(timeout=30)
        self.owner_id = owner_id
        self.bot = bot

    @discord.ui.button(label="🛑 Xác Nhận Tắt Bot", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title="🛑 THIÊN ĐẠO QUY TỊCH — ĐANG TẮT BOT",
            description="Bot đang tiến hành đóng kết nối và tắt tiến trình an toàn. Hẹn gặp lại các vị đạo hữu!",
            color=0xe74c3c
        )
        await interaction.response.edit_message(embed=embed, view=self)
        await self.bot.close()

    @discord.ui.button(label="❌ Hủy Bỏ", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ Chỉ Chủ Nhân Bot (Owner) mới có quyền bấm nút này!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title="✅ ĐÃ HỦY LỆNH TẮT BOT",
            description="Bot vẫn tiếp tục vận hành bình thường.",
            color=0x2ecc71
        )
        await interaction.response.edit_message(embed=embed, view=self)


class AdminCog(commands.Cog, name="Quản Trị Thiên Đạo"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def check_is_owner(self, user: discord.User | discord.Member) -> bool:
        """Kiểm tra xem người dùng có phải Owner Bot không (qua OWNER_ID trong .env hoặc app owner)"""
        if is_owner_id(user.id):
            return True
        if self.bot.owner_id and user.id == self.bot.owner_id:
            return True
        if self.bot.owner_ids and user.id in self.bot.owner_ids:
            return True
        try:
            return await self.bot.is_owner(user)
        except Exception:
            return False

    @app_commands.command(name="addlinhthach", description="[Owner Bot] Thêm hoặc bớt Linh Thạch cho một đạo hữu")
    @app_commands.describe(
        dao_huu="Đạo hữu muốn thêm/bớt Linh Thạch",
        so_luong="Số lượng Linh Thạch (nhập số âm nếu muốn trừ)"
    )
    async def addlinhthach(self, interaction: discord.Interaction, dao_huu: discord.User, so_luong: int):
        # Kiểm tra quyền Owner Bot
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền năng can thiệp vào tài nguyên tu tiên!",
                ephemeral=True
            )

        if so_luong == 0:
            return await interaction.response.send_message("⚠️ Số lượng Linh Thạch không thể bằng 0!", ephemeral=True)

        player = get_player(dao_huu.id)
        if not player:
            return await interaction.response.send_message(
                f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo! Hãy nhắc họ dùng lệnh `/nhapdao` trước.",
                ephemeral=True
            )

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = MAX(0, linh_thach + ?) WHERE user_id = ?", (so_luong, dao_huu.id))
        conn.commit()
        conn.close()

        updated_player = get_player(dao_huu.id)
        new_balance = updated_player[6]
        is_positive = so_luong > 0

        embed = discord.Embed(
            title="⚡ THIÊN ĐẠO BAN THƯỞNG — LINH THẠCH GIÁNG THẾ" if is_positive else "⚡ THIÊN ĐẠO TRỪNG PHẠT — KHẤU TRỪ LINH THẠCH",
            description=(
                f"Chủ Nhân Bot **{interaction.user.display_name}** đã {'ban tặng' if is_positive else 'khấu trừ'} Linh Thạch của **{dao_huu.mention}**!\n\n"
                f"💎 **Biến động:** `+{so_luong:,}` Linh Thạch" if is_positive else f"💎 **Biến động:** `{so_luong:,}` Linh Thạch"
            ),
            color=0xf1c40f if is_positive else 0xe74c3c
        )
        embed.add_field(name="💰 Túi Trữ Vật Hiện Tại", value=f"`{new_balance:,}` Linh Thạch", inline=True)
        embed.add_field(name="👤 Người Nhận", value=dao_huu.mention, inline=True)
        embed.set_footer(text="Thiên Đạo chí cao — chưởng quản vạn vật trong thiên địa!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setlinhthach", description="[Owner Bot] Thiết lập số lượng Linh Thạch chính xác cho một đạo hữu")
    @app_commands.describe(
        dao_huu="Đạo hữu muốn thiết lập Linh Thạch",
        so_luong="Số lượng Linh Thạch muốn đặt (>= 0)"
    )
    async def setlinhthach(self, interaction: discord.Interaction, dao_huu: discord.User, so_luong: int):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )

        if so_luong < 0:
            return await interaction.response.send_message("⚠️ Số lượng Linh Thạch không thể âm!", ephemeral=True)

        player = get_player(dao_huu.id)
        if not player:
            return await interaction.response.send_message(
                f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo!",
                ephemeral=True
            )

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = ? WHERE user_id = ?", (so_luong, dao_huu.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="⚡ THIÊN ĐẠO QUY ĐỊNH — CẢI BIẾN LINH THẠCH",
            description=(
                f"Chủ Nhân Bot **{interaction.user.display_name}** đã điều chỉnh số dư của **{dao_huu.mention}**!\n\n"
                f"💰 **Số dư mới:** `{so_luong:,}` Linh Thạch"
            ),
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addtuvi", description="[Owner Bot] Ban thưởng tu vi (Linh Khí) cho một đạo hữu")
    @app_commands.describe(
        dao_huu="Đạo hữu muốn ban thưởng tu vi",
        so_luong="Số lượng Linh Khí"
    )
    async def addtuvi(self, interaction: discord.Interaction, dao_huu: discord.User, so_luong: int):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )

        if so_luong == 0:
            return await interaction.response.send_message("⚠️ Số lượng Linh Khí không thể bằng 0!", ephemeral=True)

        player = get_player(dao_huu.id)
        if not player:
            return await interaction.response.send_message(
                f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo!",
                ephemeral=True
            )

        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET exp = MAX(0, exp + ?), total_exp_gained = MAX(0, total_exp_gained + ?) WHERE user_id = ?",
                  (so_luong, max(0, so_luong), dao_huu.id))
        conn.commit()
        conn.close()

        updated_player = get_player(dao_huu.id)
        embed = discord.Embed(
            title="✨ THIÊN ĐẠO QUÁN ĐỈNH — BAN THƯỞNG TU VI",
            description=(
                f"Chủ Nhân Bot **{interaction.user.display_name}** đã quán đỉnh truyền thụ cho **{dao_huu.mention}**!\n\n"
                f"✨ **Tu vi nhận thêm:** `+{so_luong:,}` Linh Khí\n"
                f"📈 **Tu vi hiện tại:** `{updated_player[5]:,}` Linh Khí"
            ),
            color=0x9b59b6
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name="addlinhthach", aliases=["addlt", "addlichthach", "themlt", "themlinhthach", "themlichthach"])
    async def prefix_addlinhthach(self, ctx: commands.Context, dao_huu: discord.Member = None, so_luong: int = None):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        if dao_huu is None or so_luong is None or so_luong == 0:
            return await ctx.send(f"⚠️ **Cách dùng:** `{ctx.prefix}addlinhthach @User <số_lượng>` (VD: `{ctx.prefix}addlt @Shin 1000`)")
        player = get_player(dao_huu.id)
        if not player:
            return await ctx.send(f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo!")
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = MAX(0, linh_thach + ?) WHERE user_id = ?", (so_luong, dao_huu.id))
        conn.commit()
        conn.close()
        updated = get_player(dao_huu.id)
        is_pos = so_luong > 0
        embed = discord.Embed(
            title="⚡ THIÊN ĐẠO BAN THƯỞNG — LINH THẠCH GIÁNG THẾ" if is_pos else "⚡ THIÊN ĐẠO TRỪNG PHẠT — KHẤU TRỪ LINH THẠCH",
            description=f"Chủ Nhân Bot **{ctx.author.display_name}** đã {'ban tặng' if is_pos else 'khấu trừ'} Linh Thạch của **{dao_huu.mention}**!\n\n💎 **Biến động:** `+{so_luong:,}` Linh Thạch" if is_pos else f"Chủ Nhân Bot **{ctx.author.display_name}** đã khấu trừ Linh Thạch của **{dao_huu.mention}**!\n\n💎 **Biến động:** `{so_luong:,}` Linh Thạch",
            color=0xf1c40f if is_pos else 0xe74c3c
        )
        embed.add_field(name="💰 Túi Trữ Vật Hiện Tại", value=f"`{updated[6]:,}` Linh Thạch", inline=True)
        embed.add_field(name="👤 Người Nhận", value=dao_huu.mention, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="setlinhthach", aliases=["setlt", "setlichthach"])
    async def prefix_setlinhthach(self, ctx: commands.Context, dao_huu: discord.Member = None, so_luong: int = None):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        if dao_huu is None or so_luong is None or so_luong < 0:
            return await ctx.send(f"⚠️ **Cách dùng:** `{ctx.prefix}setlinhthach @User <số_lượng>` (VD: `{ctx.prefix}setlt @Shin 5000`)")
        player = get_player(dao_huu.id)
        if not player:
            return await ctx.send(f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo!")
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET linh_thach = ? WHERE user_id = ?", (so_luong, dao_huu.id))
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="⚡ THIÊN ĐẠO QUY ĐỊNH — CẢI BIẾN LINH THẠCH",
            description=f"Chủ Nhân Bot **{ctx.author.display_name}** đã điều chỉnh số dư của **{dao_huu.mention}**!\n\n💰 **Số dư mới:** `{so_luong:,}` Linh Thạch",
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="addtuvi", aliases=["addexp", "addlk", "addlinhkhi"])
    async def prefix_addtuvi(self, ctx: commands.Context, dao_huu: discord.Member = None, so_luong: int = None):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        if dao_huu is None or so_luong is None or so_luong == 0:
            return await ctx.send(f"⚠️ **Cách dùng:** `{ctx.prefix}addtuvi @User <số_lượng>` (VD: `{ctx.prefix}addtuvi @Shin 5000`)")
        player = get_player(dao_huu.id)
        if not player:
            return await ctx.send(f"❌ Đạo hữu **{dao_huu.display_name}** chưa nhập đạo!")
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE players SET exp = MAX(0, exp + ?), total_exp_gained = MAX(0, total_exp_gained + ?) WHERE user_id = ?",
                  (so_luong, max(0, so_luong), dao_huu.id))
        conn.commit()
        conn.close()
        updated = get_player(dao_huu.id)
        embed = discord.Embed(
            title="✨ THIÊN ĐẠO QUÁN ĐỈNH — BAN THƯỞNG TU VI",
            description=f"Chủ Nhân Bot **{ctx.author.display_name}** đã quán đỉnh truyền thụ cho **{dao_huu.mention}**!\n\n✨ **Tu vi nhận thêm:** `+{so_luong:,}` Linh Khí\n📈 **Tu vi hiện tại:** `{updated[5]:,}` Linh Khí",
            color=0x9b59b6
        )
        await ctx.send(embed=embed)

    @app_commands.command(name="resetplayer", description="[Owner Bot] Reset toàn bộ dữ liệu một người chơi về lại ban đầu (Phàm nhân)")
    @app_commands.describe(
        dao_huu="Đạo hữu muốn reset dữ liệu về ban đầu"
    )
    async def resetplayer(self, interaction: discord.Interaction, dao_huu: discord.User):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )
        player = get_player(dao_huu.id)
        if not player:
            return await interaction.response.send_message(
                f"❌ Đạo hữu **{dao_huu.display_name}** chưa từng nhập đạo hoặc dữ liệu đã trống!",
                ephemeral=True
            )

        embed = discord.Embed(
            title="⚠️ XÁC NHẬN RESET DỮ LIỆU NGƯỜI CHƠI",
            description=(
                f"Chủ nhân có chắc chắn muốn **xóa toàn bộ dữ liệu** của **{dao_huu.mention}** không?\n\n"
                f"• Nhân vật: **{player[1]}** (ID: `{player[0]}`)\n"
                f"• Hành động này sẽ xóa sạch: Cảnh giới, Tu vi, Linh thạch, 5 món Pháp bảo, Linh thú, Động phủ, Vấn đỉnh tháp...\n"
                f"• Người này sẽ trở về làm **Phàm Nhân** và có thể quay lại Linh căn mới bằng `/nhapdao`.\n\n"
                f"🔴 **LƯU Ý:** Thao tác này **KHÔNG THỂ HOÀN TÁC!**"
            ),
            color=0xe67e22
        )
        view = ConfirmResetPlayerView(interaction.user.id, dao_huu, player)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="resetplayer", aliases=["resetuser", "resetnhanvat", "reset"])
    async def prefix_resetplayer(self, ctx: commands.Context, *, user_input: str = None):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")

        if not user_input:
            return await ctx.send(f"⚠️ **Cách dùng:** `{ctx.prefix}resetplayer @User` hoặc `{ctx.prefix}resetplayer <user_id>`")

        target_user = None
        if ctx.message.mentions:
            target_user = ctx.message.mentions[0]
        else:
            clean_id = user_input.strip("<@!> ")
            if clean_id.isdigit():
                try:
                    target_user = await self.bot.fetch_user(int(clean_id))
                except Exception:
                    class DummyUser:
                        def __init__(self, uid):
                            self.id = uid
                            self.display_name = f"User {uid}"
                            self.mention = f"<@{uid}>"
                    target_user = DummyUser(int(clean_id))

        if not target_user:
            return await ctx.send("❌ Không tìm thấy đạo hữu hợp lệ! Vui lòng mention hoặc nhập User ID.")

        player = get_player(target_user.id)
        if not player:
            return await ctx.send(f"❌ Người chơi {target_user.mention} chưa từng nhập đạo hoặc dữ liệu đã trống!")

        embed = discord.Embed(
            title="⚠️ XÁC NHẬN RESET DỮ LIỆU NGƯỜI CHƠI",
            description=(
                f"Chủ nhân có chắc chắn muốn **xóa toàn bộ dữ liệu** của **{target_user.mention}** không?\n\n"
                f"• Nhân vật: **{player[1]}** (ID: `{player[0]}`)\n"
                f"• Hành động này sẽ xóa sạch: Cảnh giới, Tu vi, Linh thạch, 5 món Pháp bảo, Linh thú, Động phủ, Vấn đỉnh tháp...\n"
                f"• Người này sẽ trở về làm **Phàm Nhân** và có thể quay lại Linh căn mới bằng `{ctx.prefix}nhapdao`.\n\n"
                f"🔴 **LƯU Ý:** Thao tác này **KHÔNG THỂ HOÀN TÁC!**"
            ),
            color=0xe67e22
        )
        view = ConfirmResetPlayerView(ctx.author.id, target_user, player)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="resetall", description="[Owner Bot] Reset toàn bộ cơ sở dữ liệu người chơi về lại ban đầu (Wipe Database)")
    async def resetall(self, interaction: discord.Interaction):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )
        embed = discord.Embed(
            title="☠️ CẢNH BÁO: XÁC NHẬN WIPE TOÀN BỘ SERVER",
            description=(
                "⚠️ **CẢNH BÁO TỐI CAO:** Thao tác này sẽ **XÓA SẠCH DỮ LIỆU CỦA TOÀN BỘ NGƯỜI CHƠI** trên tất cả các server!\n\n"
                "• Mọi nhân vật, cấp bậc, trang bị, chợ, tông môn, linh thú sẽ biến mất vĩnh viễn!\n"
                "• Hãy chắc chắn rằng bạn thật sự muốn làm điều này.\n\n"
                "Nhấp nút đỏ bên dưới nếu bạn chắc chắn muốn reset toàn bộ thế giới tu tiên!"
            ),
            color=0xc0392b
        )
        view = ConfirmResetAllView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="resetall", aliases=["resetallplayers", "wipeserver"])
    async def prefix_resetall(self, ctx: commands.Context):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        embed = discord.Embed(
            title="☠️ CẢNH BÁO: XÁC NHẬN WIPE TOÀN BỘ SERVER",
            description=(
                "⚠️ **CẢNH BÁO TỐI CAO:** Thao tác này sẽ **XÓA SẠCH DỮ LIỆU CỦA TOÀN BỘ NGƯỜI CHƠI** trên tất cả các server!\n\n"
                "• Mọi nhân vật, cấp bậc, trang bị, chợ, tông môn, linh thú sẽ biến mất vĩnh viễn!\n"
                "• Hãy chắc chắn rằng bạn thật sự muốn làm điều này.\n\n"
                "Nhấp nút đỏ bên dưới nếu bạn chắc chắn muốn reset toàn bộ thế giới tu tiên!"
            ),
            color=0xc0392b
        )
        view = ConfirmResetAllView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    def _build_status_embed(self) -> discord.Embed:
        # Thời gian hoạt động
        uptime_str = "Chưa ghi nhận"
        if hasattr(self.bot, "start_time"):
            delta = datetime.datetime.now() - self.bot.start_time
            days = delta.days
            hours, rem = divmod(delta.seconds, 3600)
            mins, secs = divmod(rem, 60)
            parts = []
            if days > 0:
                parts.append(f"{days} ngày")
            if hours > 0 or days > 0:
                parts.append(f"{hours} giờ")
            parts.append(f"{mins} phút {secs} giây")
            uptime_str = " ".join(parts)

        # Bộ nhớ RAM sử dụng
        ram_mb = "N/A"
        try:
            import psutil
            ram_mb = f"{psutil.Process().memory_info().rss / (1024 * 1024):.1f} MB"
        except Exception:
            pass

        # Chế độ chạy (pythonw = chạy ngầm, python = cửa sổ console)
        exe_name = os.path.basename(sys.executable).lower()
        mode_str = "Chạy ngầm (Background / pythonw)" if "pythonw" in exe_name else "Cửa sổ lệnh (Console / python)"

        # Thống kê người chơi
        player_count = 0
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM players")
            player_count = c.fetchone()[0]
            conn.close()
        except Exception:
            pass

        latency_ms = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="⛩️ TRẠNG THÁI VẬN HÀNH THIÊN ĐẠO BOT",
            color=0x2ecc71
        )
        embed.add_field(name="🟢 Trạng Thái", value="`ONLINE (Đang hoạt động)`", inline=True)
        embed.add_field(name="⚙️ Chế Độ Chạy", value=f"`{mode_str}`", inline=True)
        embed.add_field(name="🆔 Process ID (PID)", value=f"`{os.getpid()}`", inline=True)
        embed.add_field(name="⏱️ Thời Gian Hoạt Động", value=f"`{uptime_str}`", inline=True)
        embed.add_field(name="💾 Bộ Nhớ RAM", value=f"`{ram_mb}`", inline=True)
        embed.add_field(name="📶 Độ Trễ (Ping)", value=f"`{latency_ms} ms`", inline=True)
        embed.add_field(name="🌐 Máy Chủ (Guilds)", value=f"`{len(self.bot.guilds):,}` server", inline=True)
        embed.add_field(name="👥 Người Chơi Tu Tiên", value=f"`{player_count:,}` đạo hữu", inline=True)
        embed.add_field(name="🐍 Môi Trường", value=f"Python `{platform.python_version()}` ({platform.system()})", inline=True)
        embed.set_footer(text="Thiên Đạo vận hành bất tức — Tự động mở tắt theo PC")
        return embed

    @app_commands.command(name="botstatus", description="[Owner Bot] Kiểm tra trạng thái vận hành của bot (RAM, Uptime, PID, Chế độ chạy)")
    async def botstatus(self, interaction: discord.Interaction):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )
        embed = self._build_status_embed()
        await interaction.response.send_message(embed=embed)

    @commands.command(name="botstatus", aliases=["status", "tstatus", "botinfo", "pingbot"])
    async def prefix_botstatus(self, ctx: commands.Context):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        embed = self._build_status_embed()
        await ctx.send(embed=embed)

    @app_commands.command(name="shutdown", description="[Owner Bot] Dừng và tắt bot an toàn từ xa")
    async def shutdown(self, interaction: discord.Interaction):
        if not await self.check_is_owner(interaction.user):
            return await interaction.response.send_message(
                "❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!",
                ephemeral=True
            )
        embed = discord.Embed(
            title="🛑 XÁC NHẬN TẮT BOT TỪ XA",
            description=(
                "Chủ nhân có chắc chắn muốn tắt tiến trình Tu Tiên Bot không?\n\n"
                "• Sau khi tắt, bot sẽ dừng phản hồi cho đến khi được khởi động lại hoặc khi PC khởi động lại.\n"
                "• Toàn bộ dữ liệu SQLite đã được bảo lưu an toàn."
            ),
            color=0xe67e22
        )
        view = ConfirmShutdownView(interaction.user.id, self.bot)
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="shutdown", aliases=["tatbot", "dungbot", "tshutdown"])
    async def prefix_shutdown(self, ctx: commands.Context):
        if not await self.check_is_owner(ctx.author):
            return await ctx.send("❌ **Thiên Đạo Uy Nghi:** Chỉ có Chủ Nhân Bot (Owner) mới có quyền dùng lệnh này!")
        embed = discord.Embed(
            title="🛑 XÁC NHẬN TẮT BOT TỪ XA",
            description=(
                "Chủ nhân có chắc chắn muốn tắt tiến trình Tu Tiên Bot không?\n\n"
                "• Sau khi tắt, bot sẽ dừng phản hồi cho đến khi được khởi động lại hoặc khi PC khởi động lại.\n"
                "• Toàn bộ dữ liệu SQLite đã được bảo lưu an toàn."
            ),
            color=0xe67e22
        )
        view = ConfirmShutdownView(ctx.author.id, self.bot)
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
