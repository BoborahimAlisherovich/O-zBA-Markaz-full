"""
Models for the Educational Center Management System.
Simplified and cleaned up version.
"""
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
    is_important = models.BooleanField(default=False, verbose_name="Muhim")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NewsImage(BaseModel):
    """Yangilik rasmlari (inline)"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images', verbose_name="Yangilik")
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Rasm"
        verbose_name_plural = "Rasmlar"
        ordering = ['order']

    def __str__(self):
        return f"Rasm #{self.order} - {self.news.title[:30]}"


class GalleryItem(BaseModel):
    """Galereya modeli (albom - bir nechta rasm bilan)"""
    title = models.CharField(max_length=200, verbose_name="Sarlavha", blank=True, default="")
    cover_image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Muqova rasmi")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Galereya albomi"
        verbose_name_plural = "Galereya"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Albom #{self.pk}"


class GalleryImage(BaseModel):
    """Galereya ichidagi rasmlar"""
    gallery = models.ForeignKey(GalleryItem, on_delete=models.CASCADE, related_name='images', verbose_name="Galereya")
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Galereya rasmi"
        verbose_name_plural = "Galereya rasmlari"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Rasm #{self.order} - {self.gallery}"


class Listener(BaseModel):
    """Tinglovchilar (Sertifikat egasi) modeli - MO va QT"""
    RECORD_TYPE_CHOICES = [
        ('MO', 'Malaka oshirish (MO)'),
        ('QT', 'Qayta tayyorlash (QT)'),
    ]

    record_type = models.CharField(
        max_length=5,
        choices=RECORD_TYPE_CHOICES,
        default='MO',
        verbose_name="Sertifikat turi"
    )
    full_name = models.CharField(max_length=300, verbose_name="F.I.SH")
    workplace = models.CharField(max_length=500, blank=True, verbose_name="Ish joyi")
    course_type = models.CharField(max_length=300, blank=True, verbose_name="Yo'nalish")
    series = models.CharField(max_length=20, verbose_name="Seriya")
    number = models.CharField(max_length=50, verbose_name="Raqam")
    duration = models.CharField(max_length=200, blank=True, verbose_name="O'qish muddati (davri)")
    is_verified = models.BooleanField(default=True, verbose_name="Tasdiqlangan")

    class Meta:
        verbose_name = "Tinglovchi"
        verbose_name_plural = "Tinglovchilar (Sertifikatlar)"
        ordering = ['-created_at']
        unique_together = ['series', 'number']

    def __str__(self):
        return f"{self.full_name} - {self.series} {self.number}"

    def save(self, *args, **kwargs):
        # Ensure record_type is uppercase and valid
        if self.record_type:
            self.record_type = self.record_type.upper()
        if self.record_type not in ['MO', 'QT']:
            self.record_type = 'MO'
        
        # ALWAYS set series from record_type for consistent search
        self.series = self.record_type
        
        super().save(*args, **kwargs)


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
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"
        ordering = ['order', 'full_name']

    def __str__(self):
        return self.full_name


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
    year = models.CharField(max_length=10, verbose_name="Yil")
    issue_number = models.CharField(max_length=20, blank=True, verbose_name="Son raqami")
    pdf_file = models.FileField(
        upload_to=generate_unique_filename,
        verbose_name="PDF fayl"
    )
    thumbnail = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Muqova rasmi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Jurnal soni"
        verbose_name_plural = "Jurnal sonlari"
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"Jurnal {self.year} #{self.issue_number}"


class Document(BaseModel):
    """Hujjatlar modeli"""
    CATEGORY_CHOICES = [
        ('regulatory', "Me'yoriy hujjatlar"),
        ('plan', 'Ish rejalari'),
        ('open_data', "Ochiq ma'lumotlar"),
    ]

    title = models.CharField(max_length=500, verbose_name="Hujjat nomi")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='open_data',
        verbose_name="Kategoriya"
    )
    file = models.FileField(
        upload_to=generate_unique_filename,
        verbose_name="Fayl"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Hujjat"
        verbose_name_plural = "Hujjatlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class InternationalRelation(BaseModel):
    """Xalqaro aloqalar sahifasi uchun asosiy ma'lumotlar (singleton)."""
    title = models.CharField(
        max_length=255,
        default="Xalqaro aloqalar to'g'risida",
        verbose_name="Sarlavha"
    )
    description = models.TextField(blank=True, verbose_name="Tavsif")

    class Meta:
        verbose_name = "Xalqaro aloqalar"
        verbose_name_plural = "Xalqaro aloqalar"

    def __str__(self):
        return self.title

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class ForeignPartner(BaseModel):
    """Xorijiy hamkor tashkilotlar modeli."""
    organization_name = models.CharField(max_length=255, verbose_name="Tashkilot nomi")
    country = models.CharField(max_length=150, verbose_name="Mamlakat")
    short_info = models.TextField(verbose_name="Qisqacha ma'lumot")
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Xorijiy hamkor"
        verbose_name_plural = "Xorijiy hamkorlar"
        ordering = ['order', 'organization_name']

    def __str__(self):
        return self.organization_name


class CollaborationProject(BaseModel):
    """Hamkorlikda amalga oshirilgan loyihalar."""
    STATUS_PLANNED = 'planned'
    STATUS_ONGOING = 'ongoing'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Rejalashtirilmoqda'),
        (STATUS_ONGOING, 'Davom etmoqda'),
        (STATUS_COMPLETED, 'Yakunlangan'),
    ]

    name = models.CharField(max_length=255, verbose_name="Loyiha nomi")
    description = models.TextField(verbose_name="Tavsif")
    date = models.DateField(verbose_name="Sana")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
        verbose_name="Holati"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Hamkorlik loyihasi"
        verbose_name_plural = "Hamkorlik loyihalari"
        ordering = ['-date', 'order']

    def __str__(self):
        return self.name


class InternationalPhoto(BaseModel):
    """Xalqaro aloqalar fotosuratlari (inline)."""
    international_relation = models.ForeignKey(
        InternationalRelation,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Xalqaro aloqalar"
    )
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Fotosurat"
        verbose_name_plural = "Fotosuratlar"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Fotosurat #{self.order}"


class InternationalVideo(BaseModel):
    """Xalqaro aloqalar video to'plami (inline)."""
    international_relation = models.ForeignKey(
        InternationalRelation,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="Xalqaro aloqalar"
    )
    title = models.CharField(max_length=255, blank=True, verbose_name="Sarlavha")
    video_url = models.URLField(verbose_name="Video havola")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Video to'plami"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Video #{self.order}"


class ArtGalleryItem(BaseModel):
    """Bosh sahifadagi Art Galereya kartasi."""
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    name = models.CharField(max_length=255, verbose_name="Nomi")
    author_full_name = models.CharField(max_length=255, verbose_name="Ism familiya")
    text = models.TextField(verbose_name="Matn")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Art galereya elementi"
        verbose_name_plural = "Art galereya"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class ArtGalleryImage(BaseModel):
    """Art galereya elementining qo'shimcha rasmlari (inline)."""
    art_item = models.ForeignKey(
        ArtGalleryItem,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Art galereya elementi"
    )
    image = models.ImageField(upload_to=generate_unique_filename, verbose_name="Rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Art galereya rasmi"
        verbose_name_plural = "Art galereya rasmlari"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.art_item.name} - {self.order}"


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
    """Markaz haqida ma'lumotlar (singleton model)"""
    # Umumiy ma'lumot
    history = models.TextField(blank=True, verbose_name="Umumiy ma'lumot")
    
    # Markaz tuzilmasi
    structure = models.TextField(blank=True, verbose_name="Tuzilma haqida matn")
    structure_image = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Tuzilma rasmi"
    )
    
    # Tinglovchilar uchun eslatmalar
    student_notes = models.TextField(blank=True, verbose_name="Tinglovchilar uchun eslatma")
    
    # Aloqa ma'lumotlari
    contact_info = models.TextField(blank=True, verbose_name="Aloqa ma'lumotlari")
    address = models.TextField(blank=True, verbose_name="Manzil")

    class Meta:
        verbose_name = "Markaz haqida"
        verbose_name_plural = "Markaz haqida"

    def __str__(self):
        return "Markaz haqida ma'lumotlar"

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(pk=1)
        return instance


class JournalSettings(BaseModel):
    """Ilmiy jurnal sozlamalari (singleton model)"""
    # Maqola berish tartibi
    article_rules_text = models.TextField(blank=True, verbose_name="Maqola berish tartibi matni")
    article_rules_pdf = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        verbose_name="Maqola berish tartibi (PDF)"
    )
    
    # Jurnal haqida
    about_journal = models.TextField(blank=True, verbose_name="Jurnal haqida")

    class Meta:
        verbose_name = "Jurnal sozlamalari"
        verbose_name_plural = "Jurnal sozlamalari"

    def __str__(self):
        return "Ilmiy jurnal sozlamalari"

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(pk=1)
        return instance
