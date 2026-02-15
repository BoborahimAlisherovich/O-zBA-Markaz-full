"""
Models for the Educational Center Management System.
Following Django best practices and PEP8 standards.
"""

#Ulug'bek uchun test uchun yozilgan model fayli, aslida models.py deb nomlanishi kerak edi, lekin test uchun models_backup.py deb nomlandi.
import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


def generate_unique_filename(instance, filename):
    """Generate unique filename for uploaded files."""
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    model_name = instance.__class__.__name__.lower()
    return os.path.join(f'uploads/{model_name}/', unique_name)


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqt")

    class Meta:
        abstract = True


class News(BaseModel):
    """Yangiliklar modeli"""
    title = models.CharField(max_length=500, verbose_name="Sarlavha")
    content = models.TextField(verbose_name="Matn")
    image = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Rasm"
    )
    image_url = models.URLField(blank=True, null=True, verbose_name="Rasm URL (tashqi)")
    video_url = models.URLField(blank=True, null=True, verbose_name="Video URL")
    external_link = models.URLField(blank=True, null=True, verbose_name="Tashqi havola")
    is_important = models.BooleanField(default=False, verbose_name="Muhim")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_image_url(self):
        """Return the image URL (uploaded or external)."""
        if self.image:
            return self.image.url
        return self.image_url


class GalleryItem(BaseModel):
    """Galereya modeli (rasmlar va videolar)"""
    TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]

    image = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Rasm fayli"
    )
    url = models.URLField(blank=True, null=True, verbose_name="Media URL (tashqi)")
    media_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='image',
        verbose_name="Media turi"
    )
    caption = models.CharField(max_length=500, blank=True, verbose_name="Izoh")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Galereya elementi"
        verbose_name_plural = "Galereya"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.caption or f"Media #{self.pk}"

    def get_media_url(self):
        """Return the media URL (uploaded or external)."""
        if self.image:
            return self.image.url
        return self.url


class Listener(BaseModel):
    """Tinglovchilar (Talabalar) modeli"""
    RECORD_TYPE_CHOICES = [
        ('certificate', 'Malaka oshirish (MO)'),
        ('diploma', 'Qayta tayyorlash (QT)'),
    ]

    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='certificate',
        verbose_name="Hujjat turi"
    )
    full_name = models.CharField(max_length=300, verbose_name="F.I.SH")
    institution = models.CharField(max_length=500, blank=True, verbose_name="Muassasa")
    workplace = models.CharField(max_length=500, blank=True, verbose_name="Asosiy ish joyi")
    course_type = models.CharField(max_length=300, blank=True, verbose_name="Yo'nalish/Kurs")
    reg_number = models.CharField(max_length=100, blank=True, verbose_name="Qayd raqami")
    series = models.CharField(max_length=20, blank=True, verbose_name="Seriya")
    number = models.CharField(max_length=50, verbose_name="Hujjat raqami")
    rating = models.CharField(max_length=50, blank=True, verbose_name="Reyting")
    duration = models.CharField(max_length=100, blank=True, verbose_name="O'qish muddati")
    issue_date = models.DateField(blank=True, null=True, verbose_name="Berilgan sana")
    is_verified = models.BooleanField(default=True, verbose_name="Tasdiqlangan")

    class Meta:
        verbose_name = "Tinglovchi"
        verbose_name_plural = "Tinglovchilar"
        ordering = ['-created_at']
        unique_together = ['series', 'number']

    def __str__(self):
        return f"{self.full_name} - {self.series} {self.number}"

    def save(self, *args, **kwargs):
        # Auto-set series based on record type if not provided
        if not self.series:
            self.series = 'MO' if self.record_type == 'certificate' else 'QT'
        super().save(*args, **kwargs)


class Certificate(BaseModel):
    """Sertifikatlar modeli (alohida bo'lim)"""
    CERTIFICATE_TYPE_CHOICES = [
        ('professional', 'Professional rivojlanish'),
        ('course_completion', 'Kurs tugallash'),
        ('award', 'Mukofot'),
        ('other', 'Boshqa'),
    ]

    certificate_type = models.CharField(
        max_length=30,
        choices=CERTIFICATE_TYPE_CHOICES,
        default='course_completion',
        verbose_name="Sertifikat turi"
    )
    title = models.CharField(max_length=500, verbose_name="Sertifikat nomi")
    holder_name = models.CharField(max_length=300, verbose_name="Egasi F.I.SH")
    holder_workplace = models.CharField(max_length=500, blank=True, verbose_name="Ish joyi")
    series = models.CharField(max_length=20, blank=True, verbose_name="Seriya")
    number = models.CharField(max_length=50, verbose_name="Raqam")
    issue_date = models.DateField(blank=True, null=True, verbose_name="Berilgan sana")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="Amal qilish muddati")
    issued_by = models.CharField(max_length=500, blank=True, verbose_name="Kim tomonidan berilgan")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    certificate_file = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Sertifikat fayli"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.holder_name}"


class Teacher(BaseModel):
    """O'qituvchilar modeli"""
    full_name = models.CharField(max_length=300, verbose_name="F.I.SH")
    position = models.CharField(max_length=200, verbose_name="Lavozimi")
    degree = models.CharField(max_length=200, blank=True, verbose_name="Ilmiy darajasi")
    title = models.CharField(max_length=200, blank=True, verbose_name="Unvoni")
    photo = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Rasm"
    )
    photo_url = models.URLField(blank=True, null=True, verbose_name="Rasm URL")
    bio = models.TextField(blank=True, verbose_name="Tarjimai hol")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"
        ordering = ['order', 'full_name']

    def __str__(self):
        return self.full_name

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return self.photo_url


class Personnel(BaseModel):
    """Xodimlar modeli"""
    CATEGORY_CHOICES = [
        ('leadership', 'Rahbariyat'),
        ('staff', 'Markaziy apparat'),
    ]

    full_name = models.CharField(max_length=300, verbose_name="F.I.SH")
    position = models.CharField(max_length=200, verbose_name="Lavozimi")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    reception_hours = models.CharField(max_length=200, blank=True, verbose_name="Qabul soatlari")
    photo = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Rasm"
    )
    photo_url = models.URLField(blank=True, null=True, verbose_name="Rasm URL")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='staff',
        verbose_name="Kategoriya"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class Course(BaseModel):
    """Kurslar modeli"""
    TYPE_CHOICES = [
        ('professional_development', 'Malaka oshirish'),
        ('retraining', 'Qayta tayyorlash'),
    ]

    title = models.CharField(max_length=500, verbose_name="Kurs nomi")
    course_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='professional_development',
        verbose_name="Kurs turi"
    )
    duration = models.CharField(max_length=100, blank=True, verbose_name="Davomiyligi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    requirements = models.TextField(blank=True, verbose_name="Talablar")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Narxi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class JournalIssue(BaseModel):
    """Ilmiy jurnal sonlari modeli"""
    title = models.CharField(max_length=500, verbose_name="Jurnal nomi/soni")
    year = models.CharField(max_length=10, verbose_name="Yil")
    issue_number = models.CharField(max_length=20, blank=True, verbose_name="Son raqami")
    pdf_file = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="PDF fayl"
    )
    pdf_url = models.URLField(blank=True, null=True, verbose_name="PDF URL")
    thumbnail = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Muqova rasmi"
    )
    thumbnail_url = models.URLField(blank=True, null=True, verbose_name="Muqova URL")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Jurnal soni"
        verbose_name_plural = "Jurnal sonlari"
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.year})"


class Document(BaseModel):
    """Hujjatlar modeli"""
    CATEGORY_CHOICES = [
        ('regulatory', "Me'yoriy hujjatlar"),
        ('plan', 'Ish rejalari'),
        ('open_data', "Ochiq ma'lumotlar"),
    ]

    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('doc', 'Word'),
        ('xls', 'Excel'),
        ('other', 'Boshqa'),
    ]

    title = models.CharField(max_length=500, verbose_name="Hujjat nomi")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='open_data',
        verbose_name="Kategoriya"
    )
    file_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='pdf',
        verbose_name="Fayl turi"
    )
    file = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Fayl"
    )
    file_url = models.URLField(blank=True, null=True, verbose_name="Fayl URL")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Hujjat"
        verbose_name_plural = "Hujjatlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Statistics(BaseModel):
    """Statistika modeli (faqat bitta yozuv bo'ladi)"""
    professors = models.PositiveIntegerField(default=0, verbose_name="Professorlar soni")
    dotsents = models.PositiveIntegerField(default=0, verbose_name="Dotsentlar soni")
    academics = models.PositiveIntegerField(default=0, verbose_name="Akademiklar soni")
    potential = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Ilmiy salohiyat (%)"
    )

    class Meta:
        verbose_name = "Statistika"
        verbose_name_plural = "Statistika"

    def __str__(self):
        return "Markaz Statistikasi"

    @classmethod
    def get_instance(cls):
        """Get or create the singleton Statistics instance."""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class YearlyStatistics(BaseModel):
    """Yillik statistika modeli"""
    year = models.CharField(max_length=10, unique=True, verbose_name="Yil")
    professional_development_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Malaka oshirish soni"
    )
    retraining_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Qayta tayyorlash soni"
    )

    class Meta:
        verbose_name = "Yillik statistika"
        verbose_name_plural = "Yillik statistikalar"
        ordering = ['-year']

    def __str__(self):
        return f"Statistika {self.year}"


class AppContent(BaseModel):
    """Sayt kontenti modeli (faqat bitta yozuv bo'ladi)"""
    history = models.TextField(blank=True, verbose_name="Markaz tarixi")
    structure = models.TextField(blank=True, verbose_name="Tuzilma haqida")
    structure_image = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Tuzilma rasmi"
    )
    structure_image_url = models.URLField(blank=True, null=True, verbose_name="Tuzilma rasm URL")
    student_notes = models.TextField(blank=True, verbose_name="Tinglovchilarga eslatma")
    contact_info = models.TextField(blank=True, verbose_name="Aloqa ma'lumotlari")
    address = models.TextField(blank=True, verbose_name="Manzil")

    class Meta:
        verbose_name = "Sayt kontenti"
        verbose_name_plural = "Sayt kontenti"

    def __str__(self):
        return "Sayt Kontenti"

    @classmethod
    def get_instance(cls):
        """Get or create the singleton AppContent instance."""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance
