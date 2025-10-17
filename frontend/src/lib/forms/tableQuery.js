// lib/tableQuery.js

/**
 * Constrói os parâmetros de query para requisições de listagem
 * baseado no schema da tabela e nos parâmetros atuais
 * 
 * @param {Object} schema - Schema da tabela contendo configurações
 * @param {Object} params - Parâmetros atuais da tabela
 * @param {Number} params.rows - Número de linhas por página
 * @param {Number} params.first - Índice do primeiro item
 * @param {String} params.sortField - Campo de ordenação
 * @param {Number} params.sortOrder - Direção da ordenação (1 ou -1)
 * @param {Object} params.filters - Objeto de filtros
 * @param {Object} params.extra - Parâmetros extras personalizados
 * @returns {Object} Objeto com parâmetros formatados para a API
 */
export function buildListParams(schema, params) {
  const { rows, first, sortField, sortOrder, filters, extra } = params;
  
  // Objeto base de parâmetros
  const queryParams = {};

  // === PAGINAÇÃO ===
  if (schema.server?.paginationMode === 'offset') {
    // Modo offset/limit
    const limitKey = schema.server?.limitParam || 'limit';
    const offsetKey = schema.server?.offsetParam || 'offset';
    
    queryParams[limitKey] = rows;
    queryParams[offsetKey] = first;
  } else if (schema.server?.paginationMode === 'page') {
    // Modo page/per_page
    const pageKey = schema.server?.pageParam || 'page';
    const perPageKey = schema.server?.perPageParam || 'per_page';
    
    queryParams[pageKey] = Math.floor(first / rows) + 1;
    queryParams[perPageKey] = rows;
  } else {
    // Padrão: offset/limit
    queryParams.limit = rows;
    queryParams.offset = first;
  }

  // === ORDENAÇÃO ===
  if (sortField) {
    const sortKey = schema.server?.sortParam || 'sort';
    const orderKey = schema.server?.orderParam || 'order';

    if (schema.server?.sortMode === 'combined') {
      // Formato: sort=field:asc ou sort=-field
      const direction = sortOrder === 1 ? 'asc' : 'desc';
      const prefix = sortOrder === 1 ? '' : '-';
      
      if (schema.server?.sortFormat === 'prefix') {
        queryParams[sortKey] = `${prefix}${sortField}`;
      } else {
        queryParams[sortKey] = `${sortField}:${direction}`;
      }
    } else {
      // Formato separado: sort=field&order=asc
      queryParams[sortKey] = sortField;
      queryParams[orderKey] = sortOrder === 1 ? 'asc' : 'desc';
    }
  }

  // === FILTROS ===
  if (filters && typeof filters === 'object') {
    const filterParams = buildFilterParams(schema, filters);
    Object.assign(queryParams, filterParams);
  }

  // === PARÂMETROS EXTRAS ===
  if (extra && typeof extra === 'object') {
    Object.entries(extra).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        queryParams[key] = value;
      }
    });
  }

  return queryParams;
}

/**
 * Constrói parâmetros de filtro baseado nas constraints do PrimeVue
 * 
 * @param {Object} schema - Schema da tabela
 * @param {Object} filters - Objeto de filtros do PrimeVue
 * @returns {Object} Parâmetros de filtro formatados
 */
function buildFilterParams(schema, filters) {
  const filterParams = {};
  const filterMode = schema.server?.filterMode || 'default';

  Object.entries(filters).forEach(([key, filterMeta]) => {
    // Ignora filtro global ou valores vazios
    if (key === 'global' || !filterMeta) return;

    // Filtros com constraints (múltiplas condições)
    if (filterMeta.constraints && Array.isArray(filterMeta.constraints)) {
      filterMeta.constraints.forEach((constraint, index) => {
        if (!constraint.value && constraint.value !== 0) return;

        const paramName = index === 0 ? key : `${key}_${index}`;
        filterParams[paramName] = formatFilterValue(
          constraint.value,
          constraint.matchMode,
          filterMode
        );
      });
    }
    // Filtros simples (valor único)
    else if (filterMeta.value !== null && filterMeta.value !== undefined) {
      filterParams[key] = formatFilterValue(
        filterMeta.value,
        filterMeta.matchMode,
        filterMode
      );
    }
  });

  return filterParams;
}

/**
 * Formata o valor do filtro baseado no matchMode
 * 
 * @param {*} value - Valor a ser formatado
 * @param {String} matchMode - Modo de correspondência (CONTAINS, EQUALS, etc)
 * @param {String} filterMode - Modo de filtro do servidor
 * @returns {*} Valor formatado
 */
function formatFilterValue(value, matchMode, filterMode) {
  // Para arrays (IN, BETWEEN)
  if (Array.isArray(value)) {
    if (filterMode === 'json') {
      return JSON.stringify(value);
    }
    return value.join(',');
  }

  // Para strings com CONTAINS, adiciona wildcards se necessário
  if (matchMode === 'contains' && typeof value === 'string') {
    if (filterMode === 'sql-like') {
      return `%${value}%`;
    }
    if (filterMode === 'wildcard') {
      return `*${value}*`;
    }
  }

  // Para STARTS_WITH
  if (matchMode === 'startsWith' && typeof value === 'string') {
    if (filterMode === 'sql-like') {
      return `${value}%`;
    }
    if (filterMode === 'wildcard') {
      return `${value}*`;
    }
  }

  // Para ENDS_WITH
  if (matchMode === 'endsWith' && typeof value === 'string') {
    if (filterMode === 'sql-like') {
      return `%${value}`;
    }
    if (filterMode === 'wildcard') {
      return `*${value}`;
    }
  }

  // Retorna valor sem modificação
  return value;
}

/**
 * Parseia a resposta do servidor para o formato esperado pela tabela
 * 
 * @param {Object} response - Resposta da API
 * @param {Object} schema - Schema da tabela
 * @returns {Object} { items: Array, count: Number }
 */
export function parseListResponse(response, schema) {
  // Se a resposta já está no formato correto
  if (response?.items && typeof response?.count === 'number') {
    return response;
  }

  // Tenta extrair baseado no schema
  const dataKey = schema.server?.dataKey || 'data';
  const countKey = schema.server?.countKey || 'total';

  let items = [];
  let count = 0;

  // Se a resposta for um array direto
  if (Array.isArray(response)) {
    items = response;
    count = response.length;
  }
  // Se a resposta tiver estrutura aninhada
  else if (response) {
    items = response[dataKey] || response.items || response.results || [];
    count = response[countKey] || response.count || response.total || items.length;
  }

  return { items, count };
}

/**
 * Constrói URL com query parameters
 * 
 * @param {String} baseUrl - URL base
 * @param {Object} params - Parâmetros de query
 * @returns {String} URL completa com query string
 */
export function buildQueryUrl(baseUrl, params) {
  if (!params || Object.keys(params).length === 0) {
    return baseUrl;
  }

  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => {
      const encodedKey = encodeURIComponent(key);
      const encodedValue = encodeURIComponent(String(value));
      return `${encodedKey}=${encodedValue}`;
    })
    .join('&');

  return queryString ? `${baseUrl}?${queryString}` : baseUrl;
}

/**
 * Valida se os parâmetros de paginação são válidos
 * 
 * @param {Object} params - Parâmetros a validar
 * @returns {Boolean} true se válidos
 */
export function validatePaginationParams(params) {
  const { rows, first } = params;

  if (typeof rows !== 'number' || rows <= 0) {
    console.warn('Invalid rows parameter:', rows);
    return false;
  }

  if (typeof first !== 'number' || first < 0) {
    console.warn('Invalid first parameter:', first);
    return false;
  }

  return true;
}

/**
 * Calcula metadados de paginação
 * 
 * @param {Number} total - Total de registros
 * @param {Number} first - Índice do primeiro item
 * @param {Number} rows - Itens por página
 * @returns {Object} Metadados calculados
 */
export function calculatePaginationMeta(total, first, rows) {
  const totalPages = Math.max(1, Math.ceil(total / rows));
  const currentPage = Math.floor(first / rows) + 1;
  const hasNext = currentPage < totalPages;
  const hasPrev = currentPage > 1;
  const startItem = total ? first + 1 : 0;
  const endItem = Math.min(first + rows, total);

  return {
    totalPages,
    currentPage,
    hasNext,
    hasPrev,
    startItem,
    endItem,
    total
  };
}

/**
 * Exemplo de schema.server para referência:
 * 
 * schema.server = {
 *   paginationMode: 'offset',  // 'offset' | 'page'
 *   limitParam: 'limit',
 *   offsetParam: 'offset',
 *   pageParam: 'page',
 *   perPageParam: 'per_page',
 *   
 *   sortMode: 'combined',      // 'combined' | 'separate'
 *   sortFormat: 'prefix',      // 'prefix' | 'colon'
 *   sortParam: 'sort',
 *   orderParam: 'order',
 *   
 *   filterMode: 'default',     // 'default' | 'sql-like' | 'wildcard' | 'json'
 *   
 *   searchParam: 'search',
 *   
 *   startParam: 'start_date',
 *   endParam: 'end_date',
 *   
 *   dataKey: 'data',
 *   countKey: 'total'
 * }
 */