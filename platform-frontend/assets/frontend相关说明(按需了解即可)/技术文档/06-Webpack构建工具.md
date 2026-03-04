# Webpack构建工具

## 什么是Webpack？

Webpack是一个现代JavaScript应用程序的静态模块打包器（Static Module Bundler）。它将项目中的各种资源（JavaScript、CSS、图片等）视为模块，通过依赖关系图（Dependency Graph）将它们打包成浏览器可以识别的静态资源。

**英文原意**：Web + Pack（网络打包器）
**中文理解**：前端资源的"打包机"，把各种碎片化的资源打包成浏览器能识别的格式

**生活类比**：就像搬家时的打包服务，Webpack会把你的各种物品（JS文件、CSS样式、图片等）分类整理、压缩打包，确保它们能安全、高效地运送到新家（浏览器）。

## 为什么选择Webpack？

### 1. 构建工具对比

| 工具 | 特点 | 优点 | 缺点 |
|------|------|------|------|
| **Webpack** | 模块打包器 | 功能强大、生态丰富、配置灵活 | 配置复杂、学习成本高 |
| Vite | 构建工具 | 启动快、热更新快、配置简单 | 生态相对较新 |
| Parcel | 零配置打包器 | 零配置、自动优化 | 自定义能力有限 |
| Rollup | ES模块打包器 | 打包体积小、Tree Shaking好 | 主要用于库开发 |
| Gulp | 任务运行器 | 流式处理、插件丰富 | 需要手动配置流程 |

### 2. Webpack的核心优势

- **模块化支持**：支持CommonJS、AMD、ES6模块等各种模块规范
- **代码分割**：按需加载，减少首屏加载时间
- **资源管理**：统一处理JS、CSS、图片等各种资源
- **开发体验**：热模块替换（HMR）、Source Map等开发工具
- **优化能力**：Tree Shaking、代码压缩、图片优化等
- **生态丰富**：大量的loader和plugin

## 核心概念

### 1. 入口（Entry）

**英文原意**：入口、进入点
**技术含义**：Webpack构建的起点，从这里开始分析依赖关系

```javascript
// webpack.config.js
module.exports = {
  entry: './src/main.js' // 单入口
}

// 多入口配置
module.exports = {
  entry: {
    app: './src/app.js',
    vendor: './src/vendor.js'
  }
}
```

### 2. 输出（Output）

**英文原意**：输出、出口
**技术含义**：Webpack打包后的文件输出配置

```javascript
module.exports = {
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js', // 单入口输出文件名
    // 多入口输出文件名
    filename: '[name].[chunkhash].js',
    publicPath: '/' // 公共资源路径
  }
}
```

### 3. Loader

**英文原意**：加载器
**技术含义**：Webpack用来预处理文件的模块

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/, // 匹配.css文件
        use: ['style-loader', 'css-loader'] // 使用哪些loader处理
      },
      {
        test: /\.js$/, // 匹配.js文件
        exclude: /node_modules/, // 排除node_modules目录
        use: 'babel-loader' // 使用babel-loader处理
      }
    ]
  }
}
```

### 4. Plugin

**英文原意**：插件
**技术含义**：Webpack的扩展插件，用于执行更广泛的任务

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')

module.exports = {
  plugins: [
    new CleanWebpackPlugin(), // 清理dist目录
    new HtmlWebpackPlugin({ // 生成HTML文件
      template: './src/index.html'
    })
  ]
}
```

### 5. 模式（Mode）

**英文原意**：模式、方式
**技术含义**：Webpack的构建模式，影响优化策略

```javascript
module.exports = {
  mode: 'development', // 开发模式
  // mode: 'production', // 生产模式
  // mode: 'none', // 无优化模式
}
```

## 在LiuMa项目中的应用

### 1. 基础配置（/build/webpack.base.conf.js）

```javascript
const path = require('path')
const utils = require('./utils')
const { VueLoaderPlugin } = require('vue-loader')

function resolve(dir) {
  return path.join(__dirname, '..', dir)
}

const createLintingRule = () => ({
  test: /\.(js|vue)$/,
  loader: 'eslint-loader',
  enforce: 'pre',
  include: [resolve('src'), resolve('test')],
  options: {
    formatter: require('eslint-friendly-formatter'),
    emitWarning: !config.dev.showEslintErrorsInOverlay
  }
})

module.exports = {
  context: path.resolve(__dirname, '../'),
  entry: {
    app: './src/main.js' // 入口文件
  },
  output: {
    path: config.build.assetsRoot,
    filename: '[name].js',
    publicPath: process.env.NODE_ENV === 'production'
      ? config.build.assetsPublicPath
      : config.dev.assetsPublicPath
  },
  resolve: {
    extensions: ['.js', '.vue', '.json'], // 自动解析的文件扩展名
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
      '@': resolve('src'), // 设置@指向src目录
    }
  },
  module: {
    rules: [
      ...(config.dev.useEslint ? [createLintingRule()] : []),
      {
        test: /\.vue$/, // 处理.vue文件
        loader: 'vue-loader',
        options: {
          cacheBusting: config.dev.cacheBusting,
          transformToRequire: {
            video: ['src', 'poster'],
            source: 'src',
            img: 'src',
            image: 'xlink:href'
          }
        }
      },
      {
        test: /\.js$/, // 处理.js文件
        loader: 'babel-loader',
        include: [resolve('src'), resolve('test'), resolve('node_modules/webpack-dev-server/client')]
      },
      {
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/, // 处理图片文件
        loader: 'url-loader',
        options: {
          limit: 10000, // 小于10kb的图片转为base64
          name: utils.assetsPath('img/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/, // 处理媒体文件
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('media/[name].[hash:7].[ext]')
        }
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/, // 处理字体文件
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: utils.assetsPath('fonts/[name].[hash:7].[ext]')
        }
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin() // Vue加载器插件
  ],
  node: {
    // 防止webpack注入无用的setImmediate polyfill
    setImmediate: false,
    // 防止webpack注入无用的mock
    dgram: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty',
    child_process: 'empty'
  }
}
```

### 2. 开发环境配置（/build/webpack.dev.conf.js）

```javascript
const utils = require('./utils')
const webpack = require('webpack')
const merge = require('webpack-merge')
const path = require('path')
const baseWebpackConfig = require('./webpack.base.conf')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin')
const portfinder = require('portfinder')

const HOST = process.env.HOST
const PORT = process.env.PORT && Number(process.env.PORT)

const devWebpackConfig = merge(baseWebpackConfig, {
  mode: 'development', // 开发模式
  module: {
    rules: utils.styleLoaders({ sourceMap: config.dev.cssSourceMap, usePostCSS: false })
  },
  // 开发工具：增强调试
  devtool: config.dev.devtool,
  
  devServer: {
    clientLogLevel: 'warning',
    historyApiFallback: {
      rewrites: [
        { from: /.*/, to: path.posix.join(config.dev.assetsPublicPath, 'index.html') },
      ],
    },
    hot: true, // 启用热模块替换
    contentBase: false, // 告诉服务器从哪里提供内容
    compress: true, // 启用gzip压缩
    host: HOST || config.dev.host,
    port: PORT || config.dev.port,
    open: config.dev.autoOpenBrowser, // 自动打开浏览器
    overlay: config.dev.errorOverlay
      ? { warnings: false, errors: true }
      : false,
    publicPath: config.dev.assetsPublicPath,
    proxy: config.dev.proxyTable, // 代理配置
    quiet: true, // 启用FriendlyErrorsPlugin
    watchOptions: {
      poll: config.dev.poll, // 文件系统检测间隔
    }
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': require('../config/dev.env')
    }),
    new webpack.HotModuleReplacementPlugin(), // 热模块替换插件
    new webpack.NamedModulesPlugin(), // 显示模块的相对路径
    new webpack.NoEmitOnErrorsPlugin(), // 在编译出现错误时，使用NoEmitOnErrorsPlugin来跳过输出阶段
    // https://github.com/ampedandwired/html-webpack-plugin
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index.html',
      inject: true
    }),
    // 复制静态资源
    new CopyWebpackPlugin([
      {
        from: path.resolve(__dirname, '../static'),
        to: config.dev.assetsSubDirectory,
        ignore: ['.*']
      }
    ])
  ]
})

module.exports = new Promise((resolve, reject) => {
  portfinder.basePort = process.env.PORT || config.dev.port
  portfinder.getPort((err, port) => {
    if (err) {
      reject(err)
    } else {
      // 发布e2e测试所需的端口
      process.env.PORT = port
      // 将端口添加到devServer配置
      devWebpackConfig.devServer.port = port

      // 添加FriendlyErrorsPlugin
      devWebpackConfig.plugins.push(new FriendlyErrorsPlugin({
        compilationSuccessInfo: {
          messages: [`Your application is running here: http://${devWebpackConfig.devServer.host}:${port}`],
        },
        onErrors: config.dev.notifyOnErrors
        ? utils.createNotifierCallback()
        : undefined
      }))

      resolve(devWebpackConfig)
    }
  })
})
```

### 3. 生产环境配置（/build/webpack.prod.conf.js）

```javascript
const path = require('path')
const utils = require('./utils')
const webpack = require('webpack')
const config = require('../config')
const merge = require('webpack-merge')
const baseWebpackConfig = require('./webpack.base.conf')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const OptimizeCSSPlugin = require('optimize-css-assets-webpack-plugin')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')

const env = require('../config/prod.env')

const webpackConfig = merge(baseWebpackConfig, {
  mode: 'production', // 生产模式
  module: {
    rules: utils.styleLoaders({
      sourceMap: config.build.productionSourceMap,
      extract: true,
      usePostCSS: true
    })
  },
  devtool: config.build.productionSourceMap ? config.build.devtool : false,
  output: {
    path: config.build.assetsRoot,
    filename: utils.assetsPath('js/[name].[chunkhash].js'), // 带hash的文件名
    chunkFilename: utils.assetsPath('js/[id].[chunkhash].js')
  },
  plugins: [
    // http://vuejs.github.io/vue-loader/en/workflow/production.html
    new webpack.DefinePlugin({
      'process.env': env
    }),
    new UglifyJsPlugin({ // JS压缩
      uglifyOptions: {
        compress: {
          warnings: false
        }
      },
      sourceMap: config.build.productionSourceMap,
      parallel: true
    }),
    // 提取CSS到单独文件
    new ExtractTextPlugin({
      filename: utils.assetsPath('css/[name].[contenthash].css'),
      // 将以下选项设置为`false`不会从代码分割块中提取CSS。
      // 它们的CSS将使用与提取的主文件相同的CSS文件插入。
      // 这在Vue.js单文件组件中很常见。
      // 当使用`extract`选项时，必须将其设置为`true`
      allChunks: true,
    }),
    // 压缩提取的CSS。我们正在使用这个插件，这样复制的提取文件中的
    // 不同组件中的重复CSS可以利用这个插件。
    new OptimizeCSSPlugin({
      cssProcessorOptions: config.build.productionSourceMap
        ? { safe: true, map: { inline: false } }
        : { safe: true }
    }),
    // 生成dist index.html with correct asset hash for caching.
    // you can customize output by editing /index.html
    // see https://github.com/ampedandwired/html-webpack-plugin
    new HtmlWebpackPlugin({
      filename: config.build.index,
      template: 'index.html',
      inject: true,
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true
        // more options:
        // https://github.com/kangax/html-minifier#options-quick-reference
      },
      // necessary to consistently work with multiple chunks via CommonsChunkPlugin
      chunksSortMode: 'dependency'
    }),
    // keep module.id stable when vendor modules does not change
    new webpack.HashedModuleIdsPlugin(),
    // enable scope hoisting
    new webpack.optimize.ModuleConcatenationPlugin(),
    // split vendor js into its own file
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      minChunks(module) {
        // any required modules inside node_modules are extracted to vendor
        return (
          module.resource &&
          /\.js$/.test(module.resource) &&
          module.resource.indexOf(
            path.join(__dirname, '../node_modules')
          ) === 0
        )
      }
    }),
    // extract webpack runtime and module manifest to its own file in order to
    // prevent vendor hash from being updated whenever app bundle is updated
    new webpack.optimize.CommonsChunkPlugin({
      name: 'manifest',
      minChunks: Infinity
    }),
    // This instance extracts shared chunks from code splitted chunks and bundles them
    // in a separate chunk, similar to the vendor chunk
    // see: https://webpack.js.org/plugins/commons-chunk-plugin/#extra-async-commons-chunk
    new webpack.optimize.CommonsChunkPlugin({
      name: 'app',
      async: 'vendor-async',
      children: true,
      minChunks: 3
    }),

    // copy custom static assets
    new CopyWebpackPlugin([
      {
        from: path.resolve(__dirname, '../static'),
        to: config.build.assetsSubDirectory,
        ignore: ['.*']
      }
    ])
  ]
})

if (config.build.productionGzip) {
  const CompressionWebpackPlugin = require('compression-webpack-plugin')

  webpackConfig.plugins.push(
    new CompressionWebpackPlugin({
      asset: '[path].gz[query]',
      algorithm: 'gzip',
      test: new RegExp(
        '\\.(' +
        config.build.productionGzipExtensions.join('|') +
        ')$'
      ),
      threshold: 10240,
      minRatio: 0.8
    })
  )
}

if (config.build.bundleAnalyzerReport) {
  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
  webpackConfig.plugins.push(new BundleAnalyzerPlugin())
}

module.exports = webpackConfig
```

## 核心概念详解

### 1. 模块解析（Module Resolution）

**英文原意**：模块解析
**技术含义**：Webpack如何找到模块的位置

```javascript
module.exports = {
  resolve: {
    // 自动解析的扩展名
    extensions: ['.js', '.vue', '.json'],
    
    // 路径别名
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
      '@': resolve('src'),
      'components': resolve('src/components'),
      'utils': resolve('src/utils')
    },
    
    // 模块搜索目录
    modules: [
      resolve('src'),
      resolve('node_modules')
    ]
  }
}
```

### 2. 代码分割（Code Splitting）

**英文原意**：代码分割
**技术含义**：将代码分割成多个包，按需加载

```javascript
// 方法1：入口点分割
module.exports = {
  entry: {
    index: './src/index.js',
    another: './src/another-module.js'
  }
}

// 方法2：动态导入（推荐）
// 在代码中使用动态import()
function getComponent() {
  return import(/* webpackChunkName: "lodash" */ 'lodash').then(({ default: _ }) => {
    const element = document.createElement('div')
    element.innerHTML = _.join(['Hello', 'webpack'], ' ')
    return element
  }).catch(error => 'An error occurred while loading the component')
}

// 方法3：使用SplitChunksPlugin
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
}
```

### 3. 热模块替换（HMR）

**英文原意**：Hot Module Replacement（热模块替换）
**技术含义**：在应用运行时更新模块，无需刷新整个页面

```javascript
// webpack.config.js
const webpack = require('webpack')

module.exports = {
  devServer: {
    hot: true, // 启用HMR
    contentBase: './dist'
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ]
}

// 在应用代码中处理HMR
if (module.hot) {
  module.hot.accept('./print.js', function() {
    console.log('Accepting the updated printMe module!')
    printMe()
  })
}
```

### 4. Source Map

**英文原意**：源码映射
**技术含义**：将编译后的代码映射回原始源代码

```javascript
module.exports = {
  devtool: 'source-map' // 生成完整的source map
  // devtool: 'eval-source-map', // 开发环境推荐
  // devtool: 'cheap-module-eval-source-map', // 更快的构建
  // devtool: 'hidden-source-map', // 生产环境推荐
}
```

Source Map类型对比：

| devtool | 构建速度 | 重新构建速度 | 生产环境 | 品质 |
|---------|----------|--------------|----------|------|
| eval | +++ | +++ | no | 生成的代码 |
| cheap-eval-source-map | + | ++ | no | 转换过的代码（仅限行） |
| cheap-module-eval-source-map | o | ++ | no | 原始源代码（仅限行） |
| eval-source-map | -- | + | no | 原始源代码 |
| source-map | -- | -- | yes | 原始源代码 |
| hidden-source-map | -- | -- | yes | 原始源代码 |

### 5. Tree Shaking

**英文原意**：摇树优化
**技术含义**：消除JavaScript中未使用的代码

```javascript
// 在package.json中设置sideEffects
{
  "name": "your-project",
  "sideEffects": [
    "*.css",
    "*.less",
    "*.scss"
  ]
}

// webpack配置
module.exports = {
  mode: 'production', // 生产模式自动启用Tree Shaking
  optimization: {
    usedExports: true, // 标记未使用的导出
    sideEffects: false // 跳过sideEffects检查
  }
}
```

## 高级用法

### 1. 多环境配置

```javascript
// webpack.common.js - 通用配置
const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  entry: './src/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js'
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin()
  ]
}

// webpack.dev.js - 开发环境
const { merge } = require('webpack-merge')
const common = require('./webpack.common.js')

module.exports = merge(common, {
  mode: 'development',
  devtool: 'eval-source-map',
  devServer: {
    hot: true,
    port: 8080
  }
})

// webpack.prod.js - 生产环境
const { merge } = require('webpack-merge')
const common = require('./webpack.common.js')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = merge(common, {
  mode: 'production',
  optimization: {
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true // 移除console.log
          }
        }
      })
    ]
  },
  plugins: [
    new CleanWebpackPlugin()
  ]
})
```

### 2. 自定义Loader

```javascript
// 自定义loader：reverse-loader.js
module.exports = function(source) {
  // 将源代码反转
  return source.split('').reverse().join('')
}

// 使用自定义loader
module.exports = {
  module: {
    rules: [
      {
        test: /\.txt$/,
        use: './loaders/reverse-loader.js'
      }
    ]
  }
}

// 更复杂的loader示例：处理markdown文件
const marked = require('marked')

module.exports = function(source) {
  const html = marked(source)
  
  // 返回JavaScript模块
  return `module.exports = ${JSON.stringify(html)}`
}
```

### 3. 自定义Plugin

```javascript
// 自定义plugin：文件列表插件
class FileListPlugin {
  constructor(options) {
    this.options = options || {}
    this.filename = this.options.filename || 'filelist.md'
  }
  
  apply(compiler) {
    // 在emit阶段钩入
    compiler.hooks.emit.tapAsync('FileListPlugin', (compilation, callback) => {
      // 创建文件列表
      let filelist = '# 文件列表\\n\\n'
      
      for (let filename in compilation.assets) {
        filelist += `- ${filename}\\n`
      }
      
      // 添加文件到webpack输出
      compilation.assets[this.filename] = {
        source: function() {
          return filelist
        },
        size: function() {
          return filelist.length
        }
      }
      
      callback()
    })
  }
}

module.exports = FileListPlugin

// 使用自定义plugin
const FileListPlugin = require('./plugins/FileListPlugin')

module.exports = {
  plugins: [
    new FileListPlugin({
      filename: 'my-file-list.md'
    })
  ]
}
```

### 4. 性能优化

```javascript
// webpack性能优化配置
const path = require('path')
const TerserPlugin = require('terser-webpack-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')

module.exports = {
  optimization: {
    // 代码分割
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        // 第三方库
        vendor: {
          name: 'vendor',
          test: /[\\/]node_modules[\\/]/,
          priority: 10,
          chunks: 'initial'
        },
        // 公共代码
        common: {
          name: 'common',
          minChunks: 2,
          priority: 5,
          chunks: 'initial',
          reuseExistingChunk: true
        }
      }
    },
    
    // 运行时chunk
    runtimeChunk: {
      name: 'runtime'
    },
    
    // 压缩优化
    minimizer: [
      new TerserPlugin({
        parallel: true, // 并行压缩
        terserOptions: {
          compress: {
            drop_console: true, // 移除console.log
            drop_debugger: true // 移除debugger
          }
        }
      }),
      new OptimizeCSSAssetsPlugin({})
    ]
  },
  
  performance: {
    hints: 'warning', // 性能提示
    maxEntrypointSize: 250000, // 入口文件最大体积
    maxAssetSize: 250000 // 资源文件最大体积
  },
  
  plugins: [
    // 分析打包结果（仅在分析时使用）
    // new BundleAnalyzerPlugin()
  ],
  
  // 缓存配置
  cache: {
    type: 'filesystem', // 使用文件系统缓存
    cacheDirectory: path.resolve(__dirname, '.webpack-cache')
  }
}
```

### 5. 环境变量配置

```javascript
// config/dev.env.js - 开发环境变量
module.exports = {
  NODE_ENV: '"development"',
  BASE_API: '"http://localhost:8080"'
}

// config/prod.env.js - 生产环境变量
module.exports = {
  NODE_ENV: '"production"',
  BASE_API: '"https://api.liuma.com"'
}

// 在webpack配置中使用环境变量
const webpack = require('webpack')

module.exports = {
  plugins: [
    new webpack.DefinePlugin({
      'process.env': require('../config/dev.env')
    })
  ]
}

// 在代码中使用环境变量
if (process.env.NODE_ENV === 'production') {
  console.log('生产环境')
} else {
  console.log('开发环境')
}
```

## 常见问题解答

### Q1：Webpack和Vite有什么区别？

**A**：
- **Webpack**：基于打包的开发模式，所有文件都需要打包后才能在浏览器中运行
- **Vite**：基于原生ES模块的开发模式，利用浏览器对ESM的支持，按需编译

**类比**：Webpack像传统餐厅，所有菜品都要提前准备好；Vite像快餐店，现点现做。

### Q2：如何优化Webpack构建速度？

**A**：
1. **使用缓存**：配置cache选项
2. **并行处理**：使用thread-loader、parallel-webpack
3. **减少搜索范围**：配置resolve.modules、resolve.extensions
4. **使用DllPlugin**：预编译第三方库
5. **升级硬件**：使用SSD、增加内存

### Q3：如何处理Webpack打包体积过大？

**A**：
1. **代码分割**：使用splitChunks
2. **Tree Shaking**：移除未使用的代码
3. **按需加载**：使用动态import()
4. **压缩优化**：使用TerserPlugin、OptimizeCSSAssetsPlugin
5. **CDN引入**：将大型库通过CDN引入

### Q4：Webpack的loader和plugin有什么区别？

**A**：
- **Loader**：文件加载器，用于处理特定类型的文件
- **Plugin**：插件，用于执行更广泛的任务，如打包优化、资源管理、环境变量注入等

**类比**：Loader像工厂里的工人，负责处理原材料；Plugin像工厂里的机器，负责整体生产流程。

### Q5：如何处理Webpack的跨域问题？

**A**：
```javascript
// webpack.dev.js
devServer: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      pathRewrite: {
        '^/api': ''
      }
    }
  }
}
```

## 实战：从零配置Vue项目

```javascript
// 1. 安装依赖
// npm install vue vue-loader vue-template-compiler webpack webpack-cli webpack-dev-server babel-loader @babel/core @babel/preset-env css-loader vue-style-loader html-webpack-plugin -D

// 2. webpack.config.js
const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  mode: 'development',
  entry: './src/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader']
      }
    ]
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: './public/index.html'
    })
  ],
  devServer: {
    hot: true,
    open: true
  }
}

// 3. src/main.js
import Vue from 'vue'
import App from './App.vue'

new Vue({
  render: h => h(App)
}).$mount('#app')

// 4. src/App.vue
<template>
  <div id="app">
    <h1>Hello Vue + Webpack!</h1>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

// 5. package.json scripts
"scripts": {
  "dev": "webpack serve --config webpack.config.js",
  "build": "webpack --mode production"
}
```

## 下一步学习

掌握了Webpack后，建议继续学习：
1. **Vite** - 新一代构建工具
2. **Rollup** - 库打包工具
3. **Parcel** - 零配置打包工具
4. **esbuild** - 超快的JavaScript打包器
5. **Turbopack** - Webpack的继任者

## 面试常见问题

1. **Webpack的构建流程是怎样的？**
2. **Loader和Plugin的区别是什么？**
3. **如何优化Webpack的构建速度？**
4. **什么是Tree Shaking？如何实现？**
5. **什么是Code Splitting？有哪些实现方式？**
6. **如何配置Webpack的多入口？**
7. **Webpack的热模块替换是如何实现的？**
8. **如何处理Webpack中的CSS文件？**

通过本教程的学习，你应该对Webpack有了全面的了解。LiuMa项目中的Webpack配置是一个很好的实战案例，建议你仔细研究其多环境配置、性能优化和插件使用的实现思路。