import React from 'react';
import { useTranslation } from 'react-i18next';

interface Language {
  code: string;
  name: string;
  flag: string;
}

const LANGUAGES: Language[] = [
  { code: 'uz', name: 'O\'zbek', flag: '🇺🇿' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
 { code: 'en', name: 'English', flag: '🇺🇸' },
]

export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange = (langCode: string) => {
    i18n.changeLanguage(langCode);
  };

  return (
    <div className="flex items-center gap-2">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => handleLanguageChange(lang.code)}
          title={lang.name}
          className={`
            w-8 h-8 rounded-full flex items-center justify-center text-sm
            transition-transform duration-200
            ${i18n.language === lang.code
              ? 'bg-blue-600 text-white shadow-md scale-110 ring-2 ring-blue-300'
              : 'bg-white text-gray-800 shadow-sm hover:shadow-md border border-gray-100 hover:border-blue-200'
            }
          `}
          aria-pressed={i18n.language === lang.code}
          aria-label={`Switch to ${lang.name}`}
        >
          <span className="leading-none">{lang.flag}</span>
        </button>
      ))}
    </div>
  );
};

export default LanguageSwitcher;
