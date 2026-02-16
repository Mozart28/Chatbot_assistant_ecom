// AdminDashboard.jsx - Complete Admin Interface with Purple Theme
import React, { useState, useEffect } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  Search,
  BarChart,
  LogOut,
  Database,
  HardDrive,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';

const API_URL = process.env.REACT_APP_ADMIN_API_URL || 'http://localhost:5003';

function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({});
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('documents');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('admin_token');
    const userData = localStorage.getItem('admin_user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
      loadDocuments();
      loadStats();
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('admin_token', data.token);
        localStorage.setItem('admin_user', JSON.stringify(data.user));
        setIsAuthenticated(true);
        setUser(data.user);
        loadDocuments();
        loadStats();
      } else {
        alert('❌ ' + data.error);
      }
    } catch (error) {
      alert('❌ Login failed: ' + error.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    setIsAuthenticated(false);
    setUser(null);
  };

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${API_URL}/admin/documents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();
      if (data.success) {
        setDocuments(data.documents);
        setStats(prev => ({ ...prev, ...data.stats }));
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${API_URL}/admin/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    setUploadProgress('📤 Uploading file...');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', 'product_catalog');

    try {
      const token = localStorage.getItem('admin_token');
      
      setUploadProgress('📄 Extracting text...');
      const response = await fetch(`${API_URL}/admin/upload-pdf`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setUploadProgress('✅ Upload successful!');
        alert(`✅ ${data.document.filename} uploaded!\n\n` +
              `📊 Chunks: ${data.document.chunks}\n` +
              `☁️  Vectors: ${data.document.vectors_uploaded}`);
        loadDocuments();
        loadStats();
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      setUploadProgress('');
      alert('❌ Upload failed: ' + error.message);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(''), 3000);
    }
  };

  const handleDeleteDocument = async (documentId, filename) => {
    if (!window.confirm(`Delete "${filename}"?\n\nThis will remove all vectors from Pinecone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${API_URL}/admin/document/${documentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.success) {
        alert('✅ Document deleted');
        loadDocuments();
        loadStats();
      } else {
        throw new Error(data.error);
      }
    } catch (error) {
      alert('❌ Delete failed: ' + error.message);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setSearchResults([]);

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`${API_URL}/admin/search-test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: searchQuery, top_k: 5 })
      });

      const data = await response.json();

      if (data.success) {
        setSearchResults(data.results);
      }
    } catch (error) {
      alert('❌ Search failed: ' + error.message);
    } finally {
      setSearching(false);
    }
  };

  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Purple gradient */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">🔐 SmartShop Admin Panel</h1>
              <p className="text-purple-100 text-sm mt-1">PDF Management & Vector Database</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-purple-200">{user?.email}</p>
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
        </div>
      </header>

      {/* Tabs - Purple theme */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-6">
            {[
              { id: 'documents', label: '📚 Documents', icon: FileText },
              { id: 'upload', label: '📤 Upload', icon: Upload },
              { id: 'search', label: '🔍 Search Test', icon: Search },
              { id: 'stats', label: '📊 Statistics', icon: BarChart }
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
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={FileText}
            label="Total Documents"
            value={stats.total_documents || 0}
            color="purple"
          />
          <StatCard
            icon={Database}
            label="Total Vectors"
            value={(stats.total_vectors || 0).toLocaleString()}
            color="green"
          />
          <StatCard
            icon={HardDrive}
            label="Storage Used"
            value={`${stats.total_storage_mb || 0} MB`}
            color="blue"
          />
          <StatCard
            icon={BarChart}
            label="Index Fullness"
            value={`${((stats.index_fullness || 0) * 100).toFixed(1)}%`}
            color="orange"
          />
        </div>

        {/* Tab Content */}
        {activeTab === 'documents' && (
          <DocumentsTab
            documents={documents}
            onDelete={handleDeleteDocument}
          />
        )}

        {activeTab === 'upload' && (
          <UploadTab
            onUpload={handleFileUpload}
            uploading={uploading}
            progress={uploadProgress}
          />
        )}

        {activeTab === 'search' && (
          <SearchTab
            query={searchQuery}
            setQuery={setSearchQuery}
            onSearch={handleSearch}
            searching={searching}
            results={searchResults}
          />
        )}

        {activeTab === 'stats' && (
          <StatsTab stats={stats} />
        )}
      </main>
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState('admin@smartshop.com');
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Login</h1>
          <p className="text-gray-600">SmartShop Vector Database Management</p>
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

        <div className="mt-6 p-4 bg-purple-50 rounded-lg text-sm text-gray-600">
          <p className="font-medium mb-1">Default Credentials:</p>
          <p>Email: admin@smartshop.com</p>
          <p>Password: admin123</p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colors = {
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200'
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border">
      <div className="flex items-center gap-3">
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon size={24} />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

function DocumentsTab({ documents, onDelete }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">📚 Uploaded Documents</h2>
        <p className="text-sm text-gray-500 mt-1">
          {documents.length} document{documents.length !== 1 ? 's' : ''} in database
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vectors</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {documents.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                  No documents uploaded yet. Upload your first PDF!
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <FileText size={18} className="text-gray-400" />
                      <span className="font-medium text-gray-900">{doc.filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{doc.document_type}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 font-medium">{doc.vector_count?.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{(doc.file_size / 1024).toFixed(0)} KB</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => onDelete(doc.document_id, doc.filename)}
                      className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded transition"
                      title="Delete document"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function UploadTab({ onUpload, uploading, progress }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile);
      setSelectedFile(null);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">📤 Upload PDF Document</h2>

      <div className="border-2 border-dashed border-purple-300 rounded-xl p-12 text-center bg-purple-50/30">
        <Upload size={48} className="mx-auto text-purple-400 mb-4" />
        
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
          id="pdf-upload"
          disabled={uploading}
        />
        
        <label
          htmlFor="pdf-upload"
          className="inline-block bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 cursor-pointer transition"
        >
          {uploading ? 'Processing...' : 'Choose PDF File'}
        </label>

        {selectedFile && !uploading && (
          <div className="mt-6">
            <div className="flex items-center justify-center gap-2 text-gray-900 mb-4">
              <FileText size={20} />
              <span className="font-medium">{selectedFile.name}</span>
              <span className="text-gray-500">({(selectedFile.size / 1024).toFixed(0)} KB)</span>
            </div>
            <button
              onClick={handleUpload}
              className="bg-green-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-green-700 transition"
            >
              Upload & Process
            </button>
          </div>
        )}

        {uploading && progress && (
          <div className="mt-6">
            <div className="flex items-center justify-center gap-2 text-purple-600">
              <Loader className="animate-spin" size={20} />
              <span>{progress}</span>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 bg-purple-50 border border-purple-200 rounded-lg p-4">
        <p className="text-sm text-purple-900 font-medium mb-2">ℹ️ What happens when you upload:</p>
        <ol className="text-sm text-purple-800 space-y-1 ml-4 list-decimal">
          <li>PDF text is extracted with pdfplumber</li>
          <li>Products are auto-detected and added to catalog</li>
          <li>Text is split into chunks (~500 chars each)</li>
          <li>Embeddings are generated using E5</li>
          <li>Vectors are uploaded to Pinecone</li>
          <li>Chatbot can immediately use the new data!</li>
        </ol>
      </div>
    </div>
  );
}

function SearchTab({ query, setQuery, onSearch, searching, results }) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Test Vector Search</h2>
        
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSearch()}
            placeholder="Enter search query... (e.g., 'baskets sport')"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={searching}
          />
          <button
            onClick={onSearch}
            disabled={searching || !query.trim()}
            className="bg-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition flex items-center gap-2"
          >
            {searching ? <Loader className="animate-spin" size={18} /> : <Search size={18} />}
            Search
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="font-bold text-gray-900">Results ({results.length})</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {results.map((result, idx) => (
              <div key={idx} className="p-6">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium">
                      Score: {result.score}
                    </span>
                    <span className="text-sm text-gray-600">{result.filename}</span>
                  </div>
                  <span className="text-xs text-gray-500">Chunk {result.chunk_index}</span>
                </div>
                <p className="text-gray-700 text-sm">{result.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatsTab({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-4">📊 Vector Database Stats</h3>
        <div className="space-y-3">
          <StatRow label="Total Vectors" value={stats.total_vectors?.toLocaleString()} />
          <StatRow label="Total Documents" value={stats.total_documents} />
          <StatRow label="Dimensions" value={stats.dimensions} />
          <StatRow label="Index Fullness" value={`${((stats.index_fullness || 0) * 100).toFixed(2)}%`} />
          <StatRow label="Embedding Model" value={stats.embedding_model || 'E5'} />
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-4">💾 Storage Stats</h3>
        <div className="space-y-3">
          <StatRow label="Total Storage" value={`${stats.total_storage_mb} MB`} />
          <StatRow label="Average per Document" value={stats.total_documents ? `${(stats.total_storage_mb / stats.total_documents).toFixed(2)} MB` : 'N/A'} />
          <StatRow label="Products Extracted" value={stats.total_products_extracted || 0} />
        </div>
      </div>
    </div>
  );
}

function StatRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100">
      <span className="text-gray-600">{label}</span>
      <span className="font-semibold text-gray-900">{value}</span>
    </div>
  );
}

export default AdminDashboard;
