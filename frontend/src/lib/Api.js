// src/lib/Api.js
import axios from "axios";
import qs from "qs";
import { useAuthStore } from "../store/auth/auth";
import { toast } from "./toast";

const baseURL = import.meta.env.VITE_API_BASE_URL;

function cleanParams(obj) {
  if (obj == null) return obj;
  if (Array.isArray(obj)) {
    const v = obj
      .map(cleanParams)
      .filter((x) => x !== null && x !== undefined && x !== "");
    return v.length ? v : undefined;
  }
  if (typeof obj === "object") {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      const cv = cleanParams(v);
      if (cv !== null && cv !== undefined && cv !== "") out[k] = cv;
    }
    return Object.keys(out).length ? out : undefined;
  }
  return obj;
}

function applyFieldError(field, msg) {
  if (!field || !msg) return;
  const name = String(field).trim();
  if (!name || name === "non_field_errors") return;
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
          .map((v) =>
            v && typeof v === "object" && "message" in v
              ? String(v.message)
              : typeof v === "string"
              ? v
              : null
          )
          .filter(Boolean);
        if (messages.length) applyFieldError(field, messages.join(" "));
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
    this.http = axios.create({
      baseURL,
      withCredentials: false,
      paramsSerializer: {
        serialize: (params) =>
          qs.stringify(cleanParams(params) || {}, {
            arrayFormat: "brackets", 
            encodeValuesOnly: true, 
          }),
      },
    });

    this.http.interceptors.request.use((config) => {
      const auth = useAuthStore();
      const token = auth?.access;
      if (token) config.headers.Authorization = `Bearer ${token}`;

      const slug = auth?.user?.account?.slug || auth?.user?.Account?.slug;
      if (slug) config.headers["X-Account-Slug"] = slug;

      // Se por acaso alguém setar config.params manualmente depois:
      if (config.params) config.params = cleanParams(config.params);

      return config;
    });

    this.http.interceptors.response.use(
      (res) => {
        const status = res?.status ?? 200;
        const method = String(res?.config?.method || "").toUpperCase();

        const silent =
          res?.config?.toast === false ||
          res?.config?.headers?.["X-Silent-Toast"] === "1";

        if (status >= 200 && status < 300 && method !== "GET" && !silent) {
          const title = "Resposta do servidor";
          const msg =
            res?.data?.detail ||
            res?.data?.message ||
            "Operação concluída com sucesso.";
          toast.success(msg, { title });
        }
        return res;
      },
      (err) => {
        const data = err?.response?.data || {};
        const title = "Ocorreu um erro.";
        const generalMsg =
          data?.detail || data?.message || err?.message || "Ocorreu um erro.";

        const silent =
          err?.config?.toast === false ||
          err?.config?.headers?.["X-Silent-Toast"] === "1";

        if (!silent) {
          toast.error(generalMsg, { title, duration: 6000 });
        }

        try {
          const fieldPayload =
            data.errors || data.field_errors || data?.data?.errors || null;
          dispatchFieldErrors(fieldPayload);
        } catch (_) {}

        return Promise.reject(err);
      }
    );
  }

  get(url, config) {
    return this.http.get(url, config);
  }
  post(url, body, c) {
    return this.http.post(url, body, c);
  }
  put(url, body, c) {
    return this.http.put(url, body, c);
  }
  delete(url, config) {
    return this.http.delete(url, config);
  }
}

const api = new Api();
export default api;
export { Api };
