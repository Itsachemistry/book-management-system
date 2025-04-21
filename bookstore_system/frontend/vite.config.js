import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: true, // 允许通过 IP 地址访问
    port: 5174, // 可以指定端口，默认为 5174
    strictPort: false, // 允许在端口被占用时使用下一个可用端口
    open: true, // 自动打开浏览器
    cors: true, // 允许跨域
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 后端地址
        changeOrigin: true
        // 删除rewrite，让/api保留在请求路径中
      }
    }
  },
  // 添加详细的构建日志
  logLevel: 'info',
  // 添加更清晰的错误信息
  clearScreen: false
});
