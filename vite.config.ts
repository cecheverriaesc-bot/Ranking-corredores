import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: process.env.PORT ? parseInt(process.env.PORT) : 3000,
      host: '0.0.0.0',
    },
    plugins: [react()],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-react': ['react', 'react-dom'],
            'vendor-recharts': ['recharts'],
            'vendor-lucide': ['lucide-react'],
            'vendor-zustand': ['zustand'],
          }
        }
      },
      chunkSizeWarningLimit: 600,
      sourcemap: mode === 'development',
      minify: 'esbuild',
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'recharts', 'lucide-react', 'zustand'],
    }
  };
});
