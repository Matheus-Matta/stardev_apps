import axios from "axios";
import { useAuthStore } from "../store/auth";
import { toast } from "./toast";

const baseURL = import.meta.env.VITE_API_BASE_URL;

class Api {
  constructor() {
    this.http = axios.create({ baseURL, withCredentials: false });

    this.http.interceptors.request.use((config) => {
      const auth = useAuthStore();
      const token = auth?.access;
      if (token) config.headers.Authorization = `Bearer ${token}`;
      const slug = auth?.user?.account?.slug;
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
        const msg =
          err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Ocorreu um erro.";
        toast.error(msg);
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
