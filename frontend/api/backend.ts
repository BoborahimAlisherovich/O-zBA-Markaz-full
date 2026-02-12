/**
 * Backend API Service
 * Connects to Django REST Framework backend
 */
import { NewsItem, Personnel, JournalIssue, Document, PDPlanRecord, Statistics, GalleryItem, GalleryImage, Teacher, Course } from '../types';
import {
  AppContent, InternationalContent, ForeignPartner,
  CollaborationProject, ArtGalleryItem
} from '../types';
import { INITIAL_STATS } from '../constants';

function resolveApiBaseUrl() {
  const envUrl = (import.meta.env.VITE_API_URL || '').trim();
  if (envUrl) return envUrl.replace(/\/+$/, '');

  if (typeof window !== 'undefined') {
    const { protocol, hostname, port, origin } = window.location;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      if (port === '5173' || port === '3000') {
        return `${protocol}//${hostname}:8000/api`;
      }
      return `${origin}/api`;
    }
    return `${origin}/api`;
  }
  return 'https://uzbamalaka.uz/api';
}

const API_BASE_URL = resolveApiBaseUrl();

// Token storage keys
const TOKEN_KEY = 'auth_token';
const REFRESH_KEY = 'refresh_token';

/**
 * Helper function for API requests
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retried = false
): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);

  const headers: HeadersInit = {
    ...options.headers,
  };

  // Add auth token if available and valid (not fake)
  if (token && !token.startsWith('dev_session_') && token !== 'local') {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  // Add Content-Type for JSON requests (not for FormData)
  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 - try to refresh token
  if (response.status === 401 && !retried) {
    const refreshed = await BackendAPI.refreshToken();
    if (refreshed) {
      return apiRequest<T>(endpoint, options, true);
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `HTTP error! status: ${response.status}`);
  }

  // Handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : {} as T;
}

/**
 * Transform backend data to frontend format
 */
function transformNewsItem(item: any): NewsItem {
  // Get first image from images array or use image_url
  const firstImageUrl = item.images && item.images.length > 0 
    ? item.images[0].image_url 
    : (item.image_url || '');
  
  return {
    id: String(item.id),
    title: item.title,
    content: item.content,
    date: new Date(item.created_at).toLocaleDateString('uz-UZ'),
    image: firstImageUrl,
    images: item.images?.map((img: any) => ({
      id: String(img.id),
      imageUrl: img.image_url,
      order: img.order
    })),
    isImportant: item.is_important,
    isActive: item.is_active,
  };
}

function transformGalleryItem(item: any): GalleryItem {
  return {
    id: String(item.id),
    title: item.title || '',
    coverImageUrl: item.cover_image_url || '',
    images: (item.images || []).map((img: any): GalleryImage => ({
      id: String(img.id),
      imageUrl: img.image_url || '',
      order: img.order || 0,
    })),
    order: item.order || 0,
    isActive: item.is_active,
  };
}

function transformTeacher(item: any): Teacher {
  return {
    id: String(item.id),
    fullName: item.full_name,
    position: item.position,
    degree: item.degree,
    title: item.title,
    photoUrl: item.photo_url || '',
  };
}

function transformCourse(item: any): Course {
  return {
    id: String(item.id),
    title: item.title,
    type: item.course_type as 'retraining' | 'professional_development',
    duration: item.duration,
    description: item.description,
  };
}

function transformPersonnel(item: any): Personnel {
  return {
    id: String(item.id),
    fullName: item.full_name,
    position: item.position,
    phone: item.phone,
    receptionHours: item.reception_hours,
    photoUrl: item.photo_url || '',
    category: item.category as 'leadership' | 'staff',
  };
}

function transformJournalIssue(item: any): JournalIssue {
  return {
    id: String(item.id),
    year: item.year,
    issueNumber: item.issue_number,
    pdfUrl: item.pdf_url || '',
    thumbnailUrl: item.thumbnail_url,
  };
}

function transformDocument(item: any): Document {
  return {
    id: String(item.id),
    title: item.title,
    category: item.category as 'regulatory' | 'plan' | 'open_data',
    fileUrl: item.file_url || '',
    date: new Date(item.created_at).toLocaleDateString('uz-UZ'),
  };
}

function transformPDPlanRecord(item: any): PDPlanRecord {
  // Ensure record_type is uppercase MO or QT
  const rawType = (item.record_type || item.series || 'MO').toUpperCase();
  const recordType = (rawType === 'QT' ? 'QT' : 'MO') as 'MO' | 'QT';
  
  return {
    id: String(item.id),
    recordType,
    fullName: item.full_name,
    workplace: item.workplace || '',
    courseType: item.course_type || '',
    series: (item.series || recordType).toUpperCase(),
    number: item.number || '',
    duration: item.duration || '',
    isVerified: item.is_verified,
  };
}

function transformStatistics(data: any): Statistics {
  if (!data) return INITIAL_STATS;
  return {
    professors: data.professors || 0,
    dotsents: data.dotsents || 0,
    academics: data.academics || 0,
    potential: data.potential || 0,
    studentsCount: (data.yearly_data || INITIAL_STATS.studentsCount).map((y: any) => ({
      year: y.year,
      count: y.professional_development_count || y.count || 0,
      retraining: y.retraining_count || y.retraining || 0,
    })),
    retrainingCount: (data.yearly_data || INITIAL_STATS.retrainingCount).map((y: any) => ({
      year: y.year,
      count: y.retraining_count || y.count || 0,
    })),
  };
}

function transformAppContent(data: any): AppContent {
  return {
    history: data?.history || '',
    structure: data?.structure || '',
    structureImage: data?.structure_image_url || '',
  };
}

function transformInternationalContent(data: any): InternationalContent {
  return {
    title: data?.title || "Xalqaro aloqalar to'g'risida",
    description: data?.description || '',
    photos: (data?.photos || []).map((item: any) => ({
      id: String(item.id),
      imageUrl: item.image_url || '',
      order: item.order || 0,
    })),
    videos: (data?.videos || []).map((item: any) => ({
      id: String(item.id),
      title: item.title || '',
      videoUrl: item.video_url || '',
      embedUrl: item.embed_url || item.video_url || '',
      order: item.order || 0,
    })),
  };
}

function transformForeignPartner(item: any): ForeignPartner {
  return {
    id: String(item.id),
    organizationName: item.organization_name,
    country: item.country,
    shortInfo: item.short_info,
    imageUrl: item.image_url || '',
    order: item.order || 0,
  };
}

function transformCollaborationProject(item: any): CollaborationProject {
  return {
    id: String(item.id),
    name: item.name,
    description: item.description,
    date: item.date,
    status: item.status,
    statusDisplay: item.status_display || '',
    order: item.order || 0,
  };
}

function transformArtGalleryItem(item: any): ArtGalleryItem {
  return {
    id: String(item.id),
    imageUrl: item.image_url || '',
    name: item.name,
    authorFullName: item.author_full_name,
    text: item.text,
    images: (item.images || []).map((img: any) => ({
      id: String(img.id),
      imageUrl: img.image_url || '',
      order: img.order || 0,
    })),
    order: item.order || 0,
  };
}

export const BackendAPI = {
  /**
   * Get all data for initial load - try API first, fallback to localStorage
   */
  async getAllData() {
    try {
      console.log('Calling API: /all-data/');
      const data = await apiRequest<any>('/all-data/');
      console.log('API Response:', data);
      return {
        news: (data.news || []).map(transformNewsItem),
        gallery: (data.gallery || []).map(transformGalleryItem),
        teachers: (data.teachers || []).map(transformTeacher),
        courses: (data.courses || []).map(transformCourse),
        personnel: (data.personnel || []).map(transformPersonnel),
        stats: transformStatistics(data.stats),
        documents: (data.documents || []).map(transformDocument),
        pdPlans: (data.listeners || data.pdPlans || []).map(transformPDPlanRecord),
        journalIssues: (data.journalIssues || []).map(transformJournalIssue),
        about: transformAppContent(data.about),
        notes: data.about?.student_notes || "Tinglovchilar uchun eslatma matni...",
        internationalContent: transformInternationalContent(data.international),
        foreignPartners: (data.foreignPartners || []).map(transformForeignPartner),
        collaborationProjects: (data.collaborationProjects || []).map(transformCollaborationProject),
        artGallery: (data.artGallery || []).map(transformArtGalleryItem),
      };
    } catch (error) {
      console.warn('API error, using localStorage fallback:', error);
      // Fallback to localStorage for offline capability
      const statsStr = localStorage.getItem('bt_stats');
      return {
        news: JSON.parse(localStorage.getItem('bt_news') || '[]') as NewsItem[],
        gallery: JSON.parse(localStorage.getItem('bt_gallery') || '[]') as GalleryItem[],
        teachers: JSON.parse(localStorage.getItem('bt_teachers') || '[]') as Teacher[],
        courses: JSON.parse(localStorage.getItem('bt_courses') || '[]') as Course[],
        personnel: JSON.parse(localStorage.getItem('bt_personnel') || '[]') as Personnel[],
        stats: statsStr ? JSON.parse(statsStr) : INITIAL_STATS,
        documents: JSON.parse(localStorage.getItem('bt_docs') || '[]') as Document[],
        pdPlans: JSON.parse(localStorage.getItem('bt_plans') || '[]') as PDPlanRecord[],
        journalIssues: JSON.parse(localStorage.getItem('bt_journal') || '[]') as JournalIssue[],
        about: JSON.parse(localStorage.getItem('bt_about') || '{"history": "", "structure": "", "structureImage": ""}') as AppContent,
        notes: localStorage.getItem('bt_notes') || "Tinglovchilar uchun eslatma matni...",
        internationalContent: JSON.parse(localStorage.getItem('bt_international_content') || "{\"title\":\"Xalqaro aloqalar to'g'risida\",\"description\":\"\",\"photos\":[],\"videos\":[]}") as InternationalContent,
        foreignPartners: JSON.parse(localStorage.getItem('bt_foreign_partners') || '[]') as ForeignPartner[],
        collaborationProjects: JSON.parse(localStorage.getItem('bt_collaboration_projects') || '[]') as CollaborationProject[],
        artGallery: JSON.parse(localStorage.getItem('bt_art_gallery') || '[]') as ArtGalleryItem[],
      };
    }
  },

  async saveNews(news: NewsItem[]) {
    localStorage.setItem('bt_news', JSON.stringify(news));
    return { success: true };
  },

  async saveGallery(gallery: GalleryItem[]) {
    localStorage.setItem('bt_gallery', JSON.stringify(gallery));
    return { success: true };
  },

  async saveTeachers(teachers: Teacher[]) {
    localStorage.setItem('bt_teachers', JSON.stringify(teachers));
    return { success: true };
  },

  async saveCourses(courses: Course[]) {
    localStorage.setItem('bt_courses', JSON.stringify(courses));
    return { success: true };
  },

  async savePersonnel(personnel: Personnel[]) {
    localStorage.setItem('bt_personnel', JSON.stringify(personnel));
    return { success: true };
  },

  async saveStats(stats: Statistics) {
    localStorage.setItem('bt_stats', JSON.stringify(stats));
    try {
      await apiRequest('/statistics/', {
        method: 'POST',
        body: JSON.stringify({
          professors: stats.professors,
          dotsents: stats.dotsents,
          academics: stats.academics,
          potential: stats.potential,
        }),
      });
    } catch (e) {
      console.warn('Could not save stats to API:', e);
    }
    return { success: true };
  },

  async saveDocuments(docs: Document[]) {
    localStorage.setItem('bt_docs', JSON.stringify(docs));
    return { success: true };
  },

  async savePlans(plans: PDPlanRecord[]) {
    localStorage.setItem('bt_plans', JSON.stringify(plans));
    return { success: true };
  },

  async saveJournalIssues(issues: JournalIssue[]) {
    localStorage.setItem('bt_journal', JSON.stringify(issues));
    return { success: true };
  },

  async saveContent(about: AppContent, notes: string) {
    localStorage.setItem('bt_about', JSON.stringify(about));
    localStorage.setItem('bt_notes', notes);
    try {
      await apiRequest('/content/', {
        method: 'POST',
        body: JSON.stringify({
          history: about.history,
          structure: about.structure,
          structure_image_url: about.structureImage,
          student_notes: notes,
        }),
      });
    } catch (e) {
      console.warn('Could not save content to API:', e);
    }
    return { success: true };
  },

  async login(credentials: { username: string; password: string }) {
    // Try Django JWT endpoint first
    try {
      const response = await fetch(`${API_BASE_URL}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.access) {
          localStorage.setItem(TOKEN_KEY, data.access);
          localStorage.setItem(REFRESH_KEY, data.refresh);
          return { success: true, token: data.access };
        }
      }
    } catch (e) {
      console.warn('JWT login failed, trying custom login...');
    }

    // Try custom login endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.token) {
          localStorage.setItem(TOKEN_KEY, data.token);
          if (data.refresh) {
            localStorage.setItem(REFRESH_KEY, data.refresh);
          }
          return { success: true, token: data.token };
        }
      }
    } catch (e) {
      console.warn('Custom login failed...');
    }

    // Fallback for development (no backend)
    if (credentials.username === 'admin' && credentials.password === 'admin123') {
      localStorage.removeItem(TOKEN_KEY); // Don't use fake token
      localStorage.removeItem(REFRESH_KEY);
      return { success: true, token: 'local' };
    }
    
    throw new Error("Login yoki parol noto'g'ri!");
  },

  async refreshToken() {
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) return false;
    
    try {
      const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.access) {
          localStorage.setItem(TOKEN_KEY, data.access);
          return true;
        }
      }
    } catch (e) {
      console.warn('Token refresh failed');
    }
    
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    return false;
  },

  async bulkImportListeners(file: File, recordType: 'certificate' | 'diploma') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('record_type', recordType === 'diploma' ? 'QT' : 'MO');
    return apiRequest<any>('/listeners/bulk_import/', {
      method: 'POST',
      body: formData,
    });
  },

  async searchListener(series: string, number: string) {
    try {
      return await apiRequest<any>(`/listeners/search/?series=${encodeURIComponent(series)}&number=${encodeURIComponent(number)}`);
    } catch (e) {
      return { found: false };
    }
  },

  // ===== FILE UPLOAD METHODS =====

  // Upload gallery image
  async uploadGalleryImage(file: File, caption: string, mediaType: 'image' | 'video' = 'image') {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('caption', caption);
    formData.append('media_type', mediaType);
    return apiRequest<any>('/gallery/', {
      method: 'POST',
      body: formData,
    });
  },

  async deleteGalleryItem(id: string) {
    return apiRequest<any>(`/gallery/${id}/`, { method: 'DELETE' });
  },

  // Upload news with image file
  async createNews(data: { title: string; content: string; isImportant?: boolean }, imageFile?: File) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('content', data.content);
    formData.append('is_active', 'true'); // Always active by default
    if (data.isImportant) formData.append('is_important', 'true');
    if (imageFile) formData.append('image', imageFile);
    return apiRequest<any>('/news/', {
      method: 'POST',
      body: formData,
    });
  },

  async updateNews(id: string, data: { title?: string; content?: string; isImportant?: boolean; isActive?: boolean }, imageFile?: File) {
    const formData = new FormData();
    if (data.title) formData.append('title', data.title);
    if (data.content) formData.append('content', data.content);
    if (data.isImportant !== undefined) formData.append('is_important', data.isImportant ? 'true' : 'false');
    if (data.isActive !== undefined) formData.append('is_active', data.isActive ? 'true' : 'false');
    if (imageFile) formData.append('image', imageFile);
    return apiRequest<any>(`/news/${id}/`, {
      method: 'PATCH',
      body: formData,
    });
  },

  async toggleNewsActive(id: string, isActive: boolean) {
    return apiRequest<any>(`/news/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive }),
    });
  },

  async deleteNews(id: string) {
    return apiRequest<any>(`/news/${id}/`, { method: 'DELETE' });
  },

  // Upload teacher with photo file
  async createTeacher(data: { fullName: string; position: string; degree?: string; title?: string }, photoFile?: File) {
    const formData = new FormData();
    formData.append('full_name', data.fullName);
    formData.append('position', data.position);
    if (data.degree) formData.append('degree', data.degree);
    if (data.title) formData.append('title', data.title);
    if (photoFile) formData.append('photo', photoFile);
    return apiRequest<any>('/teachers/', {
      method: 'POST',
      body: formData,
    });
  },

  async deleteTeacher(id: string) {
    return apiRequest<any>(`/teachers/${id}/`, { method: 'DELETE' });
  },

  // Upload personnel with photo file
  async createPersonnel(data: { fullName: string; position: string; phone?: string; receptionHours?: string; category: string }, photoFile?: File) {
    const formData = new FormData();
    formData.append('full_name', data.fullName);
    formData.append('position', data.position);
    formData.append('category', data.category);
    if (data.phone) formData.append('phone', data.phone);
    if (data.receptionHours) formData.append('reception_hours', data.receptionHours);
    if (photoFile) formData.append('photo', photoFile);
    return apiRequest<any>('/personnel/', {
      method: 'POST',
      body: formData,
    });
  },

  async deletePersonnel(id: string) {
    return apiRequest<any>(`/personnel/${id}/`, { method: 'DELETE' });
  },

  // Upload journal issue with PDF and thumbnail files
  async createJournalIssue(data: { title: string; year: string }, pdfFile?: File, thumbnailFile?: File) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('year', data.year);
    if (pdfFile) formData.append('pdf_file', pdfFile);
    if (thumbnailFile) formData.append('thumbnail', thumbnailFile);
    return apiRequest<any>('/journal/', {
      method: 'POST',
      body: formData,
    });
  },

  async deleteJournalIssue(id: string) {
    return apiRequest<any>(`/journal/${id}/`, { method: 'DELETE' });
  },

  // Upload document with file
  async createDocument(data: { title: string; category: string; fileType: string }, docFile?: File) {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('category', data.category);
    formData.append('file_type', data.fileType);
    if (docFile) formData.append('file', docFile);
    return apiRequest<any>('/documents/', {
      method: 'POST',
      body: formData,
    });
  },

  async deleteDocument(id: string) {
    return apiRequest<any>(`/documents/${id}/`, { method: 'DELETE' });
  },

  // Create listener (single)
  async createListener(data: Partial<PDPlanRecord>) {
    return apiRequest<any>('/listeners/', {
      method: 'POST',
      body: JSON.stringify({
        record_type: data.recordType,
        full_name: data.fullName,
        workplace: data.workplace,
        course_type: data.courseType,
        series: data.series,
        number: data.number,
        duration: data.duration,
      }),
    });
  },

  async deleteListener(id: string) {
    return apiRequest<any>(`/listeners/${id}/`, { method: 'DELETE' });
  },

  // Course operations
  async createCourse(data: { title: string; type: string; duration?: string; description?: string }) {
    return apiRequest<any>('/courses/', {
      method: 'POST',
      body: JSON.stringify({
        title: data.title,
        course_type: data.type,
        duration: data.duration,
        description: data.description,
      }),
    });
  },

  async deleteCourse(id: string) {
    return apiRequest<any>(`/courses/${id}/`, { method: 'DELETE' });
  },

  // Save content with structure image file
  async saveContentWithFile(data: { history: string; structure: string; studentNotes: string }, structureImageFile?: File) {
    const formData = new FormData();
    formData.append('history', data.history);
    formData.append('structure', data.structure);
    formData.append('student_notes', data.studentNotes);
    if (structureImageFile) formData.append('structure_image', structureImageFile);
    return apiRequest<any>('/content/', {
      method: 'POST',
      body: formData,
    });
  },

  // Refresh data from server
  async refreshData() {
    return this.getAllData();
  },
};
