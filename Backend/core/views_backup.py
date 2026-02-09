"""
DRF Views for the Educational Center Management System.
Includes standard CRUD operations and bulk import functionality.
"""
import pandas as pd
from io import BytesIO
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    News, GalleryItem, Listener, Certificate, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics, AppContent
)
from .serializers import (
    NewsSerializer, GalleryItemSerializer, ListenerSerializer,
    ListenerBulkImportSerializer, CertificateSerializer,
    CertificateBulkImportSerializer, TeacherSerializer, PersonnelSerializer,
    CourseSerializer, JournalIssueSerializer, DocumentSerializer,
    StatisticsSerializer, YearlyStatisticsSerializer, AppContentSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission: read-only for everyone, write only for admins.
    In DEBUG mode, allows all write operations for easier development."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if DEBUG mode - allow all writes for development
        from django.conf import settings
        if settings.DEBUG:
            return True
        return request.user and request.user.is_staff


class NewsViewSet(viewsets.ModelViewSet):
    """ViewSet for News CRUD operations."""
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # For admin users, show all news; for public, show only active
        from django.conf import settings
        if self.request.user.is_staff or settings.DEBUG:
            queryset = News.objects.all().order_by('-created_at')
        else:
            queryset = News.objects.filter(is_active=True).order_by('-created_at')
        
        important_only = self.request.query_params.get('important', None)
        if important_only == 'true':
            queryset = queryset.filter(is_important=True)
        
        # Filter by active status if specified
        show_all = self.request.query_params.get('all', None)
        if show_all != 'true' and not (self.request.user.is_staff or settings.DEBUG):
            queryset = queryset.filter(is_active=True)
        
        return queryset

    def perform_create(self, serializer):
        # Ensure is_active is True by default
        serializer.save(is_active=True)


class GalleryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Gallery CRUD operations with image upload support."""
    queryset = GalleryItem.objects.filter(is_active=True)
    serializer_class = GalleryItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = GalleryItem.objects.filter(is_active=True)
        media_type = self.request.query_params.get('type', None)
        if media_type in ['image', 'video']:
            queryset = queryset.filter(media_type=media_type)
        return queryset


class ListenerViewSet(viewsets.ModelViewSet):
    """ViewSet for Listener (Student) CRUD operations with bulk import."""
    queryset = Listener.objects.all()
    serializer_class = ListenerSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Listener.objects.all()
        record_type = self.request.query_params.get('record_type', None)
        if record_type in ['certificate', 'diploma']:
            queryset = queryset.filter(record_type=record_type)

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                full_name__icontains=search
            ) | queryset.filter(
                number__icontains=search
            ) | queryset.filter(
                workplace__icontains=search
            )
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search listeners by number and series."""
        series = request.query_params.get('series', '').upper()
        number = request.query_params.get('number', '')

        if not number:
            return Response(
                {'error': 'Number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Map series to record_type
        record_type = 'certificate' if series == 'MO' else 'diploma'

        listener = Listener.objects.filter(
            record_type=record_type,
            number=number.strip()
        ).first()

        if listener:
            serializer = ListenerSerializer(listener, context={'request': request})
            return Response({'found': True, 'data': serializer.data})
        return Response({'found': False})

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        """Bulk import listeners from Excel file."""
        serializer = ListenerBulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        record_type = serializer.validated_data['record_type']

        try:
            # Read Excel file
            df = pd.read_excel(BytesIO(file.read()))

            # Column mapping for different record types
            if record_type == 'diploma':
                column_mapping = {
                    'Tinglovchi': 'full_name',
                    'Qayta tayyorlagan muassasa': 'institution',
                    'Asosiy ish joyi': 'workplace',
                    'Qayta tayyorlash kursi': 'course_type',
                    'Qayd raqami': 'reg_number',
                    'Diplom seriyasi': 'series',
                    'Raqami': 'number',
                    'Reyting': 'rating',
                    "O'qish muddati (davri)": 'duration',
                }
                default_series = 'QT'
            else:
                column_mapping = {
                    'Tinglovchi': 'full_name',
                    'Muassasa': 'institution',
                    'Asosiy ish joyi': 'workplace',
                    'Kursi': 'course_type',
                    'Qayd raqami': 'reg_number',
                    'Seriyasi': 'series',
                    'Raqami': 'number',
                    'Reyting': 'rating',
                    "O'qish muddati (davri)": 'duration',
                }
                default_series = 'MO'

            # Process rows
            created_count = 0
            updated_count = 0
            errors = []

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        listener_data = {
                            'record_type': record_type,
                        }

                        for excel_col, model_field in column_mapping.items():
                            if excel_col in df.columns:
                                value = row[excel_col]
                                if pd.notna(value):
                                    listener_data[model_field] = str(value).strip()

                        # Skip rows without required fields
                        if not listener_data.get('full_name') or not listener_data.get('number'):
                            continue

                        # Set default series if not provided
                        if not listener_data.get('series'):
                            listener_data['series'] = default_series

                        # Check for existing record
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

                    except Exception as e:
                        errors.append(f"Row {idx + 2}: {str(e)}")

            return Response({
                'success': True,
                'message': f"{created_count} ta yangi yozuv qo'shildi, {updated_count} ta yangilandi.",
                'created': created_count,
                'updated': updated_count,
                'errors': errors[:10] if errors else []
            })

        except Exception as e:
            return Response(
                {'error': f"Faylni o'qishda xatolik: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CertificateViewSet(viewsets.ModelViewSet):
    """ViewSet for Certificate CRUD operations with bulk import."""
    queryset = Certificate.objects.filter(is_active=True)
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Certificate.objects.filter(is_active=True)
        cert_type = self.request.query_params.get('certificate_type', None)
        if cert_type:
            queryset = queryset.filter(certificate_type=cert_type)

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                holder_name__icontains=search
            ) | queryset.filter(
                number__icontains=search
            ) | queryset.filter(
                title__icontains=search
            )
        return queryset

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        """Bulk import certificates from Excel file."""
        serializer = CertificateBulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        certificate_type = serializer.validated_data.get('certificate_type', 'course_completion')

        try:
            df = pd.read_excel(BytesIO(file.read()))

            column_mapping = {
                'Sertifikat nomi': 'title',
                'Egasi': 'holder_name',
                'Ish joyi': 'holder_workplace',
                'Seriya': 'series',
                'Raqam': 'number',
                'Berilgan sana': 'issue_date',
                'Kim tomonidan': 'issued_by',
                'Tavsif': 'description',
            }

            created_count = 0
            updated_count = 0
            errors = []

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        cert_data = {
                            'certificate_type': certificate_type,
                        }

                        for excel_col, model_field in column_mapping.items():
                            if excel_col in df.columns:
                                value = row[excel_col]
                                if pd.notna(value):
                                    if model_field == 'issue_date':
                                        try:
                                            cert_data[model_field] = pd.to_datetime(value).date()
                                        except Exception:
                                            pass
                                    else:
                                        cert_data[model_field] = str(value).strip()

                        if not cert_data.get('holder_name') or not cert_data.get('number'):
                            continue

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

                    except Exception as e:
                        errors.append(f"Row {idx + 2}: {str(e)}")

            return Response({
                'success': True,
                'message': f"{created_count} ta yangi sertifikat qo'shildi, {updated_count} ta yangilandi.",
                'created': created_count,
                'updated': updated_count,
                'errors': errors[:10] if errors else []
            })

        except Exception as e:
            return Response(
                {'error': f"Faylni o'qishda xatolik: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet for Teacher CRUD operations."""
    queryset = Teacher.objects.filter(is_active=True)
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class PersonnelViewSet(viewsets.ModelViewSet):
    """ViewSet for Personnel CRUD operations."""
    queryset = Personnel.objects.filter(is_active=True)
    serializer_class = PersonnelSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Personnel.objects.filter(is_active=True)
        category = self.request.query_params.get('category', None)
        if category in ['leadership', 'staff']:
            queryset = queryset.filter(category=category)
        return queryset


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course CRUD operations."""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        course_type = self.request.query_params.get('type', None)
        if course_type in ['professional_development', 'retraining']:
            queryset = queryset.filter(course_type=course_type)
        return queryset


class JournalIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for JournalIssue CRUD operations."""
    queryset = JournalIssue.objects.filter(is_active=True)
    serializer_class = JournalIssueSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document CRUD operations."""
    queryset = Document.objects.filter(is_active=True)
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Document.objects.filter(is_active=True)
        category = self.request.query_params.get('category', None)
        if category in ['regulatory', 'plan', 'open_data']:
            queryset = queryset.filter(category=category)
        return queryset


class StatisticsViewSet(viewsets.ViewSet):
    """ViewSet for Statistics (singleton model)."""
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        """Get the statistics singleton instance."""
        stats = Statistics.get_instance()
        serializer = StatisticsSerializer(stats, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Update the statistics singleton instance."""
        stats = Statistics.get_instance()
        serializer = StatisticsSerializer(stats, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YearlyStatisticsViewSet(viewsets.ModelViewSet):
    """ViewSet for YearlyStatistics CRUD operations."""
    queryset = YearlyStatistics.objects.all()
    serializer_class = YearlyStatisticsSerializer
    permission_classes = [IsAdminOrReadOnly]


class AppContentViewSet(viewsets.ViewSet):
    """ViewSet for AppContent (singleton model)."""
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        """Get the app content singleton instance."""
        content = AppContent.get_instance()
        serializer = AppContentSerializer(content, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Update the app content singleton instance."""
        content = AppContent.get_instance()
        serializer = AppContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_all_data(request):
    """
    Get all data for initial frontend load.
    Returns all active content in a single request.
    """
    data = {
        'news': NewsSerializer(
            News.objects.filter(is_active=True).order_by('-created_at'),
            many=True,
            context={'request': request}
        ).data,
        'gallery': GalleryItemSerializer(
            GalleryItem.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'teachers': TeacherSerializer(
            Teacher.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'courses': CourseSerializer(
            Course.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'personnel': PersonnelSerializer(
            Personnel.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'stats': StatisticsSerializer(
            Statistics.get_instance(),
            context={'request': request}
        ).data,
        'documents': DocumentSerializer(
            Document.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'pdPlans': ListenerSerializer(
            Listener.objects.all(),
            many=True,
            context={'request': request}
        ).data,
        'journalIssues': JournalIssueSerializer(
            JournalIssue.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
        'about': AppContentSerializer(
            AppContent.get_instance(),
            context={'request': request}
        ).data,
        'certificates': CertificateSerializer(
            Certificate.objects.filter(is_active=True),
            many=True,
            context={'request': request}
        ).data,
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def custom_login(request):
    """
    Custom login endpoint for backward compatibility.
    Returns success and token for valid credentials.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)

    if user is not None and user.is_staff:
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'token': str(refresh.access_token),
            'refresh': str(refresh),
        })

    return Response(
        {'success': False, 'message': "Login yoki parol noto'g'ri!"},
        status=status.HTTP_401_UNAUTHORIZED
    )
