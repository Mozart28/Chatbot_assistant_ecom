import React, { useState, useEffect, useRef } from 'react';
import { Menu, X } from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import { chatAPI } from './services/api';
import { generateId, scrollToBottom, storage } from './utils/helpers';
import { cn } from './utils/helpers';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [cart, setCart] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  // Load persisted data on mount
  useEffect(() => {
    const savedMessages = storage.get('messages', []);
    const savedCart = storage.get('cart', []);
    
    if (savedMessages.length > 0) {
      setMessages(savedMessages);
    } else {
      // Welcome message
      setMessages([
        {
          id: generateId(),
          role: 'assistant',
          content: '👋 Bonjour ! Je suis votre assistant SmartShop. Que recherchez-vous aujourd\'hui ?',
          timestamp: new Date().toISOString(),
        },
      ]);
    }
    
    setCart(savedCart);
  }, []);

  // Persist messages and cart
  useEffect(() => {
    storage.set('messages', messages);
  }, [messages]);

  useEffect(() => {
    storage.set('cart', cart);
  }, [cart]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    scrollToBottom('chat-container');
  }, [messages]);

  const handleSendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    // Add user message
    const userMsg = {
      id: generateId(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Call REAL backend API
      const response = await chatAPI.sendMessage(userMessage, conversationId);
      
      // Update conversation ID if provided
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      // Handle different response types
      handleBackendResponse(response);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMsg = {
        id: generateId(),
        role: 'assistant',
        content: '❌ Erreur: Vérifiez que le backend est lancé (python backend_api.py)',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackendResponse = (response) => {
    
    const assistantMsg = {
      id: generateId(),
      role: 'assistant',
      timestamp: new Date().toISOString(),
    };

    switch (response.type) {
      case 'text':
        assistantMsg.content = response.message;
        setMessages((prev) => [...prev, assistantMsg]);
        break;

      case 'product_image':
        assistantMsg.content = response.message;
        assistantMsg.product = response.product;
        assistantMsg.image_url = response.product?.image_url;
        setMessages((prev) => [...prev, assistantMsg]);
        break;

      case 'cart_updated':
        assistantMsg.content = response.message;
        setMessages((prev) => [...prev, assistantMsg]);
        if (response.cart) {
          setCart(response.cart);
        }
        break;

        case 'contact_agent':
          assistantMsg.content = response.message;
          assistantMsg.type = 'CONTACT_AGENT';
          assistantMsg.rated = false;
          assistantMsg.rating = 0;
          
          // ← ADD THIS DEBUG ALERT:
          alert(`Debug: type=${assistantMsg.type}, rated=${assistantMsg.rated}, rating=${assistantMsg.rating}`);
          
          setMessages((prev) => [...prev, assistantMsg]);
          break;

      default:
        assistantMsg.content = response.message || 'Réponse reçue';
        setMessages((prev) => [...prev, assistantMsg]);
    }
  };

  const handlePhotoUpload = async (file) => {
    const msg = {
      id: generateId(),
      role: 'user',
      content: '📷 Image envoyée',
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, msg]);
    // TODO: Implement image upload endpoint
  };

  const handleContactAgent = async () => {
    
    await handleSendMessage('Je veux parler à un agent');
  };

  const handleRate = async (messageId, rating) => {
    try {
      await chatAPI.submitRating(rating, messageId);
      
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, rating, rated: true } : msg
        )
      );
    } catch (error) {
      console.error('Error submitting rating:', error);
    }
  };

  const handleNewOrder = async () => {
    try {
      const response = await chatAPI.resetConversation(conversationId);
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      setMessages([
        {
          id: generateId(),
          role: 'assistant',
          content: '👋 Nouvelle session ! Que puis-je vous proposer ?',
          timestamp: new Date().toISOString(),
        },
      ]);
      setCart([]);
      
    } catch (error) {
      console.error('Error resetting conversation:', error);
      setMessages([
        {
          id: generateId(),
          role: 'assistant',
          content: '👋 Nouvelle session ! Que puis-je vous proposer ?',
          timestamp: new Date().toISOString(),
        },
      ]);
      setCart([]);
      setConversationId(null);
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Voulez-vous vraiment vider le panier ?')) {
      try {
        await chatAPI.clearCart(conversationId);
        setCart([]);
      } catch (error) {
        console.error('Error clearing cart:', error);
        setCart([]);
      }
    }
  };

  const handleCheckout = () => {
    alert('🎉 Commande envoyée ! Merci pour votre achat.');
    setCart([]);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        cart={cart}
        onClearCart={handleClearCart}
        onCheckout={handleCheckout}
        onNewOrder={handleNewOrder}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gradient">
                🛒 Smart Shop
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Trouvez, comparez et achetez avec l'IA
              </p>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              {sidebarOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </header>

        {/* Messages Container */}
        <div
          id="chat-container"
          className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6 lg:px-8"
        >
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onRate={(rating) => handleRate(message.id, rating)}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <ChatInput
          onSend={handleSendMessage}
          onPhotoUpload={handlePhotoUpload}
          onContactAgent={handleContactAgent}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

export default Chatbot;
