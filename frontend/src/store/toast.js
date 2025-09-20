// src/store/toast.js
import { defineStore } from "pinia";

let _id = 0;

export const useToastStore = defineStore("toast", {
  state: () => ({
    items: [], // { id, type: 'success'|'error'|'info', message, duration }
  }),
  actions: {
    push({ type = "success", message = "", duration = 3000 }) {
      const id = ++_id;
      const item = { id, type, message, duration };
      this.items.push(item);
      if (duration) setTimeout(() => this.remove(id), duration);
      return id;
    },
    success(message, opts = {}) { return this.push({ ...opts, type: "success", message }); },
    error(message, opts = {})   { return this.push({ ...opts, type: "error",   message, duration: opts.duration ?? 5000 }); },
    info(message, opts = {})    { return this.push({ ...opts, type: "info",    message }); },
    remove(id) { this.items = this.items.filter(t => t.id !== id); },
    clear() { this.items = []; },
  },
});
