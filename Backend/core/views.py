"""
DRF Views for the Educational Center Management System.
Cleaned up version with simplified models and improved functionality.
"""
import pandas as pd
from io import BytesIO
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    News, NewsImage, GalleryItem, Listener, Teacher, Personnel,
    Course, JournalIssue, Document, Statistics, YearlyStatistics,
    AppContent, JournalSettings, InternationalRelation, ForeignPartner,
    CollaborationProject, ArtGalleryItem
)
from .serializers import (
    NewsSerializer, NewsCreateSerializer, NewsImageSerializer,
    GalleryItemSerializer, ListenerSerializer, ListenerBulkImportSerializer,
    TeacherSerializer, PersonnelSerializer, CourseSerializer,
    JournalIssueSerializer, DocumentSerializer, StatisticsSerializer,
    YearlyStatisticsSerializer, AppContentSerializer, JournalSettingsSerializer,
    InternationalRelationSerializer, ForeignPartnerSerializer,
    CollaborationProjectSerializer, ArtGalleryItemSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission: read-only for everyone, write only for admins.
    In DEBUG mode, allows all write operations for easier development."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        from django.conf import settings
        if settings.DEBUG:
            return True
        return request.user and request.user.is_staff


class TwelveItemsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class NewsViewSet(viewsets.ModelViewSet):
    """ViewSet for News CRUD operations with inline images."""
    queryset = News.objects.all().order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        from django.conf import settings
        if self.request.user.is_staff or settings.DEBUG:
            queryset = News.objects.all().order_by('-created_at')
        else:
            queryset = News.objects.filter(is_active=True).order_by('-created_at')
        
        important_only = self.request.query_params.get('important', None)
        if important_only == 'true':
            queryset = queryset.filter(is_important=True)

        show_all = self.request.query_params.get('all', None)
        if show_all != 'true' and not (self.request.user.is_staff or settings.DEBUG):
            queryset = queryset.filter(is_active=True)
        
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NewsCreateSerializer
        return NewsSerializer

    def perform_create(self, serializer):
        serializer.save(is_active=True)

    def create(self, request, *args, **kwargs):
        """Create news with optional images."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        news = serializer.save(is_active=True)

        # Handle multiple image upload
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            NewsImage.objects.create(news=news, image=img, order=idx)

        # Return full serialized response
        response_serializer = NewsSerializer(news, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def add_images(self, request, pk=None):
        """Add images to existing news."""
        news = self.get_object()
        images = request.FILES.getlist('images')
        last_order = news.images.count()

        for idx, img in enumerate(images):
            NewsImage.objects.create(news=news, image=img, order=last_order + idx)

        serializer = NewsSerializer(news, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the is_active status of a news item."""
        news = self.get_object()
        news.is_active = not news.is_active
        news.save()
        serializer = NewsSerializer(news, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_important(self, request, pk=None):
        """Toggle the is_important status of a news item."""
        news = self.get_object()
        news.is_important = not news.is_important
        news.save()
        serializer = NewsSerializer(news, context={'request': request})
        return Response(serializer.data)


class GalleryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Gallery CRUD operations - simple images only."""
    queryset = GalleryItem.objects.filter(is_active=True).order_by('order', '-created_at')
    serializer_class = GalleryItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_upload(self, request):
        """Upload multiple images at once."""
        images = request.FILES.getlist('images')
        last_order = GalleryItem.objects.count()
        created = []

        for idx, img in enumerate(images):
            item = GalleryItem.objects.create(image=img, order=last_order + idx)
            created.append(item)

        serializer = GalleryItemSerializer(created, many=True, context={'request': request})
        return Response({
            'success': True,
            'message': f"{len(created)} ta rasm qo'shildi",
            'items': serializer.data
        }, status=status.HTTP_201_CREATED)


class ListenerViewSet(viewsets.ModelViewSet):
    """ViewSet for Listener CRUD operations with MO/QT types."""
    queryset = Listener.objects.all()
    serializer_class = ListenerSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @staticmethod
    def normalize_record_type(value):
        normalized = str(value or '').strip().upper()
        mapping = {
            'MO': 'MO',
            'QT': 'QT',
            'CERTIFICATE': 'MO',
            'DIPLOMA': 'QT',
        }
        return mapping.get(normalized)

    def get_queryset(self):
        queryset = Listener.objects.all()
        record_type = self.normalize_record_type(self.request.query_params.get('record_type', None))
        if record_type:
            queryset = queryset.filter(record_type=record_type)

        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(number__icontains=search) |
                Q(workplace__icontains=search) |
                Q(series__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search listeners by record_type (MO/QT) and number."""
        series = request.query_params.get('series', '').upper().strip()
        number = request.query_params.get('number', '').strip()

        if not number:
            return Response(
                {'error': 'Raqam kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.db.models import Q
        
        listener = None
        
        # Convert series to valid record_type
        record_type = self.normalize_record_type(series)
        
        if record_type:
            # Search by exact record_type and number
            listener = Listener.objects.filter(
                record_type=record_type,
                number__iexact=number
            ).first()
            
            # Try number with leading zeros stripped
            if not listener:
                listener = Listener.objects.filter(
                    record_type=record_type,
                    number__endswith=number.lstrip('0') if number.lstrip('0') else number
                ).first()
            
            # Try number containing
            if not listener:
                listener = Listener.objects.filter(
                    record_type=record_type,
                    number__icontains=number
                ).first()
        else:
            # No record_type specified - search across all
            listener = Listener.objects.filter(number__iexact=number).first()
            
            if not listener:
                listener = Listener.objects.filter(number__icontains=number).first()
            
            if not listener:
                listener = Listener.objects.filter(number__endswith=number).first()

        if listener:
            serializer = ListenerSerializer(listener, context={'request': request})
            return Response({'found': True, 'data': serializer.data})
        return Response({'found': False, 'message': "Ma'lumot topilmadi"})

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        """Bulk import listeners from Excel file."""
        serializer = ListenerBulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        record_type = self.normalize_record_type(serializer.validated_data['record_type']) or 'MO'

        try:
            # Read all columns as strings to preserve leading zeros
            df = pd.read_excel(BytesIO(file.read()), dtype=str)
            found_columns = list(df.columns)
            print(f"Excel ustunlari: {found_columns}")

            # Flexible column mapping
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

            actual_mapping = {}
            for model_field, possible_names in column_mapping.items():
                found_col = find_column(possible_names, df.columns)
                if found_col:
                    actual_mapping[found_col] = model_field
                    print(f"Topildi: '{found_col}' -> {model_field}")

            created_count = 0
            updated_count = 0
            errors = []

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        listener_data = {'record_type': record_type}

                        for excel_col, model_field in actual_mapping.items():
                            value = row[excel_col]
                            if pd.notna(value):
                                listener_data[model_field] = str(value).strip()

                        if not listener_data.get('full_name'):
                            continue

                        if not listener_data.get('number'):
                            listener_data['number'] = str(idx + 1).zfill(6)

                        if not listener_data.get('series'):
                            listener_data['series'] = record_type

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


class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet for Teacher CRUD operations."""
    queryset = Teacher.objects.filter(is_active=True).order_by('order', 'full_name')
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class PersonnelViewSet(viewsets.ModelViewSet):
    """ViewSet for Personnel CRUD operations."""
    queryset = Personnel.objects.filter(is_active=True).order_by('order', 'full_name')
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
    queryset = Course.objects.filter(is_active=True).order_by('order', 'title')
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
    queryset = JournalIssue.objects.filter(is_active=True).order_by('-year', '-created_at')
    serializer_class = JournalIssueSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document CRUD operations."""
    queryset = Document.objects.filter(is_active=True).order_by('-created_at')
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
        stats = Statistics.get_instance()
        serializer = StatisticsSerializer(stats, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        stats = Statistics.get_instance()
        serializer = StatisticsSerializer(stats, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YearlyStatisticsViewSet(viewsets.ModelViewSet):
    """ViewSet for YearlyStatistics CRUD operations."""
    queryset = YearlyStatistics.objects.all().order_by('-year')
    serializer_class = YearlyStatisticsSerializer
    permission_classes = [IsAdminOrReadOnly]


class AppContentViewSet(viewsets.ViewSet):
    """ViewSet for AppContent (singleton model) - Markaz haqida."""
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        content = AppContent.get_instance()
        serializer = AppContentSerializer(content, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        content = AppContent.get_instance()
        serializer = AppContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JournalSettingsViewSet(viewsets.ViewSet):
    """ViewSet for JournalSettings (singleton model) - Jurnal sozlamalari."""
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        settings = JournalSettings.get_instance()
        serializer = JournalSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        settings = JournalSettings.get_instance()
        serializer = JournalSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InternationalRelationViewSet(viewsets.ViewSet):
    """ViewSet for InternationalRelation (singleton model)."""
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request):
        content = InternationalRelation.get_instance()
        serializer = InternationalRelationSerializer(content, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        content = InternationalRelation.get_instance()
        serializer = InternationalRelationSerializer(content, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForeignPartnerViewSet(viewsets.ModelViewSet):
    """ViewSet for foreign partners."""
    queryset = ForeignPartner.objects.filter(is_active=True).order_by('order', 'organization_name')
    serializer_class = ForeignPartnerSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = TwelveItemsPagination

    def get_queryset(self):
        from django.conf import settings
        queryset = ForeignPartner.objects.all().order_by('order', 'organization_name')
        if not (self.request.user.is_staff or settings.DEBUG):
            queryset = queryset.filter(is_active=True)
        return queryset


class CollaborationProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for collaboration projects."""
    queryset = CollaborationProject.objects.filter(is_active=True).order_by('-date', 'order')
    serializer_class = CollaborationProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        from django.conf import settings
        queryset = CollaborationProject.objects.all().order_by('-date', 'order')
        if not (self.request.user.is_staff or settings.DEBUG):
            queryset = queryset.filter(is_active=True)
        return queryset


class ArtGalleryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Art gallery items."""
    queryset = ArtGalleryItem.objects.filter(is_active=True).order_by('order', '-created_at')
    serializer_class = ArtGalleryItemSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        from django.conf import settings
        queryset = ArtGalleryItem.objects.all().order_by('order', '-created_at')
        if not (self.request.user.is_staff or settings.DEBUG):
            queryset = queryset.filter(is_active=True)
        return queryset


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
            GalleryItem.objects.filter(is_active=True).order_by('order', '-created_at'),
            many=True,
            context={'request': request}
        ).data,
        'teachers': TeacherSerializer(
            Teacher.objects.filter(is_active=True).order_by('order', 'full_name'),
            many=True,
            context={'request': request}
        ).data,
        'courses': CourseSerializer(
            Course.objects.filter(is_active=True).order_by('order', 'title'),
            many=True,
            context={'request': request}
        ).data,
        'personnel': PersonnelSerializer(
            Personnel.objects.filter(is_active=True).order_by('order', 'full_name'),
            many=True,
            context={'request': request}
        ).data,
        'stats': StatisticsSerializer(
            Statistics.get_instance(),
            context={'request': request}
        ).data,
        'documents': DocumentSerializer(
            Document.objects.filter(is_active=True).order_by('-created_at'),
            many=True,
            context={'request': request}
        ).data,
        'listeners': ListenerSerializer(
            Listener.objects.all().order_by('-created_at'),
            many=True,
            context={'request': request}
        ).data,
        'journalIssues': JournalIssueSerializer(
            JournalIssue.objects.filter(is_active=True).order_by('-year', '-created_at'),
            many=True,
            context={'request': request}
        ).data,
        'about': AppContentSerializer(
            AppContent.get_instance(),
            context={'request': request}
        ).data,
        'journalSettings': JournalSettingsSerializer(
            JournalSettings.get_instance(),
            context={'request': request}
        ).data,
        'international': InternationalRelationSerializer(
            InternationalRelation.get_instance(),
            context={'request': request}
        ).data,
        'foreignPartners': ForeignPartnerSerializer(
            ForeignPartner.objects.filter(is_active=True).order_by('order', 'organization_name'),
            many=True,
            context={'request': request}
        ).data,
        'collaborationProjects': CollaborationProjectSerializer(
            CollaborationProject.objects.filter(is_active=True).order_by('-date', 'order'),
            many=True,
            context={'request': request}
        ).data,
        'artGallery': ArtGalleryItemSerializer(
            ArtGalleryItem.objects.filter(is_active=True).order_by('order', '-created_at'),
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
