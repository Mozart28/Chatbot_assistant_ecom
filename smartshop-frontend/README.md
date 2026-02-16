# SmartShop Frontend - React + Tailwind

Modern, responsive e-commerce chat interface built with React, Tailwind CSS, and JavaScript.

## 🚀 Features

✅ **Modern UI/UX**
- Beautiful gradient design
- Smooth animations
- Responsive (mobile, tablet, desktop)
- Dark mode ready

✅ **Chat Interface**
- Real-time messaging
- Typing indicators
- Message timestamps
- Image support
- Product cards
- Rating system

✅ **Shopping Cart**
- Add/remove products
- Live total calculation
- Persistent storage (localStorage)
- Checkout flow

✅ **Performance**
- Optimized re-renders
- Lazy loading
- Local storage caching
- Fast animations

## 📦 Installation

### Prerequisites
- Node.js 16+ and npm

### Setup

1. **Install dependencies**
```bash
cd smartshop-frontend
npm install
```

2. **Configure API endpoint**

Create `.env` file in root:
```env
REACT_APP_API_URL=http://localhost:8000
```

3. **Start development server**
```bash
npm start
```

App will open at `http://localhost:3000`

4. **Build for production**
```bash
npm run build
```

## 🏗️ Project Structure

```
smartshop-frontend/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── components/
│   │   ├── ChatMessage.jsx  # Message bubble component
│   │   ├── ChatInput.jsx    # Input area with actions
│   │   └── Sidebar.jsx      # Cart & navigation
│   ├── services/
│   │   └── api.js           # API client (Axios)
│   ├── utils/
│   │   └── helpers.js       # Utility functions
│   ├── App.jsx              # Main app component
│   ├── index.js             # Entry point
│   └── index.css            # Tailwind + custom styles
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## 🔌 Backend Integration

### API Endpoints Expected

The frontend expects these backend endpoints:

```javascript
POST   /chat              // Send message
GET    /products/search   // Search products
GET    /products/:id/image // Get product image
POST   /cart/add          // Add to cart
GET    /cart              // Get cart
DELETE /cart              // Clear cart
POST   /feedback          // Submit rating
```

### Example API Response Format

**Chat Message Response:**
```json
{
  "message": "Voici les produits...",
  "type": "text",
  "products": [],
  "image_url": null
}
```

**Add to Cart Response:**
```json
{
  "success": true,
  "message": "Produit ajouté",
  "cart": [...items]
}
```

## 🎨 Customization

### Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#8b5cf6', // Change main color
        600: '#7c3aed',
      }
    }
  }
}
```

### Fonts

Add to `public/index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

Then in `tailwind.config.js`:
```javascript
fontFamily: {
  sans: ['YourFont', 'sans-serif'],
}
```

## 🔧 Components API

### ChatMessage

```jsx
<ChatMessage 
  message={{
    role: 'user' | 'assistant',
    content: 'text',
    image_url?: 'url',
    product?: {...},
    type?: 'CONTACT_AGENT',
    timestamp: 'ISO date'
  }}
  onRate={(rating) => {...}}
/>
```

### ChatInput

```jsx
<ChatInput
  onSend={(message) => {...}}
  onPhotoUpload={(file) => {...}}
  onContactAgent={() => {...}}
  isLoading={false}
  disabled={false}
/>
```

### Sidebar

```jsx
<Sidebar
  cart={[...products]}
  onClearCart={() => {...}}
  onCheckout={() => {...}}
  onNewOrder={() => {...}}
  isOpen={true}
  onClose={() => {...}}
/>
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Drag & drop `build/` folder to Netlify
```

### Traditional Hosting

```bash
npm run build
# Upload `build/` folder to your server
```

## 🔒 Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000    # Backend URL
REACT_APP_ENABLE_ANALYTICS=false           # Analytics toggle
REACT_APP_SENTRY_DSN=                      # Error tracking
```

## 🐛 Troubleshooting

**Issue**: Tailwind styles not applying
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: API calls failing
- Check `REACT_APP_API_URL` in `.env`
- Verify backend is running
- Check browser console for CORS errors

**Issue**: Build errors
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules build
npm install
npm run build
```

## 📚 Tech Stack

- **React 18** - UI framework
- **Tailwind CSS 3** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons
- **clsx + tailwind-merge** - Class management

## 🎯 Performance Tips

1. **Image Optimization**
   - Use WebP format
   - Lazy load images
   - Add loading placeholders

2. **Code Splitting**
   - Use React.lazy() for routes
   - Dynamic imports for heavy components

3. **Caching**
   - Enable service workers
   - Cache API responses in localStorage

## 📄 License

MIT License - feel free to use for commercial projects

## 👨‍💻 Author

Mozart Codjo - Data Scientist & AI Engineer

---

**Need help?** Open an issue or contact support.
