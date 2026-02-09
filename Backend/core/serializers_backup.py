"""
DRF Serializers for the Educational Center Management System.
"""
from rest_framework import serializers
from .models import (
    News, GalleryItem, Listener, Certificate, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics, AppContent
)


class NewsSerializer(serializers.ModelSerializer):
    """Serializer for News model."""
    image_url_display = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image', 'image_url', 'image_url_display',
            'video_url', 'external_link', 'is_important', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url_display(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.image_url


class GalleryItemSerializer(serializers.ModelSerializer):
    """Serializer for GalleryItem model."""
    media_url_display = serializers.SerializerMethodField()

    class Meta:
        model = GalleryItem
        fields = [
            'id', 'image', 'url', 'media_type', 'media_url_display',
            'caption', 'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_media_url_display(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return obj.url


class ListenerSerializer(serializers.ModelSerializer):
    """Serializer for Listener (Student) model."""
    record_type_display = serializers.CharField(
        source='get_record_type_display',
        read_only=True
    )

    class Meta:
        model = Listener
        fields = [
            'id', 'record_type', 'record_type_display', 'full_name',
            'institution', 'workplace', 'course_type', 'reg_number',
            'series', 'number', 'rating', 'duration', 'issue_date',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListenerBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing listeners from Excel."""
    file = serializers.FileField()
    record_type = serializers.ChoiceField(choices=[
        ('certificate', 'Malaka oshirish (MO)'),
        ('diploma', 'Qayta tayyorlash (QT)'),
    ])


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for Certificate model."""
    certificate_type_display = serializers.CharField(
        source='get_certificate_type_display',
        read_only=True
    )

    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_type', 'certificate_type_display', 'title',
            'holder_name', 'holder_workplace', 'series', 'number',
            'issue_date', 'expiry_date', 'issued_by', 'description',
            'certificate_file', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CertificateBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing certificates from Excel."""
    file = serializers.FileField()
    certificate_type = serializers.ChoiceField(choices=[
        ('professional', 'Professional rivojlanish'),
        ('course_completion', 'Kurs tugallash'),
        ('award', 'Mukofot'),
        ('other', 'Boshqa'),
    ], default='course_completion')


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for Teacher model."""
    photo_url_display = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'position', 'degree', 'title',
            'photo', 'photo_url', 'photo_url_display', 'bio',
            'email', 'phone', 'order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url_display(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.photo_url


class PersonnelSerializer(serializers.ModelSerializer):
    """Serializer for Personnel model."""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    photo_url_display = serializers.SerializerMethodField()

    class Meta:
        model = Personnel
        fields = [
            'id', 'full_name', 'position', 'phone', 'reception_hours',
            'photo', 'photo_url', 'photo_url_display', 'category',
            'category_display', 'order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url_display(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.photo_url


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    course_type_display = serializers.CharField(
        source='get_course_type_display',
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'course_type', 'course_type_display',
            'duration', 'description', 'requirements', 'price',
            'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JournalIssueSerializer(serializers.ModelSerializer):
    """Serializer for JournalIssue model."""
    pdf_url_display = serializers.SerializerMethodField()
    thumbnail_url_display = serializers.SerializerMethodField()

    class Meta:
        model = JournalIssue
        fields = [
            'id', 'title', 'year', 'issue_number',
            'pdf_file', 'pdf_url', 'pdf_url_display',
            'thumbnail', 'thumbnail_url', 'thumbnail_url_display',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_pdf_url_display(self, obj):
        request = self.context.get('request')
        if obj.pdf_file:
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return obj.pdf_url

    def get_thumbnail_url_display(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return obj.thumbnail_url


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    file_url_display = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'category', 'category_display',
            'file_type', 'file', 'file_url', 'file_url_display',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url_display(self, obj):
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return obj.file_url


class YearlyStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for YearlyStatistics model."""

    class Meta:
        model = YearlyStatistics
        fields = [
            'id', 'year', 'professional_development_count',
            'retraining_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StatisticsSerializer(serializers.ModelSerializer):
    """Serializer for Statistics model."""
    yearly_data = serializers.SerializerMethodField()

    class Meta:
        model = Statistics
        fields = [
            'id', 'professors', 'dotsents', 'academics', 'potential',
            'yearly_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_yearly_data(self, obj):
        yearly_stats = YearlyStatistics.objects.all()
        return YearlyStatisticsSerializer(yearly_stats, many=True).data


class AppContentSerializer(serializers.ModelSerializer):
    """Serializer for AppContent model."""
    structure_image_url_display = serializers.SerializerMethodField()

    class Meta:
        model = AppContent
        fields = [
            'id', 'history', 'structure', 'structure_image',
            'structure_image_url', 'structure_image_url_display',
            'student_notes', 'contact_info', 'address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_structure_image_url_display(self, obj):
        request = self.context.get('request')
        if obj.structure_image:
            if request:
                return request.build_absolute_uri(obj.structure_image.url)
            return obj.structure_image.url
        return obj.structure_image_url


class AllDataSerializer(serializers.Serializer):
    """Serializer for returning all data at once (for initial load)."""
    news = NewsSerializer(many=True, read_only=True)
    gallery = GalleryItemSerializer(many=True, read_only=True)
    listeners = ListenerSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    teachers = TeacherSerializer(many=True, read_only=True)
    personnel = PersonnelSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    journal_issues = JournalIssueSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    statistics = StatisticsSerializer(read_only=True)
    app_content = AppContentSerializer(read_only=True)
