import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import { ArtGalleryItem } from '../types';

interface ArtGallerySectionProps {
  items: ArtGalleryItem[];
}

const VISIBLE_COUNT = 4;

const ArtGallerySection: React.FC<ArtGallerySectionProps> = ({ items }) => {
  const [selectedArt, setSelectedArt] = useState<ArtGalleryItem | null>(null);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [modalImageIndex, setModalImageIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (items.length <= VISIBLE_COUNT) return;
    const interval = setInterval(() => {
      setCarouselIndex((prev) => (prev + 1) % items.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [items.length]);

  const visibleItems = useMemo(() => {
    if (!items.length) return [];
    if (items.length <= VISIBLE_COUNT) return items;
    return Array.from({ length: VISIBLE_COUNT }).map((_, idx) => items[(carouselIndex + idx) % items.length]);
  }, [items, carouselIndex]);

  const openModal = useCallback((item: ArtGalleryItem) => {
    setSelectedArt(item);
    setModalImageIndex(0);
    setIsAutoPlaying(true);
  }, []);

  const closeModal = useCallback(() => {
    setSelectedArt(null);
    setModalImageIndex(0);
  }, []);

  const modalImages = useMemo(() => {
    if (!selectedArt) return [];
    const additional = selectedArt.images || [];
    return [selectedArt.imageUrl, ...additional.map((img) => img.imageUrl)].filter(Boolean);
  }, [selectedArt]);

  useEffect(() => {
    if (!selectedArt || !isAutoPlaying || modalImages.length <= 1) return;
    const timer = setInterval(() => {
      setModalImageIndex((prev) => (prev + 1) % modalImages.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [selectedArt, isAutoPlaying, modalImages.length]);

  const goPrevModalImage = () => {
    if (!modalImages.length) return;
    setModalImageIndex((prev) => (prev - 1 + modalImages.length) % modalImages.length);
    setIsAutoPlaying(false);
  };

  const goNextModalImage = () => {
    if (!modalImages.length) return;
    setModalImageIndex((prev) => (prev + 1) % modalImages.length);
    setIsAutoPlaying(false);
  };

  const goPrevList = () => {
    if (items.length <= VISIBLE_COUNT) return;
    setCarouselIndex((prev) => (prev - 1 + items.length) % items.length);
  };

  const goNextList = () => {
    if (items.length <= VISIBLE_COUNT) return;
    setCarouselIndex((prev) => (prev + 1) % items.length);
  };

  return (
    <>
      <section className="container mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <span className="text-sm font-bold text-pink-600 uppercase tracking-wider">San'at</span>
          <h2 className="text-4xl font-black text-slate-900 mt-2">Art Galereya</h2>
          <center><p>Ustozlarimiz va tinglovchilarimizning TOP asarlari galereyasi</p></center>
        </div>

        {visibleItems.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {visibleItems.map((item) => (
                <div
                  key={item.id}
                  className="group bg-white rounded-2xl overflow-hidden shadow-lg border border-slate-100 cursor-pointer"
                  onClick={() => openModal(item)}
                >
                  <div className="relative h-64 overflow-hidden bg-slate-200">
                    <img src={item.imageUrl} alt={item.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                  </div>
                  <div className="p-5">
                    <h3 className="text-xl font-black text-slate-900 mb-1 line-clamp-2">{item.name}</h3>
                    <p className="text-sm font-semibold text-pink-600 mb-3">{item.authorFullName}</p>
                    <p className="text-slate-600 text-sm line-clamp-2">{item.text}</p>
                  </div>
                </div>
              ))}
            </div>

            {items.length > VISIBLE_COUNT && (
              <div className="flex justify-center gap-3 mt-8">
                <button onClick={goPrevList} className="w-11 h-11 rounded-full border border-slate-300 bg-white flex items-center justify-center">
                  <ChevronLeft size={18} />
                </button>
                <button onClick={goNextList} className="w-11 h-11 rounded-full border border-slate-300 bg-white flex items-center justify-center">
                  <ChevronRight size={18} />
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="py-20 text-center bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
            <p className="text-slate-400 font-medium">Hozircha asarlar mavjud emas</p>
          </div>
        )}
      </section>

      {selectedArt && (
        <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4" onClick={closeModal}>
          <button onClick={closeModal} className="absolute top-4 right-4 z-50 p-3 bg-white/10 hover:bg-white/20 rounded-full transition-colors">
            <X className="text-white" size={28} />
          </button>

          {modalImages.length > 1 && (
            <>
              <button onClick={(e) => { e.stopPropagation(); goPrevModalImage(); }} className="absolute left-4 top-1/2 -translate-y-1/2 z-50 p-3 bg-white/10 rounded-full">
                <ChevronLeft className="text-white" size={26} />
              </button>
              <button onClick={(e) => { e.stopPropagation(); goNextModalImage(); }} className="absolute right-4 top-1/2 -translate-y-1/2 z-50 p-3 bg-white/10 rounded-full">
                <ChevronRight className="text-white" size={26} />
              </button>
            </>
          )}

          <div className="relative w-full max-w-5xl max-h-[90vh] flex flex-col bg-black rounded-lg overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="relative flex items-center justify-center bg-black flex-1 overflow-auto">
              <img src={modalImages[modalImageIndex]} alt={selectedArt.name} className="max-h-full max-w-full object-contain p-4" />
            </div>
            <div className="bg-gradient-to-t from-black via-black/85 to-transparent p-6 text-white">
              <h3 className="text-3xl font-black mb-1">{selectedArt.name}</h3>
              <p className="text-pink-400 font-semibold mb-3">{selectedArt.authorFullName}</p>
              <p className="text-slate-300">{selectedArt.text}</p>
            </div>
          </div>

          {modalImages.length > 1 && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-3">
              <button
                onClick={(e) => { e.stopPropagation(); setIsAutoPlaying(!isAutoPlaying); }}
                className={`px-3 py-1 rounded-full text-xs font-semibold ${isAutoPlaying ? 'bg-emerald-500 text-white' : 'bg-white/20 text-white'}`}
              >
                {isAutoPlaying ? 'Avto yoqilgan' : 'Avto o‘chirilgan'}
              </button>
              <div className="flex gap-2">
                {modalImages.map((_, index) => (
                  <button
                    key={index}
                    onClick={(e) => { e.stopPropagation(); setModalImageIndex(index); setIsAutoPlaying(false); }}
                    className={`w-2.5 h-2.5 rounded-full ${index === modalImageIndex ? 'bg-white' : 'bg-white/45'}`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default ArtGallerySection;
