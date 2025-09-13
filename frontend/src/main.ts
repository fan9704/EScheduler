import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { InstallCodeMirror } from 'codemirror-editor-vue3';

import router from './router';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';
import App from './App.vue';
import 'codemirror/mode/javascript/javascript.js';
import 'codemirror/addon/lint/lint.css';
import 'codemirror/addon/lint/lint.js';
import 'codemirror/addon/lint/json-lint';
import 'codemirror/theme/tomorrow-night-bright.css';
import 'codemirror/addon/edit/closebrackets.js';
import 'codemirror/addon/edit/matchbrackets.js';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(vuetify);
app.use(i18n);
app.use(InstallCodeMirror);

app.mount('#app');
