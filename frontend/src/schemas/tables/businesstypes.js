// forms/schemas/tables/businesstypesTableSchema.js


export const businesstypeTableSchema = {
  name: 'businesstype',
  id: 'businesstype',
  title: 'Tipos de Negócio',
  icon: 'pi pi-briefcase',
  store: 'businesstype',
  pageSize: 20,
  rowsPerPageOptions: [10, 20, 30, 50, 100],
  defaultSort: {
    field: 'code',
    order: 1
  },
  selection: true,
  ListFields: [
    'code',
    'name',
    'is_active',
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
      field: 'is_active',
      header: 'Status',
      type: 'tag',
      width: '120px',
      sortable: true,
      severityMap: {
        true: 'success',
        false: 'danger'
      },
      format: (value) => {
        return value ? 'Ativo' : 'Inativo';
      }
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