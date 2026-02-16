import React from 'react';
import { 
  ShoppingCart, 
  Trash2, 
  Check, 
  X, 
  User, 
  LogIn,
  RotateCcw,
  Package
} from 'lucide-react';
import { cn, formatPrice } from '../utils/helpers';

const Sidebar = ({ 
  cart = [], 
  onClearCart, 
  onCheckout,
  onNewOrder,
  isOpen = true,
  onClose 
}) => {
  const total = cart.reduce((sum, item) => {
    const price = parseInt(item.price) || 0;
    return sum + price;
  }, 0);

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:relative inset-y-0 right-0 z-50',
          'w-80 bg-white border-l border-gray-200',
          'flex flex-col transition-transform duration-300',
          isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
        )}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-bold text-lg text-gray-900">SmartShop</h2>
                <p className="text-xs text-gray-500">Assistant IA</p>
              </div>
            </div>
            
            {/* Close button (mobile) */}
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <p className="text-sm text-gray-600">
            Votre guide d'achat de vêtements et accessoires homme
          </p>
        </div>

        {/* Actions */}
        <div className="p-4 border-b border-gray-200 space-y-2">
          <button
            onClick={onNewOrder}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-lg font-medium hover:shadow-lg transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            Nouvelle commande
          </button>

          <button
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
          >
            <Package className="w-4 h-4" />
            Mon panier ({cart.length})
          </button>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <ShoppingCart className="w-4 h-4" />
            Panier ({cart.length})
          </h3>

          {cart.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
                <ShoppingCart className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-sm text-gray-500">Votre panier est vide</p>
              <p className="text-xs text-gray-400 mt-1">
                Ajoutez des produits pour commencer
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {cart.map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded-lg p-3 border border-gray-200 hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-sm text-gray-900 flex-1 pr-2">
                      {item.name}
                    </h4>
                    <button
                      className="p-1 hover:bg-red-100 rounded text-red-500 transition-colors"
                      title="Retirer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-primary-600">
                      {formatPrice(item.price)}
                    </span>
                    
                    {item.in_stock && (
                      <span className="text-xs text-green-600 flex items-center gap-1">
                        <Check className="w-3 h-3" />
                        En stock
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cart Footer */}
        {cart.length > 0 && (
          <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-3">
            <div className="flex items-center justify-between py-2">
              <span className="font-semibold text-gray-900">Total</span>
              <span className="text-xl font-bold text-gradient">
                {formatPrice(total)}
              </span>
            </div>

            <button
              onClick={onCheckout}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium hover:shadow-lg transition-all"
            >
              <Check className="w-5 h-5" />
              Commander
            </button>

            <button
              onClick={onClearCart}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg text-sm transition-all"
            >
              <Trash2 className="w-4 h-4" />
              Vider le panier
            </button>
          </div>
        )}

        {/* Admin Section */}
        <div className="p-4 border-t border-gray-200">
          <details className="group">
            <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
              <span className="flex items-center gap-2">
                <User className="w-4 h-4" />
                Espace administrateur
              </span>
              <span className="text-gray-400">▼</span>
            </summary>
            
            <div className="mt-3 space-y-2">
              <input
                type="email"
                placeholder="Email"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="password"
                placeholder="Mot de passe"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gray-800 text-white rounded-lg text-sm hover:bg-gray-900 transition-all">
                <LogIn className="w-4 h-4" />
                Connexion
              </button>
            </div>
          </details>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500">Mozart Solutions</p>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
