from enum import Enum

# ✅ Kullanıcı Rolleri (Admin, Driver, Passenger)
class UserRole(str, Enum):
    ADMIN = "admin"
    DRIVER = "driver"
    PASSENGER = "passenger"

# ✅ Ödeme Durumları
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# ✅ Ödeme Yöntemleri
class PaymentMethod(str, Enum):
    WALLET = "wallet"
    CREDIT_CARD = "credit_card"
    IDEAL = "ideal"
    PAYPAL = "paypal"

# ✅ Rezervasyon Durumları
class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

# ✅ İnceleme (Review) Kategorileri
class ReviewCategory(str, Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"
    CAR = "car"
    SERVICE = "service"

# ✅ İnceleme Oy Türleri (Like/Dislike)  
# 🔹 'ReviewVoteType' yerine daha açıklayıcı olması için 'ReviewReviewVoteType' olarak değiştirildi
class ReviewVoteType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"

# ✅ Şikayet (Complaint) Durumları
class ComplaintStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

# ✅ Genel Durumlar (Aktif/Pasif vb. için)  
# 🔹 Sistemdeki farklı model ve süreçler için kullanılabilecek genel durumlar  
class GeneralStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class NumberOfSeats(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4

class RideStatus(str, Enum):
    past = "past"  
    upcoming = "upcoming"
