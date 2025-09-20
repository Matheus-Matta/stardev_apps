import { defineStore } from "pinia";
import api from "../lib/Api";
import { useFilesStore } from "./files";

const KEY = "user";

function unwrapData(resp) {
  const root = resp?.data ?? resp;
  const data = root?.data ?? root;
  const { ok, detail, ...rest } = data || {};
  return data && data !== root ? data : rest;
}

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null,
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
        const raw = localStorage.getItem(KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        this.user = parsed.user || null;
      } catch {}
    },

    persist() {
      try {
        localStorage.setItem(KEY, JSON.stringify(this.user));
      } catch {}
    },

    setOne(user) {
      if (!user?.id) return;
      this.user = user;
      this.persist();
    },

    removeOne() {
      this.user = null;
      this.persist();
    },

    async fetchById(id, { force = false } = {}) {
      if (!force && this.user && !this.isStale && this.user.id === id) {
        return this.user;
      }
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.get(`api/${KEY}/${id}`);
        const user = unwrapData(resp)?.user ?? unwrapData(resp);
        if (!user?.id) throw new Error("Usuário não encontrado");
        this.setOne(user);
        return user;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao buscar usuário";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async ensure(id, { force = false } = {}) {
      if (!id) return null;
      if (this.user && this.user.id === id && !this.isStale && !force) {
        return this.user;
      }
      return this.fetchById(id, { force });
    },

    async createUser(payload) {
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.post("api/user/add", payload);
        const user = unwrapData(resp)?.user ?? unwrapData(resp);
        if (!user?.id) throw new Error("Erro ao criar usuário");
        this.setOne(user);
        return user;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao criar usuário";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateUser(id, payload) {
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.put(`api/user/${id}/update`, payload);
        const user = unwrapData(resp)?.user ?? unwrapData(resp);
        if (!user?.id) throw new Error("Erro ao atualizar usuário");
        this.setOne(user);
        return user;
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          "Falha ao atualizar usuário";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteUser(id) {
      this.loading = true;
      this.error = null;
      try {
        await api.delete(`api/user/${id}/delete`);
        this.removeOne();
        return true;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao deletar usuário";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async setAvatarByFileId(userId, fileId) {
      if (!userId || !fileId) throw new Error("userId e fileId são obrigatórios.");
      this.loading = true;
      this.error = null;
      try {
        const updated = await this.updateUser(userId, { avatar: fileId });
        return updated;
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          "Falha ao atualizar avatar do usuário";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async uploadAndSetAvatar({ userId, file }) {
      if (!userId) throw new Error("userId é obrigatório.");
      if (!file) throw new Error("file é obrigatório.");

      this.loading = true;
      this.error = null;
      try {
        const user = await this.fetchById(userId);
        const filesStore = useFilesStore();
        let uploaded;
        if (user && user.avatar) {
          uploaded = await filesStore.updateFile({ fileId: user.avatar, file });
        } else {
          uploaded = await filesStore.createFile({ file });
        }
        const updatedUser = await this.setAvatarByFileId(userId, uploaded.id);
        return { file: uploaded, user: updatedUser || this.user };
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          "Falha ao enviar e aplicar avatar";
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },

});