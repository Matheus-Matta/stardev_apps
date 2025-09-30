import { createI18n } from 'vue-i18n';

export const i18n = createI18n({
  legacy: false,
  locale: 'pt-BR',
  fallbackLocale: 'pt-BR',
  messages: {}, // será preenchido dinamicamente
});

// Import dinâmico de todos os JSONs de locale (lazy)
const modules = import.meta.glob('../locales/*/*.json'); // ex.: ../locales/pt-BR/forms.json

const loaded = new Set();

async function loadMessages(locale) {
  if (loaded.has(locale)) return;

  const key = (name) => `../locales/${locale}/${name}.json`;
  const importActions = modules[key('actions')];
  const importCommon  = modules[key('common')];
  const importForms   = modules[key('forms')];

  if (!importActions || !importCommon || !importForms) {
    console.warn(`[i18n] Arquivos faltando para ${locale}:`, {
      actions: !!importActions, common: !!importCommon, forms: !!importForms,
    });
  }

  const [actions, common, forms] = await Promise.all([
    importActions ? importActions() : Promise.resolve({ default: {} }),
    importCommon  ? importCommon()  : Promise.resolve({ default: {} }),
    importForms   ? importForms()   : Promise.resolve({ default: {} }),
  ]);

  i18n.global.setLocaleMessage(locale, {
    actions: actions.default || {},
    common:  common.default  || {},
    forms:   forms.default   || {},
  });

  loaded.add(locale);
}

export async function setLocale(locale) {
  await loadMessages(locale);
  i18n.global.locale.value = locale;
  localStorage.setItem('locale', locale);
}

// bootstrap inicial
const saved   = localStorage.getItem('locale');
const browser = navigator.language || 'en';
const initial = saved || (browser.toLowerCase().startsWith('pt') ? 'pt-BR' : 'en');

export const i18nReady = setLocale(initial);
