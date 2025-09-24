// src/store/account.js
import { defineStore } from "pinia";
import api from "../lib/Api";
import { unwrapData } from "./utils";

const LS_KEY = "account";

export const useAccountStore = defineStore("account", {
  state: () => ({
    account: null,
    updatedAt: null,
    loading: false,
    error: null,
    ttlMs: 5 * 60 * 1000,
  }),

  getters: {
    isStale: (s) => {
      if (!s.updatedAt) return true;
      return Date.now() - s.updatedAt > s.ttlMs;
    },
  },

  actions: {
    hydrate() {
      try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        this.account = parsed.account || null;
      } catch {}
    },

    persist() {
      try {
        localStorage.setItem(LS_KEY, JSON.stringify(this.account));
      } catch {}
    },

    setOne(account) {
      if (!account?.id) return;
      this.account = account;
      this.updatedAt = Date.now();
      this.persist();
    },

    clear() {
      this.account = null;
      this.updatedAt = null;
      this.persist();
    },

    async fetch({ force = false } = {}) {
      if (!force && this.account && !this.isStale) {
        return this.account;
      }
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.get(`api/account/${this.account?.id}`);
        const payload = unwrapData(resp);
        const account = payload?.account ?? payload;
        if (!account?.id) throw new Error("Account não encontrada");
        this.setOne(account);
        return account;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao buscar account";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchById(id, { force = false } = {}) {
      if (!force && this.account && this.account.id === id && !this.isStale) {
        return this.account;
      }
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.get(`api/account/${id}`);
        const payload = unwrapData(resp);
        const account = payload?.account ?? payload;
        if (!account?.id) throw new Error("Account não encontrada");
        this.setOne(account);
        return account;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao buscar account";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async ensure(id, { force = false } = {}) {
      if (!id) return null;
      if (this.account && this.account.id === id && !this.isStale && !force) {
        return this.account;
      }
      return this.fetchById(id, { force });
    },

    async updateById(id, payload) {
      if (!id) throw new Error("id é obrigatório.");
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.put(`api/account/${id}/update`, payload);
        const data = unwrapData(resp);
        const updated = data?.account ?? data;
        if (!updated?.id) throw new Error("Erro ao atualizar account");
        this.setOne(updated);
        return updated;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao atualizar account";
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },
});
