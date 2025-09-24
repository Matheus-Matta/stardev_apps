// src/forms/show-field-error.js
/**
 * Aplica estilos de erro e a mensagem no Field correspondente ao `name`.
 * Procura por [data-input-name="<name>"] e por .field-error no container [data-field-root].
 */
export function showFieldErrorByName(name, message, root = document) {
  if (!name || !root) return false;
  const input = root.querySelector(`[data-input-name="${CSS.escape(name)}"]`);
  if (!input) return false;

  const fieldRoot = input.closest("[data-field-root]");
  const errorEl = fieldRoot?.querySelector(".field-error");

  input.setAttribute("aria-invalid", "true");
  input.classList.add("ring-1", "ring-red-500", "border-red-500");

  if (errorEl) {
    errorEl.textContent = String(message || "Valor inválido.");
    errorEl.style.display = "block";
  }

  return true;
}

export function clearFieldErrorByName(name, root = document) {
  if (!name || !root) return false;
  const input = root.querySelector(`[data-input-name="${CSS.escape(name)}"]`);
  if (!input) return false;

  const fieldRoot = input.closest("[data-field-root]");
  const errorEl = fieldRoot?.querySelector(".field-error");

  input.setAttribute("aria-invalid", "false");
  input.classList.remove("ring-1", "ring-red-500", "border-red-500");

  if (errorEl) {
    errorEl.textContent = "";
    errorEl.style.display = "none";
  }
  return true;
}
