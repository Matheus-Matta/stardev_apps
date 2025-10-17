// src/store/model.js
import { defineStore } from "pinia";
import api from "../lib/Api";
import { unwrapData } from "./utils";

const __modelFactories = new Map();

function buildLsKey(modelName, lsKey) {
  return `mdl:${lsKey || modelName}`;
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

export function useModelStore(modelName, opts = {}) {
  if (!modelName || typeof modelName !== "string") {
    throw new Error("useModelStore: 'modelName' é obrigatório (string).");
  }

  if (!__modelFactories.has(modelName)) {
    const id = `model:${modelName}`;
    const { ttlMs = 5 * 60 * 1000, lsKey = null } = opts;

    const useStoreDef = defineStore(id, {
      state: () => ({
        modelName,
        lsKey: buildLsKey(modelName, lsKey),
        byId: {},
        items: [],
        count: 0,
        updatedAt: null,
        loading: false,
        error: null,
        ttlMs,
        lastListParams: null,
      }),

      getters: {
        isStale: (s) => {
          if (!s.updatedAt) return true;
          return Date.now() - s.updatedAt > s.ttlMs;
        },
        tree: (s) => {
          const map = Object.create(null);
          s.items.forEach((item) => (map[item.id] = { ...item, children: [] }));
          const roots = [];
          s.items.forEach((item) => {
            const node = map[item.id];
            const parentId = item.parent || item.parent_id || item.parentId || null;
            if (parentId && map[parentId]) map[parentId].children.push(node);
            else roots.push(node);
          });
          return roots;
        },
      },

      actions: {
        hydrate() {
          try {
            const raw = localStorage.getItem(this.lsKey);
            if (!raw) return;
            const parsed = JSON.parse(raw);
            if (parsed?.items && Array.isArray(parsed.items)) {
              this.items = parsed.items;
              this.count = parsed.count || 0;
              this.updatedAt = parsed.updatedAt || null;
              this.byId = Object.fromEntries(this.items.map((x) => [x.id, x]));
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
            localStorage.setItem(this.lsKey, JSON.stringify(data));
          } catch {}
        },

        _setMany(list = [], count = null) {
          this.items = list;
          this.count = typeof count === "number" ? count : list.length;
          this.byId = Object.fromEntries(list.map((x) => [x.id, x]));
          this.updatedAt = Date.now();
          this.persist();
        },

        _setOne(rec) {
          if (!rec?.id) return;
          this.byId = { ...this.byId, [rec.id]: rec };
          const idx = this.items.findIndex((x) => x.id === rec.id);
          if (idx >= 0) {
            const clone = this.items.slice();
            clone[idx] = rec;
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

        async getById(id, { force = true } = {}) {
          if (id == null || id === "") throw new Error("id é obrigatório.");
          if (!force && this.byId[id]) return this.byId[id];
           
          this.loading = true;
          this.error = null;
          try {
            const resp = await api.get(`/api/${this.modelName}/${id}`);
            const payload = unwrapData(resp);
            const rec = payload?.[this.modelName] ?? payload;
            if (!rec?.id) throw new Error("Registro não encontrado");
            this._setOne(rec);
            console.log(rec);
            return rec;
          } catch (e) {
            this.error =
              e?.response?.data?.detail || e?.message || "Falha ao buscar registro";
            throw e;
          } finally {
            this.loading = false;
          }
        },

        async fetchById(id, opts) {
          return this.getById(id, opts);
        },

        async get(arg1, arg2) {
          if (typeof arg1 === "string" || typeof arg1 === "number") {
            return this.getById(arg1, arg2);
          }
          const { items } = await this.list(arg1 || {}, { force: true });
          return items;
        },

        async list(params = {}, { force = true } = {}) {
          if (!force && !this.isStale && shallowEqual(params, this.lastListParams)) {
            return { items: this.items, count: this.count };
          }

          this.loading = true;
          this.error = null;
          try {
            const resp = await api.get(`/api/${this.modelName}/list`, { params });
            const data = unwrapData(resp);
            const list = data?.items ?? data?.rows ?? [];
            const count = data?.count ?? list.length;
            this._setMany(list, count);
            this.lastListParams = { ...params };
            return { items: this.items, count: this.count };
          } catch (e) {
            this.error =
              e?.response?.data?.detail || e?.message || "Falha ao listar";
            throw e;
          } finally {
            this.loading = false;
          }
        },

        async create(payload) {
          this.loading = true;
          this.error = null;
          try {
            const resp = await api.post(`/api/${this.modelName}/add`, payload);
            const data = unwrapData(resp);
            const rec = data?.[this.modelName] ?? data;
            if (!rec?.id) throw new Error("Erro ao criar registro");
            this._setOne(rec);
            return rec;
          } catch (e) {
            this.error =
              e?.response?.data?.detail || e?.message || "Falha ao criar";
            throw e;
          } finally {
            this.loading = false;
          }
        },

        async update(id, payload) {
          if (!id) throw new Error("id é obrigatório.");
          this.loading = true;
          this.error = null;
          try {
            const resp = await api.put(`/api/${this.modelName}/${id}/update`, payload);
            const data = unwrapData(resp);
            const rec = data?.[this.modelName] ?? data;
            if (!rec?.id) throw new Error("Erro ao atualizar");
            this._setOne(rec);
            return rec;
          } catch (e) {
            this.error =
              e?.response?.data?.detail || e?.message || "Falha ao atualizar";
            throw e;
          } finally {
            this.loading = false;
          }
        },

        async delete(id) {
          if (!id) throw new Error("id é obrigatório.");
          this.loading = true;
          this.error = null;
          try {
            await api.delete(`/api/${this.modelName}/${id}/delete`);
            this._removeOne(id);
            return true;
          } catch (e) {
            this.error =
              e?.response?.data?.detail || e?.message || "Falha ao deletar";
            throw e;
          } finally {
            this.loading = false;
          }
        },

        async listActions() {
          const resp = await api.get(`/api/${this.modelName}/actions`);
          return resp?.data ?? resp;
        },

        async runAction(actionName, items) {
          if (!actionName || typeof actionName !== "string") {
            throw new Error("actionName inválido.");
          }
          const body = Array.isArray(items) ? items : [items];
          if (!body.length) throw new Error("Payload da action deve conter ao menos um item.");
          const resp = await api.post(`/api/${this.modelName}/action/${actionName}`, body);
          return resp?.data ?? resp;
        },
      },
    });

    __modelFactories.set(modelName, useStoreDef);
  }

  const useStoreDef = __modelFactories.get(modelName);
  const store = useStoreDef();

  if (!store.updatedAt) {
    try { store.hydrate(); } catch {}
  }

  return store;
}
