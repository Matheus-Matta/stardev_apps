import { useUserStore } from "./user";
import { useBusinessStore } from "./business";

/**
 * @typedef {Object} ListParams
 * @property {string}  [search]
 * @property {string}  [ordering]          // ex.: "name" ou "-created_at"
 * @property {number}  [page=1]
 * @property {number}  [pageSize=10]
 * @property {Object}  [filters]           // ex.: { "created_at__gte": "2025-01-01" }
 */

/**
 * @typedef {Object} NormalizedStore
 * @property {(id: string|number, options?: any) => Promise<any>} get
 * @property {(params?: ListParams) => Promise<{rows:any[], count:number}>} list
 * @property {(payload: Object) => Promise<any>} create
 * @property {(id: string|number, payload: Object) => Promise<any>} update
 * @property {(id: string|number) => Promise<void>} delete
 */

// Registro com função que retorna a instância do store e o mapa de métodos
const REGISTRY = {
  user: {
    use: useUserStore,
    methods: {
      get: " fetchById",
      list: "list",
      create: "createUser",
      update: "updateUser",
      delete: "deleteUser",
    },
  },
  business: {
    use: useBusinessStore,
    methods: {
      get:    "fetchById",
      list:   "listBusinesses",
      create: "createBusiness",
      update: "updateBusiness",
      delete: "deleteBusiness",
    },
  },
};

/**
 * Retorna uma interface normalizada para o store do `model_name`.
 * @param {string} model_name - ex.: "user" | "business"
 * @returns {NormalizedStore}
 */
export function useStore(model_name) {
  const entry = REGISTRY[model_name];
  if (!entry) {
    throw new Error(`Store não registrado para: ${model_name}`);
  }

  const store = entry.use(); // cria UMA instância
  const {
    get: getName,
    list: listName,
    create: createName,
    update: updateName,
    delete: deleteName,
  } = entry.methods;

  // ---- WRAPPERS COM ASSINATURA PADRÃO ----

  // GET: id obrigatório, options opcional
  const get = (id, options) => {
    if (!store[getName]) throw new Error(`${model_name}.${getName} não existe`);
    return store[getName](id, options);
  };

  // LIST: { search, ordering, page, pageSize, filters }
  /** @param {ListParams} [params] */
  const list = (params = {}) => {


    if (!store[listName]) throw new Error(`${model_name}.${listName} não existe`);

    return store[listName](params);
  };

  const create = (payload) => {
    if (!store[createName]) throw new Error(`${model_name}.${createName} não existe`);
    return store[createName](payload);
  };

  const update = (id, payload) => {
    if (!store[updateName]) throw new Error(`${model_name}.${updateName} não existe`);
    return store[updateName](id, payload);
  };

  const remove = (id) => {
    if (!store[deleteName]) throw new Error(`${model_name}.${deleteName} não existe`);
    return store[deleteName](id);
  };

  return {
    get,
    list,
    create,
    update,
    delete: remove,
  };
}
