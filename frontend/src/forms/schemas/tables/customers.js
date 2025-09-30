import { FilterMatchMode, FilterOperator } from '@primevue/core/api'
const BRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export const CustomerstableSchemas = {
  customers: {
    title: 'Clientes',
    model: 'customers',                   
    store: 'customer',                
    pageSize: 10,
    rowsPerPageOptions: [10, 20, 50, 100],
    globalFilterFields: ['name', 'country.name', 'representative.name', 'balance', 'status'],
    selection: 'multiple',             
    defaultSort: { field: 'name', order: 1 }, 
    server: {
      limitParam: 'limit',
      offsetParam: 'offset',
      searchParam: 'search',
      orderingParam: 'order_by',
      startParam: 'start_date',
      endParam: 'end_date'
    },
    options: {
      statuses: ['unqualified', 'qualified', 'new', 'negotiation', 'renewal'],
      representatives: [
        { name: 'Amy Elsner', image: 'amyelsner.png' },
        { name: 'Anna Fali', image: 'annafali.png' },
        { name: 'Asiya Javayant', image: 'asiyajavayant.png' },
        { name: 'Bernardo Dominic', image: 'bernardodominic.png' }
      ]
    },
    columns: [
      {
        type: 'selection',               
      },
      {
        field: 'name',
        header: 'Name',
        sortable: true,
        filter: {
          matchMode: FilterMatchMode.STARTS_WITH,
          operator: FilterOperator.AND,
          ui: 'text',                  
          server: { param: 'name', op: 'startswith' } 
        }
      },
      {
        header: 'Country',
        sortField: 'country.name',
        filterField: 'country.name',
        sortable: true,
        type: 'avatarText',                 
        avatar: (row) => `https://primefaces.org/cdn/primevue/images/flag/flag_placeholder.png`,
        text:   (row) => row?.country?.name ?? '',
        filter: {
          matchMode: FilterMatchMode.STARTS_WITH,
          operator: FilterOperator.AND,
          ui: 'text',
          server: { param: 'country__name', op: 'istartswith' }
        }
      },
      {
        header: 'Agent',
        sortField: 'representative.name',
        filterField: 'representative',
        sortable: true,
        type: 'avatarText',
        avatar: (row) => `https://primefaces.org/cdn/primevue/images/avatar/${row?.representative?.image}`,
        text:   (row) => row?.representative?.name ?? '',
        filter: {
          matchMode: FilterMatchMode.IN,
          ui: 'multiselect',                
          optionsKey: 'representatives',
          optionLabel: 'name',
          server: { param: 'representative__in', op: 'in', map: (items) => items.map(i => i.name) }
        }
      },
      {
        field: 'date',
        header: 'Date',
        sortable: true,
        type: 'date',
        format: (d) => new Date(d).toLocaleDateString('pt-BR'),
        filter: {
          matchMode: FilterMatchMode.DATE_IS,
          operator: FilterOperator.AND,
          ui: 'date',      
          server: { param: 'date__date', op: 'eq' }
        }
      },
      {
        field: 'balance',
        header: 'Balance',
        sortable: true,
        type: 'currency',
        format: (v) => BRL.format(v ?? 0),
        filter: {
          matchMode: FilterMatchMode.EQUALS,
          operator: FilterOperator.AND,
          ui: 'number',                  
          server: { param: 'balance', op: 'eq' }
        }
      },
      {
        field: 'status',
        header: 'Status',
        sortable: true,
        type: 'tag',                        
        severityMap: {         
          unqualified: 'danger',
          qualified: 'success',
          new: 'info',
          negotiation: 'warn',
          renewal: null
        },
        filter: {
          matchMode: FilterMatchMode.EQUALS,
          operator: FilterOperator.OR,
          ui: 'select',                      
          optionsKey: 'statuses',
          server: { param: 'status', op: 'eq' }
        }
      },
      {
        field: 'activity',
        header: 'Activity',
        sortable: true,
        type: 'progress',                   
        filter: {
          matchMode: FilterMatchMode.BETWEEN,
          ui: 'range',                     
          server: { param: 'activity__between', op: 'between' }
        }
      },
      {
        type: 'actions',
        header: '',
        width: '5rem',
        actions: [
          { icon: 'pi pi-cog', rounded: true, onClick: (row) => console.log('Action row', row?.id) }
        ]
      }
    ],
    extraFilters: {
      dateRange: {
        startKey: 'start_date',
        endKey:   'end_date'
      }
    }
  }
}