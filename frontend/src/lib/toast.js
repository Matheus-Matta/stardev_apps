// src/lib/toast.js
import { useToastStore } from "../store/toast";

export const toast = {
  success: (message, opts) => useToastStore().success(message, opts),
  error:   (message, opts) => useToastStore().error(message, opts),
  info:    (message, opts) => useToastStore().info(message, opts),
};
