import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { ChevronRight, ChevronLeft, Award, Users, GraduationCap, TrendingUp, Zap, Image as ImageIcon, BookOpen, Layers, ShieldCheck, CheckCircle2, XCircle, Globe, Palette, Gavel, X, FileText, Briefcase } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PDPlanRecord, GalleryItem } from '../types';

// Animation hook for scroll reveal
const useScrollReveal = () => {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, isVisible };
};

const Home: React.FC = () => {
  const { news, stats, gallery, teachers, courses, pdPlans } = useApp();
  
  // Reestr state
  const [activeReestrTab, setActiveReestrTab] = useState<'mo' | 'qt'>('mo');
  const [docNumber, setDocNumber] = useState('');
  const [searchResult, setSearchResult] = useState<{status: 'idle' | 'found' | 'not_found', data?: PDPlanRecord}>({status: 'idle'});
  
  // News pagination
  const [newsPage, setNewsPage] = useState(1);
  const newsPerPage = 8;
  const totalNewsPages = Math.ceil(news.length / newsPerPage);
  const paginatedNews = news.slice((newsPage - 1) * newsPerPage, newsPage * newsPerPage);
  
  // Gallery modal state
  const [selectedGallery, setSelectedGallery] = useState<GalleryItem | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  
  // Course detail expansion
  const [expandedCourse, setExpandedCourse] = useState<string | null>(null);

  // Auto-slide effect for gallery
  useEffect(() => {
    if (!selectedGallery || !isAutoPlaying) return;
    const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
    if (allImages.length <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % allImages.length);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [selectedGallery, isAutoPlaying]);

  const openGalleryModal = useCallback((item: GalleryItem) => {
    setSelectedGallery(item);
    setCurrentImageIndex(0);
    setIsAutoPlaying(true);
  }, []);

  const closeGalleryModal = useCallback(() => {
    setSelectedGallery(null);
    setCurrentImageIndex(0);
  }, []);

  const nextImage = useCallback(() => {
    if (!selectedGallery) return;
    const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
    setCurrentImageIndex((prev) => (prev + 1) % allImages.length);
    setIsAutoPlaying(false);
  }, [selectedGallery]);

  const prevImage = useCallback(() => {
    if (!selectedGallery) return;
    const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
    setCurrentImageIndex((prev) => (prev - 1 + allImages.length) % allImages.length);
    setIsAutoPlaying(false);
  }, [selectedGallery]);

  const totalMalaka = stats.studentsCount.reduce((sum, item) => sum + item.count, 0);
  const totalQayta = stats.studentsCount.reduce((sum, item) => sum + item.retraining, 0);
  const totalOverall = totalMalaka + totalQayta;

  const distributionData = [
    { name: 'Malaka oshirish', value: totalMalaka, color: '#10b981' },
    { name: 'Qayta tayyorlash', value: totalQayta, color: '#3b82f6' },
  ];

  const yearlyData = stats.studentsCount.map(item => ({
    name: item.year,
    malaka: item.count,
    qayta: item.retraining
  }));

  const retrainingCourses = courses.filter(c => c.type === 'retraining');
  const pdCourses = courses.filter(c => c.type === 'professional_development');

  const handleReestrSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!docNumber.trim()) return;

    const targetType = activeReestrTab === 'mo' ? 'MO' : 'QT';
    const searchNum = docNumber.trim();
    
    // Filter by selected type (MO or QT)
    const typeRecords = pdPlans.filter(p => 
      (p.recordType || '').toUpperCase() === targetType ||
      (p.series || '').toUpperCase() === targetType
    );
    
    // Try exact match first
    let found = typeRecords.find(p => p.number.trim() === searchNum);
    
    // Try case-insensitive
    if (!found) {
      found = typeRecords.find(p => p.number.toLowerCase().trim() === searchNum.toLowerCase());
    }
    
    // Try ending match
    if (!found) {
      found = typeRecords.find(p => p.number.trim().endsWith(searchNum));
    }
    
    // Try contains
    if (!found) {
      found = typeRecords.find(p => p.number.includes(searchNum));
    }

    if (found) {
      setSearchResult({status: 'found', data: found});
    } else {
      setSearchResult({status: 'not_found'});
    }
  };

  const usefulLinks = [
    { name: "Masofaviy ta'lim", url: "https://mt.uzbamalaka.uz/", icon: <Globe size={32} />, color: "bg-gradient-to-br from-blue-500 to-blue-700" },
    { name: "Badiiy akademiya", url: "https://art-academy.uz/", icon: <Palette size={32} />, color: "bg-gradient-to-br from-amber-500 to-orange-600" },
    { name: "MY.BIMM.UZ", url: "https://my.bimm.uz/home", icon: <ShieldCheck size={32} />, color: "bg-gradient-to-br from-emerald-500 to-teal-600" },
    { name: "LEX.UZ", url: "https://lex.uz/uz/", icon: <Gavel size={32} />, color: "bg-gradient-to-br from-red-500 to-rose-700" },
  ];

  // Scroll reveal sections
  const statsReveal = useScrollReveal();
  const reestrReveal = useScrollReveal();
  const chartsReveal = useScrollReveal();
  const newsReveal = useScrollReveal();
  const teachersReveal = useScrollReveal();
  const coursesReveal = useScrollReveal();
  const galleryReveal = useScrollReveal();
  const linksReveal = useScrollReveal();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white overflow-x-hidden">
      {/* Hero Section with Parallax Effect */}
      <section className="relative h-[85vh] overflow-hidden flex items-center">
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=2071&auto=format&fit=crop" 
            alt="Hero" 
            className="w-full h-full object-cover"
            style={{ filter: 'brightness(0.25)' }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-slate-50"></div>
        </div>
        
        <div className="container mx-auto px-6 relative z-10 text-white">
          <div className="max-w-4xl animate-fade-in-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full mb-8">
              <Zap size={14} className="text-yellow-400 fill-yellow-400" />
              <span className="text-xs font-semibold tracking-wide">Rasmiy veb-sahifa</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-[1.1] tracking-tight">
              Badiiy ta'limning <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">kelajagi</span> biz bilan
            </h1>
            <p className="text-xl text-gray-300 mb-10 leading-relaxed max-w-2xl font-light">
              Malaka oshirish va qayta tayyorlash markazida professional pedagoglar tayyorlaymiz
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/about" className="group px-8 py-4 bg-white text-slate-900 hover:bg-blue-500 hover:text-white rounded-2xl font-bold transition-all duration-300 shadow-2xl shadow-white/20 flex items-center gap-3">
                Batafsil
                <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link to="/students" className="px-8 py-4 bg-white/10 backdrop-blur-xl border border-white/30 text-white hover:bg-white/20 rounded-2xl font-bold transition-all duration-300">
                Tinglovchilar
              </Link>
            </div>
          </div>
        </div>
        
        {/* Scroll indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-8 h-12 border-2 border-white/30 rounded-full flex justify-center pt-2">
            <div className="w-1.5 h-3 bg-white/60 rounded-full animate-scroll-down"></div>
          </div>
        </div>
      </section>

      {/* Stats Cards */}
      <section 
        ref={statsReveal.ref}
        className={`container mx-auto px-6 -mt-20 relative z-20 transition-all duration-1000 ${
          statsReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Professorlar', value: stats.professors, icon: <GraduationCap size={24} />, gradient: 'from-blue-500 to-indigo-600' },
            { label: 'Dotsentlar', value: stats.dotsents, icon: <Users size={24} />, gradient: 'from-emerald-500 to-teal-600' },
            { label: 'Akademiklar', value: stats.academics, icon: <Award size={24} />, gradient: 'from-amber-500 to-orange-600' },
            { label: 'Ilmiy salohiyat', value: `${stats.potential}%`, icon: <TrendingUp size={24} />, gradient: 'from-purple-500 to-pink-600' },
          ].map((stat, idx) => (
            <div 
              key={idx} 
              className="group bg-white p-6 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
              style={{ transitionDelay: `${idx * 100}ms` }}
            >
              <div className={`w-14 h-14 bg-gradient-to-br ${stat.gradient} text-white rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                {stat.icon}
              </div>
              <p className="text-3xl font-black text-slate-900 mb-1">{stat.value}</p>
              <p className="text-sm font-medium text-slate-500">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* REESTR MODULE - with MO/QT Selection */}
      <section 
        ref={reestrReveal.ref}
        className={`container mx-auto px-6 py-24 transition-all duration-1000 ${
          reestrReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-full mb-6">
              <FileText size={18} className="text-blue-600" />
              <span className="text-sm font-bold text-blue-600">Online tekshiruv</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-slate-900 mb-4">
              Hujjat haqiqiyligini tekshiring
            </h2>
            <p className="text-lg text-slate-500">
              Diplom yoki sertifikat turini tanlang va raqamni kiriting
            </p>
          </div>

          <div className="bg-white rounded-[2rem] shadow-2xl shadow-slate-200/50 overflow-hidden border border-slate-100">
            {/* Type Selection Tabs */}
            <div className="grid grid-cols-2 border-b border-slate-100">
              <button 
                onClick={() => { setActiveReestrTab('mo'); setSearchResult({status: 'idle'}); setDocNumber(''); }}
                className={`relative py-6 px-6 text-center transition-all ${
                  activeReestrTab === 'mo' 
                    ? 'bg-emerald-50 text-emerald-700' 
                    : 'bg-slate-50 text-slate-400 hover:bg-slate-100'
                }`}
              >
                <div className={`w-16 h-16 mx-auto mb-3 rounded-2xl flex items-center justify-center transition-all ${
                  activeReestrTab === 'mo' 
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30' 
                    : 'bg-slate-200 text-slate-400'
                }`}>
                  <Award size={28} />
                </div>
                <p className="font-black text-lg">Sertifikat (MO)</p>
                <p className="text-xs font-medium mt-1 opacity-70">Malaka oshirish</p>
                {activeReestrTab === 'mo' && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
                )}
              </button>
              
              <button 
                onClick={() => { setActiveReestrTab('qt'); setSearchResult({status: 'idle'}); setDocNumber(''); }}
                className={`relative py-6 px-6 text-center transition-all ${
                  activeReestrTab === 'qt' 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'bg-slate-50 text-slate-400 hover:bg-slate-100'
                }`}
              >
                <div className={`w-16 h-16 mx-auto mb-3 rounded-2xl flex items-center justify-center transition-all ${
                  activeReestrTab === 'qt' 
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30' 
                    : 'bg-slate-200 text-slate-400'
                }`}>
                  <Briefcase size={28} />
                </div>
                <p className="font-black text-lg">Diplom (QT)</p>
                <p className="text-xs font-medium mt-1 opacity-70">Qayta tayyorlash</p>
                {activeReestrTab === 'qt' && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500"></div>
                )}
              </button>
            </div>

            {/* Search Form */}
            <form onSubmit={handleReestrSearch} className="p-8">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    {activeReestrTab === 'mo' ? 'Sertifikat' : 'Diplom'} raqami
                  </label>
                  <div className="relative">
                    <span className={`absolute left-4 top-1/2 -translate-y-1/2 font-black text-lg ${
                      activeReestrTab === 'mo' ? 'text-emerald-500' : 'text-blue-500'
                    }`}>
                      {activeReestrTab === 'mo' ? 'MO' : 'QT'}
                    </span>
                    <input 
                      type="text" 
                      placeholder="000831" 
                      className="w-full pl-16 pr-4 py-4 bg-slate-50 border-2 border-slate-100 rounded-xl text-slate-700 font-bold text-xl outline-none focus:border-blue-500 transition-all"
                      value={docNumber}
                      onChange={(e) => setDocNumber(e.target.value)}
                    />
                  </div>
                </div>
                <button 
                  type="submit" 
                  className={`px-10 py-4 rounded-xl font-black text-white text-sm uppercase tracking-wider transition-all hover:scale-105 active:scale-95 shadow-xl ${
                    activeReestrTab === 'mo' 
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-600 shadow-emerald-500/30' 
                      : 'bg-gradient-to-r from-blue-500 to-indigo-600 shadow-blue-500/30'
                  }`}
                >
                  Tekshirish
                </button>
              </div>
            </form>

            {/* Search Result */}
            {searchResult.status !== 'idle' && (
              <div className="px-8 pb-8 animate-fade-in-up">
                {searchResult.status === 'found' && searchResult.data ? (
                  <div className={`p-6 rounded-2xl ${
                    searchResult.data.recordType === 'QT' ? 'bg-blue-50' : 'bg-emerald-50'
                  }`}>
                    <div className="flex items-start gap-4">
                      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center shrink-0 ${
                        searchResult.data.recordType === 'QT' ? 'bg-blue-500' : 'bg-emerald-500'
                      } text-white`}>
                        <CheckCircle2 size={32} />
                      </div>
                      <div className="flex-1">
                        <div className="flex flex-wrap items-center gap-3 mb-4">
                          <h4 className="text-2xl font-black text-slate-900">{searchResult.data.fullName}</h4>
                          <span className={`px-3 py-1 text-white text-xs font-black rounded-full ${
                            searchResult.data.recordType === 'QT' ? 'bg-blue-500' : 'bg-emerald-500'
                          }`}>
                            HAQIQIY
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          {[
                            { label: 'Hujjat turi', value: searchResult.data.recordType === 'QT' ? 'Qayta tayyorlash diplomi' : 'Malaka oshirish sertifikati' },
                            { label: 'Seriya va raqam', value: `${searchResult.data.series} ${searchResult.data.number}` },
                            { label: 'Ish joyi', value: searchResult.data.workplace || '-' },
                            { label: "Yo'nalishi", value: searchResult.data.courseType || '-' },
                            { label: "O'qish muddati", value: searchResult.data.duration || '-' },
                          ].map((item, idx) => (
                            <div key={idx}>
                              <p className="text-xs font-bold text-slate-400 uppercase mb-1">{item.label}</p>
                              <p className="text-sm font-bold text-slate-700">{item.value}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-8 bg-red-50 rounded-2xl text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-500 text-white flex items-center justify-center">
                      <XCircle size={32} />
                    </div>
                    <h4 className="text-xl font-black text-slate-900 mb-2">Ma'lumot topilmadi</h4>
                    <p className="text-slate-500 mb-4">Kiritilgan hujjat bazada mavjud emas</p>
                    <button 
                      onClick={() => setSearchResult({status: 'idle'})} 
                      className="text-red-600 font-bold text-sm hover:underline"
                    >
                      Qayta urinish
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Charts Section */}
      <section 
        ref={chartsReveal.ref}
        className={`container mx-auto px-6 py-16 transition-all duration-1000 ${
          chartsReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/40 border border-slate-100">
            <h3 className="text-xl font-black text-slate-900 mb-6">Umumiy taqsimot</h3>
            <div className="relative h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={distributionData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} paddingAngle={5} dataKey="value">
                    {distributionData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center flex-col pointer-events-none">
                <span className="text-4xl font-black text-slate-900">{totalOverall}</span>
                <span className="text-sm text-slate-500">Jami</span>
              </div>
            </div>
            <div className="flex justify-center gap-8 mt-4">
              {distributionData.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm font-medium text-slate-600">{item.name}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/40 border border-slate-100">
            <h3 className="text-xl font-black text-slate-900 mb-6">Yillar kesimida</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={yearlyData}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 40px rgba(0,0,0,0.1)' }}
                  />
                  <Bar name="Malaka oshirish" dataKey="malaka" fill="#10b981" radius={[4,4,0,0]} />
                  <Bar name="Qayta tayyorlash" dataKey="qayta" fill="#3b82f6" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>
      
      {/* News Section - 2 per row, with pagination */}
      <section 
        ref={newsReveal.ref}
        className={`container mx-auto px-6 py-16 transition-all duration-1000 ${
          newsReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="flex justify-between items-end mb-12">
          <div>
            <span className="text-sm font-bold text-blue-600 uppercase tracking-wider">Yangiliklar</span>
            <h2 className="text-4xl font-black text-slate-900 mt-2">So'nggi yangiliklar</h2>
          </div>
          {totalNewsPages > 1 && (
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setNewsPage(p => Math.max(1, p - 1))}
                disabled={newsPage === 1}
                className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all"
              >
                <ChevronLeft size={20} />
              </button>
              <span className="px-4 py-2 text-sm font-bold text-slate-600">
                {newsPage} / {totalNewsPages}
              </span>
              <button 
                onClick={() => setNewsPage(p => Math.min(totalNewsPages, p + 1))}
                disabled={newsPage === totalNewsPages}
                className="w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </div>
        
        {paginatedNews.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {paginatedNews.map((item, idx) => (
              <Link 
                to={`/news/${item.id}`} 
                key={item.id} 
                className="group bg-white rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 border border-slate-100"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="relative h-64 overflow-hidden">
                  <img 
                    src={item.images?.[0]?.imageUrl || item.image || '/placeholder.jpg'} 
                    alt={item.title} 
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                  {item.isImportant && (
                    <div className="absolute top-4 left-4 px-3 py-1.5 bg-red-500 text-white text-xs font-bold uppercase rounded-full flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
                      Muhim
                    </div>
                  )}

                </div>
                <div className="p-6">
                  <span className="text-sm font-medium text-slate-400">{item.date}</span>
                  <h3 className="text-xl font-black text-slate-900 mt-2 mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-slate-500 line-clamp-2 text-sm">{item.content}</p>
                  <div className="flex items-center gap-2 mt-4 text-blue-600 font-bold text-sm group-hover:gap-3 transition-all">
                    Batafsil <ChevronRight size={16} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="py-20 text-center bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
            <p className="text-slate-400 font-medium">Hozircha yangiliklar mavjud emas</p>
          </div>
        )}
      </section>

      {/* Teachers Section - mehrgo.uz style */}
      <section 
        ref={teachersReveal.ref}
        className={`py-24 bg-gradient-to-b from-slate-50 to-white transition-all duration-1000 ${
          teachersReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-sm font-bold text-emerald-600 uppercase tracking-wider">Jamoa</span>
            <h2 className="text-4xl md:text-5xl font-black text-slate-900 mt-2 mb-4">Bizning ustozlar</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">
              Yuqori malakali mutaxassislar va tajribali pedagoglar jamoasi
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {teachers.length > 0 ? teachers.map((teacher, idx) => (
              <div 
                key={teacher.id} 
                className="group bg-white rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                {/* Square Image */}
                <div className="relative aspect-square overflow-hidden">
                  <img 
                    src={teacher.photoUrl || 'https://via.placeholder.com/400x400?text=Ustoz'} 
                    alt={teacher.fullName} 
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
                
                {/* Info */}
                <div className="p-5 text-center">
                  <h3 className="text-lg font-black text-slate-900 mb-1 line-clamp-1">{teacher.fullName}</h3>
                  <p className="text-sm font-bold text-emerald-600 mb-2">{teacher.position}</p>
                  <div className="pt-3 border-t border-slate-100">
                    <p className="text-xs text-slate-500 line-clamp-1">{teacher.degree}</p>
                    {teacher.title && (
                      <p className="text-xs text-slate-400 mt-1">{teacher.title}</p>
                    )}
                  </div>
                </div>
              </div>
            )) : (
              <div className="col-span-full py-20 text-center bg-white rounded-3xl border-2 border-dashed border-slate-200">
                <p className="text-slate-400 font-medium">Ma'lumotlar kiritilmagan</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Courses Section */}
      <section 
        ref={coursesReveal.ref}
        className={`container mx-auto px-6 py-16 transition-all duration-1000 ${
          coursesReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="text-center mb-12">
          <span className="text-sm font-bold text-blue-600 uppercase tracking-wider">Ta'lim</span>
          <h2 className="text-4xl font-black text-slate-900 mt-2">Bizning dasturlar</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Retraining */}
          <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-black">Qayta tayyorlash</h3>
                  <p className="text-blue-200 text-sm mt-1">Professional qayta tayyorlov kurslari</p>
                </div>
                <Layers size={40} className="opacity-50" />
              </div>
            </div>
            <div className="p-6 space-y-3 max-h-[400px] overflow-y-auto">
              {retrainingCourses.length > 0 ? retrainingCourses.map(course => (
                <div 
                  key={course.id} 
                  className="group p-4 bg-slate-50 hover:bg-blue-50 rounded-2xl transition-all cursor-pointer border border-transparent hover:border-blue-200"
                  onClick={() => setExpandedCourse(expandedCourse === course.id ? null : course.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center text-blue-600">
                        <BookOpen size={18} />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 group-hover:text-blue-700 transition-colors">{course.title}</h4>
                        {course.duration && <p className="text-xs text-slate-400 mt-0.5">{course.duration}</p>}
                      </div>
                    </div>
                    <ChevronRight size={18} className={`text-slate-300 transition-transform ${expandedCourse === course.id ? 'rotate-90' : ''}`} />
                  </div>
                  {expandedCourse === course.id && course.description && (
                    <div className="mt-3 pt-3 border-t border-blue-100 animate-fade-in">
                      <p className="text-sm text-slate-600">{course.description}</p>
                    </div>
                  )}
                </div>
              )) : (
                <div className="py-16 text-center">
                  <p className="text-slate-400">Kurslar kiritilmagan</p>
                </div>
              )}
            </div>
          </div>

          {/* Professional Development */}
          <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100">
            <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-black">Malaka oshirish</h3>
                  <p className="text-emerald-200 text-sm mt-1">Kasbiy mahoratni oshirish kurslari</p>
                </div>
                <TrendingUp size={40} className="opacity-50" />
              </div>
            </div>
            <div className="p-6 space-y-3 max-h-[400px] overflow-y-auto">
              {pdCourses.length > 0 ? pdCourses.map(course => (
                <div 
                  key={course.id} 
                  className="group p-4 bg-slate-50 hover:bg-emerald-50 rounded-2xl transition-all cursor-pointer border border-transparent hover:border-emerald-200"
                  onClick={() => setExpandedCourse(expandedCourse === course.id ? null : course.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center text-emerald-600">
                        <GraduationCap size={18} />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">{course.title}</h4>
                        {course.duration && <p className="text-xs text-slate-400 mt-0.5">{course.duration}</p>}
                      </div>
                    </div>
                    <ChevronRight size={18} className={`text-slate-300 transition-transform ${expandedCourse === course.id ? 'rotate-90' : ''}`} />
                  </div>
                  {expandedCourse === course.id && course.description && (
                    <div className="mt-3 pt-3 border-t border-emerald-100 animate-fade-in">
                      <p className="text-sm text-slate-600">{course.description}</p>
                    </div>
                  )}
                </div>
              )) : (
                <div className="py-16 text-center">
                  <p className="text-slate-400">Kurslar kiritilmagan</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Gallery Section */}
      <section 
        ref={galleryReveal.ref}
        className={`container mx-auto px-6 py-16 transition-all duration-1000 ${
          galleryReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="text-center mb-12">
          <span className="text-sm font-bold text-purple-600 uppercase tracking-wider">Media</span>
          <h2 className="text-4xl font-black text-slate-900 mt-2">Fotogalereya</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {gallery.length > 0 ? gallery.slice(0, 8).map((item, idx) => (
            <div 
              key={item.id} 
              onClick={() => openGalleryModal(item)}
              className="group relative aspect-square overflow-hidden rounded-2xl bg-slate-200 cursor-pointer shadow-lg hover:shadow-2xl transition-all duration-500"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <img 
                src={item.coverImageUrl} 
                alt={item.title || "Gallery"} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute bottom-4 left-4 right-4">
                  {item.title && <p className="text-white font-bold text-sm truncate">{item.title}</p>}
                </div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <ImageIcon className="text-white" size={24} />
                </div>
              </div>
            </div>
          )) : (
            <div className="col-span-full py-20 text-center bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
              <p className="text-slate-400">Media fayllar kiritilmagan</p>
            </div>
          )}
        </div>
      </section>

      {/* Gallery Modal */}
      {selectedGallery && (
        <div 
          className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center animate-fade-in"
          onClick={closeGalleryModal}
        >
          <button 
            onClick={closeGalleryModal}
            className="absolute top-4 right-4 z-50 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="text-white" size={28} />
          </button>
          
          {selectedGallery.title && (
            <div className="absolute top-4 left-4 z-50">
              <h3 className="text-white text-xl font-bold">{selectedGallery.title}</h3>
            </div>
          )}

          {(() => {
            const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
            return allImages.length > 1 && (
              <>
                <button 
                  onClick={(e) => { e.stopPropagation(); prevImage(); }}
                  className="absolute left-4 top-1/2 -translate-y-1/2 z-50 p-4 bg-white/10 hover:bg-white/20 rounded-full transition-all hover:scale-110"
                >
                  <ChevronLeft className="text-white" size={32} />
                </button>
                <button 
                  onClick={(e) => { e.stopPropagation(); nextImage(); }}
                  className="absolute right-4 top-1/2 -translate-y-1/2 z-50 p-4 bg-white/10 hover:bg-white/20 rounded-full transition-all hover:scale-110"
                >
                  <ChevronRight className="text-white" size={32} />
                </button>
              </>
            );
          })()}

          <div 
            className="relative w-full h-full flex items-center justify-center p-8 md:p-16"
            onClick={(e) => e.stopPropagation()}
          >
            {(() => {
              const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
              return (
                <img 
                  key={allImages[currentImageIndex].id}
                  src={allImages[currentImageIndex].imageUrl} 
                  alt={selectedGallery.title || "Gallery image"}
                  className="max-h-full max-w-full object-contain rounded-lg shadow-2xl animate-scale-in"
                />
              );
            })()}
          </div>

          {(() => {
            const allImages = [{ imageUrl: selectedGallery.coverImageUrl, id: 'cover' }, ...selectedGallery.images];
            return allImages.length > 1 && (
              <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-50">
                {allImages.map((_, idx) => (
                  <button 
                    key={idx}
                    onClick={(e) => { e.stopPropagation(); setCurrentImageIndex(idx); setIsAutoPlaying(false); }}
                    className={`w-2.5 h-2.5 rounded-full transition-all ${
                      idx === currentImageIndex ? 'bg-white scale-125' : 'bg-white/40 hover:bg-white/60'
                    }`}
                  />
                ))}
              </div>
            );
          })()}

          <div className="absolute bottom-6 right-6 z-50">
            <button 
              onClick={(e) => { e.stopPropagation(); setIsAutoPlaying(!isAutoPlaying); }}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                isAutoPlaying ? 'bg-green-500/80 text-white' : 'bg-white/10 text-white/70'
              }`}
            >
              {isAutoPlaying ? 'Avto ▶' : 'To\'xtatildi'}
            </button>
          </div>
        </div>
      )}

      {/* Useful Links Section */}
      <section 
        ref={linksReveal.ref}
        className={`container mx-auto px-6 py-16 transition-all duration-1000 ${
          linksReveal.isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="text-center mb-12">
          <span className="text-sm font-bold text-indigo-600 uppercase tracking-wider">Resurslar</span>
          <h2 className="text-4xl font-black text-slate-900 mt-2">Foydali manzillar</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {usefulLinks.map((link, idx) => (
            <a 
              key={idx} 
              href={link.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="group flex flex-col items-center p-8 bg-white rounded-3xl shadow-lg border border-slate-100 hover:shadow-2xl hover:-translate-y-2 transition-all duration-500"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className={`w-16 h-16 ${link.color} text-white rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                {link.icon}
              </div>
              <h3 className="text-sm font-black text-slate-900 text-center">{link.name}</h3>
            </a>
          ))}
        </div>
      </section>

      {/* Custom CSS for animations */}
      <style>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        @keyframes scroll-down {
          0%, 100% {
            transform: translateY(0);
            opacity: 1;
          }
          50% {
            transform: translateY(8px);
            opacity: 0.5;
          }
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
        }
        
        .animate-fade-in {
          animation: fade-in-up 0.5s ease-out forwards;
        }
        
        .animate-scale-in {
          animation: scale-in 0.5s ease-out forwards;
        }
        
        .animate-scroll-down {
          animation: scroll-down 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default Home;
