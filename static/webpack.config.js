const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (env, argv) => ({
    devtool: argv.mode === "production" ? 'hidden-source-map' : 'cheap-module-eval-source-map',
    entry: {
        app: ['./js/whyis_vue/main.js']
    },
    externals: {
        "jquery": "jQuery"
    },
    module: {
        rules: [
            {
            test: /(\.css$)/,
            use: [MiniCssExtractPlugin.loader, "css-loader"]
            },
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            }
        ]
    },
    name: "whyis",
    output: {
        filename: 'js/whyis_vue_bundle.js',
        libraryTarget: 'umd',
        path: __dirname
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: "css/whyis_vue_bundle.css"
        }),
        new VueLoaderPlugin()
    ],
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js' // Include the runtime template compiler
        },
        extensions: ['.js', '.vue'],
        modules: [path.join(__dirname, 'js', 'whyis_vue'), path.join(__dirname, 'node_modules')]
    },
    resolveLoader: {
        modules: [path.join(__dirname, 'node_modules')]
    },
    target: "web"
});
