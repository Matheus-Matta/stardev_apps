// src/forms/input-validate.js
import { inputValue } from "./input-map";

export function inputValidate(el, cfg, formEl, errorEl) {
  if (!el || !cfg) return;

  const renderError = (msg) => {
    if (msg) {
      el.setAttribute("aria-invalid", "true");
      el.classList.add("ring-1", "ring-red-500", "border-red-500");
      if (errorEl) {
        errorEl.textContent = msg;
        errorEl.style.display = "block";
      }
    } else {
      el.setAttribute("aria-invalid", "false");
      el.classList.remove("ring-1", "ring-red-500", "border-red-500");
      if (errorEl) {
        errorEl.textContent = "";
        errorEl.style.display = "none";
      }
    }
  };

  const run = () => {
    let val = el.value;
    if (typeof cfg.normalizeOnInput === "function") {
      const before = val;
      val = cfg.normalizeOnInput(val);
      if (val !== before) el.value = val;
    }
    const ok = typeof cfg.validate === "function" ? cfg.validate(val) : true;
    renderError(ok ? "" : cfg.error || "Valor inválido.");
    return !!ok;
  };

  el.addEventListener("input", run);
  el.addEventListener("blur", run);

  // validação no submit do form pai
  const form = formEl || el.closest("form");
  if (form && !form.__has_inputs_validator__) {
    form.__has_inputs_validator__ = true;

    form.addEventListener("submit", (evt) => {
      const inputs = form.querySelectorAll("[data-input-name]");
      let firstInvalid = null;

      inputs.forEach((inputEl) => {
        const name = inputEl.getAttribute("data-input-name");
        const conf = inputValue(name);

        const isOk =
          typeof conf.validate === "function"
            ? conf.validate(inputEl.value)
            : true;

        const errorTarget =
          inputEl.closest("[data-field-root]")?.querySelector(".field-error");

        if (!isOk) {
          inputEl.setAttribute("aria-invalid", "true");
          inputEl.classList.add("ring-1", "ring-red-500", "border-red-500");
          if (errorTarget) {
            errorTarget.textContent = conf.error || "Valor inválido.";
            errorTarget.style.display = "block";
          }
          if (!firstInvalid) firstInvalid = inputEl;
        } else {
          inputEl.setAttribute("aria-invalid", "false");
          inputEl.classList.remove("ring-1", "ring-red-500", "border-red-500");
          if (errorTarget) {
            errorTarget.textContent = "";
            errorTarget.style.display = "none";
          }
        }
      });

      if (firstInvalid) {
        evt.preventDefault();
        firstInvalid.focus();
      }
    });
  }

  // estado inicial
  run();
}
