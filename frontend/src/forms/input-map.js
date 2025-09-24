// src/forms/input-map.js
export function inputValue(name) {
  const MAP = {
    display_name: {
      label: "Nome de Exibição",
      placeholder: "Ex.: João da Silva",
      mask: null,
      icon: "badge",
      error: "Informe um nome de exibição válido (2 a 80 caracteres).",
      validate: (v) => {
        const s = String(v ?? "").trim();
        return s.length >= 2 && s.length <= 80;
      },
    },
    username: {
      label: "Nome de Usuário",
      placeholder: "Ex.: joao.silva",
      mask: null,
      icon: "account_circle",
      error:
        "Usuário inválido. Use 3–30 caracteres (letras, números, ponto ou _).",
      validate: (v) => /^[a-z0-9_.]{3,30}$/i.test(String(v ?? "").trim()),
      normalizeOnInput: (v) =>
        String(v ?? "")
          .trim()
          .toLowerCase()
          .replace(/\s+/g, "")
          .replace(/[^a-z0-9_.]/g, ""),
    },
    first_name: {
      label: "Nome",
      placeholder: "Seu nome",
      mask: null,
      icon: "person",
      error: "Informe um nome válido (mínimo 2 caracteres).",
      validate: (v) => String(v ?? "").trim().length >= 2,
    },
    last_name: {
      label: "Sobrenome",
      placeholder: "Seu sobrenome",
      mask: null,
      icon: "person",
      error: "Informe um sobrenome válido (mínimo 2 caracteres).",
      validate: (v) => String(v ?? "").trim().length >= 2,
    },
    email: {
      label: "E-mail",
      placeholder: "email@exemplo.com",
      mask: null,
      icon: "email",
      error: "E-mail inválido.",
      validate: (v) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v ?? "").trim()),
      normalizeOnInput: (v) => String(v ?? "").trim().toLowerCase(),
    },
    phone: {
        label: "Telefone",
        placeholder: "+5521912345678",
        mask: "+559999999999[9][9][9][9]",
        icon: "phone",
        error: "Número inválido. Use o formato: +5521912345678",
        validate: (v) => /^\+55\d{10,14}$/.test(String(v ?? "").trim()),
        normalizeOnSave: (v) => {
            const raw = String(v ?? "").trim();
            if (!raw) return "";
            if (raw.startsWith("+")) return raw;
            return `+${raw.replace(/\D/g, "")}`;
        },
    },
    bio: {
      label: "Biografia",
      placeholder: "Breve descrição",
      mask: null,
      icon: "info",
      error: "Tamanho máximo: 240 caracteres.",
      validate: (v) => String(v ?? "").length <= 240,
    },
    legal_name: {
      label: "Razão Social",
      placeholder: "stardev LTDA",
      mask: null,
      icon: "business",
      error: "Informe a razão social (2 a 120 caracteres).",
      validate: (v) => {
        const s = String(v ?? "").trim();
        return s.length >= 2 && s.length <= 120;
      },
    },
    slug: {
      label: "Slug",
      placeholder: "star",
      mask: null,
      icon: "tag",
      error: "Slug inválido. Use 3–30 caracteres (letras minúsculas, números ou hífen).",
      validate: (v) => /^[a-z0-9-]{3,30}$/.test(String(v ?? "").trim()),
      normalizeOnInput: (v) =>
        String(v ?? "")
          .toLowerCase()
          .trim()
          .replace(/\s+/g, "-")
          .replace(/[^a-z0-9-]/g, "")
          .replace(/--+/g, "-"),
    },
    time_zone: {
      label: "Fuso Horário",
      placeholder: "America/Sao_Paulo",
      mask: null,
      icon: "schedule",
      error: "Fuso horário inválido. Ex.: America/Sao_Paulo",
      validate: (v) => /^[A-Za-z]+(?:[_-][A-Za-z]+)*\/[A-Za-z]+(?:[_-][A-Za-z]+)*$/.test(String(v ?? "").trim()),
    },
  };

  return (
    MAP[name] || {
      label: name,
      placeholder: "",
      mask: null,
      icon: "",
      error: "Valor inválido.",
      validate: () => true,
    }
  );
}
