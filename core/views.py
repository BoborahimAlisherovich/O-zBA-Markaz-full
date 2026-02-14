import re
from django.shortcuts import get_object_or_404, render

from .models import (
    AppContent,
    ArtGalleryItem,
    CollaborationProject,
    Course,
    Document,
    ForeignPartner,
    GalleryItem,
    InternationalRelation,
    JournalIssue,
    Listener,
    News,
    Personnel,
    Statistics,
    StudentTrainingRecord,
    Teacher,
    YearlyStatistics,
)


MENU_ITEMS = [
    {"label": "Bosh sahifa", "url_name": "home"},
    {"label": "Markaz haqida", "url_name": "about"},
    {"label": "Ilmiy jurnal", "url_name": "journal"},
    {"label": "Xalqaro aloqalar", "url_name": "international"},
    {"label": "Tinglovchilar uchun", "url_name": "students"},
    {"label": "Ochiq ma'lumotlar", "url_name": "open_data"},
]

COMMON_CONTEXT = {
    "center_phone": "(+99877) 363-38-36",
    "center_email": "uzbahuzuridagimarkaz@gmail.com",
    "center_address": "Toshkent shahri, Uchtepa tumani, Chilonzor 26-daha, Shirin ko'cha, 1A",
    "site_logo_url": "/static/logo/uzba_markaz.png",
    "menu_items": MENU_ITEMS,
}


def base_context(active_page):
    context = dict(COMMON_CONTEXT)
    context["active_page"] = active_page
    return context


def to_embed_url(url):
    value = (url or "").strip()
    if not value:
        return ""

    iframe_src = re.search(r'src=["\']([^"\']+)["\']', value, flags=re.IGNORECASE)
    if iframe_src:
        value = iframe_src.group(1).strip()

    value = value.replace("&amp;", "&")

    embed_match = re.search(r'youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{6,})', value, flags=re.IGNORECASE)
    if embed_match:
        return f"https://www.youtube.com/embed/{embed_match.group(1)}"

    short_match = re.search(r'youtu\.be/([A-Za-z0-9_-]{6,})', value, flags=re.IGNORECASE)
    if short_match:
        return f"https://www.youtube.com/embed/{short_match.group(1)}"

    watch_match = re.search(r'[?&]v=([A-Za-z0-9_-]{6,})', value, flags=re.IGNORECASE)
    if watch_match:
        return f"https://www.youtube.com/embed/{watch_match.group(1)}"

    shorts_match = re.search(r'youtube\.com/shorts/([A-Za-z0-9_-]{6,})', value, flags=re.IGNORECASE)
    if shorts_match:
        return f"https://www.youtube.com/embed/{shorts_match.group(1)}"

    id_only = re.fullmatch(r'[A-Za-z0-9_-]{11}', value)
    if id_only:
        return f"https://www.youtube.com/embed/{value}"

    return value


def home(request):
    stats = Statistics.get_instance()
    yearly_data = list(YearlyStatistics.objects.all().order_by("year"))
    listeners = list(
        Listener.objects.all().values(
            "id",
            "record_type",
            "full_name",
            "workplace",
            "course_type",
            "series",
            "number",
            "duration",
            "is_verified",
        )
    )

    gallery = list(
        GalleryItem.objects.filter(is_active=True)
        .prefetch_related("images")
        .order_by("order", "-created_at")
    )

    gallery_json = []
    for item in gallery:
        gallery_json.append(
            {
                "id": item.id,
                "title": item.title,
                "cover_image_url": item.cover_image.url if item.cover_image else "",
                "images": [
                    {
                        "id": image.id,
                        "image_url": image.image.url if image.image else "",
                    }
                    for image in item.images.all().order_by("order", "-created_at")
                ],
            }
        )

    art_items = (
        ArtGalleryItem.objects.filter(is_active=True)
        .prefetch_related("images")
        .order_by("order", "-created_at")[:8]
    )
    art_gallery_json = []
    for item in art_items:
        art_gallery_json.append(
            {
                "id": item.id,
                "name": item.name,
                "author": item.author_full_name,
                "text": item.text,
                "image_url": item.image.url if item.image else "",
                "images": [
                    {
                        "id": image.id,
                        "image_url": image.image.url if image.image else "",
                    }
                    for image in item.images.all().order_by("order", "-created_at")
                ],
            }
        )

    context = base_context("home")
    context.update(
        {
            "stats": stats,
            "yearly_data": yearly_data,
            "news_list": News.objects.filter(is_active=True).order_by("-created_at")[:8],
            "teachers": Teacher.objects.filter(is_active=True).order_by("order", "full_name")[:12],
            "courses_retraining": Course.objects.filter(
                is_active=True,
                course_type="retraining",
            ).order_by("order", "title"),
            "courses_pd": Course.objects.filter(
                is_active=True,
                course_type="professional_development",
            ).order_by("order", "title"),
            "gallery": gallery,
            "gallery_json": gallery_json,
            "listeners_json": listeners,
            "art_gallery": art_items,
            "art_gallery_json": art_gallery_json,
            "useful_links": [
                {"name": "Masofaviy ta'lim", "url": "https://mt.uzbamalaka.uz/"},
                {"name": "Badiiy akademiya", "url": "https://art-academy.uz/"},
                {"name": "MY.BIMM.UZ", "url": "https://my.bimm.uz/home"},
                {"name": "LEX.UZ", "url": "https://lex.uz/uz/"},
            ],
        }
    )
    return render(request, "site/home.html", context)


def about(request):
    context = base_context("about")
    context.update(
        {
            "about_content": AppContent.get_instance(),
            "leadership": Personnel.objects.filter(
                is_active=True,
                category="leadership",
            ).order_by("order", "full_name"),
            "staff": Personnel.objects.filter(
                is_active=True,
                category="staff",
            ).order_by("order", "full_name"),
        }
    )
    return render(request, "site/about.html", context)


def journal(request):
    context = base_context("journal")
    context["journal_issues"] = JournalIssue.objects.filter(is_active=True).order_by("-year", "-created_at")
    return render(request, "site/journal.html", context)


def international(request):
    content = InternationalRelation.get_instance()
    partners = list(ForeignPartner.objects.filter(is_active=True).order_by("order", "organization_name"))
    photos = list(content.photos.filter(is_active=True).order_by("order", "-created_at"))
    videos = list(content.videos.filter(is_active=True).order_by("order", "-created_at"))
    partners_json = [
        {
            "id": item.id,
            "organization_name": item.organization_name,
            "country": item.country,
            "short_info": item.short_info,
            "image_url": item.image.url if item.image else "",
        }
        for item in partners
    ]
    photos_json = [
        {
            "id": item.id,
            "image_url": item.image.url if item.image else "",
        }
        for item in photos
    ]
    videos_json = [
        {
            "id": item.id,
            "title": item.title or "Video",
            "embed_url": to_embed_url(item.video_url),
            "video_url": item.video_url,
        }
        for item in videos
    ]
    context = base_context("international")
    context.update(
        {
            "international_content": content,
            "foreign_partners": partners,
            "projects": CollaborationProject.objects.filter(is_active=True).order_by("-date", "order"),
            "photos": photos,
            "videos": videos,
            "partners_json": partners_json,
            "photos_json": photos_json,
            "videos_json": videos_json,
        }
    )
    return render(request, "site/international.html", context)


def students(request):
    student_records = list(
        StudentTrainingRecord.objects.filter(is_active=True).values(
            "id",
            "full_name",
            "workplace",
            "course_name",
            "training_time",
        )
    )
    context = base_context("students")
    context.update(
        {
            "students_records_json": student_records,
            "regulatory_docs": Document.objects.filter(is_active=True, category="regulatory").order_by("-created_at"),
            "student_notes": AppContent.get_instance().student_notes,
        }
    )
    return render(request, "site/students.html", context)


def open_data(request):
    documents = Document.objects.filter(is_active=True).exclude(category="regulatory").order_by("-created_at")
    context = base_context("open_data")
    context.update(
        {
            "documents": documents,
            "docs_open_data": documents.filter(category="open_data"),
            "docs_plan": documents.filter(category="plan"),
        }
    )
    return render(request, "site/open_data.html", context)


def news_detail(request, news_id):
    news_item = get_object_or_404(News, pk=news_id, is_active=True)
    context = base_context(None)
    context.update(
        {
            "news_item": news_item,
            "news_images": news_item.images.all().order_by("order"),
            "related_news": News.objects.filter(is_active=True).exclude(pk=news_id).order_by("-created_at")[:3],
        }
    )
    return render(request, "site/news_detail.html", context)
