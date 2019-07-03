const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const path = require('path');

module.exports = (env, argv) => ({
    devServer: {
        contentBase: ".",
        host: "localhost",
        hot: false,
        inline: true,
        port: 9000,
        proxy: {
            "/api": {
                "target": {
                    "host": "localhost",
                    "protocol": 'http:',
                    "port": 5000
                },
                secure: false
            }
        }
    },
    devtool: argv.mode === "production" ? 'hidden-source-map' : 'cheap-module-eval-source-map',
    entry: {
        app: ['./js/whyis_vue/main.js']
    },
    externals: {
        "jquery": "jQuery"
    },
    module: {
        rules: [{
            test: /(\.css$)/,
            use: [MiniCssExtractPlugin.loader, "css-loader"]
        }]
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
        })
    ],
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js' // Include the runtime template compiler
        },
        extensions: ['.js'],
        modules: [path.join(__dirname, 'js', 'whyis_vue'), path.join(__dirname, 'node_modules')]
    },
    resolveLoader: {
        modules: [path.join(__dirname, 'node_modules')]
    },
    target: "web"
});
