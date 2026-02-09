
import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Phone, Clock, Calendar, Mail, Image as ImageIcon } from 'lucide-react';

const About: React.FC = () => {
  const { personnel, aboutContent } = useApp();
  const [activeTab, setActiveTab] = useState<'info' | 'structure' | 'leadership' | 'staff'>('info');

  const leadership = personnel.filter(p => p.category === 'leadership');
  const staff = personnel.filter(p => p.category === 'staff');

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4 text-center lg:text-left">Markaz haqida</h1>
          <p className="text-blue-200 max-w-2xl text-center lg:text-left">Markaz tarixi, tuzilmasi va xodimlar jamoasi haqida ma'lumotlar.</p>
        </div>
      </div>

      <div className="container mx-auto px-4 -mt-10">
        <div className="bg-white rounded-xl shadow-lg p-4 flex flex-wrap gap-2 mb-10 overflow-x-auto justify-center lg:justify-start">
          {[
            { id: 'info', label: 'Umumiy ma`lumot' },
            { id: 'structure', label: 'Markaz tuzilmasi' },
            { id: 'leadership', label: 'Rahbariyat' },
            { id: 'staff', label: 'Markaziy apparat' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-blue-700 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-[2.5rem] p-8 lg:p-16 shadow-xl border border-gray-100 min-h-[500px]">
          {activeTab === 'info' && (
            <div className="prose prose-lg max-w-none">
              <h2 className="text-3xl font-black mb-8 text-slate-900 border-l-4 border-blue-600 pl-4">Tarixi va faoliyati</h2>
              <div className="text-slate-700 leading-relaxed space-y-6 text-lg">
                {aboutContent.history.split('\n').map((para, i) => (
                   <p key={i}>{para}</p>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'structure' && (
            <div className="space-y-8">
              <div className="max-w-5xl mx-auto">
                <h2 className="text-3xl font-black mb-6 text-slate-900 text-center">Markaz tashkiliy tuzilmasi</h2>
                <p className="text-slate-600 leading-relaxed mb-12 text-center text-lg italic max-w-3xl mx-auto">
                  {aboutContent.structure || "Tuzilma haqida ma'lumot kiritilmagan."}
                </p>
                
                <div className="bg-white rounded-[3rem] overflow-hidden shadow-2xl border border-gray-100 p-4 lg:p-10 group">
                  {aboutContent.structureImage ? (
                    <img 
                      src={aboutContent.structureImage} 
                      alt="Markaz tuzilmasi" 
                      className="w-full h-auto object-contain cursor-zoom-in group-hover:scale-[1.02] transition-transform duration-700" 
                    />
                  ) : (
                    <div className="p-32 flex flex-col items-center justify-center text-gray-400 bg-gray-50 border-4 border-dashed border-gray-100 rounded-[2.5rem]">
                      <ImageIcon size={80} className="mb-6 opacity-20" />
                      <p className="font-black uppercase tracking-[0.2em] text-sm">Tuzilma rasmi yuklanmagan</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {(activeTab === 'leadership' || activeTab === 'staff') && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-20 gap-x-12 pt-10">
              {(activeTab === 'leadership' ? leadership : staff).length > 0 ? (activeTab === 'leadership' ? leadership : staff).map(person => (
                <div key={person.id} className="flex flex-col items-center text-center animate-in fade-in slide-in-from-bottom-6 duration-700">
                  {/* Circular Image matching the provided screenshot style */}
                  <div className="w-64 h-64 rounded-full overflow-hidden mb-10 shadow-2xl border-[12px] border-white ring-1 ring-slate-100 shrink-0">
                    <img 
                      src={person.photoUrl || 'https://via.placeholder.com/300?text=Xodim'} 
                      alt={person.fullName} 
                      className="w-full h-full object-cover transition-transform duration-700 hover:scale-110" 
                    />
                  </div>
                  
                  {/* Centered text style from screenshot */}
                  <h3 className="text-2xl font-black text-slate-900 mb-4 px-2 leading-tight">
                    {person.fullName}
                  </h3>
                  <p className="text-slate-600 text-base leading-relaxed px-6 max-w-xs mx-auto">
                    {person.position}
                  </p>
                  
                  {/* Optional contact info in subtle style */}
                  <div className="mt-6 flex flex-col gap-2 opacity-50 hover:opacity-100 transition-opacity">
                    <span className="text-xs font-bold text-slate-400 flex items-center justify-center gap-2">
                      <Phone size={12} /> {person.phone || 'Noma`lum'}
                    </span>
                    <span className="text-xs font-bold text-slate-400 flex items-center justify-center gap-2">
                      <Clock size={12} /> {person.receptionHours || 'Noma`lum'}
                    </span>
                  </div>
                </div>
              )) : (
                <div className="col-span-full py-32 text-center bg-slate-50 rounded-[2.5rem] border-2 border-dashed border-slate-200">
                  <p className="text-slate-400 font-bold uppercase tracking-[0.2em] text-xs italic">Ma'lumotlar kiritilmagan</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default About;
