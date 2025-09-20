import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import { isJwtExpired } from "../lib/jwt";

// views
import LoginView from "../views/LoginView.vue";

const HomeView = () => import("../views/HomeView.vue");
const SettingsView = () => import("../views/SettingsView.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView, meta: { requiresAuth: true } },
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/settings", name: "settings", component: SettingsView, meta: { requiresAuth: true } },

    // catch-all
    { path: "/:pathMatch(.*)*", redirect: { name: "home" } },
  ],
});

// Guard global
router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (to.meta.public && auth.isAuthenticated && !isJwtExpired(auth.access)) {
    return { name: "home" };
  }

  if (to.meta.requiresAuth) {
    const access = auth.access;
    if (!access) {
      return { name: "login", query: { next: to.fullPath } };
    }
    if (isJwtExpired(access)) {
      auth._clearSession();
      return { name: "login", query: { next: to.fullPath } };
    }
  }

  return true;
});

export default router;
