"""
Django Admin Configuration for the Educational Center Management System.
Cleaned up version with improved Excel import.
"""
import pandas as pd
from io import BytesIO

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse

from .models import (
    News, NewsImage, GalleryItem, GalleryImage, Listener, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics,
    AppContent, JournalSettings, InternationalRelation, ForeignPartner,
    CollaborationProject, InternationalPhoto, InternationalVideo, StudentTrainingRecord,
    ArtGalleryItem, ArtGalleryImage
)


# Custom Admin Site Configuration
admin.site.site_header = "Markaz Boshqaruv Paneli"
admin.site.site_title = "Markaz Admin"
admin.site.index_title = "Boshqaruv Paneli"


class ExcelImportForm(forms.Form):
    """Form for Excel file import."""
    excel_file = forms.FileField(
        label="Excel fayl (.xlsx yoki .csv)",
        help_text="Yuklanadigan Excel faylni tanlang"
    )


class ListenerRecordTypeFilter(SimpleListFilter):
    """Filter listeners by record type (MO/QT)."""
    title = 'Sertifikat turi'
    parameter_name = 'record_type'

    def lookups(self, request, model_admin):
        return [
            ('MO', 'Malaka oshirish (MO)'),
            ('QT', 'Qayta tayyorlash (QT)'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(record_type=self.value())
        return queryset


class NewsImageInline(admin.TabularInline):
    """Inline admin for News images."""
    model = NewsImage
    extra = 3
    fields = ['image', 'order']
    ordering = ['order']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Admin configuration for News model with inline images."""
    list_display = ['title', 'created_at', 'is_important', 'is_active', 'image_count']
    list_filter = ['is_important', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_important', 'is_active']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [NewsImageInline]

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'content')
        }),
        ('Sozlamalar', {
            'fields': ('is_important', 'is_active')
        }),
    )

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Rasmlar soni'


class GalleryImageInline(admin.TabularInline):
    """Inline for gallery images."""
    model = GalleryImage
    extra = 3
    fields = ['image', 'order']
    ordering = ['order']


class InternationalPhotoInline(admin.TabularInline):
    model = InternationalPhoto
    extra = 3
    fields = ['image', 'order', 'is_active']
    ordering = ['order']


class InternationalVideoInline(admin.TabularInline):
    model = InternationalVideo
    extra = 2
    fields = ['title', 'video_url', 'order', 'is_active']
    ordering = ['order']


class ArtGalleryImageInline(admin.TabularInline):
    model = ArtGalleryImage
    extra = 3
    fields = ['image', 'order']
    ordering = ['order']


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    """Admin configuration for GalleryItem model - album with multiple images."""
    list_display = ['__str__', 'title', 'order', 'is_active', 'image_count', 'created_at']
    list_filter = ['is_active'] 
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    inlines = [GalleryImageInline]

    fieldsets = (
        ('Albom ma\'lumotlari', {
            'fields': ('title', 'cover_image')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Rasmlar soni'


@admin.register(Listener)
class ListenerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Listener model with bulk import.
    Supports both MO (Malaka oshirish) and QT (Qayta tayyorlash) types.
    """
    list_display = ['full_name', 'get_series_display', 'number', 'get_record_type_display', 'workplace', 'is_verified']
    list_filter = [ListenerRecordTypeFilter, 'is_verified', 'created_at']
    search_fields = ['full_name', 'number', 'workplace', 'series', 'course_type', 'record_type']
    list_editable = ['is_verified']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Sertifikat turi', {
            'fields': ('record_type',),
            'description': 'MO = Malaka oshirish, QT = Qayta tayyorlash'
        }),
        ('Sertifikat ma\'lumotlari', {
            'fields': ('number',)
        }),
        ('Tinglovchi ma\'lumotlari', {
            'fields': ('full_name', 'workplace', 'course_type')
        }),
        ('Qo\'shimcha', {
            'fields': ('duration', 'is_verified')
        }),
    )

    change_list_template = "admin/listener_change_list.html"

    def get_series_display(self, obj):
        return obj.series or obj.record_type or 'MO'
    get_series_display.short_description = 'Seriya'
    get_series_display.admin_order_field = 'series'

    def get_record_type_display(self, obj):
        if obj.record_type == 'QT':
            return 'Qayta tayyorlash (QT)'
        return 'Malaka oshirish (MO)'
    get_record_type_display.short_description = 'Sertifikat turi'
    get_record_type_display.admin_order_field = 'record_type'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='listener_import_excel'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='listener_export_excel'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='listener_download_template'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        """Handle Excel file import for listeners with MO/QT types."""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                raw_type = request.POST.get('record_type', 'MO')
                mapping = {
                    'MO': 'MO',
                    'QT': 'QT',
                    'CERTIFICATE': 'MO',
                    'DIPLOMA': 'QT',
                }
                record_type = mapping.get(str(raw_type).strip().upper(), 'MO')

                try:
                    # Read all columns as strings to preserve leading zeros
                    df = pd.read_excel(BytesIO(excel_file.read()), dtype=str)
                    
                    found_columns = list(df.columns)
                    print(f"Excel ustunlari: {found_columns}")

                    # Flexible column mapping - supports both MO and QT formats
                    column_mapping = {
                        'full_name': ['Tinglovchi', 'F.I.SH', 'FIO', 'Ism', 'Ismi', 'F.I.O', 'Familiya'],
                        'workplace': ['Asosiy ish joyi', 'Ish joyi', 'Lavozimi', 'Tashkilot', 'Muassasa', 
                                      'Ta\'lim muassasasi', 'Qayta tayyorlagan muassasa'],
                        'course_type': ['Kursi', 'Kurs', 'Yo\'nalishi', 'Yo\'nalish', 
                                       'Qayta tayyorlash kursi', 'Kurs nomi'],
                        'series': ['Seriyasi', 'Seriya', 'Sertifikat seriyasi', 'Diplom seriyasi'],
                        'number': ['Raqami', 'Raqam', '№', 'Sertifikat raqami', 'Diplom raqami'],
                        'duration': ["O'qish muddati (davri)", "O'qish muddati", 'Muddat', 'Davri', 
                                    'Kurs davri', 'Boshlanish - tugash'],
                    }

                    # Find matching columns (case-insensitive with partial match)
                    def find_column(possible_names, df_columns):
                        df_columns_lower = {col.lower().strip(): col for col in df_columns}
                        for name in possible_names:
                            name_lower = name.lower().strip()
                            if name_lower in df_columns_lower:
                                return df_columns_lower[name_lower]
                            # Partial match
                            for col_lower, col_orig in df_columns_lower.items():
                                if name_lower in col_lower or col_lower in name_lower:
                                    return col_orig
                        return None

                    # Build actual column mapping
                    actual_mapping = {}
                    for model_field, possible_names in column_mapping.items():
                        found_col = find_column(possible_names, df.columns)
                        if found_col:
                            actual_mapping[found_col] = model_field
                            print(f"Topildi: '{found_col}' -> {model_field}")
                    
                    print(f"Topilgan ustunlar: {actual_mapping}")

                    created_count = 0
                    updated_count = 0
                    skipped_count = 0

                    with transaction.atomic():
                        for idx, row in df.iterrows():
                            listener_data = {'record_type': record_type}

                            for excel_col, model_field in actual_mapping.items():
                                value = row[excel_col]
                                if pd.notna(value):
                                    listener_data[model_field] = str(value).strip()

                            # Skip if no name found
                            if not listener_data.get('full_name'):
                                skipped_count += 1
                                continue

                            # Auto-generate number if missing
                            if not listener_data.get('number'):
                                listener_data['number'] = str(idx + 1).zfill(6)

                            # Auto-set series if missing
                            if not listener_data.get('series'):
                                listener_data['series'] = record_type

                            # Check for existing record
                            existing = Listener.objects.filter(
                                series=listener_data.get('series', record_type),
                                number=listener_data['number']
                            ).first()

                            if existing:
                                for key, value in listener_data.items():
                                    setattr(existing, key, value)
                                existing.save()
                                updated_count += 1
                            else:
                                Listener.objects.create(**listener_data)
                                created_count += 1

                    msg = f"Muvaffaqiyat! {created_count} ta yangi qo'shildi, {updated_count} ta yangilandi."
                    if skipped_count > 0:
                        msg += f" {skipped_count} ta qator o'tkazib yuborildi (ism topilmadi)."
                    
                    messages.success(request, msg)
                    return redirect('..')

                except Exception as e:
                    messages.error(request, f"Xatolik: {str(e)}")

        form = ExcelImportForm()
        context = {
            'form': form,
            'title': 'Tinglovchilarni Excel fayldan import qilish',
            'opts': self.model._meta,
        }
        return render(request, 'admin/excel_import.html', context)

    def export_excel(self, request):
        """Export listeners to Excel file."""
        record_type = request.GET.get('record_type', None)
        queryset = Listener.objects.all()
        if record_type:
            queryset = queryset.filter(record_type=record_type)

        data = []
        for listener in queryset:
            data.append({
                'F.I.SH': listener.full_name,
                'Ish joyi': listener.workplace,
                'Yo\'nalish': listener.course_type,
                'Seriya': listener.series,
                'Raqam': listener.number,
                "O'qish muddati (davri)": listener.duration,
                'Turi': listener.get_record_type_display(),
            })

        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"tinglovchilar_{record_type or 'all'}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response

    def download_template(self, request):
        """Download Excel template for import."""
        record_type = request.GET.get('record_type', 'MO')

        if record_type == 'QT':
            columns = [
                'Tinglovchi', 'Asosiy ish joyi', 'Qayta tayyorlash kursi',
                'Seriyasi', 'Raqami', "O'qish muddati (davri)"
            ]
            filename = 'qayta_tayyorlash_template.xlsx'
        else:
            columns = [
                'Tinglovchi', 'Asosiy ish joyi', 'Kursi',
                'Seriyasi', 'Raqami', "O'qish muddati (davri)"
            ]
            filename = 'malaka_oshirish_template.xlsx'

        df = pd.DataFrame(columns=columns)
        # Add sample row
        sample = {
            columns[0]: 'Ism Familiya',
            columns[1]: 'Maktab nomi',
            columns[2]: 'Kurs nomi',
            columns[3]: record_type,
            columns[4]: '000001',
            columns[5]: '01.01.2024 - 01.03.2024',
        }
        df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Admin configuration for Teacher model - simplified."""
    list_display = ['full_name', 'position', 'degree', 'title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['full_name', 'position', 'degree']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'full_name']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('full_name', 'position', 'degree', 'title')
        }),
        ('Rasm', {
            'fields': ('photo',)
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )    


@admin.register(StudentTrainingRecord)
class StudentTrainingRecordAdmin(admin.ModelAdmin):
    """Admin for students page records with Excel import."""
    list_display = ['full_name', 'workplace', 'course_name', 'training_time', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'workplace', 'course_name', 'training_time']
    list_editable = ['is_active']
    ordering = ['-created_at']
    change_list_template = "admin/student_training_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='student_training_import_excel'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='student_training_download_template'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                try:
                    if excel_file.name.lower().endswith('.csv'):
                        df = pd.read_csv(BytesIO(excel_file.read()), dtype=str)
                    else:
                        df = pd.read_excel(BytesIO(excel_file.read()), dtype=str)

                    column_mapping = {
                        'full_name': ['F.I.SH', 'FIO', 'F.I.O', 'Tinglovchi', 'Ism familiya'],
                        'workplace': ['Asosiy ish joyi', 'Ish joyi', 'Tashkilot', 'Muassasa'],
                        'course_name': ['Malaka oshirish yo\'nalishi', 'Malaka oshirish yonalishi', 'Yo\'nalish', 'Kurs', 'Kursi'],
                        'training_time': ['Malaka oshirish vaqti', 'O\'qish muddati', 'Muddat', 'Vaqt', 'Oy'],
                    }

                    def find_column(possible_names, columns):
                        columns_lower = {c.lower().strip(): c for c in columns}
                        for name in possible_names:
                            key = name.lower().strip()
                            if key in columns_lower:
                                return columns_lower[key]
                            for col_key, col_orig in columns_lower.items():
                                if key in col_key or col_key in key:
                                    return col_orig
                        return None

                    actual_mapping = {}
                    for model_field, candidates in column_mapping.items():
                        found = find_column(candidates, df.columns)
                        if found:
                            actual_mapping[found] = model_field

                    if not any(v == 'full_name' for v in actual_mapping.values()):
                        messages.error(request, "Excel faylda 'F.I.SH' ustuni topilmadi.")
                        return redirect('..')

                    created_count = 0
                    updated_count = 0
                    skipped_count = 0

                    with transaction.atomic():
                        for _, row in df.iterrows():
                            data = {}
                            for excel_col, model_field in actual_mapping.items():
                                val = row.get(excel_col)
                                if pd.notna(val):
                                    data[model_field] = str(val).strip()

                            full_name = data.get('full_name', '')
                            if not full_name:
                                skipped_count += 1
                                continue

                            obj, created = StudentTrainingRecord.objects.update_or_create(
                                full_name=full_name,
                                workplace=data.get('workplace', ''),
                                course_name=data.get('course_name', ''),
                                defaults={
                                    'training_time': data.get('training_time', ''),
                                    'is_active': True,
                                }
                            )
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1

                    messages.success(
                        request,
                        f"Muvaffaqiyatli import qilindi: {created_count} ta yangi, {updated_count} ta yangilandi, {skipped_count} ta o'tkazib yuborildi."
                    )
                    return redirect('..')
                except Exception as exc:
                    messages.error(request, f"Import xatoligi: {exc}")

        form = ExcelImportForm()
        context = {
            'form': form,
            'title': 'Tinglovchilar yozuvlarini Excel dan import qilish',
            'opts': self.model._meta,
        }
        return render(request, 'admin/student_excel_import.html', context)

    def download_template(self, request):
        df = pd.DataFrame([{
            'F.I.SH': 'Barakayev Ixtiyor Qaxramonovich',
            'Asosiy ish joyi': "Buxoro ixtisoslashgan san'at maktab-internati",
            "Malaka oshirish yo'nalishi": "Tasviriy san'at (turlari bo'yicha)",
            'Malaka oshirish vaqti': 'Yanvar',
        }])
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="tinglovchilar_namuna.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    """Admin configuration for Personnel model."""
    list_display = ['full_name', 'position', 'category', 'phone', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['full_name', 'position']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'full_name']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('full_name', 'position', 'category')
        }),
        ('Aloqa', {
            'fields': ('phone', 'reception_hours')
        }),
        ('Rasm va sozlamalar', {
            'fields': ('photo', 'order', 'is_active')
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    list_display = ['title', 'course_type', 'duration', 'order', 'is_active']
    list_filter = ['course_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'title']


@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    """Admin configuration for JournalIssue model - simplified."""
    list_display = ['__str__', 'year', 'issue_number', 'is_active']
    list_filter = ['year', 'is_active']
    search_fields = ['year', 'issue_number']
    ordering = ['-year', '-created_at']

    fieldsets = (
        ('Jurnal ma\'lumotlari', {
            'fields': ('year', 'issue_number')
        }),
        ('Fayllar', {
            'fields': ('pdf_file', 'thumbnail')
        }),
        ('Sozlamalar', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model - simplified."""
    list_display = ['title', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title']
    ordering = ['-created_at']

    fieldsets = (
        ('Hujjat', {
            'fields': ('title', 'category', 'file')
        }),
        ('Sozlamalar', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    """Admin configuration for Statistics singleton model."""
    list_display = ['__str__', 'professors', 'dotsents', 'academics', 'potential']

    def has_add_permission(self, request):
        # Only allow one instance
        return not Statistics.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(YearlyStatistics)
class YearlyStatisticsAdmin(admin.ModelAdmin):
    """Admin configuration for YearlyStatistics model."""
    list_display = ['year', 'professional_development_count', 'retraining_count']
    ordering = ['-year']


@admin.register(AppContent)
class AppContentAdmin(admin.ModelAdmin):
    """Admin configuration for AppContent (Markaz haqida) singleton model."""
    list_display = ['__str__', 'updated_at']

    fieldsets = (
        ('Umumiy ma\'lumot', {
            'fields': ('history',)
        }),
        ('Markaz tuzilmasi', {
            'fields': ('structure', 'structure_image'),
            'description': 'Tuzilma rasmi (download qilish uchun)'
        }),
        ('Tinglovchilar uchun', {
            'fields': ('student_notes',)
        }),
        ('Aloqa', {
            'fields': ('contact_info', 'address')
        }),
    )

    def has_add_permission(self, request):
        return not AppContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InternationalRelation)
class InternationalRelationAdmin(admin.ModelAdmin):
    """Admin configuration for InternationalRelation singleton model."""
    list_display = ['title', 'updated_at']
    inlines = [InternationalPhotoInline, InternationalVideoInline]

    fieldsets = (
        ("Xalqaro aloqalar to'g'risida", {
            'fields': ('title', 'description')
        }),
    )

    def has_add_permission(self, request):
        return not InternationalRelation.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ForeignPartner)
class ForeignPartnerAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'country', 'order', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['organization_name', 'country', 'short_info']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'organization_name']

    fieldsets = (
        ("Xorijiy hamkor", {
            'fields': ('organization_name', 'country', 'short_info', 'image')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(CollaborationProject)
class CollaborationProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'status', 'order', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['status', 'order', 'is_active']
    ordering = ['-date', 'order']

    fieldsets = (
        ('Loyiha ma\'lumotlari', {
            'fields': ('name', 'description', 'date', 'status')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(ArtGalleryItem)
class ArtGalleryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'author_full_name', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'author_full_name', 'text']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    inlines = [ArtGalleryImageInline]

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('image', 'name', 'author_full_name', 'text')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(JournalSettings)
class JournalSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for JournalSettings (Jurnal sozlamalari) singleton model."""
    list_display = ['__str__', 'updated_at']

    fieldsets = (
        ('Maqola berish tartibi', {
            'fields': ('article_rules_text', 'article_rules_pdf'),
            'description': 'PDF faylni yuklash mumkin (download qilish uchun)'
        }),
        ('Jurnal haqida', {
            'fields': ('about_journal',)
        }),
    )

    def has_add_permission(self, request):
        return not JournalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
