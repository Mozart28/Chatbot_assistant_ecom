#!/bin/bash

# SmartShop Frontend - Quick Fix Script
# Run this if you encounter errors

echo "🔧 SmartShop Frontend - Error Fix Script"
echo "========================================"
echo ""

# Fix 1: Replace index.css
echo "📝 Fixing index.css..."
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-gray-200;
  }
  body {
    @apply bg-gray-50 text-gray-900;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

@layer components {
  /* Custom scrollbar */
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-track {
    @apply bg-gray-100;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb {
    @apply bg-gray-300 rounded-full;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    @apply bg-gray-400;
  }

  /* Message animations */
  .message-enter {
    animation: slideUp 0.3s ease-out;
  }

  /* Product card hover effect */
  .product-card {
    @apply transition-all duration-300 hover:shadow-xl hover:-translate-y-1;
  }

  /* Button styles */
  .btn-primary {
    @apply bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-6 py-3 rounded-lg font-medium hover:from-primary-700 hover:to-secondary-700 transition-all duration-300 shadow-md hover:shadow-lg;
  }

  .btn-secondary {
    @apply bg-white text-primary-700 border-2 border-primary-600 px-6 py-3 rounded-lg font-medium hover:bg-primary-50 transition-all duration-300;
  }

  .btn-ghost {
    @apply text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100 transition-all duration-200;
  }
}

@layer utilities {
  .text-gradient {
    @apply bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent;
  }
}

/* Keyframe animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
EOF

echo "✅ index.css fixed!"
echo ""

# Fix 2: Clear cache and reinstall
echo "🧹 Clearing cache and node_modules..."
rm -rf node_modules package-lock.json
echo "✅ Cleared!"
echo ""

echo "📦 Reinstalling dependencies..."
npm install
echo "✅ Dependencies installed!"
echo ""

echo "🎉 All fixed! Now run: npm start"
echo ""
