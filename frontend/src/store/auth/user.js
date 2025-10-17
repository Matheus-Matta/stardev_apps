// src/store/user.js
import api from '../../lib/Api'
import { defineStore } from 'pinia'
import { unwrapData } from '../utils'

const KEY = 'user'

function now() {
  return Date.now()
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    updatedAt: null,
    loading: false,
    error: null,
    ttlMs: 5 * 60 * 1000, // 5min
  }),

  getters: {
    isStale(s) {
      if (!s.updatedAt) return true
      return Date.now() - s.updatedAt > s.ttlMs
    },
  },

  actions: {
    hydrate() {
      try {
        const raw = localStorage.getItem(KEY)
        if (!raw) return false
        const parsed = JSON.parse(raw)

        if (parsed && parsed.user) {
          this.user = parsed.user || null
          this.updatedAt = parsed.updatedAt || now()
        } else if (parsed && parsed.id) {
          this.user = parsed
          this.updatedAt = now()
        } else {
          this.user = null
          this.updatedAt = null
        }
        return !!this.user
      } catch {
        return false
      }
    },

    persist() {
      try {
        localStorage.setItem(
          KEY,
          JSON.stringify({ user: this.user, updatedAt: this.updatedAt })
        )
      } catch {}
    },

    setOne(user) {
      if (!user || !user.id) return
      this.user = user
      this.updatedAt = now()
      this.persist()
    },

    removeOne() {
      this.user = null
      this.updatedAt = null
      try {
        localStorage.removeItem(KEY)
      } catch {}
    },

    async fetch({ force = false } = {}) {
      this.hydrate()
      if (!force && this.user && !this.isStale) return this.user

      this.loading = true
      this.error = null
      try {
        const endpoint = `api/${KEY}/${this.user.id}`
        const resp = await api.get(endpoint)
        const user = unwrapData(resp)?.user ?? unwrapData(resp)
        if (!user?.id) throw new Error('Usuário não encontrado')
        this.setOne(user)
        return user
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao buscar usuário'
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchById(id, { force = false } = {}) {
      if (!id) return null
      if (!force && this.user && !this.isStale && this.user.id === id) {
        return this.user
      }

      this.loading = true
      this.error = null
      try {
        const resp = await api.get(`api/${KEY}/${id}`)
        const user = unwrapData(resp)?.user ?? unwrapData(resp)
        if (!user?.id) throw new Error('Usuário não encontrado')
        this.setOne(user)
        return user
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao buscar usuário'
        throw e
      } finally {
        this.loading = false
      }
    },

    async ensure(id, { force = false } = {}) {
      if (id) return this.fetchById(id, { force })
      return this.fetchMe({ force })
    },

    // -------- CRUD --------
    async createUser(payload) {
      this.loading = true
      this.error = null
      try {
        const resp = await api.post(`api/${KEY}/add`, payload)
        const user = unwrapData(resp)?.user ?? unwrapData(resp)
        if (!user?.id) throw new Error('Erro ao criar usuário')
        this.setOne(user)
        return user
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao criar usuário'
        throw e
      } finally {
        this.loading = false
      }
    },

    async update(payload) {
      const id = this.user?.id
      if (!id) throw new Error('ID é obrigatório')
      this.loading = true
      this.error = null
      try {
        const resp = await api.put(`api/${KEY}/${id}/update`, payload)
        const user = unwrapData(resp)?.user ?? unwrapData(resp)
        if (!user?.id) throw new Error('Erro ao atualizar usuário')
        this.setOne(user)
        return user
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          'Falha ao atualizar usuário'
        throw e
      } finally {
        this.loading = false
      }
    },
    
    async deleteUser(id) {
      if (!id) throw new Error('ID é obrigatório')
      this.loading = true
      this.error = null
      try {
        await api.delete(`api/${KEY}/${id}/delete`)
        this.removeOne()
        return true
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao deletar usuário'
        throw e
      } finally {
        this.loading = false
      }
    },

    hasPermissions(required = [], { mode = 'all' } = {}) {
      if (this.user?.is_superuser) return true
      const list = Array.isArray(this.user?.groups_permissions)
        ? this.user.groups_permissions
        : []

      if (!required?.length) return true
      if (mode === 'all') return required.every(p => list.includes(p))
      if (mode === 'any') return required.some(p => list.includes(p))
      return false
    },

    hasPermission(p) {
      return this.hasPermissions([p], { mode: 'all' })
    },
  },
})
