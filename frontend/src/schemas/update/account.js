const toStr   = (v) => String(v ?? '').trim();
const URL_RE  = /^(https?):\/\/[^\s/$.?#].[^\s]*$/i;
const SLUG_RE = /^[a-z0-9-]{3,30}$/;
const EMAIL_RE= /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[+\d]{7,14}$/;

const normalizeSlug = (v) =>
  toStr(v).toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/--+/g, '-');

const ensureHttp = (v) => {
  const s = toStr(v);
  if (!s) return '';
  if (/^https?:\/\//i.test(s)) return s;
  return `https://${s}`;
};

export const accountSchema = {
  id: 'account.defaults',
  title: 'Configurações da Conta',
  icon: 'pi pi-id-card',
  submitLabel: 'Atualizar Conta',
  sections: [
    {
      title: 'Detalhes da Conta',
      store: 'account',
      permission: 'change_account',
      description: 'Visualize e edite os detalhes da sua conta.',
      rows: [
        {
          cols: [
            {
              key: 'display_name',
              iconLeft: 'pi pi-user',
              label: 'Nome de Exibição',
              placeholder: 'Ex.: Minha Empresa',
              type: 'text',
              error: 'Informe um nome de exibição válido (2 a 80 caracteres).',
              validate: (v) => { const s = toStr(v); return s.length >= 2 && s.length <= 80 },
              col: { sm: 12, md: 4, lg: 4 }
            },
            {
              key: 'legal_name',
              label: 'Razão Social',
              iconLeft: 'pi pi-briefcase',
              placeholder: 'Ex.: Minha Empresa LTDA',
              type: 'text',
              error: 'Informe a razão social (2 a 120 caracteres).',
              validate: (v) => { const s = toStr(v); return s.length >= 2 && s.length <= 120 },
              col: { sm: 12, md: 4, lg: 4 }
            },
            {
              key: 'slug',
              label: 'Slug',
              iconLeft: 'pi pi-hashtag',
              placeholder: 'ex.: minha-empresa',
              type: 'text',
              error: 'Slug inválido. Use 3–30 caracteres (letras minúsculas, números ou hífen).',
              validate: (v) => SLUG_RE.test(toStr(v)),
              normalizeOnInput: normalizeSlug,
              col: { sm: 12, md: 4, lg: 4 }
            }
          ]
        },
        {
          cols: [
            {
              key: 'email_principal',
              label: 'E-mail principal',
              iconLeft: 'pi pi-envelope',
              placeholder: 'contato@empresa.com',
              type: 'text',
              error: 'E-mail inválido.',
              validate: (v) => !toStr(v) || EMAIL_RE.test(toStr(v)),
              normalizeOnInput: (v) => toStr(v).toLowerCase(),
              col: { sm: 12, md: 6, lg: 6 }
            },
            {
              key: 'phone_principal',
              label: 'Telefone principal',
              iconLeft: 'pi pi-phone',
              placeholder: '+5521912345678',
              type: 'text',
              directives: {
                keyfilter: { pattern: /^\+?\d*$/, validateOnly: true }
              },
              error: 'Número inválido. Use o formato: +55XXXXXXXXXXX',
              validate: (v) => !toStr(v) || PHONE_RE.test(toStr(v).replace(/\s/g, '')),
              normalizeOnSave: (v) => {
                const raw = toStr(v)
                if (!raw) return ''
                const digits = raw.replace(/\D/g, '')
                return '+' + digits
              },
              col: { sm: 12, md: 6, lg: 6 }
            }
          ]
        },
        {
          cols: [
            {
              key: 'site_url',
              label: 'Site',
              iconLeft: 'pi pi-globe',
              placeholder: 'https://exemplo.com',
              type: 'text',
              error: 'URL inválida. Use http(s)://',
              validate: (v) => !toStr(v) || URL_RE.test(toStr(v)),
              normalizeOnSave: ensureHttp,
              col: { sm: 12, md: 6, lg: 6 }
            }
          ]
        },
        {
          cols: [
            {
              key: 'logo_url',
              label: 'Logo URL',
              iconLeft: 'pi pi-image',
              placeholder: 'https://exemplo.com/logo.png',
              type: 'text',
              error: 'URL inválida do logo. Use http(s)://',
              validate: (v) => !toStr(v) || URL_RE.test(toStr(v)),
              normalizeOnSave: ensureHttp,
              col: { sm: 12, md: 12, lg: 12 }
            }
          ]
        }
      ]
    }
  ]
};
