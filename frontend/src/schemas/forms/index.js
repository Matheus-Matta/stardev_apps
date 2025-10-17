import { businessSchema } from "./business"
import { businessTypeSchema } from "./businessType"
  
export const createSchemas = {
    business: businessSchema,
    businesstype: businessTypeSchema
}

export function getCreateSchema(modelNome) {
  const key = (modelNome || '').toLowerCase()
  const s = createSchemas[key]
  if (!s) throw new Error(`CreateSchema não encontrado: ${modelNome}`)
  return s
}
