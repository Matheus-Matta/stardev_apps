export function buildListParams(schema, state) {
  const server = schema.server || {}
  const {
    limitParam = 'limit',
    offsetParam = 'offset',
    searchParam = 'search',
    orderingParam = 'order_by',
    startParam = 'start_date',
    endParam = 'end_date'
  } = server

  const {
    rows, first,
    sortField, sortOrder,
    filters, 
    extra = {} 
  } = state

  const params = {}

  params[limitParam]  = rows
  params[offsetParam] = first

  if (sortField) {
    params[orderingParam] = (sortOrder === -1 ? '-' : '') + sortField
  }

  const global = filters?.global?.value
  if (global != null && String(global).trim() !== '') {
    params[searchParam] = String(global).trim()
  }

  for (const col of schema.columns) {
    if (!col.filter) continue
    const fieldKey = col.filterField || col.field
    if (!fieldKey) continue

    const fModel = filters?.[fieldKey]
    if (!fModel) continue

    let fValue = null

    if (Array.isArray(fModel?.constraints)) {
      fValue = fModel.constraints?.[0]?.value
    } else {
      fValue = fModel.value
    }
    if (fValue == null || fValue === '') continue
    const serverCfg = col.filter.server || { param: fieldKey, op: 'eq' }
    let paramName = serverCfg.param || fieldKey
    let value = fValue
    if (col.filter.ui === 'multiselect') {
      const map = serverCfg.map || ((items) => items)
      value = map(Array.isArray(fValue) ? fValue : [fValue])
      value = Array.isArray(value) ? value.join(',') : value
    } else if (col.filter.ui === 'range') {
      value = Array.isArray(fValue) ? fValue.join(',') : String(fValue)
    } else if (col.type === 'date' && fValue) {
      try {
        const d = new Date(fValue)
        value = d.toISOString()
      } catch (e) { /* noop */ }
    }

    params[paramName] = value
  }
  if (extra?.[startParam]) params[startParam] = extra[startParam]
  if (extra?.[endParam])   params[endParam]   = extra[endParam]

  return params
}
