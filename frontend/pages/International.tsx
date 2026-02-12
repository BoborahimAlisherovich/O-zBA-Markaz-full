import React, { useMemo, useState, useEffect, useRef } from 'react';
import { Globe, ChevronLeft, ChevronRight, PlayCircle } from 'lucide-react';
import { useApp } from '../context/AppContext';

const PARTNERS_PER_PAGE = 12;

const International: React.FC = () => {
  const { internationalContent, foreignPartners, collaborationProjects } = useApp();
  const [partnerPage, setPartnerPage] = useState(1);
  const [photoIndex, setPhotoIndex] = useState(0);
  const photosTimer = useRef<number | null>(null);

  const totalPartnerPages = Math.max(1, Math.ceil(foreignPartners.length / PARTNERS_PER_PAGE));
  const paginatedPartners = useMemo(() => {
    const start = (partnerPage - 1) * PARTNERS_PER_PAGE;
    return foreignPartners.slice(start, start + PARTNERS_PER_PAGE);
  }, [foreignPartners, partnerPage]);

  const photos = internationalContent.photos || [];

  useEffect(() => {
    if (partnerPage > totalPartnerPages) {
      setPartnerPage(1);
    }
  }, [partnerPage, totalPartnerPages]);

  useEffect(() => {
    if (photos.length <= 3) {
      return;
    }
    photosTimer.current = window.setInterval(() => {
      setPhotoIndex((prev) => (prev + 1) % photos.length);
    }, 3000);
    return () => {
      if (photosTimer.current) {
        window.clearInterval(photosTimer.current);
      }
    };
  }, [photos.length]);

  const getStatusBadge = (status: string) => {
    if (status === 'planned') return 'bg-amber-100 text-amber-700';
    if (status === 'ongoing') return 'bg-emerald-100 text-emerald-700';
    return 'bg-slate-100 text-slate-700';
  };

  const carouselIndexes = useMemo(() => {
    if (!photos.length) return [];
    const current = photoIndex % photos.length;
    const prev = (current - 1 + photos.length) % photos.length;
    const next = (current + 1) % photos.length;
    return [prev, current, next];
  }, [photoIndex, photos.length]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <section className="relative h-[44vh] overflow-hidden flex items-center bg-gradient-to-r from-sky-700 to-cyan-700">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.18),transparent_40%),radial-gradient(circle_at_80%_10%,rgba(255,255,255,0.12),transparent_35%)]" />
        <div className="container mx-auto px-6 relative z-10 text-white">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/25 mb-4">
            <Globe size={16} />
            <span className="text-sm font-semibold">Xalqaro bo'lim</span>
          </div>
          <h1 className="text-5xl font-black">Xalqaro aloqalar</h1>
        </div>
      </section>

      <section className="container mx-auto px-6 py-16">
        <h2 className="text-4xl font-black text-slate-900 mb-4">{internationalContent.title || "Xalqaro aloqalar to'g'risida"}</h2>
        <div className="text-slate-600 leading-8 whitespace-pre-line">
          {internationalContent.description || "Hozircha ma'lumot kiritilmagan."}
        </div>
      </section>

      <section className="container mx-auto px-6 pb-12">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-black text-slate-900">Xorijiy hamkorlar</h2>
        </div>

        {paginatedPartners.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {paginatedPartners.map((partner) => (
                <div key={partner.id} className="rounded-3xl bg-white border border-slate-200 shadow-lg overflow-hidden h-full flex flex-col">
                  <div className="aspect-[4/3] bg-slate-100 overflow-hidden p-4 flex items-center justify-center">
                    <img
                      src={partner.imageUrl || 'https://via.placeholder.com/500x500?text=Hamkor'}
                      alt={partner.organizationName}
                      className="max-w-full max-h-full object-contain rounded-xl"
                    />
                  </div>
                  <div className="p-5 flex-1 flex flex-col">
                    <h3 className="text-lg font-black text-slate-900 line-clamp-2 min-h-[3.5rem]">{partner.organizationName}</h3>
                    <p className="text-sm font-semibold text-cyan-700 mt-1">{partner.country}</p>
                    <p className="text-sm text-slate-600 mt-3 line-clamp-4">{partner.shortInfo}</p>
                  </div>
                </div>
              ))}
            </div>

            {totalPartnerPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button
                  className="px-4 py-2 rounded-xl border border-slate-300 text-slate-600 disabled:opacity-40"
                  onClick={() => setPartnerPage((prev) => Math.max(1, prev - 1))}
                  disabled={partnerPage === 1}
                >
                  Oldingi
                </button>
                {Array.from({ length: totalPartnerPages }).map((_, index) => (
                  <button
                    key={index}
                    className={`w-10 h-10 rounded-xl font-bold ${partnerPage === index + 1 ? 'bg-cyan-600 text-white' : 'bg-white border border-slate-300 text-slate-700'}`}
                    onClick={() => setPartnerPage(index + 1)}
                  >
                    {index + 1}
                  </button>
                ))}
                <button
                  className="px-4 py-2 rounded-xl border border-slate-300 text-slate-600 disabled:opacity-40"
                  onClick={() => setPartnerPage((prev) => Math.min(totalPartnerPages, prev + 1))}
                  disabled={partnerPage === totalPartnerPages}
                >
                  Keyingi
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="py-16 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-300 text-slate-400">
            Hamkorlar kiritilmagan
          </div>
        )}
      </section>

      <section className="container mx-auto px-6 py-12">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-black text-slate-900">Hamkorlikda qilingan loyihalar</h2>
        </div>
        <div className="space-y-5">
          {collaborationProjects.length > 0 ? collaborationProjects.map((project) => (
            <div key={project.id} className="rounded-3xl bg-white border border-slate-200 shadow-md p-6">
              <div className="flex flex-wrap justify-between gap-3 mb-2">
                <h3 className="text-2xl font-black text-slate-900">{project.name}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusBadge(project.status)}`}>
                  {project.statusDisplay}
                </span>
              </div>
              <p className="text-slate-600">{project.description}</p>
              <p className="text-sm text-slate-500 mt-3">
                Sana: {new Date(project.date).toLocaleDateString('uz-UZ')}
              </p>
            </div>
          )) : (
            <div className="py-16 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-300 text-slate-400">
              Loyihalar kiritilmagan
            </div>
          )}
        </div>
      </section>

      <section className="container mx-auto px-6 py-12">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-black text-slate-900">Fotosuratlar</h2>
        </div>
        {photos.length > 0 ? (
          <div className="relative overflow-hidden py-6">
            <div className="flex items-center justify-center gap-4">
              <button
                className="w-12 h-12 rounded-full bg-white border border-slate-300 flex items-center justify-center"
                onClick={() => setPhotoIndex((prev) => (prev - 1 + photos.length) % photos.length)}
              >
                <ChevronLeft size={20} />
              </button>

              {carouselIndexes.length === 3 ? carouselIndexes.map((photoIdx, idx) => (
                <div
                  key={photos[photoIdx].id}
                  className={`rounded-3xl overflow-hidden transition-all duration-700 ${idx === 1 ? 'w-[58%] opacity-100 scale-100' : 'w-[18%] opacity-65 scale-90 blur-[1.4px]'}`}
                >
                  <div className="aspect-[16/9]">
                    <img src={photos[photoIdx].imageUrl} alt="Karusel rasmi" className="w-full h-full object-cover" />
                  </div>
                </div>
              )) : (
                <div className="w-[58%] rounded-3xl overflow-hidden">
                  <div className="aspect-[16/9]">
                    <img src={photos[photoIndex % photos.length].imageUrl} alt="Karusel rasmi" className="w-full h-full object-cover" />
                  </div>
                </div>
              )}

              <button
                className="w-12 h-12 rounded-full bg-white border border-slate-300 flex items-center justify-center"
                onClick={() => setPhotoIndex((prev) => (prev + 1) % photos.length)}
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        ) : (
          <div className="py-16 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-300 text-slate-400">
            Fotosuratlar kiritilmagan
          </div>
        )}
      </section>

      <section className="container mx-auto px-6 py-12 pb-20">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-black text-slate-900">Video to'plami</h2>
        </div>
        {internationalContent.videos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {internationalContent.videos.map((video) => (
              <div key={video.id} className="rounded-3xl overflow-hidden shadow-lg border border-slate-200 bg-white">
                <div className="aspect-video bg-slate-900">
                  <iframe
                    src={video.embedUrl || video.videoUrl}
                    title={video.title || "Video"}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                  />
                </div>
                <div className="p-4 flex items-center gap-2">
                  <PlayCircle size={18} className="text-red-600" />
                  <p className="font-semibold text-slate-800">{video.title || "Video"}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-300 text-slate-400">
            Videolar kiritilmagan
          </div>
        )}
      </section>
    </div>
  );
};

export default International;
