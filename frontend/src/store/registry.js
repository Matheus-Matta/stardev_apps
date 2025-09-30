// src/store/useStore.js
import { useUserStore } from './user'
import { useBusinessStore } from './business'
import { useAccountStore } from './account'

export const REGISTRY = {
  user: {
    use: useUserStore,
    methods: {
      get:     'fetch',      
      getById: 'fetchById',  
      list:    'list',       
      create:  'createUser',
      update:  'updateUser',
      delete:  'deleteUser',
    },
  },
  business: {
    use: useBusinessStore,
    methods: {
      get:     'fetch',         
      getById: 'fetchById',
      list:    'listBusinesses',
      create:  'createBusiness',
      update:  'updateBusiness',
      delete:  'deleteBusiness',
    },
  },
  account: {
    use: useAccountStore,
    methods: {
      get:     'fetch',
      getById: 'fetchById',
      list:    '',
      create:  '',
      update:  'updateAccount',
      delete:  '',
    },
  },
}