"""
Django Admin Configuration for the Educational Center Management System.
Features advanced admin interface with bulk import functionality.
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
    News, GalleryItem, Listener, Certificate, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics, AppContent
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
    """Filter listeners by record type."""
    title = 'Hujjat turi'
    parameter_name = 'record_type'

    def lookups(self, request, model_admin):
        return [
            ('certificate', 'Malaka oshirish (MO)'),
            ('diploma', 'Qayta tayyorlash (QT)'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(record_type=self.value())
        return queryset


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Admin configuration for News model."""
    list_display = ['title', 'created_at', 'is_important', 'is_active']
    list_filter = ['is_important', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_important', 'is_active']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'content')
        }),
        ('Media', {
            'fields': ('image', 'image_url', 'video_url', 'external_link')
        }),
        ('Sozlamalar', {
            'fields': ('is_important', 'is_active')
        }),
    )


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    """Admin configuration for GalleryItem model with image upload."""
    list_display = ['caption', 'media_type', 'order', 'is_active', 'created_at']
    list_filter = ['media_type', 'is_active']
    search_fields = ['caption']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Media', {
            'fields': ('image', 'url', 'media_type'),
            'description': 'Rasmni yuklang YOKI tashqi URL kiriting.'
        }),
        ('Tavsif', {
            'fields': ('caption', 'order', 'is_active')
        }),
    )


@admin.register(Listener)
class ListenerAdmin(admin.ModelAdmin):
    """
    Admin configuration for Listener (Student) model with bulk import.
    """
    list_display = ['full_name', 'series', 'number', 'record_type', 'workplace', 'is_verified']
    list_filter = [ListenerRecordTypeFilter, 'is_verified', 'created_at']
    search_fields = ['full_name', 'number', 'workplace', 'institution']
    list_editable = ['is_verified']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Hujjat ma\'lumotlari', {
            'fields': ('record_type', 'series', 'number', 'reg_number')
        }),
        ('Tinglovchi ma\'lumotlari', {
            'fields': ('full_name', 'institution', 'workplace', 'course_type')
        }),
        ('Qo\'shimcha', {
            'fields': ('rating', 'duration', 'issue_date', 'is_verified')
        }),
    )

    change_list_template = "admin/listener_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='listener_import_excel'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='listener_export_excel'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='listener_download_template'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        """Handle Excel file import for listeners."""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                record_type = request.POST.get('record_type', 'certificate')

                try:
                    df = pd.read_excel(BytesIO(excel_file.read()))
                    
                    # Debug: show found columns
                    found_columns = list(df.columns)
                    print(f"Excel ustunlari: {found_columns}")

                    # Flexible column mapping - try multiple possible names
                    if record_type == 'diploma':
                        column_mapping = {
                            'full_name': ['Tinglovchi', 'F.I.SH', 'FIO', 'Ism', 'Ismi', 'F.I.O', 'Familiya'],
                            'institution': ['Qayta tayyorlagan muassasa', 'Muassasa', 'Ta\'lim muassasasi', 'Tashkilot'],
                            'workplace': ['Asosiy ish joyi', 'Ish joyi', 'Lavozimi', 'Tashkilot'],
                            'course_type': ['Qayta tayyorlash kursi', 'Kurs', 'Kursi', 'Yo\'nalishi', 'Yo\'nalish'],
                            'reg_number': ['Qayd raqami', 'Qayd №', 'Ro\'yxat raqami', 'Reg raqami'],
                            'series': ['Diplom seriyasi', 'Seriyasi', 'Seriya', 'Sertifikat seriyasi'],
                            'number': ['Raqami', 'Raqam', '№', 'Diplom raqami', 'Sertifikat raqami'],
                            'rating': ['Reyting', 'Baho', 'Ball'],
                            'duration': ["O'qish muddati (davri)", 'Muddat', 'Davri', "O'qish muddati"],
                        }
                        default_series = 'QT'
                    else:
                        column_mapping = {
                            'full_name': ['Tinglovchi', 'F.I.SH', 'FIO', 'Ism', 'Ismi', 'F.I.O', 'Familiya'],
                            'institution': ['Muassasa', 'Ta\'lim muassasasi', 'Tashkilot', 'Qayta tayyorlagan muassasa'],
                            'workplace': ['Asosiy ish joyi', 'Ish joyi', 'Lavozimi', 'Tashkilot'],
                            'course_type': ['Kursi', 'Kurs', 'Yo\'nalishi', 'Yo\'nalish'],
                            'reg_number': ['Qayd raqami', 'Qayd №', 'Ro\'yxat raqami', 'Reg raqami'],
                            'series': ['Seriyasi', 'Seriya', 'Sertifikat seriyasi'],
                            'number': ['Raqami', 'Raqam', '№', 'Sertifikat raqami'],
                            'rating': ['Reyting', 'Baho', 'Ball'],
                            'duration': ["O'qish muddati (davri)", 'Muddat', 'Davri', "O'qish muddati"],
                        }
                        default_series = 'MO'

                    # Find matching columns (case-insensitive)
                    def find_column(possible_names, df_columns):
                        df_columns_lower = {col.lower().strip(): col for col in df_columns}
                        for name in possible_names:
                            name_lower = name.lower().strip()
                            if name_lower in df_columns_lower:
                                return df_columns_lower[name_lower]
                            # Also try partial match
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

                            # Generate number if missing
                            if not listener_data.get('number'):
                                listener_data['number'] = str(idx + 1).zfill(6)

                            if not listener_data.get('series'):
                                listener_data['series'] = default_series

                            existing = Listener.objects.filter(
                                series=listener_data.get('series', default_series),
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
                    msg += f" Excel ustunlari: {', '.join(found_columns)}"
                    
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
                'Muassasa': listener.institution,
                'Ish joyi': listener.workplace,
                'Kurs': listener.course_type,
                'Qayd raqami': listener.reg_number,
                'Seriya': listener.series,
                'Raqam': listener.number,
                'Reyting': listener.rating,
                'Muddat': listener.duration,
                'Turi': listener.get_record_type_display(),
            })

        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="tinglovchilar.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response

    def download_template(self, request):
        """Download Excel template for import."""
        record_type = request.GET.get('record_type', 'certificate')

        if record_type == 'diploma':
            columns = [
                'Tinglovchi', 'Qayta tayyorlagan muassasa', 'Asosiy ish joyi',
                'Qayta tayyorlash kursi', 'Qayd raqami', 'Diplom seriyasi',
                'Raqami', 'Reyting', "O'qish muddati (davri)"
            ]
            filename = 'diplom_template.xlsx'
        else:
            columns = [
                'Tinglovchi', 'Muassasa', 'Asosiy ish joyi', 'Kursi',
                'Qayd raqami', 'Seriyasi', 'Raqami', 'Reyting', "O'qish muddati (davri)"
            ]
            filename = 'sertifikat_template.xlsx'

        df = pd.DataFrame(columns=columns)
        # Add sample row
        sample = {col: 'Namuna' for col in columns}
        df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin configuration for Certificate model with bulk import."""
    list_display = ['title', 'holder_name', 'series', 'number', 'certificate_type', 'is_active']
    list_filter = ['certificate_type', 'is_active', 'issue_date']
    search_fields = ['title', 'holder_name', 'number']
    list_editable = ['is_active']
    ordering = ['-issue_date', '-created_at']

    change_list_template = "admin/certificate_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='certificate_import_excel'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel), name='certificate_export_excel'),
            path('download-template/', self.admin_site.admin_view(self.download_template), name='certificate_download_template'),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        """Handle Excel file import for certificates."""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                cert_type = request.POST.get('certificate_type', 'course_completion')

                try:
                    df = pd.read_excel(BytesIO(excel_file.read()))
                    
                    # Debug: show found columns
                    found_columns = list(df.columns)
                    print(f"Certificate Excel ustunlari: {found_columns}")

                    # Flexible column mapping
                    column_mapping = {
                        'title': ['Sertifikat nomi', 'Nomi', 'Sarlavha', 'Kurs nomi'],
                        'holder_name': ['Egasi', 'F.I.SH', 'FIO', 'Tinglovchi', 'Ism', 'Ismi', 'F.I.O'],
                        'holder_workplace': ['Ish joyi', 'Asosiy ish joyi', 'Tashkilot', 'Lavozimi'],
                        'series': ['Seriya', 'Seriyasi', 'Sertifikat seriyasi'],
                        'number': ['Raqam', 'Raqami', '№', 'Sertifikat raqami'],
                        'issued_by': ['Kim tomonidan', 'Muassasa', 'Bergan tashkilot'],
                        'description': ['Tavsif', 'Izoh', 'Qo\'shimcha'],
                    }

                    # Find matching columns (case-insensitive)
                    def find_column(possible_names, df_columns):
                        df_columns_lower = {col.lower().strip(): col for col in df_columns}
                        for name in possible_names:
                            name_lower = name.lower().strip()
                            if name_lower in df_columns_lower:
                                return df_columns_lower[name_lower]
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
                            print(f"Certificate topildi: '{found_col}' -> {model_field}")

                    created_count = 0
                    updated_count = 0
                    skipped_count = 0

                    with transaction.atomic():
                        for idx, row in df.iterrows():
                            cert_data = {'certificate_type': cert_type}

                            for excel_col, model_field in actual_mapping.items():
                                value = row[excel_col]
                                if pd.notna(value):
                                    cert_data[model_field] = str(value).strip()

                            if not cert_data.get('holder_name'):
                                skipped_count += 1
                                continue

                            # Generate number if missing
                            if not cert_data.get('number'):
                                cert_data['number'] = str(idx + 1).zfill(6)

                            if not cert_data.get('title'):
                                cert_data['title'] = f"Sertifikat #{cert_data['number']}"

                            existing = Certificate.objects.filter(
                                series=cert_data.get('series', ''),
                                number=cert_data['number']
                            ).first()

                            if existing:
                                for key, value in cert_data.items():
                                    setattr(existing, key, value)
                                existing.save()
                                updated_count += 1
                            else:
                                Certificate.objects.create(**cert_data)
                                created_count += 1

                    msg = f"Muvaffaqiyat! {created_count} ta yangi qo'shildi, {updated_count} ta yangilandi."
                    if skipped_count > 0:
                        msg += f" {skipped_count} ta qator o'tkazib yuborildi."
                    msg += f" Ustunlar: {', '.join(found_columns)}"
                    
                    messages.success(request, msg)
                    return redirect('..')

                except Exception as e:
                    messages.error(request, f"Xatolik: {str(e)}")

        form = ExcelImportForm()
        context = {
            'form': form,
            'title': 'Sertifikatlarni Excel fayldan import qilish',
            'opts': self.model._meta,
            'is_certificate': True,
        }
        return render(request, 'admin/excel_import_certificate.html', context)

    def export_excel(self, request):
        """Export certificates to Excel file."""
        queryset = Certificate.objects.all()

        data = []
        for cert in queryset:
            data.append({
                'Sertifikat nomi': cert.title,
                'Egasi': cert.holder_name,
                'Ish joyi': cert.holder_workplace,
                'Seriya': cert.series,
                'Raqam': cert.number,
                'Kim tomonidan': cert.issued_by,
                'Tavsif': cert.description,
                'Turi': cert.get_certificate_type_display(),
                'Sana': cert.issue_date.strftime('%Y-%m-%d') if cert.issue_date else '',
            })

        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="sertifikatlar.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response

    def download_template(self, request):
        """Download Excel template for certificate import."""
        columns = [
            'Sertifikat nomi', 'Egasi', 'Ish joyi', 'Seriya',
            'Raqam', 'Kim tomonidan', 'Tavsif'
        ]

        df = pd.DataFrame(columns=columns)
        # Add sample row
        sample = {
            'Sertifikat nomi': 'Namuna sertifikat',
            'Egasi': 'Ism Familiya',
            'Ish joyi': 'Muassasa nomi',
            'Seriya': 'SN',
            'Raqam': '000001',
            'Kim tomonidan': 'Markaz nomi',
            'Tavsif': 'Tavsif matni',
        }
        df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="sertifikat_template.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
        return response


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Admin configuration for Teacher model."""
    list_display = ['full_name', 'position', 'degree', 'title', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['full_name', 'position', 'degree']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'full_name']


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    """Admin configuration for Personnel model."""
    list_display = ['full_name', 'position', 'category', 'phone', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['full_name', 'position']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'full_name']


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
    """Admin configuration for JournalIssue model."""
    list_display = ['title', 'year', 'issue_number', 'is_active']
    list_filter = ['year', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-year', '-created_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model."""
    list_display = ['title', 'category', 'file_type', 'is_active', 'created_at']
    list_filter = ['category', 'file_type', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


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
    """Admin configuration for AppContent singleton model."""
    list_display = ['__str__', 'updated_at']

    fieldsets = (
        ('Markaz haqida', {
            'fields': ('history', 'structure', 'structure_image', 'structure_image_url')
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
