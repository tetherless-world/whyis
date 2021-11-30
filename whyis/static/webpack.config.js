const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (env, argv) => ({
  devtool: argv.mode === 'production' ? 'hidden-source-map' : 'eval-cheap-module-source-map',
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
        test: /\.s?css$/,
        use: [
<<<<<<< HEAD:whyis/static/webpack.config.js
          argv.mode !== 'production'
            ? 'vue-style-loader'
            : MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      {
        test: /\.scss$/,
        use: [
          argv.mode !== 'production'
            ? 'vue-style-loader'
            : MiniCssExtractPlugin.loader,
=======
          'vue-style-loader',
>>>>>>> master:static/webpack.config.js
          'css-loader',
          'resolve-url-loader',
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
      },
      {
        test: /\.ya?ml$/,
        loader: 'raw-loader',
      },
      {
        test:/\.png$/,
        use: [{
          loader:'file-loader',
          options: {
<<<<<<< HEAD:whyis/static/webpack.config.js
            // path: path.resolve(__dirname, 'dist'),
            // publicPath: path.resolve(__dirname, 'dist'),
=======
>>>>>>> master:static/webpack.config.js
            esModule: false
          }
        }],
      },
<<<<<<< HEAD:whyis/static/webpack.config.js
=======
      {
        test:/\.rq$/,
        use: 'raw-loader'
      },
>>>>>>> master:static/webpack.config.js
    ]
  },
  name: 'whyis',
  output: {
    filename: 'whyis_vue_bundle.js',
    chunkFilename: 'whyis_vue_bundle.[name].js',
    libraryTarget: 'umd',
    path: path.resolve(__dirname, 'dist'),
<<<<<<< HEAD:whyis/static/webpack.config.js
=======
    publicPath: 'static/dist/'
>>>>>>> master:static/webpack.config.js
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'whyis_vue_bundle.css',
      chunkFilename: 'whyis_vue_bundle.[name].css'
    }),
    new VueLoaderPlugin()
  ],
  resolve: {
    alias: {
      vue$: 'vue/dist/vue.esm.js' // Include the runtime template compiler
    },
    extensions: ['.js', '.vue'],
    modules: [path.join(__dirname, 'js/whyis_vue'), 'node_modules']
  },
  resolveLoader: {
    modules: [path.join(__dirname, 'node_modules')]
  },
  target: 'web',
})
