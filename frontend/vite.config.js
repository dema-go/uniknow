import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 80,
    host: '0.0.0.0',
    hmr: {
      host: 'localhost'
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `$primary-color: #409EFF;\n$success-color: #67C23A;\n$warning-color: #E6A23C;\n$danger-color: #F56C6C;\n$info-color: #909399;\n$text-primary: #303133;\n$text-regular: #606266;\n$text-secondary: #909399;\n$border-color: #DCDFE6;\n$border-light: #E4E7ED;\n$background-color: #F5F7FA;\n`
      }
    }
  }
})
