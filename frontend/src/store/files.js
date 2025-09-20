// stores/files.js
import { defineStore } from "pinia";
import api from "../lib/Api";
import { unwrapData } from "./utils";

export const useFilesStore = defineStore("files", {
  state: () => ({
    loading: false,
    error: null,
  }),

  actions: {
    async createFile({ file }) {
      if (!file) throw new Error("Arquivo é obrigatório.");
      this.loading = true;
      this.error = null;
      try {
        const fd = new FormData();
        fd.append("file", file);

        // rota de create (ok)
        const resp = await api.post("api/files/add", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const raw = unwrapData(resp);
        const item = raw?.file ?? raw?.files ?? raw;
        if (!item?.id) throw new Error("A API não retornou o ID do arquivo.");
        return item;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || "Falha ao enviar arquivo";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateFile({ fileId, file }) {
      if (!fileId || !file) throw new Error("fileId e file são obrigatórios.");

      this.loading = true;
      this.error = null;
      try {
        const fd = new FormData();
        fd.append("file", file);

        const resp = await api.put(`api/files/${fileId}/update`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const raw = unwrapData(resp);
        const item = raw?.file ?? raw?.files ?? raw;
        if (!item?.id) throw new Error("A API não retornou o ID do arquivo.");
        return item;
      } catch (e) {
        if (e?.response?.status === 404) {
          try {
            const created = await this.createFile({ file });
            return created;
          } catch (inner) {
            this.error = inner?.response?.data?.detail || inner?.message || "Falha ao atualizar arquivo (fallback create)";
            throw inner;
          }
        }
        this.error = e?.response?.data?.detail || e?.message || "Falha ao atualizar arquivo";
        throw e;
      } finally {
        this.loading = false;
      }
    },
  },
});
