import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Chatbot from './Chatbot';
import AdminDashboard from './components/AdminDashboard';
import SuperAdmin from './components/SuperAdmin';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Chatbot />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/superadmin" element={<SuperAdmin />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;