import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  RateExpressionRequest,
  CronExpressionRequest,
  QuickScheduleRequest,
  ScheduleExpressionResponse,
  ScheduleValidationRequest,
  ScheduleValidationResponse,
  ScheduleTemplateResponse,
  CronHelpResponse,
} from '@/models/schedule_helper'
import { scheduleHelperService } from '@/services/schedule_helper'

export const useScheduleHelperStore = defineStore('scheduleHelper', () => {
  // State
  const templates = ref<ScheduleTemplateResponse[]>([])
  const cronHelp = ref<CronHelpResponse[]>([])
  const currentExpression = ref<ScheduleExpressionResponse | null>(null)
  const validationResult = ref<ScheduleValidationResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const generateRateExpression = async (request: RateExpressionRequest) => {
    try {
      loading.value = true
      error.value = null
      currentExpression.value = await scheduleHelperService.generateRateExpression(request)
      return currentExpression.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成 Rate 表達式失敗'
      console.error('Failed to generate rate expression:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateCronExpression = async (request: CronExpressionRequest) => {
    try {
      loading.value = true
      error.value = null
      currentExpression.value = await scheduleHelperService.generateCronExpression(request)
      return currentExpression.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成 Cron 表達式失敗'
      console.error('Failed to generate cron expression:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateQuickSchedule = async (request: QuickScheduleRequest) => {
    try {
      loading.value = true
      error.value = null
      currentExpression.value = await scheduleHelperService.generateQuickSchedule(request)
      return currentExpression.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : '生成快速排程失敗'
      console.error('Failed to generate quick schedule:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const validateExpression = async (request: ScheduleValidationRequest) => {
    try {
      loading.value = true
      error.value = null
      validationResult.value = await scheduleHelperService.validateExpression(request)
      return validationResult.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : '驗證表達式失敗'
      console.error('Failed to validate expression:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTemplates = async () => {
    try {
      loading.value = true
      error.value = null
      templates.value = await scheduleHelperService.getTemplates()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取模板失敗'
      console.error('Failed to fetch templates:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchCronHelp = async () => {
    try {
      loading.value = true
      error.value = null
      cronHelp.value = await scheduleHelperService.getCronHelp()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取 Cron 幫助失敗'
      console.error('Failed to fetch cron help:', err)
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentExpression = () => {
    currentExpression.value = null
  }

  const clearValidationResult = () => {
    validationResult.value = null
  }

  return {
    // State
    templates,
    cronHelp,
    currentExpression,
    validationResult,
    loading,
    error,
    // Actions
    generateRateExpression,
    generateCronExpression,
    generateQuickSchedule,
    validateExpression,
    fetchTemplates,
    fetchCronHelp,
    clearError,
    clearCurrentExpression,
    clearValidationResult,
  }
})