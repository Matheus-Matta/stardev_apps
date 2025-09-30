import { createApp, nextTick } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { i18n, i18nReady } from "./i18n";
import Ripple from 'primevue/ripple'
import Tooltip from 'primevue/tooltip'

import "./style.css";    

import PrimeVue from 'primevue/config';
import 'primeicons/primeicons.css'
import { MyPreset } from "./lib/preset"
import PrimeVuePlugin from './plugins/primevue'
import ToastService from 'primevue/toastservice'

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(i18n);
app.use(PrimeVue, {
    theme: {
      preset: MyPreset,
      options: {
          darkModeSelector: '.dark',
          cssLayer: {
              name: 'primevue',
              order: 'theme, base, primevue'
          }
        }
    },
    ripple: true
});
app.use(PrimeVuePlugin)
app.use(ToastService)
app.directive('ripple', Ripple)
app.directive('tooltip', Tooltip)
router.afterEach(async () => {
  await nextTick();
});

await i18nReady;

app.mount("#app");
