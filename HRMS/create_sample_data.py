from django.contrib.auth.models import User
from staff.models import StaffProfile, Department, Position
from django.utils import timezone
import random
from datetime import timedelta
import faker

def generate_vietnamese_name():
    # Danh sách họ phổ biến
    ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ']
    
    # Danh sách tên đệm nam/nữ
    dem_nam = ['Văn', 'Hữu', 'Đức', 'Công', 'Quang', 'Anh', 'Đình']
    dem_nu = ['Thị', 'Ngọc', 'Thùy', 'Kim', 'Thúy', 'Thanh', 'Mai']
    
    # Danh sách tên nam/nữ
    ten_nam = ['Nam', 'Hùng', 'Dũng', 'Minh', 'Long', 'Phong', 'Quân', 'Đạt', 'Hiếu', 'Trung']
    ten_nu = ['Hương', 'Lan', 'Linh', 'Hoa', 'Trang', 'Thảo', 'Mai', 'Phương', 'Anh', 'Ngọc']

    gender = random.choice(['Nam', 'Nữ'])
    
    if gender == 'Nam':
        name = f"{random.choice(ho)} {random.choice(dem_nam)} {random.choice(ten_nam)}"
    elif gender == 'Nữ':
        name = f"{random.choice(ho)} {random.choice(dem_nu)} {random.choice(ten_nu)}"
    else:  # Khác
        dem = random.choice(dem_nam + dem_nu)
        ten = random.choice(ten_nam + ten_nu)
        name = f"{random.choice(ho)} {dem} {ten}"
    
    return name, gender

def create_sample_data():
    fake = faker.Faker('vi_VN')
    
    # Theo dõi các phòng đã có trưởng phòng
    departments_with_manager = set()
    department_objects = Department.objects.all()
    
    # Tạo 30 nhân viên
    for i in range(30):
        # Tạo tên và giới tính
        full_name, gender = generate_vietnamese_name()
        
        # Tạo email và username độc nhất
        email = f'nhanvien{i+1}@company.com'
        
        # Tạo user mới
        user = User.objects.create_user(
            username=email,
            email=email,
            password='12345678'
        )

        # Chọn phòng ban ngẫu nhiên
        department = random.choice(department_objects)
        
        # Xác định chức vụ
        if department.id not in departments_with_manager:
            position = Position.objects.get(name="Trưởng Phòng")
            departments_with_manager.add(department.id)
        else:
            position = Position.objects.get(name="Nhân Sự")

        # Tạo ngày gia nhập ngẫu nhiên trong 2 năm gần đây
        join_date = timezone.now() - timedelta(days=random.randint(0, 730))
        
        # Tạo ngày sinh ngẫu nhiên (25-45 tuổi)
        birthdate = timezone.now() - timedelta(days=random.randint(9125, 16425))

        # Tạo thông tin nhân viên
        StaffProfile.objects.create(
            user=user,
            full_name=full_name,
            department=department,
            position=position,
            gender=random.choice(['Nam', 'Nữ']),
            join_date=join_date,
            phone_number=f'0{random.randint(300000000, 999999999)}',  # Số điện thoại Việt Nam
            address=fake.address(),
            birthdate=birthdate,
            base_salary=random.randint(5000000, 10000000)
        )

    print("Đã tạo xong 30 nhân viên mẫu!")
