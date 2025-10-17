// src/composables/useFormModel.js
import { isObj, isEmpty } from "./formHelpers";

export function useFormModel() {
  /**
   * Normaliza valor para o formato esperado pelo campo
   */
  function normalizeForField(field, value) {
    if (field.type === "select") {
      if (value == null || value === "") return null;
      if (isObj(value)) {
        const val =
          "value" in value ? value.value : "id" in value ? value.id : value;
        const label =
          "label" in value ? value.label : "name" in value ? value.name : "";
        return { value: val, label };
      }
      return { value, label: "" };
    }

    if (field?.type === "relation") {
      return Array.isArray(value) ? value : [];
    }

    if (["checkbox", "toggle"].includes(field.type)) {
      return isObj(value) ? !!(value.value ?? value.id ?? value) : !!value;
    }

    // text/mask
    return isObj(value) ? value.value ?? value.id ?? "" : value ?? "";
  }

  /**
   * Normaliza valor para salvar (extrai primitivo)
   */
  function normalizeForSave(field, value) {
    if (field?.normalizeOnSave) {
      return field.normalizeOnSave(value);
    }

    const normalized = normalizeForField(field, value);

    if (field?.type === "select") {
      return normalized ? normalized.value : normalized;
    }

    return normalized;
  }

  /**
   * Aplica normalização de entrada se definida
   */
  function normalizeOnInput(field, value) {
    if (!field?.normalizeOnInput) return value;
    return field.normalizeOnInput(value);
  }

  /**
   * Extrai e formata valor do registro para o campo
   */
  function extractAndFormatFieldValue(field, source, record) {
    let raw = source?.[field.key];

    // Tenta chave alternativa (ex: business_type_id -> business_type)
    if ((raw === undefined || raw === null) && /_id$/.test(field.key)) {
      const alt = field.key.replace(/_id$/, "");
      if (source && alt in source) raw = source[alt];
    }

    // Aplica formato customizado se existir
    if (typeof field?.format === "function") {
      try {
        raw = field.format(raw, source, record);
      } catch (e) {
        console.warn(`[format error] ${field.key}:`, e);
      }
    }

    return raw;
  }

  function hydrateFromRecord(sections, record, model, keyGenerator) {
    sections.forEach((sec, i) => {
      const secKey = keyGenerator(sec, i);
      let source = i === 0 ? record : record?.[secKey];
      if (source === undefined || source === null) {
        source = record;
      }
      sec.rows?.forEach((row) => {
        row.cols?.forEach((field) => {
          const raw = extractAndFormatFieldValue(field, source, record);
          model[field.key] = normalizeForField(field, raw);
        });
      });
    });
  }

  /**
   * Aplica valores padrão aos campos da seção
   */
  function applyDefaults(section, model, opts = {}) {
    const treatEmpty = (v) =>
      v === undefined ||
      v === null ||
      (opts.treatEmptyAsUnset && typeof v === "string" && v.trim() === "");
    section?.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        const def = field.defaultValue ?? field.default;
        if (def !== undefined && treatEmpty(model[field.key])) {
          model[field.key] = def;
        }
      })
    );
  }

  return {
    normalizeForField,
    normalizeForSave,
    normalizeOnInput,
    extractAndFormatFieldValue,
    applyDefaults,
    hydrateFromRecord,
  };
}
