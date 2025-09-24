// src/forms/input-mask.js
import Inputmask from "inputmask";

export function inputMask(el, cfg) {
  if (!el || !cfg || !cfg.mask) return;
  try {
    Inputmask.remove(el);
  } catch (e) {}
  const im = new Inputmask({
    mask: cfg.mask,
    showMaskOnHover: false,
    showMaskOnFocus: false,
    clearMaskOnLostFocus: false,
  });
  im.mask(el);
}
