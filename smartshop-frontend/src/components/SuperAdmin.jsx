// SuperAdmin.jsx - LLM Model Management Dashboard
import React, { useState, useEffect } from 'react';
import {
  Settings,
  TrendingUp,
  DollarSign,
  Zap,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  LogOut,
  Activity
} from 'lucide-react';

const API_URL = process.env.REACT_APP_SUPERADMIN_API_URL || 'http://localhost:5004';

function SuperAdmin() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [models, setModels] = useState({});
  const [config, setConfig] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('models'); // models, usage, config

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('superadmin_token');
    if (token) {
      setIsAuthenticated(true);
      loadData();
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/superadmin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('superadmin_token', data.token);
        setIsAuthenticated(true);
        loadData();
      } else {
        alert('❌ ' + data.error);
      }
    } catch (error) {
      alert('❌ Login failed: ' + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('superadmin_token');
    setIsAuthenticated(false);
  };

  const loadData = async () => {
    const token = localStorage.getItem('superadmin_token');
    
    try {
      // Load models
      const modelsRes = await fetch(`${API_URL}/superadmin/models`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const modelsData = await modelsRes.json();
      if (modelsData.success) setModels(modelsData.models);

      // Load config
      const configRes = await fetch(`${API_URL}/superadmin/config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const configData = await configRes.json();
      if (configData.success) setConfig(configData);

      // Load usage
      const usageRes = await fetch(`${API_URL}/superadmin/usage`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const usageData = await usageRes.json();
      if (usageData.success) setUsage(usageData);

    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleSwitchModel = async (provider, model) => {
    if (!window.confirm(`Switch to ${models[provider][model].name}?`)) return;

    setLoading(true);
    const token = localStorage.getItem('superadmin_token');

    try {
      const response = await fetch(`${API_URL}/superadmin/switch-model`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ provider, model })
      });

      const data = await response.json();

      if (data.success) {
        alert(`✅ ${data.message}`);
        loadData();
      } else {
        alert('❌ ' + data.error);
      }
    } catch (error) {
      alert('❌ Switch failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResetUsage = async () => {
    if (!window.confirm('Reset all usage statistics? This cannot be undone!')) return;

    const token = localStorage.getItem('superadmin_token');

    try {
      const response = await fetch(`${API_URL}/superadmin/usage/reset`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.success) {
        alert('✅ Usage statistics reset');
        loadData();
      }
    } catch (error) {
      alert('❌ Reset failed: ' + error.message);
    }
  };

  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">🔐 SmartShop Super Admin Panel</h1>
              <p className="text-purple-200 text-sm mt-1">LLM Model Management & Monitoring</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
            >
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      {config && usage && (
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard
              icon={Activity}
              label="Current Model"
              value={config.current_model_info?.name || 'N/A'}
              color="blue"
              subtitle={config.config.current_provider}
            />
            <StatCard
              icon={TrendingUp}
              label="Total Requests"
              value={usage.stats.requests_count.toLocaleString()}
              color="green"
            />
            <StatCard
              icon={Zap}
              label="Total Tokens"
              value={(usage.stats.total_tokens / 1000).toFixed(1) + 'K'}
              color="purple"
            />
            <StatCard
              icon={DollarSign}
              label="Total Cost"
              value={`$${usage.budget.used}`}
              color="orange"
              subtitle={`${usage.budget.percent_used}% of budget`}
            />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6">
        <div className="bg-white rounded-t-xl border-b">
          <div className="flex gap-6 px-6">
            {[
              { id: 'models', label: '🤖 Models', icon: Settings },
              { id: 'usage', label: '📊 Usage', icon: TrendingUp },
              { id: 'config', label: '⚙️ Config', icon: Settings }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon size={18} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-xl shadow-lg p-6">
          {activeTab === 'models' && (
            <ModelsTab
              models={models}
              currentProvider={config?.config.current_provider}
              currentModel={config?.config.current_model}
              onSwitch={handleSwitchModel}
              loading={loading}
            />
          )}

          {activeTab === 'usage' && usage && (
            <UsageTab
              usage={usage}
              onReset={handleResetUsage}
            />
          )}

          {activeTab === 'config' && config && (
            <ConfigTab
              config={config.config}
              onUpdate={loadData}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================
// SUB-COMPONENTS
// ============================================

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState('superadmin@smartshop.com');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🔐</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Super Admin</h1>
          <p className="text-gray-600">LLM Model Management Panel</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition"
          >
            Login
          </button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
          <p className="font-medium mb-1">Default Credentials:</p>
          <p>Email: superadmin@smartshop.com</p>
          <p>Password: superadmin123</p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, subtitle }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200'
  };

  return (
    <div className="bg-white p-6 rounded-xl border shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon size={24} />
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  );
}

function ModelsTab({ models, currentProvider, currentModel, onSwitch, loading }) {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Available LLM Models</h2>
        <p className="text-sm text-gray-600 mt-1">Switch between different AI models based on your needs</p>
      </div>

      <div className="space-y-6">
        {Object.entries(models).map(([provider, providerModels]) => (
          <div key={provider} className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-bold text-lg text-gray-900 mb-4 capitalize">
              {provider === 'mistral' ? '🔵 Mistral AI' :
               provider === 'openai' ? '🟢 OpenAI' :
               provider === 'anthropic' ? '🟣 Anthropic' :
               provider === 'qwen' ? '🟠 Qwen' :
               provider === 'llama' ? '🔴 Llama' : provider}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(providerModels).map(([modelKey, modelInfo]) => {
                const isCurrent = provider === currentProvider && modelKey === currentModel;

                return (
                  <div
                    key={modelKey}
                    className={`p-4 rounded-lg border-2 transition ${
                      isCurrent
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">{modelInfo.name}</h4>
                        <p className="text-xs text-gray-500">{modelInfo.provider}</p>
                      </div>
                      {isCurrent && (
                        <span className="flex items-center gap-1 text-xs bg-purple-600 text-white px-2 py-1 rounded">
                          <CheckCircle size={12} />
                          Active
                        </span>
                      )}
                    </div>

                    <div className="space-y-1 mb-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Cost:</span>
                        <span className="font-medium">${modelInfo.cost_per_1m_tokens}/1M tokens</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Speed:</span>
                        <span className={`font-medium ${
                          modelInfo.speed === 'very_fast' ? 'text-green-600' :
                          modelInfo.speed === 'fast' ? 'text-blue-600' :
                          modelInfo.speed === 'medium' ? 'text-orange-600' :
                          'text-red-600'
                        }`}>
                          {modelInfo.speed.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Quality:</span>
                        <span className="font-medium">{modelInfo.quality}</span>
                      </div>
                    </div>

                    {!isCurrent && (
                      <button
                        onClick={() => onSwitch(provider, modelKey)}
                        disabled={loading}
                        className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition text-sm font-medium"
                      >
                        {loading ? 'Switching...' : 'Switch to this model'}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function UsageTab({ usage, onReset }) {
  const { stats, budget } = usage;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Usage Statistics</h2>
          <p className="text-sm text-gray-600 mt-1">Monitor your API usage and costs</p>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          <RefreshCw size={18} />
          Reset Stats
        </button>
      </div>

      {/* Budget Progress */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-xl border border-purple-200">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-gray-900">Monthly Budget</h3>
          <span className="text-2xl font-bold text-purple-600">
            ${budget.used} / ${budget.monthly_limit}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
          <div
            className={`h-4 rounded-full transition-all ${
              budget.percent_used > 90 ? 'bg-red-600' :
              budget.percent_used > 70 ? 'bg-orange-600' :
              'bg-green-600'
            }`}
            style={{ width: `${Math.min(budget.percent_used, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-sm text-gray-600">
          <span>{budget.percent_used}% used</span>
          <span>${budget.remaining} remaining</span>
        </div>
      </div>

      {/* By Model */}
      <div>
        <h3 className="font-bold text-gray-900 mb-3">Usage by Model</h3>
        <div className="space-y-2">
          {Object.entries(stats.by_model || {}).map(([model, data]) => (
            <div key={model} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{model}</p>
                <p className="text-sm text-gray-600">{data.requests} requests</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-gray-900">${data.cost.toFixed(2)}</p>
                <p className="text-sm text-gray-600">{(data.tokens / 1000).toFixed(1)}K tokens</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* By Date */}
      <div>
        <h3 className="font-bold text-gray-900 mb-3">Recent Usage (Last 7 Days)</h3>
        <div className="space-y-2">
          {Object.entries(stats.by_date || {})
            .slice(-7)
            .reverse()
            .map(([date, data]) => (
              <div key={date} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{date}</p>
                  <p className="text-sm text-gray-600">{data.requests} requests</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-gray-900">${data.cost.toFixed(2)}</p>
                  <p className="text-sm text-gray-600">{(data.tokens / 1000).toFixed(1)}K tokens</p>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function ConfigTab({ config, onUpdate }) {
  const [monthlyBudget, setMonthlyBudget] = useState(config.monthly_budget);
  const [autoSwitch, setAutoSwitch] = useState(config.auto_switch_enabled);

  const handleSave = async () => {
    const token = localStorage.getItem('superadmin_token');

    try {
      const response = await fetch(`${API_URL}/superadmin/config/update`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          monthly_budget: monthlyBudget,
          auto_switch_enabled: autoSwitch
        })
      });

      const data = await response.json();

      if (data.success) {
        alert('✅ Configuration saved');
        onUpdate();
      }
    } catch (error) {
      alert('❌ Save failed: ' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-1">Configuration</h2>
        <p className="text-sm text-gray-600">Manage system settings and budget limits</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Budget ($)
          </label>
          <input
            type="number"
            value={monthlyBudget}
            onChange={(e) => setMonthlyBudget(parseFloat(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <p className="text-xs text-gray-500 mt-1">
            System will alert when budget is exceeded
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={autoSwitch}
            onChange={(e) => setAutoSwitch(e.target.checked)}
            className="w-5 h-5 text-purple-600"
          />
          <div>
            <label className="text-sm font-medium text-gray-900">
              Auto-switch to cheaper model when budget exceeded
            </label>
            <p className="text-xs text-gray-500">
              Automatically fallback to cheaper model to stay within budget
            </p>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
}

export default SuperAdmin;
