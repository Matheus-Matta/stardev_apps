// src/lib/Api.js
import axios from "axios";
import { useAuthStore } from "../store/auth";
import { toast } from "./toast";
import { showFieldErrorByName } from "../forms/show-field-error";

const baseURL = import.meta.env.VITE_API_BASE_URL;

function applyFieldError(field, msg) {
  if (!field || !msg) return;
  const name = String(field).trim();
  if (!name || name === "non_field_errors") return;
  showFieldErrorByName(name, String(msg));
}

function dispatchFieldErrors(fieldPayload) {
  if (!fieldPayload) return;

  if (typeof fieldPayload === "string") {
    const str = fieldPayload;

    str.split(";").forEach((piece) => {
      const part = piece.trim();
      if (!part) return;
      const m = part.match(/^([^:]+):\s*(.+)$/);
      if (m) applyFieldError(m[1]?.trim(), m[2]?.trim());
    });

    const rx = /([a-zA-Z0-9_]+)\s*:\s*([^;]+)/g;
    let match;
    while ((match = rx.exec(str))) {
      applyFieldError(match[1], match[2]);
    }
    return;
  }

  if (typeof fieldPayload === "object" && !Array.isArray(fieldPayload)) {
    Object.entries(fieldPayload).forEach(([field, val]) => {
      if (val == null) return;

      if (typeof val === "string") {
        applyFieldError(field, val);
        return;
      }

      if (Array.isArray(val)) {
        const messages = val
          .map((v) => {
            if (v && typeof v === "object" && "message" in v) {
              return String(v.message);
            }
            if (typeof v === "string") return v;
            return null;
          })
          .filter(Boolean);

        if (messages.length) {
          applyFieldError(field, messages.join(" "));
        }
        return;
      }

      if (typeof val === "object" && "message" in val) {
        applyFieldError(field, String(val.message));
        return;
      }
    });
  }
}

class Api {
  constructor() {
    this.http = axios.create({ baseURL, withCredentials: false });

    this.http.interceptors.request.use((config) => {
      const auth = useAuthStore();
      const token = auth?.access;
      if (token) config.headers.Authorization = `Bearer ${token}`;

      const slug = auth?.user?.account?.slug || auth?.user?.Account?.slug;
      if (slug) config.headers["X-Account-Slug"] = slug;

      return config;
    });

    this.http.interceptors.response.use(
      (res) => {
        const status = res?.status ?? 200;
        const method = res?.config?.method?.toUpperCase();
        if (status >= 200 && status < 300 && method !== "GET") {
          const msg = res?.data?.detail || "Operação concluída com sucesso.";
          toast.success(msg);
        }
        return res;
      },
      (err) => {
        const data = err?.response?.data || {};
        const generalMsg =
          data?.detail ||
          data?.message ||
          err?.message ||
          "Ocorreu um erro.";
        toast.error(generalMsg);

        try {
          const fieldPayload =
            data.errors ||
            data.field_errors ||
            data?.data?.errors ||
            null;

          dispatchFieldErrors(fieldPayload);
        } catch (_) {
        }

        return Promise.reject(err);
      }
    );
  }

  get(url, config)    { return this.http.get(url, config); }
  post(url, body, c)  { return this.http.post(url, body, c); }
  put(url, body, c)   { return this.http.put(url, body, c); }
  delete(url, config) { return this.http.delete(url, config); }
}

const api = new Api();
export default api;
export { Api };
