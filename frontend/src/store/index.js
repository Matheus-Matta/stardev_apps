
import api from '../lib/Api'
import { REGISTRY  } from './registry'

export function useStore(model_name) {
  const entry = REGISTRY[model_name]
  if (!entry) throw new Error(`Store não registrado para: ${model_name}`)

  const store = entry.use()
  const {
    get: getName,
    getById: getByName,
    list: listName,
    create: createName,
    update: updateName,
    delete: deleteName,
  } = entry.methods

  const has = (name) => !!name && typeof store[name] === 'function'
  const label = (name, fallback) => name || fallback

  const get = (arg1, arg2) => {
    const isIdCall = typeof arg1 === 'string' || typeof arg1 === 'number'
    if (isIdCall) {
      if (!has(getByName)) {
        throw new Error(`${model_name}.${label(getByName, 'getById')} não existe`)
      }
      return store[getByName](arg1, arg2)
    }
    if (!has(getName)) {
      throw new Error(`${model_name}.${label(getName, 'get')} não existe`)
    }
    const options = arg1
    return store[getName](options)
  }

  const getById = (id, options) => {
    if (!has(getByName)) {
      throw new Error(`${model_name}.${label(getByName, 'getById')} não existe`)
    }
    return store[getByName](id, options)
  }

  const list = (params = {}) => {
    if (!has(listName)) {
      throw new Error(`${model_name}.${label(listName, 'list')} não existe`)
    }
    return store[listName](params)
  }

  const create = (payload) => {
    if (!has(createName)) {
      throw new Error(`${model_name}.${label(createName, 'create')} não existe`)
    }
    return store[createName](payload)
  }

  const update = (id, payload) => {
    if (!has(updateName)) {
      throw new Error(`${model_name}.${label(updateName, 'update')} não existe`)
    }
    return store[updateName](id, payload)
  }

  const remove = (id) => {
    if (!has(deleteName)) {
      throw new Error(`${model_name}.${label(deleteName, 'delete')} não existe`)
    }
    return store[deleteName](id)
  }

  async function listActions() {
    try {
      const resp = await api.get(`api/${model_name}/actions`)
      return resp?.data ?? resp
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Falha ao listar actions'
      throw new Error(msg)
    }
  }

  async function runAction(actionName, items) {
    if (!actionName || typeof actionName !== 'string') {
      throw new Error('actionName inválido.')
    }
    const body = Array.isArray(items) ? items : [items]
    if (!body.length) throw new Error('Payload da action deve conter ao menos um item.')
    try {
      const resp = await api.post(`api/${model_name}/action/${actionName}`, body)
      return resp?.data ?? resp
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Falha ao executar action'
      const extra = e?.response?.data
      const err = new Error(msg)
      err.extra = extra
      throw err
    }
  }

  return {
    get,
    getById,
    list,
    create,
    update,
    delete: remove,
    listActions,
    runAction,
  }
}
