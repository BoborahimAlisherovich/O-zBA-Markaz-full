
import React from 'react';
import { useApp } from '../context/AppContext';
import { FileText, Download, Mail, Phone, ExternalLink } from 'lucide-react';

const Journal: React.FC = () => {
  const { journalIssues } = useApp();

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      <div className="bg-blue-900 text-white py-5">
        <div className="container mx-auto px-10 flex flex-col md:flex-row justify-between items-center gap-10">
          <div className="max-w-2xl">
            <h1 className="text-5xl font-bold mb-6">Badiiy ta’lim va pedagogika</h1>
            <p className="text-blue-100 text-lg leading-relaxed mb-6">
              Ushbu ilmiy jurnal san'at ta'limidagi so'nggi tadqiqotlar va pedagogik metodikalarni yoritib boradi.
            </p>
            <div className="flex gap-4">
               <button className="bg-amber-500 hover:bg-amber-600 text-white px-6 py-3 rounded-lg font-bold flex items-center gap-2 transition-all">
                 <FileText size={20} /> Maqola berish tartibi (PDF)
               </button>
            </div>
          </div>
                  </div>
      </div>

      <div className="container mx-auto px-4 py-16 grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Main Content: Issues */}
        <div className="lg:col-span-2 space-y-8">
          <h2 className="text-3xl font-bold text-gray-900 border-b pb-4">Jurnal sonlari</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {journalIssues.length > 0 ? journalIssues.map(issue => (
              <div key={issue.id} className="bg-white p-4 rounded-xl shadow-sm border flex gap-4 group hover:border-blue-300 transition-colors">
                <div className="w-24 h-32 bg-gray-100 rounded shrink-0 overflow-hidden">
                  <img src={issue.thumbnailUrl || "https://picsum.photos/seed/doc/100/140"} alt={`Jurnal ${issue.year}`} className="w-full h-full object-cover" />
                </div>
                <div className="flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-gray-900 group-hover:text-blue-700">Jurnal {issue.year}</h3>
                    <p className="text-sm text-gray-500">{issue.issueNumber ? `${issue.issueNumber}-son` : `${issue.year}-yil soni`}</p>
                  </div>
                  <a href={issue.pdfUrl} download className="text-blue-600 font-bold text-sm flex items-center gap-1 hover:underline">
                    <Download size={14} /> PDF yuklab olish
                  </a>
                </div>
              </div>
            )) : (
              <div className="col-span-full py-12 text-center text-gray-500 border-2 border-dashed rounded-2xl">
                Hozircha raqamli arxiv mavjud emas.
              </div>
            )}
          </div>
        </div>

        {/* Sidebar: Info */}
        <div className="space-y-8">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h3 className="text-xl font-bold mb-4 text-blue-900">Bog'lanish</h3>
            <div className="space-y-4 text-sm">
              <p className="flex items-center gap-3 text-gray-600">
                <Mail size={18} className="text-blue-600" /> @Uzbamarkaz_jurnali,  @badiiytalimvapedagogika
              </p>
              <p className="flex items-center gap-3 text-gray-600">
                <Phone size={18} className="text-blue-600" /> (+99877) 363-38-36
              </p>
            </div>
            <hr className="my-6" />
            <h4 className="font-bold mb-2">Tahririyat manzili:</h4>
            <p className="text-sm text-gray-500 leading-relaxed">
              Toshkent shahri, Uchtepa tumani, CHilonzor 26-daha, Shirin ko'cha, 1A-uy.
            </p>
          </div>

          <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
            <h3 className="text-xl font-bold mb-4 text-amber-800">Mualliflarga</h3>
            <ul className="space-y-3 text-sm text-amber-900">
              <li className="flex gap-2"><span>•</span> Maqolalar o'zbek, rus, qoraqalpoq yoki ingliz tillarida qabul qilinadi.</li>
              <li className="flex gap-2"><span>•</span> Maqola hajmi 5-8 bet bo'lishi lozim.</li>
              <li className="flex gap-2"><span>•</span> Annotatsiya va kalit so'zlar 3 tilda beriladi.</li>
            </ul>
            <button className="w-full mt-6 bg-amber-600 text-white py-2 rounded-lg font-bold hover:bg-amber-700 flex items-center justify-center gap-2">
 
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Journal;
