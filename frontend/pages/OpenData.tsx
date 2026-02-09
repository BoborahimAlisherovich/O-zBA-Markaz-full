
import React from 'react';
import { useApp } from '../context/AppContext';
import { FileText, Download, Briefcase, TrendingUp, BarChart3, Database, FolderOpen } from 'lucide-react';

const OpenData: React.FC = () => {
  const { documents } = useApp();
  
  // Get file extension from URL
  const getFileExtension = (url: string) => {
    if (!url) return 'FILE';
    const ext = url.split('.').pop()?.split('?')[0]?.toUpperCase() || 'FILE';
    return ext;
  };

  const categories = [
    { key: 'open_data', label: "Ochiq ma'lumotlar", icon: <FolderOpen className="text-blue-600" />, color: 'blue' },
    { key: 'plan', label: 'Ish rejalari', icon: <Briefcase className="text-green-600" />, color: 'green' },
    { key: 'regulatory', label: "Me'yoriy hujjatlar", icon: <TrendingUp className="text-amber-600" />, color: 'amber' },
  ];

  // Group documents by category
  const getDocsByCategory = (category: string) => {
    return documents.filter(d => d.category === category);
  };

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">Ochiq ma'lumotlar</h1>
          <p className="text-blue-200">Markazning moliyaviy, istiqbolli va statistik ma'lumotlari bilan tanishishingiz mumkin.</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-16">
        {/* Categories Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {categories.map((cat, i) => {
            const count = getDocsByCategory(cat.key).length;
            return (
              <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center mb-4">{cat.icon}</div>
                <h3 className="font-bold text-gray-900">{cat.label}</h3>
                <p className="text-2xl font-black text-gray-800 mt-2">{count}</p>
                <p className="text-xs text-gray-500 mt-1">ta hujjat mavjud</p>
              </div>
            );
          })}
        </div>

        {/* Documents by Category */}
        {categories.map((cat) => {
          const catDocs = getDocsByCategory(cat.key);
          if (catDocs.length === 0) return null;
          
          return (
            <div key={cat.key} className="bg-white rounded-2xl shadow-sm border overflow-hidden mb-8">
              <div className={`p-6 border-b bg-${cat.color}-50 flex justify-between items-center`}>
                <div className="flex items-center gap-3">
                  {cat.icon}
                  <h2 className="text-xl font-bold text-gray-900">{cat.label}</h2>
                </div>
                <span className="text-sm bg-gray-200 px-3 py-1 rounded-full font-medium">{catDocs.length} ta</span>
              </div>
              <div className="divide-y">
                {catDocs.map(doc => (
                  <div key={doc.id} className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-blue-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center shrink-0">
                        <FileText size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900">{doc.title}</h4>
                        <p className="text-xs text-gray-500 mt-1">
                          Sana: {doc.date} | Format: {getFileExtension(doc.fileUrl)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {doc.fileUrl && (
                        <a 
                          href={doc.fileUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          download
                          className="flex items-center gap-2 text-sm font-bold text-white bg-blue-600 px-5 py-2.5 rounded-xl hover:bg-blue-700 transition-colors"
                        >
                          <Download size={18} /> Yuklab olish
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Empty State */}
        {documents.length === 0 && (
          <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
            <div className="p-20 text-center text-gray-500">
              <Database size={48} className="mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-bold text-gray-700 mb-2">Hujjatlar mavjud emas</h3>
              <p>Ochiq ma'lumotlar to'plami shakllanmoqda. Yaqin kunlarda barcha hujjatlar joylanadi.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenData;
