const Path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');


module.exports = {
    entry: {
        app: Path.resolve(__dirname, '../src/index.js'),
    },
    output: {
        path: Path.join(__dirname, '../rong/static/rong/'),
        filename: 'js/[name].js',
        publicPath: '/static/rong/',
    },
    optimization: {
        splitChunks: {
            chunks: 'all',
            maxInitialRequests: Infinity,
            minSize: 0,
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name(module) {
                        // get the name. E.g. node_modules/packageName/not/this/part.js
                        // or node_modules/packageName
                        const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];

                        // npm package names are URL-safe, but some servers don't like @ symbols
                        return `npm.${packageName.replace('@', '')}`;
                    },
                },
            },
        },
        moduleIds: 'deterministic',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'})
    ],
    resolve: {
        alias: {
            '~': Path.resolve(__dirname, '../src'),
        },
    },
    module: {
        rules: [
            {
                test: /\.mjs$/,
                include: /node_modules/,
                type: 'javascript/auto',
            },
            {
                test: /\.(ico|jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2)(\?.*)?$/,
                loader: 'ignore-loader',
            },
        ],
    },
};