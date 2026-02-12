
import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { useLocation } from 'react-router-dom';
import { Search, Download, Info, CheckCircle, GraduationCap } from 'lucide-react';

const Students: React.FC = () => {
  const { pdPlans, documents, studentNotes } = useApp();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  // URL query parameter orqali qidiruvni boshlash (Home sahifasidan kelganda)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const query = params.get('q');
    if (query) {
      setSearchTerm(query);
      const results = pdPlans.filter(p => 
        p.fullName.toLowerCase().includes(query.toLowerCase()) || 
        p.workplace.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(results);
      setHasSearched(true);
    }
  }, [location.search, pdPlans]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }
    const results = pdPlans.filter(p => 
      p.fullName.toLowerCase().includes(searchTerm.toLowerCase()) || 
      p.workplace.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(results);
  };

  const regDocs = documents.filter(d => d.category === 'regulatory');

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">Tinglovchilar uchun</h1>
          <p className="text-blue-200">Malaka oshirish rejalari, me'yoriy hujjatlar va foydali eslatmalar.</p>
        </div>
      </div>

      <div className="container mx-auto px-4 -mt-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Search and Docs */}
        <div className="lg:col-span-2 space-y-8">
          {/* PD Plan Search */}
          <section className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-blue-900">
              <Search className="text-amber-500" /> Malaka oshirish rejasidan qidirish
            </h2>
            <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3 mb-8">
              <input 
                type="text" 
                placeholder="F.I.SH yoki ish joyini kiriting..." 
                className="flex-grow border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                
              />
              <button type="submit" className="bg-blue-700 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-800 transition-colors">
                Qidirish
              </button>
            </form>

            {hasSearched && (
              <div className="overflow-x-auto">
                {searchResults.length > 0 ? (
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 text-gray-500 uppercase">
                      <tr>
                        <th className="px-4 py-3 border-b">F.I.SH</th>
                        <th className="px-4 py-3 border-b">Ish joyi</th>
                        <th className="px-4 py-3 border-b">Kurs</th>
                        <th className="px-4 py-3 border-b">Muddat</th>
                        <th className="px-4 py-3 border-b">Sertifikat</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {searchResults.map(res => (
                        <tr key={res.id} className="hover:bg-blue-50 transition-colors">
                          <td className="px-4 py-4 font-medium text-gray-900">{res.fullName}</td>
                          <td className="px-4 py-4 text-gray-600">{res.workplace}</td>
                          <td className="px-4 py-4 text-gray-600">{res.courseType}</td>
                          <td className="px-4 py-4 text-gray-600">{res.duration || '-'}</td>
                          <td className="px-4 py-4">
                            <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold">{res.series} {res.number}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="text-center py-10 bg-gray-50 rounded-xl">
                    <p className="text-gray-500">Kechirasiz, bunday ma'lumot topilmadi.</p>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Regulatory Docs */}
          <section className="bg-white rounded-2xl shadow-sm border p-8">
            <h2 className="text-2xl font-bold mb-6 text-blue-900">Me’yoriy hujjatlar</h2>
            <div className="space-y-4">
              {regDocs.length > 0 ? regDocs.map(doc => (
                <div key={doc.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border group hover:border-blue-300 transition-all">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-red-100 text-red-600 rounded flex items-center justify-center">
                      <Download size={20} />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">{doc.title}</h4>
                      <p className="text-xs text-gray-500">{doc.date} da yuklangan</p>
                    </div>
                  </div>
                  <button className="text-blue-600 hover:text-blue-800">
                    <Download size={20} />
                  </button>
                </div>
              )) : (
                 <div className="text-center py-10 border-2 border-dashed rounded-xl text-gray-500">
                   Davlat ta'lim talablari va dasturlar yuklanmoqda.
                 </div>
              )}
            </div>
          </section>
        </div>

        {/* Right Column: Reminders */}
        <div className="space-y-8">
          <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100 sticky top-24">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-amber-900">
              <Info className="text-amber-600" /> Tinglovchilarga eslatma
            </h3>
            
            <div className="space-y-6">
              <p className="text-sm text-amber-900 leading-relaxed whitespace-pre-wrap">
                {studentNotes}
              </p>
            </div>

            <div className="mt-10 pt-6 border-t border-amber-200">
              <div className="flex items-center gap-2 text-green-700 font-bold mb-2">
              </div>
              <p className="text-xs text-amber-800 mb-4">
              </p>
              <a href="https://uzbamalaka.uz" target="_blank" className="w-full bg-blue-900 text-white text-center py-2 rounded-lg text-sm font-bold block hover:bg-black transition-colors">
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Students;
