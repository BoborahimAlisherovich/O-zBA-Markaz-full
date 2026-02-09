
import React from 'react';
import { 
  Home, Info, BookOpen, GraduationCap, 
  Database, Globe 
} from 'lucide-react';

export const COLORS = {
  primary: '#0f172a', // Slate 900
  secondary: '#3b82f6', // Blue 500
  accent: '#f59e0b', // Amber 500
  success: '#10b981', // Emerald 500
  info: '#06b6d4', // Cyan 500
  chart: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
};

export const MENU_ITEMS = [
  { label: 'Bosh sahifa', path: '/', icon: <Home size={18} /> },
  { label: 'Markaz haqida', path: '/about', icon: <Info size={18} /> },
  { label: 'Ilmiy jurnal', path: '/journal', icon: <BookOpen size={18} /> },
  { label: 'Tinglovchilar uchun', path: '/students', icon: <GraduationCap size={18} /> },
  { label: 'Ochiq ma’lumotlar', path: '/open-data', icon: <Database size={18} /> },
  { label: 'Masofaviy ta’lim', path: 'external', url: 'https://mt.uzbamarkaz.uz', icon: <Globe size={18} /> },

];

export const INITIAL_STATS = {
  professors: 12,
  dotsents: 24,
  academics: 5,
  potential: 78,
  studentsCount: [
    { year: '2020', count: 380, retraining: 90 },
    { year: '2021', count: 450, retraining: 120 },
    { year: '2022', count: 520, retraining: 150 },
    { year: '2023', count: 610, retraining: 180 },
    { year: '2024', count: 580, retraining: 195 },
  ],
  retrainingCount: [
    { year: '2021', count: 120 },
    { year: '2022', count: 150 },
    { year: '2023', count: 180 },
    { year: '2024', count: 195 },
  ]
};
