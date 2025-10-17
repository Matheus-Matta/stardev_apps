export const GRID_COLS = {
  1: "grid-cols-1",
  2: "grid-cols-2",
  3: "grid-cols-3",
  4: "grid-cols-4",
  5: "grid-cols-5",
  6: "grid-cols-6",
};

export function toStr(v) {
  return v == null ? "" : String(v).trim();
}

export function isObj(v) {
  return v && typeof v === "object" && !Array.isArray(v);
}

export function isEmpty(v) {
  if (v === null || v === undefined) return true;
  if (typeof v === "string") return v.trim() === "";
  if (Array.isArray(v)) return v.length === 0;
  if (isObj(v) && "value" in v) return isEmpty(v.value);
  return false;
}

export function rowClass(row) {
  const per = Math.max(1, Math.min(6, row?.colsPer || row?.cols?.length || 1));
  return `grid ${GRID_COLS[per] || GRID_COLS[1]} gap-3 w-full`;
}

export function keyFromSection(section, idx) {
  if (section?.payloadKey) return section.payloadKey;
  if (section?.key) return section.key;
  if (section?.id) return section.id;
  if (section?.title) {
    const s = String(section.title)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-zA-Z0-9 ]/g, " ")
      .trim()
      .replace(/\s+([a-zA-Z])/g, (_, c) => c.toUpperCase());
    return s.length ? s[0].toLowerCase() + s.slice(1) : `section_${idx}`;
  }
  return `section_${idx}`;
}

export function mustValidate(field, v) {
  return !!field?.required || !isEmpty(v);
}

export function getErrorText(field, value) {
  if (field?.required && isEmpty(value)) {
    return field.requiredError || "Campo obrigatório.";
  }
  if (!field?.required && isEmpty(value)) {
    return "";
  }
  return field.error || "Valor inválido.";
}

export function findSectionArray(model, fieldKey) {
  const rootVal = model?.[fieldKey];
  if (Array.isArray(rootVal)) return rootVal;

  for (const k of Object.keys(model || {})) {
    const v = model[k];
    if (v && typeof v === "object" && Array.isArray(v[fieldKey])) {
      return v[fieldKey];
    }
  }
  return [];
}