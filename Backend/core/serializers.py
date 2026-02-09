"""
DRF Serializers for the Educational Center Management System.
Cleaned up version without unnecessary URL fields.
"""
from rest_framework import serializers
from .models import (
    News, NewsImage, GalleryItem, GalleryImage, Listener, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics,
    AppContent, JournalSettings
)


class NewsImageSerializer(serializers.ModelSerializer):
    """Serializer for NewsImage model."""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsImage
        fields = ['id', 'image', 'image_url', 'order']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class NewsSerializer(serializers.ModelSerializer):
    """Serializer for News model with inline images."""
    images = NewsImageSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'images', 'image_url',
            'is_important', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        """Return first image URL for backwards compatibility."""
        request = self.context.get('request')
        first_image = obj.images.first()
        if first_image and first_image.image:
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


class NewsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating News with images."""

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'is_important', 'is_active']
        read_only_fields = ['id']


class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for GalleryImage model - individual gallery images."""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'image_url', 'order']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class GalleryItemSerializer(serializers.ModelSerializer):
    """Serializer for GalleryItem model - album with multiple images."""
    cover_image_url = serializers.SerializerMethodField()
    images = GalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = GalleryItem
        fields = [
            'id', 'title', 'cover_image', 'cover_image_url', 'images',
            'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None


class ListenerSerializer(serializers.ModelSerializer):
    """Serializer for Listener model with MO/QT types."""
    record_type_display = serializers.CharField(
        source='get_record_type_display',
        read_only=True
    )

    class Meta:
        model = Listener
        fields = [
            'id', 'record_type', 'record_type_display', 'full_name',
            'workplace', 'course_type', 'series', 'number', 'duration',
            'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListenerBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing listeners from Excel."""
    file = serializers.FileField()
    record_type = serializers.ChoiceField(choices=[
        ('MO', 'Malaka oshirish (MO)'),
        ('QT', 'Qayta tayyorlash (QT)'),
    ])


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for Teacher model - simplified."""
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'position', 'degree', 'title',
            'photo', 'photo_url', 'order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class PersonnelSerializer(serializers.ModelSerializer):
    """Serializer for Personnel model."""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Personnel
        fields = [
            'id', 'full_name', 'position', 'phone', 'reception_hours',
            'photo', 'photo_url', 'category', 'category_display',
            'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo:
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


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
            'duration', 'description', 'is_active', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JournalIssueSerializer(serializers.ModelSerializer):
    """Serializer for JournalIssue model - simplified."""
    pdf_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = JournalIssue
        fields = [
            'id', 'year', 'issue_number',
            'pdf_file', 'pdf_url', 'thumbnail', 'thumbnail_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.pdf_file:
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model - simplified."""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'category', 'category_display',
            'file', 'file_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


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


class AllDataSerializer(serializers.Serializer):
    """Serializer for returning all data at once (for initial load)."""
    news = NewsSerializer(many=True, read_only=True)
    gallery = GalleryItemSerializer(many=True, read_only=True)
    listeners = ListenerSerializer(many=True, read_only=True)
    teachers = TeacherSerializer(many=True, read_only=True)
    personnel = PersonnelSerializer(many=True, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    journal_issues = JournalIssueSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    statistics = StatisticsSerializer(read_only=True)


class AppContentSerializer(serializers.ModelSerializer):
    """Serializer for AppContent singleton model."""
    structure_image_url = serializers.SerializerMethodField()

    class Meta:
        model = AppContent
        fields = [
            'id', 'history', 'structure', 'structure_image', 'structure_image_url',
            'student_notes', 'contact_info', 'address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_structure_image_url(self, obj):
        request = self.context.get('request')
        if obj.structure_image:
            if request:
                return request.build_absolute_uri(obj.structure_image.url)
            return obj.structure_image.url
        return None


class JournalSettingsSerializer(serializers.ModelSerializer):
    """Serializer for JournalSettings singleton model."""
    article_rules_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = JournalSettings
        fields = [
            'id', 'article_rules_text', 'article_rules_pdf', 'article_rules_pdf_url',
            'about_journal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_article_rules_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.article_rules_pdf:
            if request:
                return request.build_absolute_uri(obj.article_rules_pdf.url)
            return obj.article_rules_pdf.url
        return None
