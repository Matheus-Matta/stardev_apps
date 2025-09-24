import { createApp, nextTick } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

import 'material-icons/iconfont/material-icons.css'
import "./style.css";    
import "flowbite";
import 'flowbite';
import 'flowbite-datepicker';
import { initFlowbite } from "flowbite";

const app = createApp(App);
app.use(createPinia());
app.use(router);

router.afterEach(async () => {
  await nextTick();
  initFlowbite();
});

app.mount("#app");
