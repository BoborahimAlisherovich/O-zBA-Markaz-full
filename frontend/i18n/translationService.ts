/**
 * Translation Service with Caching
 * Handles dynamic content translation with cache
 */

interface CacheEntry {
  timestamp: number;
  translation: string;
}

// In-memory cache with 1 hour expiration
const translationCache: Record<string, CacheEntry> = {};
const CACHE_DURATION = 60 * 60 * 1000; // 1 hour

// Get from localStorage for persistent caching
const getPersistedCache = (): Record<string, string> => {
  try {
    const cached = localStorage.getItem('translationCache');
    return cached ? JSON.parse(cached) : {};
  } catch (error) {
    console.error('Error reading translation cache:', error);
    return {};
  }
};

// Save to localStorage
const setPersistedCache = (cache: Record<string, string>) => {
  try {
    localStorage.setItem('translationCache', JSON.stringify(cache));
  } catch (error) {
    console.error('Error saving translation cache:', error);
  }
};

// Initialize persisted cache on app start
let persistedCache = getPersistedCache();

/**
 * Generate cache key from text and target language
 */
const getCacheKey = (text: string, targetLang: string): string => {
  return `${targetLang}:${text}`;
};

/**
 * Check if translation is in cache
 */
const getFromCache = (text: string, targetLang: string): string | null => {
  const key = getCacheKey(text, targetLang);
  
  // Check memory cache first
  if (translationCache[key]) {
    const entry = translationCache[key];
    if (Date.now() - entry.timestamp < CACHE_DURATION) {
      return entry.translation;
    } else {
      delete translationCache[key];
    }
  }
  
  // Check persisted cache
  if (persistedCache[key]) {
    return persistedCache[key];
  }
  
  return null;
};

/**
 * Add translation to cache
 */
const addToCache = (text: string, translation: string, targetLang: string) => {
  const key = getCacheKey(text, targetLang);
  
  // Add to memory cache
  translationCache[key] = {
    timestamp: Date.now(),
    translation,
  };
  
  // Add to persisted cache
  persistedCache[key] = translation;
  setPersistedCache(persistedCache);
};

/**
 * Translate text using external API
 * Falls back to returning original text if service fails
 */
const translateViaAPI = async (text: string, targetLang: string): Promise<string> => {
  try {
    // Using Google Translate API endpoint (requires backend proxy or CORS setup)
    // For now, using a simple translation service
    const response = await fetch('https://api.mymemory.translated.net/get', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    } as any).then(r => r.json());
    
    // This is a placeholder - implement actual translation service
    console.warn('Translation service not fully configured. Using fallback.');
    return text; // Fallback to original text
  } catch (error) {
    console.error('Translation error:', error);
    return text; // Fallback to original text on error
  }
};

/**
 * Main translation function
 * @param text - Text to translate
 * @param targetLang - Target language code (ru, en)
 * @returns Translated text or original if translation fails
 */
export const translateText = async (
  text: string,
  targetLang: string
): Promise<string> => {
  if (!text || targetLang === 'uz') {
    return text;
  }

  // Check cache first
  const cached = getFromCache(text, targetLang);
  if (cached) {
    return cached;
  }

  // Translate via API
  const translation = await translateViaAPI(text, targetLang);
  
  // Add to cache
  addToCache(text, translation, targetLang);
  
  return translation;
};

/**
 * Batch translate multiple texts
 */
export const translateBatch = async (
  texts: string[],
  targetLang: string
): Promise<string[]> => {
  const results = await Promise.all(
    texts.map(text => translateText(text, targetLang))
  );
  return results;
};

/**
 * Clear translation cache
 */
export const clearTranslationCache = () => {
  Object.keys(translationCache).forEach(key => delete translationCache[key]);
  persistedCache = {};
  localStorage.removeItem('translationCache');
};

/**
 * Get cache stats
 */
export const getCacheStats = () => {
  return {
    memoryCacheSize: Object.keys(translationCache).length,
    persistedCacheSize: Object.keys(persistedCache).length,
  };
};

export default {
  translateText,
  translateBatch,
  clearTranslationCache,
  getCacheStats,
};
