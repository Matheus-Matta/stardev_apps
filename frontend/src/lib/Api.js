import axios from "axios";
import { useAuthStore } from "../store/auth";

const baseURL = import.meta.env.VITE_API_BASE_URL;

class Api {
  constructor() {
    this.http = axios.create({ baseURL, withCredentials: false });

    // Request: Bearer + X-Account-Slug se houver
    this.http.interceptors.request.use((config) => {
      const auth = useAuthStore();
      const token = auth?.access;
      if (token) config.headers.Authorization = `Bearer ${token}`;

      // se já temos user com account.slug, manda para o middleware do backend
      const slug = auth?.user?.account?.slug;
      if (slug) config.headers["X-Account-Slug"] = slug;

      return config;
    });
    this.http.interceptors.response.use(
      (res) => {
        const d = res?.data;
        if (d && typeof d === "object" && "data" in d) return d.data;
        return d;
      },
      (err) => Promise.reject(err)
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
