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
import { apiService } from './api'

class ScheduleHelperService {
  private readonly basePath = '/schedule-helper'

  async generateRateExpression(request: RateExpressionRequest): Promise<ScheduleExpressionResponse> {
    console.log('API 調用 - 生成 Rate 表達式:', request)
    const response = await apiService.post<ScheduleExpressionResponse>(`${this.basePath}/rate`, request)
    console.log('API 回應 - Rate 表達式:', response)
    return response
  }

  async generateCronExpression(request: CronExpressionRequest): Promise<ScheduleExpressionResponse> {
    console.log('API 調用 - 生成 Cron 表達式:', request)
    const response = await apiService.post<ScheduleExpressionResponse>(`${this.basePath}/cron`, request)
    console.log('API 回應 - Cron 表達式:', response)
    return response
  }

  async generateQuickSchedule(request: QuickScheduleRequest): Promise<ScheduleExpressionResponse> {
    console.log('API 調用 - 生成快速排程:', request)
    const response = await apiService.post<ScheduleExpressionResponse>(`${this.basePath}/quick`, request)
    console.log('API 回應 - 快速排程:', response)
    return response
  }

  async validateExpression(request: ScheduleValidationRequest): Promise<ScheduleValidationResponse> {
    console.log('API 調用 - 驗證表達式:', request)
    const response = await apiService.post<ScheduleValidationResponse>(`${this.basePath}/validate`, request)
    console.log('API 回應 - 驗證結果:', response)
    return response
  }

  async getTemplates(): Promise<ScheduleTemplateResponse[]> {
    const response = await apiService.get<ScheduleTemplateResponse[]>(`${this.basePath}/templates`)
    console.log('API 回應 - 模板列表:', response)
    return response
  }

  async getCronHelp(): Promise<CronHelpResponse[]> {
    const response = await apiService.get<CronHelpResponse[]>(`${this.basePath}/cron-help`)
    console.log('API 回應 - Cron 幫助:', response)
    return response
  }
}

export const scheduleHelperService = new ScheduleHelperService()
export default scheduleHelperService