import axios from 'axios';

// Configure your backend URL here
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('Response Error:', error.response?.status, error.message);
    
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access');
    } else if (error.response?.status === 500) {
      console.error('Server error');
    }
    
    return Promise.reject(error);
  }
);

// API Methods
export const chatAPI = {
  /**
   * Send a message to the chatbot
   * @param {string} message - User message
   * @param {string} conversationId - Current conversation ID
   * @returns {Promise} API response
   */
  sendMessage: async (message, conversationId = null) => {
    try {
      const response = await apiClient.post('/chat', {
        message,
        conversation_id: conversationId,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to send message');
    }
  },

  /**
   * Search for products
   * @param {string} query - Search query
   * @returns {Promise} Product list
   */
  searchProducts: async (query) => {
    try {
      const response = await apiClient.get('/products/search', {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to search products');
    }
  },

  /**
   * Get product image
   * @param {string} productId - Product ID
   * @returns {Promise} Product details with image
   */
  getProductImage: async (productId) => {
    try {
      const response = await apiClient.get(`/products/${productId}/image`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to load product image');
    }
  },

  /**
   * Add product to cart
   * @param {object} product - Product object
   * @returns {Promise} Cart update response
   */
  addToCart: async (product) => {
    try {
      const response = await apiClient.post('/cart/add', { product });
      return response.data;
    } catch (error) {
      throw new Error('Failed to add to cart');
    }
  },

  /**
   * Get cart contents
   * @returns {Promise} Cart items
   */
  getCart: async () => {
    try {
      const response = await apiClient.get('/cart');
      return response.data;
    } catch (error) {
      throw new Error('Failed to load cart');
    }
  },

  /**
   * Clear cart
   * @returns {Promise} Success response
   */
  clearCart: async () => {
    try {
      const response = await apiClient.delete('/cart');
      return response.data;
    } catch (error) {
      throw new Error('Failed to clear cart');
    }
  },

  /**
   * Submit rating
   * @param {number} rating - Rating value (1-5)
   * @param {number} messageIndex - Message index
   * @returns {Promise} Success response
   */
  submitRating: async (rating, messageIndex) => {
    try {
      const response = await apiClient.post('/feedback', {
        rating,
        message_index: messageIndex,
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to submit rating');
    }
  },
};

export default apiClient;
