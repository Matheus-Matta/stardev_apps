// src/store/account.js
import { defineStore } from 'pinia'
import api from '../../lib/Api'
import { unwrapData } from '../utils'

const LS_KEY = 'account'
const now = () => Date.now()

export const useAccountStore = defineStore('account', {
  state: () => ({
    account: null,
    updatedAt: null,
    loading: false,
    error: null,
    ttlMs: 5 * 60 * 1000, 
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
        const raw = localStorage.getItem(LS_KEY)
        if (!raw) return false

        const parsed = JSON.parse(raw)

        if (parsed && parsed.account) {
          this.account = parsed.account || null
          this.updatedAt = parsed.updatedAt || now()
        } else if (parsed && parsed.id) {
          this.account = parsed
          this.updatedAt = now()
        } else {
          this.account = null
          this.updatedAt = null
        }
        return !!this.account
      } catch {
        return false
      }
    },

    persist() {
      try {
        if (this.account) {
          localStorage.setItem(
            LS_KEY,
            JSON.stringify({ account: this.account, updatedAt: this.updatedAt })
          )
        } else {
          localStorage.removeItem(LS_KEY)
        }
      } catch {}
    },

    setOne(account) {
      if (!account || !account.id) return
      this.account = { ...account }
      this.updatedAt = now()
      this.persist()
    },

    clear() {
      this.account = null
      this.updatedAt = null
      try {
        localStorage.removeItem(LS_KEY)
      } catch {}
    },

    async fetch({ force = false } = {}) {
      if (!this.account?.id) this.hydrate()
      if (!this.account?.id) return null

      if (!force && this.account && !this.isStale) {
        return this.account
      }
      this.loading = true
      this.error = null
      try {
        const resp = await api.get(`api/account/${this.account.id}`)
        const payload = unwrapData(resp)
        const account = payload?.account ?? payload
        if (!account?.id) throw new Error('Account não encontrada')
        this.setOne(account)
        return account
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao buscar account'
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchById(id, { force = false } = {}) {
      if (!id) return null
      if (!force && this.account && this.account.id === id && !this.isStale) {
        return this.account
      }
      this.loading = true
      this.error = null
      try {
        const resp = await api.get(`api/account/${id}`)
        const payload = unwrapData(resp)
        const account = payload?.account ?? payload
        if (!account?.id) throw new Error('Account não encontrada')
        this.setOne(account)
        return account
      } catch (e) {
        this.error =
          e?.response?.data?.detail || e?.message || 'Falha ao buscar account'
        throw e
      } finally {
        this.loading = false
      }
    },

    async ensure(id, { force = false } = {}) {
      if (id) return this.fetchById(id, { force })
      return this.fetch({ force })
    },

    async updateAccount(id, payload = {}) {
      if (!id) throw new Error('id é obrigatório.')
      this.loading = true
      this.error = null
      try {
        const resp = await api.put(`api/account/${id}/update`, payload)
        const data = unwrapData(resp)
        const updated = data?.account ?? data
        if (!updated?.id) throw new Error('Erro ao atualizar account')
        this.setOne(updated)
        return updated
      } catch (e) {
        this.error =
          e?.response?.data?.detail ||
          e?.message ||
          'Falha ao atualizar account'
        throw e
      } finally {
        this.loading = false
      }
    },
    async update(payload = {}) {
     let id = this.account?.id
     if (!id) throw new Error('Nenhuma conta carregada.')
     return this.updateAccount(id, payload)    
    },
  },
})
