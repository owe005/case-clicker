const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // Output to Flask's static folder
  outputDir: 'dist',
  // Don't add a static subfolder
  assetsDir: '',
  // Dev server proxy for development
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  // Ensure proper paths for production build
  publicPath: '/',
  // Disable hashing in filenames for easier debugging
  filenameHashing: false
})
