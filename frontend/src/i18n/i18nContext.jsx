import React, { createContext, useContext, useState, useEffect } from 'react';
import en from './en.json';
import es from './es.json';

const translations = {
  en,
  es
};

const I18nContext = createContext();

export function I18nProvider({ children }) {
  const [lang, setLang] = useState('en');

  useEffect(() => {
    const saved = localStorage.getItem('sentinel_lang');
    if (saved && translations[saved]) {
      setLang(saved);
    }
  }, []);

  const changeLang = (newLang) => {
    if (translations[newLang]) {
      setLang(newLang);
      localStorage.setItem('sentinel_lang', newLang);
    }
  };

  const toggleLang = () => {
    const next = lang === 'en' ? 'es' : 'en';
    changeLang(next);
  };

  const resolvePath = (obj, path) => {
    if (!obj || !path) return undefined;

    // Preserve legacy flat-dotted keys such as "arena.title".
    if (obj[path] !== undefined) {
      return obj[path];
    }

    // Support nested paths such as "exercises.py001.assisted.step1.question".
    return path.split('.').reduce((acc, part) => acc?.[part], obj);
  };

  const t = (key) => {
    const currentDict = translations[lang] || {};
    const defaultDict = translations['en'] || {};

    const result = resolvePath(currentDict, key);
    if (result !== undefined) return result;

    const defaultResult = resolvePath(defaultDict, key);
    return defaultResult !== undefined ? defaultResult : key;
  };

  return (
    <I18nContext.Provider value={{ lang, setLang: changeLang, toggleLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
}

