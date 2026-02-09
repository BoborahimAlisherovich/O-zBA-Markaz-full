// News with inline images
export interface NewsImage {
  id: string;
  imageUrl: string;
  order: number;
}

export interface NewsItem {
  id: string;
  title: string;
  content: string;
  date: string;
  image: string; // First image URL for backwards compatibility
  images?: NewsImage[]; // All images
  isImportant?: boolean;
  isActive?: boolean;
}

// Gallery image (single image in album)
export interface GalleryImage {
  id: string;
  imageUrl: string;
  order: number;
}

// Gallery album with multiple images
export interface GalleryItem {
  id: string;
  title: string;
  coverImageUrl: string;
  images: GalleryImage[];
  order: number;
  isActive?: boolean;
}

// Teacher without URL fields
export interface Teacher {
  id: string;
  fullName: string;
  position: string;
  degree: string;
  title: string;
  photoUrl?: string;
}

export interface Course {
  id: string;
  title: string;
  type: 'retraining' | 'professional_development';
  duration?: string;
  description?: string;
}

export interface Personnel {
  id: string;
  fullName: string;
  position: string;
  phone: string;
  receptionHours: string;
  photoUrl?: string;
  category: 'leadership' | 'staff';
}

// Journal without title and description
export interface JournalIssue {
  id: string;
  year: string;
  issueNumber?: string;
  pdfUrl: string;
  thumbnailUrl?: string;
}

// Document simplified
export interface Document {
  id: string;
  title: string;
  category: 'regulatory' | 'plan' | 'open_data';
  fileUrl: string;
  date: string;
}

// Listener with MO/QT types (replacing separate Certificate)
export interface PDPlanRecord {
  id: string;
  recordType: 'MO' | 'QT'; // MO - Malaka oshirish, QT - Qayta tayyorlash
  fullName: string;
  workplace: string; // Ish joyi
  courseType: string; // Yo'nalish
  series: string; // Seriya
  number: string; // Raqam
  duration: string; // O'qish muddati (davri)
  isVerified?: boolean;
}

export interface Statistics {
  professors: number;
  dotsents: number;
  academics: number;
  potential: number;
  studentsCount: { year: string; count: number; retraining: number }[];
  retrainingCount: { year: string; count: number }[];
}
