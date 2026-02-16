import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind classes with proper override handling
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format price with currency
 */
export function formatPrice(price, currency = 'FCFA') {
  if (!price) return 'Prix non disponible';
  return `${Number(price).toLocaleString('fr-FR')} ${currency}`;
}

/**
 * Format timestamp to readable time
 */
export function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('fr-FR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

/**
 * Generate unique ID
 */
export function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Debounce function for input handling
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Parse markdown-like formatting to HTML
 */
export function parseMarkdown(text) {
  if (!text) return '';
  
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br/>')
    // Emojis (preserve them)
    .replace(/([\u{1F300}-\u{1F9FF}])/gu, '$1');
}

/**
 * Detect if message contains numbered choices
 */
export function detectChoices(text) {
  const choiceRegex = /[1-3]️⃣/g;
  return text.match(choiceRegex) || [];
}

/**
 * Extract product info from message
 */
export function extractProductInfo(message) {
  // Look for price pattern
  const priceMatch = message.match(/(\d+(?:,\d+)*)\s*FCFA/);
  const price = priceMatch ? priceMatch[1].replace(/,/g, '') : null;
  
  return {
    hasPrice: !!price,
    price,
  };
}

/**
 * Validate email
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Scroll to bottom of container smoothly
 */
export function scrollToBottom(elementId, behavior = 'smooth') {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollTo({
      top: element.scrollHeight,
      behavior,
    });
  }
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}

/**
 * Local storage helpers
 */
export const storage = {
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch {
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch {
      return false;
    }
  },
};
