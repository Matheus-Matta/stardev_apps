// src/forms/input-formatter.js
import { inputValue } from "./input-map";
import { inputMask } from "./input-mask";
import { inputValidate } from "./input-validate";

export function inputFormatter(name, el, formEl, errorEl) {
  const cfg = inputValue(name);
  inputMask(el, cfg);
  inputValidate(el, cfg, formEl, errorEl);
  return cfg; 
}
