// /src/forms/tableSchemas/businesses.js
import { FilterMatchMode, FilterOperator } from "@primevue/core/api";

export const businessestableSchemas = {
  title: "Empresas",
  icon: "pi pi-briefcase",
  model: "businesses",
  store: "business",
  pageSize: 10,
  rowsPerPageOptions: [10, 20, 30, 50, 100],
  selection: "multiple",
  listDisplay: [
    "code",
    "name",
    "cnpj",
    "business_type",
    "is_active",
    "parent.name",
    "address.city",
    "created_at",
  ],
  globalFilterFields: [
    "code",
    "name",
    "cnpj",
    "business_type",
    "parent.name",
    "address.city",
    "address.state",
  ],
  server: {
    limitParam: "limit",
    offsetParam: "offset",
    searchParam: "search",
    orderingParam: "order_by",
    startParam: "start_date",
    endParam: "end_date",
  },
  options: {
    businessTypes: [],
    booleans: [
      { label: "Ativo", value: true },
      { label: "Inativo", value: false },
    ],
  },
  columns: [
    { type: "selection" },

    {
      field: "code",
      header: "Código",
      sortable: true,
      filter: {
        ui: "text",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.STARTS_WITH,
        server: { param: "code__istartswith", op: "istartswith" },
      },
    },

    {
      field: "name",
      header: "Nome",
      sortable: true,
      filter: {
        ui: "text",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.CONTAINS,
        server: { param: "name__icontains", op: "icontains" },
      },
    },

    {
      field: "cnpj",
      header: "CNPJ",
      sortable: true,
      filter: {
        ui: "text",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.CONTAINS,
        server: { param: "cnpj__icontains", op: "icontains" },
      },
    },

    {
      field: "business_type",
      header: "Tipo",
      sortable: true,
      type: "tag",
      severityMap: {
        store: "secondary",
        warehouse: "secondary",
        office: "secondary",
        franchise: "secondary",
        department: "secondary",
      },
      filter: {
        ui: "select",
        matchMode: FilterMatchMode.EQUALS,
        optionsKey: "businessTypes",
        server: { param: "business_type", op: "eq" },
      },
    },

    {
      field: "is_active",
      header: "Ativo",
      sortable: true,
      type: "tag",
      severityMap: { true: "success", false: "danger" },
      filter: {
        ui: "select",
        matchMode: FilterMatchMode.EQUALS,
        optionsKey: "booleans",
        server: { param: "is_active", op: "eq" },
      },
    },

    {
      header: "Matriz/Filial",
      type: "text",
      field: "parent.name",
      sortField: "parent.name",
      filterField: "parent.name",
      sortable: true,
      filter: {
        ui: "text",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.CONTAINS,
        server: { param: "parent__name__icontains", op: "icontains" },
      },
    },

    {
      header: "Cidade",
      type: "text",
      field: "address.city",
      sortField: "address.city",
      filterField: "address.city",
      sortable: true,
      filter: {
        ui: "text",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.CONTAINS,
        server: { param: "address__city__icontains", op: "icontains" },
      },
    },

    {
      field: "created_at",
      header: "Criado em",
      type: "date",
      sortable: true,
      filter: {
        ui: "date",
        operator: FilterOperator.AND,
        matchMode: FilterMatchMode.DATE_IS,
        server: { param: "created_at__date", op: "eq" },
      },
    },
  ],
  extraFilters: { dateRange: { startKey: "start_date", endKey: "end_date" } },
};
