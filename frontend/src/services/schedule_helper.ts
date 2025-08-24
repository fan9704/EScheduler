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
    return apiService.post<ScheduleExpressionResponse>(`${this.basePath}/rate`, request)
  }

  async generateCronExpression(request: CronExpressionRequest): Promise<ScheduleExpressionResponse> {
    return apiService.post<ScheduleExpressionResponse>(`${this.basePath}/cron`, request)
  }

  async generateQuickSchedule(request: QuickScheduleRequest): Promise<ScheduleExpressionResponse> {
    return apiService.post<ScheduleExpressionResponse>(`${this.basePath}/quick`, request)
  }

  async validateExpression(request: ScheduleValidationRequest): Promise<ScheduleValidationResponse> {
    return apiService.post<ScheduleValidationResponse>(`${this.basePath}/validate`, request)
  }

  async getTemplates(): Promise<ScheduleTemplateResponse[]> {
    return apiService.get<ScheduleTemplateResponse[]>(`${this.basePath}/templates`)
  }

  async getCronHelp(): Promise<CronHelpResponse[]> {
    return apiService.get<CronHelpResponse[]>(`${this.basePath}/cron-help`)
  }
}

export const scheduleHelperService = new ScheduleHelperService()
export default scheduleHelperService