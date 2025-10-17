import { useModelStore } from "./model";
export function useStore(modelName, options) {
  return useModelStore(modelName, options);
}
