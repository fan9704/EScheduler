import { defineStore } from 'pinia';
import { ref } from 'vue';

import type {
  RateExpressionRequest,
  CronExpressionRequest,
  QuickScheduleRequest,
  ScheduleExpressionResponse,
  ScheduleValidationRequest,
  ScheduleValidationResponse,
  ScheduleTemplateResponse,
  CronHelpResponse,
} from '@/models/schedule_helper';
import { scheduleHelperService } from '@/services/schedule_helper';

export const useScheduleHelperStore = defineStore('scheduleHelper', () => {
  // State - 確保初始化為正確的類型
  const templates = ref<ScheduleTemplateResponse[]>([]);
  const cronHelp = ref<CronHelpResponse[]>([]);
  const currentExpression = ref<ScheduleExpressionResponse | null>(null);
  const validationResult = ref<ScheduleValidationResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  const generateRateExpression = async (request: RateExpressionRequest) => {
    try {
      loading.value = true;
      error.value = null;
      console.log('Store: 發送 Rate 請求:', request);

      const response = await scheduleHelperService.generateRateExpression(request);
      console.log('Store: 收到 Rate 回應:', response);

      // 確保設置當前表達式
      currentExpression.value = response;
      console.log('Store: currentExpression 已設置:', currentExpression.value);

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '生成 Rate 表達式失敗';
      error.value = errorMessage;
      console.error('Store: 生成 Rate 表達式失敗:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const generateCronExpression = async (request: CronExpressionRequest) => {
    try {
      loading.value = true;
      error.value = null;
      console.log('Store: 發送 Cron 請求:', request);

      const response = await scheduleHelperService.generateCronExpression(request);
      console.log('Store: 收到 Cron 回應:', response);

      // 確保設置當前表達式
      currentExpression.value = response;
      console.log('Store: currentExpression 已設置:', currentExpression.value);

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '生成 Cron 表達式失敗';
      error.value = errorMessage;
      console.error('Store: 生成 Cron 表達式失敗:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const generateQuickSchedule = async (request: QuickScheduleRequest) => {
    try {
      loading.value = true;
      error.value = null;
      console.log('Store: 發送快速排程請求:', request);

      const response = await scheduleHelperService.generateQuickSchedule(request);
      console.log('Store: 收到快速排程回應:', response);

      currentExpression.value = response;

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '生成快速排程失敗';
      error.value = errorMessage;
      console.error('Store: 生成快速排程失敗:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const validateExpression = async (request: ScheduleValidationRequest) => {
    try {
      loading.value = true;
      error.value = null;
      console.log('Store: 發送驗證請求:', request);

      const response = await scheduleHelperService.validateExpression(request);
      console.log('Store: 收到驗證回應:', response);

      validationResult.value = response;

      // 如果驗證成功，也設置為當前表達式
      if (response.valid && response.type && response.description) {
        currentExpression.value = {
          expression: request.expression,
          type: response.type,
          description: response.description,
          next_runs: response.next_runs || [],
        };
        console.log('Store: 驗證成功，currentExpression 已設置:', currentExpression.value);
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '驗證表達式失敗';
      error.value = errorMessage;
      console.error('Store: 驗證表達式失敗:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchTemplates = async () => {
    try {
      loading.value = true;
      error.value = null;
      templates.value = await scheduleHelperService.getTemplates();
      console.log('Store: 模板載入成功，數量:', templates.value.length);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取模板失敗';
      console.error('Store: 獲取模板失敗:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchCronHelp = async () => {
    try {
      loading.value = true;
      error.value = null;
      cronHelp.value = await scheduleHelperService.getCronHelp();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取 Cron 幫助失敗';
      console.error('Store: 獲取 Cron 幫助失敗:', err);
    } finally {
      loading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
    console.log('Store: 錯誤已清除');
  };

  const clearCurrentExpression = () => {
    currentExpression.value = null;
    console.log('Store: currentExpression 已清除');
  };

  const clearValidationResult = () => {
    validationResult.value = null;
    console.log('Store: validationResult 已清除');
  };

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
  };
});
