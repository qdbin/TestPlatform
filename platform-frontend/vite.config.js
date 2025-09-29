import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue2'
import { resolve } from 'path'
import commonjs from 'vite-plugin-commonjs'

export default defineConfig({
  plugins: [vue(), commonjs()],
  
  // 开发服务器配置
  server: {
    port: 8888,
    host: '0.0.0.0',
    open: true,
    // 代理配置 - 保持与原项目一致
    proxy: {
      '/autotest': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        ws: true
      },
      '/openapi': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
      },
      '/websocket': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        ws: true
      }
    }
  },
  
  // 路径别名配置 - 保持与原来一致
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '~@': resolve(__dirname, 'src')
    },
    extensions: ['.js', '.vue', '.json']
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'static',
    sourcemap: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },
  
  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  // 优化CommonJS模块导入 - 解决不符CommonJS模块动态导入的相关兼容性问题-可删
  optimizeDeps: {
    include: [
      'element-resize-detector',
      'vue2-ace-editor',
      'jmuxer',
      'js-base64',
      'brace',
      'brace/ext/language_tools',
      'brace/mode/text',
      'brace/mode/xml',
      'brace/mode/html',
      'brace/mode/python',
      'brace/mode/sql',
      'brace/mode/javascript',
      'brace/mode/json',
      'brace/theme/chrome',
      'brace/snippets/javascript',
      'brace/ext/searchbox'
    ]
  }
})