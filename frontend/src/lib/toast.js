// src/lib/toast.js
import { useToastStore } from "../store/toast";

export const toast = {
  success(message, opts) { return useToastStore().success(message, opts) },
  error(message,   opts) { return useToastStore().error(message,   opts) },
  info(message,    opts) { return useToastStore().info(message,    opts) },
  warn(message,    opts) { return useToastStore().warn?.(message,  opts) },
  push(payload)          { return useToastStore().push(payload) },
  clear()                { return useToastStore().clear() },
}
