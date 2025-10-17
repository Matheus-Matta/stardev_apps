// forms/schemas/tables/businessesTableSchema.js

export const businessTableSchema = {
  name: 'business',
  id: 'business',
  title: 'Empresas',
  icon: 'pi pi-briefcase',
  store: 'business',
  pageSize: 10,
  rowsPerPageOptions: [10, 20, 30, 50, 100],
  defaultSort: {
    field: 'created_at',
    order: -1
  },
  selection: true,
  ListFields: [
    'code',
    'name',
    'cnpj',
    'business_type.name',
    'parent.name',
    'created_at',
  ],
  columns: [
    {
      field: 'code',
      header: 'Código',
      type: 'text',
      width: '84px',
      sortable: true
    },
    {
      field: 'name',
      header: 'Nome',
      type: 'text',
      width: '192px',
      sortable: true,
    },
    {
      field: 'cnpj',
      header: 'CNPJ',
      type: 'text',
      width: '192px',
      sortable: true,
      format: (value) => {
        if (!value) return '';
        const cleaned = value.replace(/\D/g, '');
        return cleaned.replace(
          /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
          '$1.$2.$3/$4-$5'
        );
      },
    },
    {
      field: 'business_type.name',
      header: 'Tipo',
      type: 'text',
      width: '140px',
      sortable: true,
    },
    {
      field: 'is_active',
      header: 'Status',
      type: 'tag',
      width: '120px',
      sortable: true,
      severityMap: {
        true: 'success',
        false: 'danger'
      },
      format: (value) => value ? 'Ativo' : 'Inativo',
    },
    {
      field: 'parent.name',
      header: 'Matriz/Filial',
      type: 'text',
      width: '180px',
      sortable: true,
    },
    {
      field: 'address.city',
      header: 'Cidade',
      type: 'text',
      width: '160px',
      sortable: true,
    },
    {
      field: 'created_at',
      header: 'Criado em',
      type: 'date',
      width: '160px',
      sortable: true,
      format: (value) => {
        if (!value) return '';
        const date = new Date(value);
        return date.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      },
    }
  ],
};