// src/store/toast.js
import { defineStore } from "pinia";

let _id = 0;

export const useToastStore = defineStore("toast", {
  state: () => ({
    // { id, type: 'success'|'error'|'info'|'warn', title, message, duration }
    items: [],
  }),
  actions: {
    push(payload = {}) {
      const {
        type = "success",
        title = "",
        message = "",
        duration = 3000,
      } = payload;

      const id = ++_id;
      const item = { id, type, title, message, duration };
      this.items.push(item);
      if (duration) setTimeout(() => this.remove(id), duration);
      return id;
    },

    // use: toast.success('Mensagem', { title: 'Sucesso', duration: 3000 })
    success(message, opts = {}) {
      return this.push({ ...opts, type: "success", message });
    },
    error(message, opts = {}) {
      return this.push({
        ...opts,
        type: "error",
        message,
        duration: opts.duration ?? 5000,
      });
    },
    info(message, opts = {}) {
      return this.push({ ...opts, type: "info", message });
    },
    // opcional:
    warn(message, opts = {}) {
      return this.push({ ...opts, type: "warn", message });
    },

    remove(id) { this.items = this.items.filter(t => t.id !== id); },
    clear() { this.items = []; },
  },
});
