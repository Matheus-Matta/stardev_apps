// src/composables/useFormValidation.js
import { reactive } from "vue";
import { isEmpty, isObj, mustValidate, getErrorText } from "./formHelpers";

export function useFormValidation() {
  const state = reactive({
    touched: {},
  });

  /**
   * Marca campo como tocado
   */
  function touch(fieldKey) {
    state.touched[fieldKey] = true;
  }

  /**
   * Verifica se campo está inválido
   */
  function isFieldInvalid(field, modelValue) {
    const value = modelValue[field.key];
    
    if (!mustValidate(field, value)) return false;
    
    if (field?.required && isEmpty(value)) return true;
    
    const val = isObj(value) && "value" in value ? value.value : value;
    
    if (typeof field?.validate === "function") {
      return !field.validate(val);
    }
    
    return false;
  }

  /**
   * Verifica se deve mostrar erro
   */
  function shouldShowError(field, modelValue) {
    return !!state.touched[field.key] && isFieldInvalid(field, modelValue);
  }

  /**
   * Obtém texto do erro
   */
  function getFieldErrorText(field, modelValue) {
    return getErrorText(field, modelValue[field.key]);
  }

  /**
   * Valida todos os campos de uma seção
   */
  function validateSection(section, modelValue) {
    let hasError = false;
    
    section?.rows?.forEach((row) =>
      row.cols?.forEach((field) => {
        touch(field.key);
        if (isFieldInvalid(field, modelValue)) {
          hasError = true;
        }
      })
    );
    
    return !hasError;
  }

  /**
   * Valida todas as seções
   */
  function validateAll(sections, modelValue) {
    let isValid = true;
    
    sections.forEach((section) => {
      if (!validateSection(section, modelValue)) {
        isValid = false;
      }
    });
    
    return isValid;
  }

  /**
   * Limpa estado de validação
   */
  function reset() {
    Object.keys(state.touched).forEach(key => {
      delete state.touched[key];
    });
  }

  return {
    state,
    touch,
    isFieldInvalid,
    shouldShowError,
    getFieldErrorText,
    validateSection,
    validateAll,
    reset,
  };
}