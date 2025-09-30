import { CustomerstableSchemas } from "./customers"
import { businessestableSchemas } from "./businesses"

export const tableSchemas = {
    customers: CustomerstableSchemas,
    businesses: businessestableSchemas
}


export function getTableSchema(namePlural) {
  const key = (namePlural || '').toLowerCase()
  const s = tableSchemas[key]
  if (!s) throw new Error(`TableSchema não encontrado: ${namePlural}`)
  return s
}
