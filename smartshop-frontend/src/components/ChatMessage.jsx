import React from 'react';
import { User, Bot, Star, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';
import { cn, formatTime } from '../utils/helpers';

const ChatMessage = ({ message, onRate }) => {
  const isUser = message.role === 'user';
  const [rating, setRating] = React.useState(message.rating || 0);
  const [isRated, setIsRated] = React.useState(message.rated || false);
  
  // NEW: Like/Dislike state
  const [reaction, setReaction] = React.useState(null);
  const [imageLoaded, setImageLoaded] = React.useState(false);
  const [showSparkles, setShowSparkles] = React.useState(false);

  const handleRate = (value) => {
    setRating(value);
    setIsRated(true);
    if (onRate) {
      onRate(value);
    }
  };

  // NEW: Handle like/dislike
  const handleReaction = (type) => {
    setReaction(type);
    
    // Send feedback to backend
    if (message.product?.id) {
      fetch('http://localhost:5002/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: message.product.id,
          reaction: type
        })
      }).catch(err => console.log('Feedback error:', err));
    }
  };

  // NEW: Image load handler with wow effect
  const handleImageLoad = () => {
    setImageLoaded(true);
    setShowSparkles(true);
    setTimeout(() => setShowSparkles(false), 1000);
  };

  // Extract image URLs from markdown syntax: ![alt](url)
  const extractImages = (text) => {
    if (!text) return { images: [], cleanText: text };
    
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
    const images = [];
    let match;
    
    while ((match = imageRegex.exec(text)) !== null) {
      images.push({
        alt: match[1] || 'Product image',
        url: match[2]
      });
    }
    
    // Remove markdown image syntax from text
    const cleanText = text.replace(imageRegex, '');
    
    return { images, cleanText };
  };

  // Parse markdown for bold, italic, etc
  const parseMarkdown = (text) => {
    if (!text) return '';
    
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
  };

  const { images, cleanText } = extractImages(message.content);
  
  // Collect all images
  const allImages = [
    ...images,
    ...(message.image_url ? [{ url: message.image_url, alt: 'Product' }] : []),
    ...(message.product?.image_url ? [{ url: message.product.image_url, alt: message.product.name }] : [])
  ];

  // Determine if this is a product image message - MORE FLEXIBLE
  const hasProductImage = allImages.length > 0 && !isUser;

  return (
    <div
      className={cn(
        'flex gap-3 mb-4 message-enter',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-gradient-to-br from-primary-500 to-secondary-500'
            : 'bg-gradient-to-br from-purple-600 to-indigo-600'
        )}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          'flex-1 max-w-[65%] space-y-2',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        {/* Text Content BEFORE image (if text exists before product image) */}
        {!hasProductImage && cleanText && (
          <div
            className={cn(
              'rounded-2xl px-4 py-3 shadow-sm',
              isUser
                ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-tr-sm'
                : 'bg-white text-gray-800 border border-gray-200 rounded-tl-sm'
            )}
          >
            <div
              className="text-sm leading-relaxed whitespace-pre-wrap"
              dangerouslySetInnerHTML={{
                __html: parseMarkdown(cleanText),
              }}
            />
          </div>
        )}

        {/* Product Image with Enhanced Display */}
        {hasProductImage && (
          <div className="relative w-full">
            {/* Sparkle Effect */}
            {showSparkles && (
              <div className="absolute inset-0 pointer-events-none z-10">
                <Sparkles className="absolute top-2 left-2 text-yellow-400 animate-ping" size={24} />
                <Sparkles className="absolute top-2 right-2 text-yellow-400 animate-ping" size={20} style={{ animationDelay: '0.1s' }} />
                <Sparkles className="absolute bottom-2 left-2 text-yellow-400 animate-ping" size={20} style={{ animationDelay: '0.2s' }} />
                <Sparkles className="absolute bottom-2 right-2 text-yellow-400 animate-ping" size={24} style={{ animationDelay: '0.3s' }} />
              </div>
            )}

            {/* Image Card */}
            <div className={cn(
              'bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-200 transition-all duration-500',
              imageLoaded ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
            )}>
              {/* Image */}
              <div className="relative bg-gray-50">
                <img
                  src={allImages[0].url}
                  alt={allImages[0].alt}
                  onLoad={handleImageLoad}
                  className="w-full h-80 object-contain bg-white"
                  onError={(e) => {
                    console.error('Image failed to load:', allImages[0].url);
                    e.target.parentElement.innerHTML = `
                      <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-600">
                        ❌ Impossible de charger l'image
                      </div>
                    `;
                  }}
                />
                {!imageLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
                  </div>
                )}
              </div>

              {/* Product Info */}
              {message.product && (
                <div className="p-4">
                  <h3 className="font-bold text-lg text-gray-900 mb-1">
                    {message.product.name}
                  </h3>
                  {message.product.price && (
                    <p className="text-2xl font-bold text-purple-600 mb-3">
                      {message.product.price?.toLocaleString()} {message.product.currency || 'FCFA'}
                    </p>
                  )}
                  
                  {message.product.description && (
                    <p className="text-sm text-gray-600 mb-3">
                      {message.product.description}
                    </p>
                  )}

                  {message.product.in_stock !== undefined && (
                    <span
                      className={cn(
                        'inline-block mb-3 px-3 py-1 text-sm rounded-full',
                        message.product.in_stock
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      )}
                    >
                      {message.product.in_stock ? '✅ En stock' : '❌ Rupture'}
                    </span>
                  )}
                </div>
              )}

              {/* Like/Dislike Buttons */}
              <div className="flex items-center justify-center gap-4 p-4 bg-gray-50 border-t border-gray-200">
                <button
                  onClick={() => handleReaction('like')}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
                    reaction === 'like'
                      ? 'bg-green-100 text-green-600 scale-110'
                      : 'bg-white text-gray-600 hover:bg-green-50 hover:text-green-600 hover:scale-105'
                  )}
                >
                  <ThumbsUp size={18} className={reaction === 'like' ? 'fill-current' : ''} />
                  <span className="text-sm font-medium">J'aime</span>
                </button>

                <button
                  onClick={() => handleReaction('dislike')}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
                    reaction === 'dislike'
                      ? 'bg-red-100 text-red-600 scale-110'
                      : 'bg-white text-gray-600 hover:bg-red-50 hover:text-red-600 hover:scale-105'
                  )}
                >
                  <ThumbsDown size={18} className={reaction === 'dislike' ? 'fill-current' : ''} />
                  <span className="text-sm font-medium">Pas pour moi</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Text Content AFTER image (suggestions, follow-up) */}
        {hasProductImage && cleanText && (
          <div className="bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
            <div
              className="text-sm leading-relaxed whitespace-pre-wrap"
              dangerouslySetInnerHTML={{
                __html: parseMarkdown(cleanText),
              }}
            />
          </div>
        )}

        {/* Regular images (non-product) */}
        {!hasProductImage && allImages.length > 0 && (
          <div className="space-y-2">
            {allImages.map((img, idx) => (
              <div key={idx} className="rounded-lg overflow-hidden shadow-md">
                <img
                  src={img.url}
                  alt={img.alt}
                  className="w-full h-auto object-cover"
                  loading="lazy"
                  onError={(e) => {
                    console.error('Image failed to load:', img.url);
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML = `
                      <div class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
                        ❌ Impossible de charger l'image
                      </div>
                    `;
                  }}
                />
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div
          className={cn(
            'text-xs text-gray-500 px-2',
            isUser ? 'text-right' : 'text-left'
          )}
        >
          {formatTime(message.timestamp)}
        </div>

        {/* Rating Component (only for agent contact messages) */}
        {message.type === 'CONTACT_AGENT' && !isUser && (
          <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <p className="text-sm text-gray-700 mb-2 font-medium">
              ⭐ Notez cette mise en relation
            </p>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => !isRated && handleRate(star)}
                  disabled={isRated}
                  className={cn(
                    'transition-all duration-200 hover:scale-125',
                    isRated && 'cursor-not-allowed opacity-50'
                  )}
                >
                  <Star
                    className={cn(
                      'w-6 h-6',
                      star <= rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300 hover:text-yellow-400'
                    )}
                  />
                </button>
              ))}
            </div>
            {isRated && (
              <p className="text-xs text-green-600 mt-2">
                Merci pour votre retour ! 🙏
              </p>
            )}
          </div>
        )}

        {/* Quick Reply Buttons (if present) */}
        {message.quickReplies && message.quickReplies.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.quickReplies.map((reply, idx) => (
              <button
                key={idx}
                className="bg-white text-primary-600 border border-primary-200 px-3 py-1.5 rounded-full text-xs hover:bg-primary-50 transition-colors"
                onClick={() => reply.onClick && reply.onClick()}
              >
                {reply.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
