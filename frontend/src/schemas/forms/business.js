// forms/schemas/create/business.js
const toStr = (v) => (v == null ? "" : String(v).trim());

export const businessSchema = {
  name: "business",
  id: "business",
  title: "Empresa",
  store: "business",
  submitLabel: "Criar Empresa",
  editTitle: "Editar Empresa",
  editSubmitLabel: "Salvar",
  icon: "pi pi-briefcase",
  sections: [
    {
      title: "Dados da Empresa",
      description:
        "Preencha os detalhes da nova empresa. O código será gerado automaticamente.",
      rows: [
        {
          colsPer: 2,
          cols: [
            {
              key: "name",
              iconLeft: "pi pi-user",
              label: "Nome",
              required: true,
              placeholder: "Ex.: Minha Empresa",
              type: "text",
              error: "Informe um nome válido (2 a 255 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 255;
              },
            },
            {
              key: "cnpj",
              label: "CNPJ",
              required: true,
              iconLeft: "pi pi-id-card",
              placeholder: "00.000.000/0000-00",
              type: "mask",
              mask: "99.999.999/9999-99",
              error: "CNPJ inválido.",
              validate: (v) => {
                let s = toStr(v).replace(/\D/g, "");
                if (s.length === 0) return true;
                if (s.length !== 14) return false;
                if (/^(\d)\1{13}$/.test(s)) return false;

                let sum = 0;
                const w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
                for (let i = 0; i < 12; i++) sum += parseInt(s[i]) * w1[i];
                let mod = sum % 11;
                const c1 = mod < 2 ? 0 : 11 - mod;
                if (c1 !== parseInt(s[12])) return false;

                sum = 0;
                const w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
                for (let i = 0; i < 13; i++) sum += parseInt(s[i]) * w2[i];
                mod = sum % 11;
                const c2 = mod < 2 ? 0 : 11 - mod;
                return c2 === parseInt(s[13]);
              },
              normalizeOnSave: (v) => {
                const s = toStr(v).replace(/\D/g, "");
                if (s.length !== 14) return "";
                return `${s.substring(0, 2)}.${s.substring(2, 5)}.${s.substring(
                  5,
                  8
                )}/${s.substring(8, 12)}-${s.substring(12)}`;
              },
            },
          ],
        },
        {
          colsPer: 2,
          cols: [
            {
              key: "business_type_id",
              label: "Tipo de Negócio",
              store: "businesstype",
              required: true,
              type: "select",
              placeholder: "Selecione...",
              async options(term) {
                const { useStore } = await import("../../store/index");
                const api = useStore("businesstype");
                const params = { limit: 5, offset: 0 };
                const q = (term || "").trim();
                if (q) params.search = q;
                const resp = await api.list(params, { force: true });
                const items = resp?.items || resp?.rows || [];
                return items.map((it) => ({ label: it.name, value: it.id }));
              },
              format: (value) =>
                value ? { label: value.name, value: value.id } : null,
            },
            {
              key: "parent_id",
              label: "Negócio Pai",
              store: "business",
              type: "select",
              placeholder: "Selecione...",
              async options(term) {
                const { useStore } = await import("../../store/index");
                const api = useStore("business");
                const params = { limit: 5, offset: 0 };
                const q = (term || "").trim();
                if (q) params.search = q;
                const resp = await api.list(params, { force: true });
                const items = resp?.items || resp?.rows || [];
                return items.map((it) => ({ label: it.name, value: it.id }));
              },
              format: (value) =>
                value ? { label: value.name, value: value.id } : null,
            },
          ],
        },
        {
          colsPer: 1,
          cols: [
            {
              key: "is_active",
              label: "Ativo",
              type: "checkbox",
              defaultValue: true,
            },
          ],
        },
      ],
    },
    {
      title: "Endereço da Empresa",
      id: "address",
      description: "Preencha o endereço da empresa.",
      rows: [
        {
          colsPer: 3,
          cols: [
            {
              key: "street",
              label: "Logradouro",
              iconLeft: "pi pi-map",
              placeholder: "Rua Exemplo",
              type: "text",
              error: "Informe o logradouro (2 a 100 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 100;
              },
            },
            {
              key: "postal_code",
              label: "CEP",
              iconLeft: "pi pi-map-marker",
              placeholder: "12345-678",
              type: "mask",
              mask: "99999-999",
              error: "CEP inválido (deve ter 8 dígitos).",
              validate: (v) => {
                const s = toStr(v).replace(/\D/g, "");
                return !s || s.length === 8;
              },
            },
            {
              key: "number",
              label: "Número",
              iconLeft: "pi pi-hashtag",
              placeholder: "123",
              type: "text",
              directives: {
                keyfilter: { pattern: /^\d*$/, validateOnly: true },
              },
              error: "Informe o número (1 a 20 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 1 && s.length <= 20;
              },
            },
          ],
        },
        {
          colsPer: 2,
          cols: [
            {
              key: "district",
              label: "Bairro",
              iconLeft: "pi pi-building",
              placeholder: "Centro",
              type: "text",
              error: "Informe o bairro (2 a 50 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 50;
              },
            },
            {
              key: "city",
              label: "Cidade",
              iconLeft: "pi pi-map",
              placeholder: "São Paulo",
              type: "text",
              error: "Informe a cidade (2 a 50 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 50;
              },
            },
          ],
        },
        {
          colsPer: 2,
          cols: [
            {
              key: "state",
              label: "Estado",
              iconLeft: "pi pi-flag",
              placeholder: "RJ",
              type: "mask",
              mask: "aa",
              defaultValue: "RJ",
              normalizeOnInput: (v) => toStr(v).toUpperCase(),
              error: "Informe o estado (2 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 1 && s.length <= 2;
              },
            },
            {
              key: "country",
              label: "País",
              iconLeft: "pi pi-globe",
              placeholder: "BR",
              type: "mask",
              mask: "aa",
              defaultValue: "BR",
              normalizeOnInput: (v) => toStr(v).toUpperCase(),
              error: "Informe o país (1 a 2 caracteres).",
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 1 && s.length <= 2;
              },
            },
          ],
        },
        {
          colsPer: 2,
          cols: [
            {
              key: "complement",
              label: "Complemento",
              iconLeft: "pi pi-plus",
              placeholder: "Apt 101",
              type: "text",
              error: "Complemento deve ter até 50 caracteres.",
              validate: (v) => toStr(v).length <= 50,
            },
            {
              key: "reference",
              label: "Referência",
              iconLeft: "pi pi-info-circle",
              placeholder: "Próximo ao shopping",
              type: "text",
              error: "Referência deve ter até 100 caracteres.",
              validate: (v) => toStr(v).length <= 100,
            },
          ],
        },
      ],
    },
    {
      title: "Empresas relacionadas",
      description: "Veja as empresas relacionadas.",
      rows: [
        {
          colsPer: 1,
          cols: [
            {
              key: "children",
              type: "relation",
              schema: "business",
              showAdd: false,
              showEdit: false,
              pk: "id",
              columns: [
                {
                  field: "code",
                  header: "Código",
                  width: "120px",
                  type: "text",
                  sortable: true,
                },
                {
                  field: "name",
                  header: "Nome",
                  width: "60%",
                  type: "text",
                  sortable: true,
                },
                {
                  field: "is_active",
                  header: "Status",
                  type: "tag",
                  width: "100px",
                  severityMap: { true: "success", false: "danger" },
                  format: (v) => (v ? "Ativo" : "Inativo"),
                },
              ],
              async rows(id, { limit = 5, offset = 0, page = 1 } = {}) {
                const { useStore } = await import("../../store/index");
                const api = useStore("business");

                const params = {
                  limit,
                  offset,
                  page,
                  fields: {
                    parent_id: { op: "equal", value: id },
                  },
                };

                const resp = await api.list(params, { force: true });

                const items = resp?.items ?? resp?.rows ?? [];
                const total = resp?.total ?? resp?.count ?? items.length;
                const page_size = resp?.page_size ?? limit;
                const total_pages =
                  resp?.total_pages ??
                  Math.max(1, Math.ceil(total / page_size));

                return {
                  items,
                  total,
                  page: resp?.page ?? page,
                  page_size,
                  total_pages,
                };
              },
            },
          ],
        },
      ],
    },
  ],
};
