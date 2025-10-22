import { defineConfig, loadEnv } from 'vite'

import { resolve } from 'path'
import vue from '@vitejs/plugin-vue2'

// https://vitejs.dev/config/
export default defineConfig({
    base : "/static",
    mode : "production",
    resolve: {
	alias: {
	    vue: 'vue/dist/vue.esm.js',
	}
    },
    define: {
	"process.env": {},
    },
    build: {
	lib: {
	    // Could also be a dictionary or array of multiple entry points
	    entry: resolve(__dirname, 'js/whyis_vue/main.js'),
	    name: 'whyis',
	    // the proper extensions will be added
	    fileName: 'whyis',
	},
    },
    plugins: [
	vue()
    ],
})
