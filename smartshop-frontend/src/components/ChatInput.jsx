import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Camera, Phone } from 'lucide-react';
import { cn } from '../utils/helpers';

const ChatInput = ({ 
  onSend, 
  onPhotoUpload, 
  onContactAgent,
  isLoading = false,
  disabled = false,
  placeholder = 'Ex : chaussures homme cuir, chemises, polo...'
}) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Auto-focus input on mount
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading || disabled) return;
    
    onSend(message.trim());
    setMessage('');
    
    // Refocus input after send
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 100);
  };

  const handleKeyPress = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onPhotoUpload) {
      onPhotoUpload(file);
    }
    // Reset input
    e.target.value = '';
  };

  const handleContactAgent = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Send contact message
    onSend("Je veux parler à un agent");
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      {/* Action Buttons Row */}
      <div className="flex gap-2 mb-3">
        <button
          onClick={handlePhotoClick}
          disabled={disabled}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            'bg-gray-100 text-gray-700 hover:bg-gray-200',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <Camera className="w-4 h-4" />
          Importer une photo
        </button>

        <button
          type="button"
          onClick={handleContactAgent}
          disabled={disabled}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
            'bg-purple-100 text-purple-700 hover:bg-purple-200',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <Phone className="w-4 h-4" />
          Parler à un agent
        </button>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* Message Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            className={cn(
              'w-full px-4 py-3 pr-12 rounded-xl border border-gray-300',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
              'disabled:bg-gray-100 disabled:cursor-not-allowed',
              'text-sm placeholder:text-gray-400'
            )}
          />
          
          {/* Character count (optional) */}
          {message.length > 100 && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
              {message.length}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className={cn(
            'flex items-center justify-center w-12 h-12 rounded-xl',
            'bg-gradient-to-r from-primary-600 to-secondary-600',
            'text-white transition-all duration-300',
            'hover:shadow-lg hover:scale-105',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100'
          )}
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </form>

      {/* Typing indicator (optional) */}
      {isLoading && (
        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span>SmartShop réfléchit...</span>
        </div>
      )}
    </div>
  );
};

export default ChatInput;
