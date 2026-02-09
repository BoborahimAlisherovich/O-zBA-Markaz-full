import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { 
  ArrowLeft, Calendar, ChevronLeft, ChevronRight, Share2, 
  ExternalLink, Play, Clock, Eye, Star, BookOpen 
} from 'lucide-react';

const NewsDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { news } = useApp();
  
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  
  const newsItem = news.find(n => n.id === id);
  
  // Get all images (from images array with imageUrl property)
  const allImages = React.useMemo(() => {
    if (!newsItem) return [];
    const imgs: string[] = [];
    // Add images from NewsImage array
    if (newsItem.images && newsItem.images.length > 0) {
      newsItem.images.forEach(img => {
        if (img.imageUrl) imgs.push(img.imageUrl);
      });
    }
    // Fallback to single image field if no images array
    if (imgs.length === 0 && newsItem.image) {
      imgs.push(newsItem.image);
    }
    return imgs.filter(Boolean);
  }, [newsItem]);

  // Auto-play carousel
  useEffect(() => {
    if (!isAutoPlaying || allImages.length <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentImageIndex(prev => (prev + 1) % allImages.length);
    }, 4000);
    
    return () => clearInterval(interval);
  }, [isAutoPlaying, allImages.length]);

  const nextImage = useCallback(() => {
    setCurrentImageIndex(prev => (prev + 1) % allImages.length);
    setIsAutoPlaying(false);
  }, [allImages.length]);

  const prevImage = useCallback(() => {
    setCurrentImageIndex(prev => (prev - 1 + allImages.length) % allImages.length);
    setIsAutoPlaying(false);
  }, [allImages.length]);

  const goToImage = useCallback((index: number) => {
    setCurrentImageIndex(index);
    setIsAutoPlaying(false);
  }, []);

  // Related news (excluding current)
  const relatedNews = news.filter(n => n.id !== id).slice(0, 3);

  if (!newsItem) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center space-y-6">
          <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mx-auto">
            <BookOpen size={40} className="text-slate-400" />
          </div>
          <h1 className="text-2xl font-black text-slate-800">Yangilik topilmadi</h1>
          <p className="text-slate-500">Ushbu yangilik mavjud emas yoki o'chirilgan</p>
          <Link to="/" className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-2xl font-bold hover:bg-blue-700 transition-colors">
            <ArrowLeft size={20} /> Bosh sahifaga qaytish
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 text-white py-6">
        <div className="container mx-auto px-4">
          <button 
            onClick={() => navigate(-1)} 
            className="flex items-center gap-2 text-blue-300 hover:text-white transition-colors font-medium"
          >
            <ArrowLeft size={20} /> Orqaga
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          
          {/* Main Content Card */}
          <article className="bg-white rounded-[3rem] shadow-2xl shadow-slate-200/50 overflow-hidden border border-slate-100">
            
            {/* Image Carousel */}
            {allImages.length > 0 && (
              <div className="relative">
                {/* Main Image */}
                <div className="relative h-[400px] md:h-[500px] overflow-hidden bg-slate-900">
                  {allImages.map((img, index) => (
                    <div
                      key={index}
                      className={`absolute inset-0 transition-all duration-700 ease-in-out ${
                        index === currentImageIndex 
                          ? 'opacity-100 scale-100' 
                          : 'opacity-0 scale-105'
                      }`}
                    >
                      <img 
                        src={img} 
                        alt={`${newsItem.title} - ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20"></div>
                    </div>
                  ))}
                  
                  {/* Navigation Arrows */}
                  {allImages.length > 1 && (
                    <>
                      <button
                        onClick={prevImage}
                        className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-md hover:bg-white/40 rounded-full flex items-center justify-center text-white transition-all hover:scale-110"
                      >
                        <ChevronLeft size={24} />
                      </button>
                      <button
                        onClick={nextImage}
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-md hover:bg-white/40 rounded-full flex items-center justify-center text-white transition-all hover:scale-110"
                      >
                        <ChevronRight size={24} />
                      </button>
                    </>
                  )}

                  {/* Important Badge */}
                  {newsItem.isImportant && (
                    <div className="absolute top-4 left-4 flex items-center gap-2 px-4 py-2 bg-amber-500 rounded-full text-white text-sm font-bold">
                      <Star size={16} className="fill-white" /> Muhim
                    </div>
                  )}
                </div>

                {/* Thumbnail Navigation */}
                {allImages.length > 1 && (
                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <div className="flex justify-center gap-2">
                      {allImages.map((img, index) => (
                        <button
                          key={index}
                          onClick={() => goToImage(index)}
                          className={`relative overflow-hidden rounded-xl transition-all duration-300 ${
                            index === currentImageIndex 
                              ? 'w-20 h-14 ring-2 ring-white shadow-lg' 
                              : 'w-14 h-14 opacity-60 hover:opacity-100'
                          }`}
                        >
                          <img 
                            src={img} 
                            alt={`Thumbnail ${index + 1}`}
                            className="w-full h-full object-cover"
                          />
                        </button>
                      ))}
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="flex justify-center gap-1 mt-3">
                      {allImages.map((_, index) => (
                        <div 
                          key={index}
                          className={`h-1 rounded-full transition-all duration-300 ${
                            index === currentImageIndex ? 'w-8 bg-white' : 'w-2 bg-white/40'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Content */}
            <div className="p-8 md:p-12 space-y-6">
              {/* Meta Info */}
              <div className="flex flex-wrap items-center gap-4 text-sm">
                <span className="flex items-center gap-2 text-slate-500">
                  <Calendar size={16} /> {newsItem.date}
                </span>
                {newsItem.externalLink && (
                  <a 
                    href={newsItem.externalLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <ExternalLink size={16} /> Tashqi havola
                  </a>
                )}
              </div>

              {/* Title */}
              <h1 className="text-3xl md:text-4xl font-black text-slate-900 leading-tight">
                {newsItem.title}
              </h1>

              {/* Divider */}
              <div className="h-1 w-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full"></div>

              {/* Content */}
              <div className="prose prose-lg max-w-none text-slate-600 leading-relaxed">
                {newsItem.content.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-4">{paragraph}</p>
                ))}
              </div>

              {/* Video */}
              {newsItem.videoUrl && (
                <div className="mt-8 p-6 bg-slate-50 rounded-2xl">
                  <h3 className="flex items-center gap-2 text-lg font-bold text-slate-800 mb-4">
                    <Play size={20} className="text-red-500" /> Video
                  </h3>
                  <div className="aspect-video rounded-xl overflow-hidden bg-slate-900">
                    <iframe
                      src={newsItem.videoUrl.replace('watch?v=', 'embed/')}
                      className="w-full h-full"
                      allowFullScreen
                      title="Video"
                    />
                  </div>
                </div>
              )}

              {/* Share */}
              <div className="pt-6 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">Ulashing:</span>
                  <div className="flex gap-2">
                    <a 
                      href={`https://t.me/share/url?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(newsItem.title)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-10 h-10 bg-blue-500 hover:bg-blue-600 rounded-xl flex items-center justify-center text-white transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                      </svg>
                    </a>
                    <a 
                      href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-10 h-10 bg-blue-700 hover:bg-blue-800 rounded-xl flex items-center justify-center text-white transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </article>

          {/* Related News */}
          {relatedNews.length > 0 && (
            <section className="mt-16">
              <h2 className="text-2xl font-black text-slate-900 mb-8">Boshqa yangiliklar</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {relatedNews.map(item => (
                  <Link 
                    key={item.id} 
                    to={`/news/${item.id}`}
                    className="group bg-white rounded-2xl overflow-hidden shadow-lg shadow-slate-200/50 hover:shadow-xl hover:-translate-y-1 transition-all border border-slate-100"
                  >
                    <div className="h-40 overflow-hidden">
                      <img 
                        src={item.image || item.images?.[0] || 'https://via.placeholder.com/400x200?text=Rasm+yo\'q'} 
                        alt={item.title} 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                      />
                    </div>
                    <div className="p-5">
                      <span className="text-xs text-slate-400">{item.date}</span>
                      <h3 className="text-sm font-bold text-slate-800 mt-1 line-clamp-2 group-hover:text-blue-600 transition-colors">
                        {item.title}
                      </h3>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewsDetail;
