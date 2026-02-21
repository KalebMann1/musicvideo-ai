// Main app router - handles navigation between all screens
// Copy and paste everything into frontend/src/App.jsx

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Upload from './pages/Upload'
import Processing from './pages/Processing'
import Preview from './pages/Preview'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Upload />} />
        <Route path="/processing/:projectId" element={<Processing />} />
        <Route path="/preview/:projectId" element={<Preview />} />
      </Routes>
    </BrowserRouter>
  )
}