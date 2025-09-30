// src/store/business.js
import { defineStore } from "pinia";
import api from "../lib/Api";
import { unwrapData } from "./utils";

const LS_KEY = "business";

export const useBusinessStore = defineStore("business", {
  state: () => ({
    byId: {},            
    items: [],           
    count: 0,           
    updatedAt: null,
    loading: false,
    error: null,
    ttlMs: 5 * 60 * 1000, 
    lastListParams: null, 
  }),

  getters: {
    isStale: (s) => {
      if (!s.updatedAt) return true;
      return Date.now() - s.updatedAt > s.ttlMs;
    },
    tree: (s) => buildTree(s.items),
  },

  actions: {
    hydrate() {
      try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        if (parsed?.items && Array.isArray(parsed.items)) {
          this.items = parsed.items;
          this.count = parsed.count || 0;
          this.updatedAt = parsed.updatedAt || null;
          this.byId = Object.fromEntries(this.items.map((b) => [b.id, b]));
        }
      } catch {}
    },

    persist() {
      try {
        const data = {
          items: this.items,
          count: this.count,
          updatedAt: this.updatedAt,
        };
        localStorage.setItem(LS_KEY, JSON.stringify(data));
      } catch {}
    },

    _setMany(list = []) {
      this.items = list;
      this.count = typeof this.count === "number" ? this.count : list.length;
      this.byId = Object.fromEntries(list.map((b) => [b.id, b]));
      this.updatedAt = Date.now();
      this.persist();
    },

    _setOne(business) {
      if (!business?.id) return;
      this.byId = { ...this.byId, [business.id]: business };

      const idx = this.items.findIndex((x) => x.id === business.id);
      if (idx >= 0) {
        const clone = this.items.slice();
        clone[idx] = business;
        this.items = clone;
      }

      this.updatedAt = Date.now();
      this.persist();
    },

    _removeOne(id) {
      if (!id) return;
      const { [id]: _, ...rest } = this.byId;
      this.byId = rest;
      this.items = this.items.filter((x) => x.id !== id);
      this.updatedAt = Date.now();
      this.persist();
    },

    async fetchById(id, { force = false } = {}) {
      if (!force && this.byId[id]) return this.byId[id];

      this.loading = true;
      this.error = null;
      try {
        const resp = await api.get(`api/business/${id}`);
        const payload = unwrapData(resp);
        const business = payload?.business ?? payload;
        if (!business?.id) throw new Error("Business não encontrado");
        this._setOne(business);
        return business;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao buscar business";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async listBusinesses(params = {}, { force = true } = {}) {
      if (!force && !this.isStale && shallowEqual(params, this.lastListParams)) {
        return { items: this.items, count: this.count };
      }

      this.loading = true;
      this.error = null;
      try {
        const resp = await api.get("api/businesses", { params });
        const data = unwrapData(resp);
        const list = data?.businesses ?? data?.rows ?? []; // compat/fallback
        const count = data?.count ?? list.length;
        this.count = count;
        this._setMany(list);
        this.lastListParams = { ...params };
        return { items: this.items, count: this.count };
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao listar businesses";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async createBusiness(payload) {
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.post("api/business/add", payload);
        const data = unwrapData(resp);
        const created = data?.business ?? data;
        if (!created?.id) throw new Error("Erro ao criar business");
        this._setOne(created);
        return created;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao criar business";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateBusiness(id, payload) {
      if (!id) throw new Error("id é obrigatório.");
      this.loading = true;
      this.error = null;
      try {
        const resp = await api.put(`api/business/${id}/update`, payload);
        const data = unwrapData(resp);
        const updated = data?.business ?? data;
        if (!updated?.id) throw new Error("Erro ao atualizar business");
        this._setOne(updated);
        return updated;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao atualizar business";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteBusiness(id) {
      if (!id) throw new Error("id é obrigatório.");
      this.loading = true;
      this.error = null;
      try {
        await api.delete(`api/business/${id}/delete`);
        this._removeOne(id);
        return true;
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || "Falha ao deletar business";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    getTree(list = null) {
      return buildTree(list || this.items);
    },
  },
});

function buildTree(list = []) {
  const map = Object.create(null);
  list.forEach((item) => {
    map[item.id] = { ...item, children: [] };
  });

  const roots = [];
  list.forEach((item) => {
    const node = map[item.id];
    const parentId = item.parent || item.parent_id || item.parentId || null;
    if (parentId && map[parentId]) {
      map[parentId].children.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
}

function shallowEqual(a, b) {
  if (a === b) return true;
  if (!a || !b) return false;
  const ka = Object.keys(a);
  const kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  for (const k of ka) {
    if (a[k] !== b[k]) return false;
  }
  return true;
}
