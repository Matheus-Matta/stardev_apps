// src/forms/schemas/update/settings.js
const toStr = (v) => String(v ?? '').trim();

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^\+?\d{7,15}$/;

export const settingsSchema = {
  id: 'settings.profile',
  title: 'Minha Conta',
  icon: 'pi pi-user',
  submitLabel: 'Atualizar Perfil',
  sections: [
    {
      store: 'user',
      title: 'Usuário',
      description: 'Atualize suas informações de perfil.',
      rows: [
        {
          colsPer: 3,
          cols: [
            {
              key: 'first_name',
              label: 'Nome',
              placeholder: 'Seu nome',
              type: 'text',
              iconLeft: 'pi pi-user',
              validate: (v) => toStr(v).length >= 2,
              error: 'Informe ao menos 2 caracteres.',
            },
            {
              key: 'last_name',
              label: 'Sobrenome',
              placeholder: 'Seu sobrenome',
              type: 'text',
              iconLeft: 'pi pi-user',
              validate: (v) => toStr(v).length >= 2,
              error: 'Informe ao menos 2 caracteres.',
            },
            {
              key: 'display_name',
              label: 'Nome de Exibição',
              placeholder: 'Ex.: João da Silva',
              type: 'text',
              iconLeft: 'pi pi-id-card',
              validate: (v) => {
                const s = toStr(v);
                return s.length >= 2 && s.length <= 80;
              },
              error: 'Use entre 2 e 80 caracteres.',
            },
          ],
        },
        {
          colsPer: 3,
          cols: [
            {
              key: 'username',
              label: 'Usuário',
              placeholder: 'ex.: joao.silva',
              type: 'text',
              iconLeft: 'pi pi-at',
              validate: (v) => /^[a-z0-9_.]{3,30}$/i.test(toStr(v)),
              error: '3–30 caracteres (letras, números, ponto ou _).',
              normalizeOnInput: (v) =>
                toStr(v)
                  .toLowerCase()
                  .replace(/\s+/g, '')
                  .replace(/[^a-z0-9_.]/g, ''),
            },
            {
              key: 'email',
              label: 'E-mail',
              placeholder: 'email@exemplo.com',
              type: 'email',
              iconLeft: 'pi pi-envelope',
              validate: (v) => !toStr(v) || EMAIL_RE.test(toStr(v)),
              error: 'E-mail inválido.',
              normalizeOnInput: (v) => toStr(v).toLowerCase(),
            },
            {
              key: 'phone',
              label: 'Telefone',
              placeholder: '+5511999999999',
              type: 'text',
              iconLeft: 'pi pi-phone',
              directives: { keyfilter: { pattern: /^\+?\d*$/, validateOnly: true } },
              validate: (v) => !toStr(v) || PHONE_RE.test(toStr(v)),
              error: 'Use + e dígitos (7–15). Ex.: +5511999999999',
              normalizeOnSave: (v) => {
                const raw = toStr(v);
                if (!raw) return '';
                const digits = raw.replace(/\D/g, '');
                return (raw.startsWith('+') ? '' : '+') + digits;
              },
            },
          ],
        },
        {
          colsPer: 1,
          cols: [
            {
              key: 'bio',
              label: 'Biografia',
              placeholder: 'Conte um pouco sobre você (máx. 240).',
              type: 'text',
              iconLeft: 'pi pi-info-circle',
              validate: (v) => toStr(v).length <= 240,
              error: 'Máximo de 240 caracteres.',
            },
          ],
        },
      ],
    },
  ],
};
