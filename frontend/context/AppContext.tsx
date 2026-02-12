
/* Corrected: Fixed malformed import and removed redundant interface definitions to resolve conflicts and syntax errors */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  NewsItem, Personnel, JournalIssue, Document, PDPlanRecord, Statistics,
  AppContent, GalleryItem, Teacher, Course, InternationalContent, ForeignPartner,
  CollaborationProject, ArtGalleryItem
} from '../types';
import { BackendAPI } from '../api/backend';
import { INITIAL_STATS } from '../constants';

interface AppState {
  news: NewsItem[];
  gallery: GalleryItem[];
  teachers: Teacher[];
  courses: Course[];
  personnel: Personnel[];
  journalIssues: JournalIssue[];
  documents: Document[];
  pdPlans: PDPlanRecord[];
  stats: Statistics;
  aboutContent: AppContent;
  studentNotes: string;
  internationalContent: InternationalContent;
  foreignPartners: ForeignPartner[];
  collaborationProjects: CollaborationProject[];
  artGallery: ArtGalleryItem[];
  loading: boolean;
  refreshData: () => Promise<void>;
  updateNews: (n: NewsItem[]) => Promise<void>;
  updateGallery: (g: GalleryItem[]) => Promise<void>;
  updateTeachers: (t: Teacher[]) => Promise<void>;
  updateCourses: (c: Course[]) => Promise<void>;
  updatePersonnel: (p: Personnel[]) => Promise<void>;
  updateStats: (s: Statistics) => Promise<void>;
  updateDocs: (d: Document[]) => Promise<void>;
  updatePlans: (p: PDPlanRecord[]) => Promise<void>;
  updateJournalIssues: (j: JournalIssue[]) => Promise<void>;
  updateContent: (about: AppContent, notes: string) => Promise<void>;
}

const AppContext = createContext<AppState | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [gallery, setGallery] = useState<GalleryItem[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [journalIssues, setJournalIssues] = useState<JournalIssue[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [pdPlans, setPdPlans] = useState<PDPlanRecord[]>([]);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [studentNotes, setStudentNotes] = useState("");
  const [aboutContent, setAboutContent] = useState<AppContent>({ history: "", structure: "" });
  const [internationalContent, setInternationalContent] = useState<InternationalContent>({
    title: "Xalqaro aloqalar to'g'risida",
    description: '',
    photos: [],
    videos: [],
  });
  const [foreignPartners, setForeignPartners] = useState<ForeignPartner[]>([]);
  const [collaborationProjects, setCollaborationProjects] = useState<CollaborationProject[]>([]);
  const [artGallery, setArtGallery] = useState<ArtGalleryItem[]>([]);

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      console.log('Fetching all data from API...');
      const data = await BackendAPI.getAllData();
      console.log('Fetched data:', { newsCount: data.news.length, news: data.news });
      setNews(data.news);
      setGallery(data.gallery);
      setTeachers(data.teachers);
      setCourses(data.courses);
      setPersonnel(data.personnel);
      setStats(data.stats);
      setDocuments(data.documents);
      setPdPlans(data.pdPlans);
      setJournalIssues(data.journalIssues);
      setStudentNotes(data.notes);
      setAboutContent(data.about);
      setInternationalContent(data.internationalContent);
      setForeignPartners(data.foreignPartners);
      setCollaborationProjects(data.collaborationProjects);
      setArtGallery(data.artGallery);
    } catch (error) {
      console.error("Ma'lumotlarni yuklashda xatolik:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const updateNews = async (n: NewsItem[]) => {
    setNews(n);
    await BackendAPI.saveNews(n);
  };

  const updateGallery = async (g: GalleryItem[]) => {
    setGallery(g);
    await BackendAPI.saveGallery(g);
  };

  const updateTeachers = async (t: Teacher[]) => {
    setTeachers(t);
    await BackendAPI.saveTeachers(t);
  };

  const updateCourses = async (c: Course[]) => {
    setCourses(c);
    await BackendAPI.saveCourses(c);
  };

  const updatePersonnel = async (p: Personnel[]) => {
    setPersonnel(p);
    await BackendAPI.savePersonnel(p);
  };

  const updateStats = async (s: Statistics) => {
    setStats(s);
    await BackendAPI.saveStats(s);
  };

  const updateDocs = async (d: Document[]) => {
    setDocuments(d);
    await BackendAPI.saveDocuments(d);
  };

  const updatePlans = async (p: PDPlanRecord[]) => {
    setPdPlans(p);
    await BackendAPI.savePlans(p);
  };

  const updateJournalIssues = async (j: JournalIssue[]) => {
    setJournalIssues(j);
    await BackendAPI.saveJournalIssues(j);
  };

  const updateContent = async (about: AppContent, notes: string) => {
    setAboutContent(about);
    setStudentNotes(notes);
    await BackendAPI.saveContent(about, notes);
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500 mb-4 mx-auto"></div>
          <p className="font-bold tracking-widest uppercase text-xs">Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  return (
    <AppContext.Provider value={{
      news, gallery, teachers, courses, personnel, journalIssues, documents, pdPlans, stats: stats || INITIAL_STATS,
      aboutContent, studentNotes, internationalContent, foreignPartners, collaborationProjects, artGallery, loading,
      refreshData, updateNews, updateGallery, updateTeachers, updateCourses, updatePersonnel, updateStats, updateDocs, updatePlans, updateJournalIssues, updateContent
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
};
