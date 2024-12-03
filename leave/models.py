from django.db import models

from staff.models import StaffProfile

class Leave(models.Model):
    # Primary Key (id)
    id = models.AutoField(primary_key=True)

    # Foreign Key liên kết tới StaffProfile
    staff = models.ForeignKey(
        StaffProfile,  # Liên kết đến model StaffProfile
        on_delete=models.CASCADE,  # Xóa Leave khi StaffProfile bị xóa
        related_name='leaves'  # Tên để truy cập từ StaffProfile
    )

    # Các cột khác
    start_date = models.DateTimeField()  # Ngày bắt đầu
    end_date = models.DateTimeField()  # Ngày kết thúc
    created_at = models.DateTimeField(auto_now_add=True)  # Tự động lưu thời gian tạo
    reason = models.CharField(max_length=255)  # Lý do
    reason_detail = models.TextField(blank=True, null=True)  # Chi tiết lý do
    status = models.CharField(max_length=50, default="Đang chờ")  # Trạng thái

    def __str__(self):
        return f"Leave {self.id} - {self.staff}"
