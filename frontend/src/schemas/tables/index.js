import { CustomertableSchemas } from "./customers"
import { businessTableSchema } from "./businesses"
import { businesstypeTableSchema } from "./businesstypes"

export const tableSchemas = {
    customer: CustomertableSchemas,
    business: businessTableSchema,
    businesstype: businesstypeTableSchema
}


export function getTableSchema(namePlural) {
  const key = (namePlural || '').toLowerCase()
  const s = tableSchemas[key]
  if (!s) throw new Error(`TableSchema não encontrado: ${namePlural}`)
  return s
}
