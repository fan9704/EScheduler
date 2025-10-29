import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [vue()],
	base: "/",
	resolve: {
		alias: {
			"@": resolve(__dirname, "src"),
		},
	},
	server: {
		port: 3000,
		host: true,
		proxy: {
			"/api": {
				target: "http://localhost:8000",
				changeOrigin: true,
				secure: false,
			},
		},
	},
	build: {
		outDir: "dist",
		sourcemap: true,
		rollupOptions: {
			input: {
				main: resolve(__dirname, "index.html"),
			},
			output:{
				manualChunks(id){
					if(id.includes('node_modules')){
						return id.toString().split('node_modules/')[1].split('/')[0].toString();
					}
				}
			}
		},
	},
	optimizeDeps: {
		include: [
			"vue",
			"vue-router",
			"pinia",
			"axios",
			"dayjs",
			"vuetify",
			"vuetify/components",
			"vuetify/directives",
		]
	},
	define: {
		__VUE_OPTIONS_API__: false,
		__VUE_PROD_DEVTOOLS__: false,
	},
});
