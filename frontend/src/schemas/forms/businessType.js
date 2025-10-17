// forms/schemas/create/businessType.js
const toStr = (v) => (v == null ? "" : String(v).trim());

export const businessTypeSchema = {
  name: "businesstype",
  id: "businesstype",
  title: "Tipo de Negócio",
  submitLabel: "Criar Tipo",
  store: "businesstype",
  editTitle: "Editar Tipo de Negócio",
  editSubmitLabel: "Salvar",
  icon: "pi pi-briefcase",
  sections: [
    {
      title: "Detalhes do Tipo",
      description:
        "Preencha os detalhes do novo tipo de negócio. O código será gerado automaticamente com base no nome.",
      rows: [
        {
          cols: [
            {
              key: "name",
              iconLeft: "pi pi-sitemap",
              label: "Nome",
              placeholder: "Ex.: Loja",
              type: "text",
              error: "Informe um nome válido (2 a 255 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 255;
              },
              col: { sm: 12, md: 8, lg: 8 },
            },
          ],
        },
        {
          cols: [
            {
              key: "is_active",
              label: "Tipo Ativo/Inativo",
              type: "checkbox",
              defaultValue: true,
              col: { sm: 12, md: 6, lg: 6 },
            },
          ],
        },
      ],
    },
  ],
};
