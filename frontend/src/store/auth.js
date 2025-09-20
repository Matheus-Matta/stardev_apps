// stores/auth.js
import { defineStore } from "pinia";
import api from "../lib/Api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access:  localStorage.getItem("access") || null,
    refresh: localStorage.getItem("refresh") || null,
    user:    JSON.parse(localStorage.getItem("user") || "null"),
    account: JSON.parse(localStorage.getItem("account") || "null"),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (s) => Boolean(s.access),
    accountSlug:     (s) => s.account?.slug || null,
  },

  actions: {
    async login(email, password) {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.post("api/auth/login", { email, password });

        // Compatível com { data: { user, account, tokens } } e também { user, tokens }
        const root    = data?.data ?? data;
        const tokens  = root?.tokens ?? data?.tokens;
        const user    = root?.user   ?? data?.user   ?? null;
        // Normaliza account (pode vir em root.account, user.account ou user.Account)
        const account =
          root?.account ??
          user?.account ??
          user?.Account ??
          null;

        const access  = tokens?.access;
        const refresh = tokens?.refresh;

        if (!access || !refresh || !user) {
          throw new Error("Resposta inválida do servidor.");
        }

        // salva em memória
        this.access  = access;
        this.refresh = refresh;
        this.user    = user;
        this.account = account;

        // persiste
        localStorage.setItem("access", access);
        localStorage.setItem("refresh", refresh);
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("account", JSON.stringify(account));

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

    async logout() {
      try {
        const refresh = this.refresh || localStorage.getItem("refresh");
        if (refresh) {
          await api.post("api/auth/logout", { refresh });
        }
      } catch {
        // silencioso
      } finally {
        this._clearSession();
      }
    },

    async changePassword({ currentPassword, newPassword }) {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.post("api/auth/change-password", {
          currentPassword,
          newPassword,
        });
        return data;
      } catch (e) {
        this.error =
          e?.response?.data?.message ||
          e?.response?.data?.detail ||
          e?.message ||
          "Não foi possível alterar a senha";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    _clearSession() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      this.account = null;
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
      localStorage.removeItem("account");
    },
  },
});
