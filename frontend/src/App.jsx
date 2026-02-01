import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import AddPromptPage from './pages/AddPromptPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/add" element={<AddPromptPage />} />
        </Routes>
        
        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-20">
          <div className="container mx-auto px-4 py-8">
            <div className="text-center text-gray-600 text-sm">
              <p className="mb-2">
                🧠 LLM Prompts Repository for Social Science Research
              </p>
              <p className="text-gray-500">
                Built with FastAPI, React, and PostgreSQL • Open Source • Anonymous
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
