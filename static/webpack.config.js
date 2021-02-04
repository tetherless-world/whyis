const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (env, argv) => ({
  devtool: argv.mode === 'production' ? 'hidden-source-map' : 'cheap-module-eval-source-map',
  entry: {
    app: ['./js/whyis_vue/main.js']
  },
  externals: {
    'jquery': 'jQuery',
    'node-fetch': 'fetch',
    'solid-auth-cli': 'null',
    'fs': 'null-fs'
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          process.env.NODE_ENV !== 'production'
            ? 'vue-style-loader'
            : MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          process.env.NODE_ENV !== 'production'
            ? 'vue-style-loader'
            : MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: "url-loader"
      },
      {
        test: /\.(ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/'
            }
          }
        ]
      }
    ]
  },
  name: 'whyis',
  output: {
    filename: 'js/whyis_vue_bundle.js',
    libraryTarget: 'umd',
    path: __dirname,
    publicPath: path.basename(__dirname) + '/',
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/whyis_vue_bundle.css'
    }),
    new VueLoaderPlugin()
  ],
  resolve: {
    alias: {
      vue$: 'vue/dist/vue.esm.js' // Include the runtime template compiler
    },
    extensions: ['.js', '.vue'],
    modules: [path.join(__dirname, 'js', 'whyis_vue'), path.join(__dirname, 'node_modules')]
  },
  resolveLoader: {
    modules: [path.join(__dirname, 'node_modules')]
  },
  target: 'web',
})
