import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// In @blocksuite/presets v0.15.0, custom elements are registered on import
import '@blocksuite/presets';
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
