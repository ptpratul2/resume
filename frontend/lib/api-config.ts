// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const API_AUTH = {
  headers: {
    Authorization: `token ${process.env.NEXT_PUBLIC_API_KEY}:${process.env.NEXT_PUBLIC_API_SECRET}`,
  },
};

// Helper function to construct API URLs
export const getApiUrl = (endpoint: string) => {
  return `${API_BASE_URL}${endpoint}`;
};

