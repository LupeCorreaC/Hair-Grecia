import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import { BookingProvider } from './BookingContext';
import App from './App';
import './styles.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider><BookingProvider><App /></BookingProvider></AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
