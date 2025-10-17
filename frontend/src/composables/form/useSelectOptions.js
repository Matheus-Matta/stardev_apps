// src/composables/form/useSelectOptions.js
import { reactive, watch } from "vue";
import { useStore } from "../../store/index";
import { isObj } from "./formHelpers";

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function looksLikeId(val, field) {
  if (val == null) return false;
  const s = String(val).trim();
  if (!s) return false;

  if (field?.idPattern instanceof RegExp) return field.idPattern.test(s);

  if (UUID_RE.test(s)) return true;
  if (/^\d+$/.test(s)) return true;

  return false;
}

export function useSelectOptions(modelValue) {
  const options = reactive({});
  const loading = reactive({});
  const searchVal = reactive({});
  const reqToken = reactive({}); // simples "cancelamento" por token
  const debounceTimers = {}; // debounce por campo

  function clearDebounce(key) {
    if (debounceTimers[key]) {
      clearTimeout(debounceTimers[key]);
      delete debounceTimers[key];
    }
  }

  async function fetchFromStore(field, term) {
    const api = useStore(field.optionsStore || field.store);
    const params = { limit: field.limit ?? 5, offset: 0 };
    const q = (term || "").trim();
    if (q) params.search = q;

    const resp = await api.list(params, { force: true });
    const items = resp?.items || resp?.rows || [];
    return items.map((it) => ({
      label: it.name ?? it.code ?? String(it.id ?? ""),
      value: it.id,
    }));
  }

  async function fetchOptions(field, term = "", { clearFirst = false } = {}) {
    const t = (reqToken[field.key] ?? 0) + 1;
    reqToken[field.key] = t;

    if (clearFirst) options[field.key] = [];
    loading[field.key] = true;

    try {
      let opts = [];

      if (Array.isArray(field.options)) {
        opts = field.options;
      } else if (typeof field.options === "function") {
        const maybe = field.options(term);
        opts = typeof maybe?.then === "function" ? await maybe : maybe || [];
      } else if (field.optionsStore || field.store) {
        opts = await fetchFromStore(field, term);
      }

      if (t === reqToken[field.key]) {
        options[field.key] = Array.isArray(opts) ? opts : [];
      }
    } finally {
      if (t === reqToken[field.key]) {
        loading[field.key] = false;
      }
    }
  }

  async function ensureSelectedLoaded(field) {
    const mv = modelValue[field.key];

    let id;
    if (isObj(mv)) {
      id = "value" in mv ? mv.value : "id" in mv ? mv.id : undefined;
    } else if (looksLikeId(mv, field)) {
      id = mv;
    } else {
      return; 
    }

    if (id == null || id === "") return;

    const exists = (options[field.key] || []).some(
      (o) => String(o.value) === String(id)
    );
    if (exists && isObj(mv) && (mv.label || mv.name)) return;

    loading[field.key] = true;

    try {
      let opt = null;

      if (typeof field.defaultValue === "function") {
        const maybe = field.defaultValue(id);
        const val = typeof maybe?.then === "function" ? await maybe : maybe;
        if (
          val &&
          typeof val === "object" &&
          ("label" in val || "name" in val)
        ) {
          opt = {
            value: val.value ?? val.id ?? id,
            label: val.label ?? val.name ?? "",
          };
        }
      }

      if (!opt && (field.store || field.optionsStore)) {
        const api = useStore(field.store || field.optionsStore);
        if (api?.get && looksLikeId(id, field)) {
          const rec = await api.get(id, { force: true }).catch(() => null);
          if (rec) {
            opt = {
              label: rec.name ?? rec.code ?? String(rec.id ?? id),
              value: rec.id ?? id,
            };
          }
        }
      }

      if (opt) {
        options[field.key] = [opt, ...(options[field.key] || [])];
        const current = modelValue[field.key];
        if (isObj(current)) {
          current.value = current.value ?? current.id ?? opt.value;
          current.label = current.label || opt.label;
        } else {
          modelValue[field.key] = opt;
        }
      }
    } finally {
      loading[field.key] = false;
    }
  }

  function setupField(field) {
    fetchOptions(field, "", { clearFirst: true });

    ensureSelectedLoaded(field);

    watch(
      () => modelValue[field.key],
      (nv) => {
        const id = isObj(nv)
          ? "value" in nv
            ? nv.value
            : "id" in nv
            ? nv.id
            : undefined
          : nv;
        if (isObj(nv) || looksLikeId(id, field)) {
          ensureSelectedLoaded(field);
        }
      }
    );
  }

  function handleShow(field) {
    const term = searchVal[field.key] || "";
    fetchOptions(field, term, { clearFirst: false });
  }

  function handleFocus(field) {
    if (!options[field.key]?.length) {
      fetchOptions(field, searchVal[field.key] || "");
    }
  }

  function handleSearch(field, event) {
    const term = (event?.target?.value ?? "").toString();
    searchVal[field.key] = term;

    options[field.key] = [];
    loading[field.key] = true;

    clearDebounce(field.key);
    debounceTimers[field.key] = setTimeout(() => {
      fetchOptions(field, term, { clearFirst: false });
    }, field.debounceMs ?? 300);
  }

  return {
    options,
    loading,
    searchVal,
    setupField,
    fetchOptions,
    ensureSelectedLoaded,
    handleShow,
    handleFocus,
    handleSearch,
  };
}
