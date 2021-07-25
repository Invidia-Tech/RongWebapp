const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'eval-source-map',
    output: {
        chunkFilename: 'js/[name].chunk.js',
    },
    plugins: [
        new Webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('development'),
        }),
        new MiniCssExtractPlugin({
            filename: 'styles/[name].css',
        }),
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                include: Path.resolve(__dirname, '../src'),
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', { targets: "defaults" }]
                        ]
                    }
                }
            },
            {
                test: /\.s?css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader?sourceMap=true&url=false', 'postcss-loader', 'sass-loader'],
            },
        ],
    },
});