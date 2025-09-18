import { defineStore } from "pinia";
import api from "../lib/Api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access: localStorage.getItem("access") || null,
    refresh: localStorage.getItem("refresh") || null,
    user: JSON.parse(localStorage.getItem("user") || "null"),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (s) => Boolean(s.access),
    accountSlug: (s) => s.user?.account?.slug || null,
  },

  actions: {
    async login(email, password) {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.post("api/auth/login", { email, password });
        console.log("Login response data:", data);
        const tokens = data?.tokens;
        const user   = data?.user;
        const access = tokens?.access;
        const refresh = tokens?.refresh;

        if (!access || !refresh || !user)
          throw new Error("Resposta inválida do servidor.");

        this.access = access;
        this.refresh = refresh;
        this.user = user;

        localStorage.setItem("access", access);
        localStorage.setItem("refresh", refresh);
        localStorage.setItem("user", JSON.stringify(user));

        return true;
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          "Falha ao autenticar";
        this._clearSession();
        return false;
      } finally {
        this.loading = false;
      }
    },

    async fetchMe() {
      this.loading = true;
      this.error = null;
      try {
        const me = await api.get("api/me");
        this.user = me;
        localStorage.setItem("user", JSON.stringify(me));
        return me;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || "Falha ao buscar perfil";
        return null;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        const refresh = this.refresh || localStorage.getItem("refresh");
        if (refresh) {
          await api.post("api/auth/logout", { refresh });
        }
      } catch {
        // ignora falha de logout
      } finally {
        this._clearSession();
      }
    },

    _clearSession() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
    },
  },
});
