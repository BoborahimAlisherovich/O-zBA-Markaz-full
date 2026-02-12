
import React, { useState } from 'react';
// Corrected: Ensured clean import from react-router-dom
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, CheckCircle, ExternalLink, Phone, Mail, MapPin } from 'lucide-react';
// Corrected: Removed .tsx extension from local import to follow TypeScript best practices
import { MENU_ITEMS } from '../constants';
import LanguageSwitcher from './LanguageSwitcher';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-blue-900 text-white text-xs py-2 hidden md:block">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div className="flex gap-4">
            <span className="flex items-center gap-1"><Phone size={12} /> (+99877) 363-38-36</span>
            <span className="flex items-center gap-1"><Mail size={12} /> uzbahuzuridagimarkaz@gmail.com</span>
          </div>
          <div className="flex gap-4">
             <Link to="/reestr" className="hover:text-amber-400 flex items-center gap-1">
              
             </Link>
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full flex items-center justify-center overflow-hidden shrink-0">
              <img src="/logo/uzba_markaz.png" alt="O'zBA Malaka oshirish markazi logosi" className="w-full h-full object-contain" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-sm font-bold leading-tight text-blue-900">
                O'zbekiston Badiiy akademiyasi huzuridagi<br/>
                Badiiy ta'lim yo‘nalishlarida pedagog<br/>
                hamda ularning malakasini oshirish markazi<br/>
                va mutaxassis kadrlarni qayta tayyorlash
              </h1>
            </div>
          </Link>

          {/* Desktop Nav (center) */}
          <nav className="hidden lg:flex flex-1 justify-center">
            <div className="flex gap-6">
              {MENU_ITEMS.map((item) => (
                item.path === 'external' ? (
                  <a key={item.label} href={item.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm font-medium hover:text-blue-700 transition-colors">
                    {item.label} <ExternalLink size={14} />
                  </a>
                ) : (
                  <Link 
                    key={item.label} 
                    to={item.path} 
                    className={`text-sm font-medium hover:text-blue-700 transition-colors ${location.pathname === item.path ? 'text-blue-900 border-b-2 border-amber-500' : 'text-gray-600'}`}
                  >
                    {item.label}
                  </Link>
                )
              ))}
            </div>
          </nav>

          {/* Actions (right) */}
          <div className="hidden lg:flex items-center gap-4">
            {/* Masofaviy ta'lim is part of MENU_ITEMS; keep a small link for actions area if needed */}
            <div className="hidden lg:block">
              {/* empty placeholder for spacing if needed */}
            </div>

            {/* Language panel (pill) */}
            <div className="bg-white/95 px-2 py-1 rounded-xl shadow-sm border border-gray-100 flex items-center gap-2">
              <LanguageSwitcher />
            </div>
          </div>

          {/* Mobile Toggle */}
          <button className="lg:hidden shrink-0" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>

        {/* Mobile Nav */}
        {isMenuOpen && (
          <div className="lg:hidden bg-white border-t px-4 py-6 flex flex-col gap-4 animate-slideDown">
            {/* Mobile Language Switcher */}
            <div className="pb-4 border-b border-gray-200">
              <div className="text-sm font-medium text-gray-600 mb-3">Tilni tanlang:</div>
              <div className="flex justify-center gap-2">
                <LanguageSwitcher />
              </div>
            </div>
            
            {MENU_ITEMS.map((item) => (
              item.path === 'external' ? (
                <a key={item.label} href={item.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
                  <span className="flex items-center gap-2">{item.icon} {item.label}</span>
                  <ExternalLink size={16} />
                </a>
              ) : (
                <Link 
                  key={item.label} 
                  to={item.path} 
                  onClick={() => setIsMenuOpen(false)}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded"
                >
                  {item.icon} {item.label}
                </Link>
              )
            ))}
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white pt-12 pb-6">
        <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <h3 className="text-xl font-bold mb-4">Markaz haqida</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Badiiy ta'lim yo'nalishlarida pedagog va mutaxassis kadrlarni qayta tayyorlash hamda ularning malakasini oshirish markazi.
            </p>
          </div>
          <div>
            <h3 className="text-xl font-bold mb-4">Bog'lanish</h3>
            <ul className="text-gray-400 text-sm space-y-3">
              <li className="flex items-center gap-2"><MapPin size={16} /> Toshkent shahri, Uchtepa tumani, Chilonzor 26-daha, Shirin ko'cha, 1A</li>
              <li className="flex items-center gap-2"><Phone size={16} /> (+99877) 363-38-36</li>
              <li className="flex items-center gap-2"><Mail size={16} /> uzbahuzuridagimarkaz@gmail.com</li>
            </ul>
          </div>
          <div>
            <h3 className="text-xl font-bold mb-4">Foydali havolalar</h3>
            <ul className="text-gray-400 text-sm space-y-2">
              <li><Link to="/journal" className="hover:text-amber-400">Ilmiy jurnal</Link></li>
              <li><a href="https://mt.uzbamalaka.uz" target="_blank" className="hover:text-amber-400">Masofaviy ta'lim</a></li>
              <li><a href="https://reestr.uzbamalaka.uz" target="_blank" className="hover:text-amber-400">Diplom va sertifikatlar yagona reestri</a></li>
            </ul>
          </div>
        </div>
        <div className="container mx-auto px-4 mt-12 pt-6 border-t border-gray-800 text-center text-gray-500 text-xs">
          &copy; {new Date().getFullYear()} O'zBA huzuridagi Markaz. Barcha huquqlar himoyalangan.
        </div>
      </footer>
    </div>
  );
};
