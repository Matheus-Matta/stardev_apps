// src/composables/form/useFormFields.js
export function useFormFields({
  normalizeForField,
  normalizeForSave,
  normalizeOnInput,
  applyDefaults,
  userStore,
}) {
  const toNullIfBlank = (v) => (v === '' ? null : v);
  const idOf = (x) => (x && typeof x === 'object' ? (x.id ?? x.value ?? x.pk ?? x) : x);
  const shallowEq = (a, b) => {
    if (a === b || (a == null && b == null)) return true;
    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) return false;
      const A = a.map(idOf);
      const B = b.map(idOf);
      return A.every((v, i) => String(v) === String(B[i]));
    }
    return false;
  };
  const isEmpty = (v) => v === undefined || v === null || (typeof v === 'string' && v.trim() === '');

  function formatField(field, value) {
    const t = String(field?.type || 'text').toLowerCase();
    const asSelectObj = (v) => (v == null || typeof v === 'object' ? v : { value: v, label: String(v) });
    const asArray = (v) => (Array.isArray(v) ? v : v == null ? [] : [v]);
    const asText = (v) => (v == null ? '' : typeof v === 'string' ? v : String(v ?? ''));

    switch (t) {
      case 'text':
        return asText(value).trim();
      case 'mask':
        return asText(value);
      case 'select':
        return asSelectObj(value);
      case 'checkbox':
      case 'toggle':
        return !!value;
      case 'relation':
        return asArray(value);
      case 'currency':
      case 'number': {
        const n = Number(value);
        return Number.isFinite(n) ? n : null;
      }
      case 'date': {
        const d = new Date(value);
        return isNaN(d) ? value : d.toISOString();
      }
      default:
        return value;
    }
  }

  function applySectionDefaults(section, model, { treatEmptyAsUnset = true } = {}) {
    applyDefaults?.(section, model, { treatEmptyAsUnset });
    section?.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        const current = model[field.key];
        model[field.key] = formatField(field, current);
      }),
    );
  }

  function getFieldValue({ field, model, mode }) {
    const current = model[field.key];
    const when = field.defaultWhen || 'create';
    let base;
    if (!isEmpty(current)) {
      base = current;
    } else {
      const def = field.defaultValue ?? field.default;
      base = when === 'always' ? def : when === 'create' && mode === 'create' ? def : current;
    }

    const val =
      field.type === 'relation'
        ? Array.isArray(base)
          ? base
          : []
        : normalizeForField?.(field, base);

    return formatField(field, val);
  }

  function setFieldValue({ key, value, field, model, emit, validation }) {
    let next = normalizeOnInput?.(field, value);
    if (['checkbox', 'toggle'].includes(field?.type)) next = !!value;
    if (field?.type === 'select') next = normalizeForField?.(field, value);
    if (field?.type === 'relation') next = Array.isArray(value) ? value : [];
    next = formatField(field, next);

    model[key] = next;
    emit?.('update:modelValue', model);
    validation?.touch?.(key);
  }

  function snapshotInitial(section, model, initialObj) {
    Object.keys(initialObj).forEach((k) => delete initialObj[k]);
    section?.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        const raw = model[field.key];
        let val;
        if (field.type === 'relation') {
          val = Array.isArray(raw) ? raw.map(idOf) : [];
        } else {
          val = toNullIfBlank(normalizeForSave?.(field, raw));
        }
        initialObj[field.key] = val;
      }),
    );
  }

  function collectPayload(section, model, initialObj) {
    const payload = {};
    section?.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        const raw = model[field.key];
        const prepared = formatField(field, raw);

        let curr;
        if (field.type === 'relation') {
          if (typeof field.serialize === 'function') {
            curr = field.serialize(prepared);
          } else {
            curr = Array.isArray(prepared) ? prepared.map(idOf) : [];
          }
        } else {
          curr = toNullIfBlank(normalizeForSave?.(field, prepared));
        }

        const prev = initialObj[field.key];
        if (shallowEq(prev, curr)) return;
        if (curr === null && field?.sendWhenCleared === false) return;
        payload[field.key] = curr;
      }),
    );
    return payload;
  }

  function sectionEditable({ permBase, section }) {
    const baseOK = permBase ? userStore?.hasPermission?.(`change_${permBase}`) : true;
    const specific = section?.permission ? userStore?.hasPermission?.(section.permission) : true;
    return !!(baseOK && specific);
  }

  return {
    toNullIfBlank,
    idOf,
    shallowEq,
    isEmpty,
    formatField,
    applySectionDefaults,
    getFieldValue,
    setFieldValue,
    snapshotInitial,
    collectPayload,
    sectionEditable,
  };
}
