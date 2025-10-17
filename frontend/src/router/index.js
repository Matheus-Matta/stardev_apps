// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth/auth";
import { isJwtExpired } from "../lib/jwt";

// Views
import LoginView from "../views/LoginView.vue";

const HomeView = () => import("../views/HomeView.vue");
const ProfileView = () => import("../views/page/ProfileView.vue");
const AccountView = () => import("../views/page/Account.vue");
const TableListView = () => import("../views/page/TableListView.vue");
const FormView = () => import("../views/page/FormView.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { public: true },
    },
    {
      path: "/profile",
      name: "settings",
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: "/account",
      name: "account",
      component: AccountView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:model/list",
      name: "list",
      component: TableListView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:model/create",
      name: "create",
      component: FormView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:model/:id/update",
      name: "update",
      component: FormView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:notFound(.*)",
      redirect: { name: "home" },
    },
  ],
});

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