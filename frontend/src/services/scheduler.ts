import type {
  ScheduledTaskResponse,
  ScheduledTaskCreate,
  ScheduledTaskUpdate,
  SchedulerStatsResponse,
  TaskStateUpdateRequest,
} from '@/models/scheduler'
import { apiService } from './api'

class SchedulerService {
  private readonly basePath = '/scheduler'

  async getTasks(): Promise<ScheduledTaskResponse[]> {
    return apiService.get<ScheduledTaskResponse[]>(`${this.basePath}/`)
  }

  async getTask(id: number): Promise<ScheduledTaskResponse> {
    return apiService.get<ScheduledTaskResponse>(`${this.basePath}/${id}`)
  }

  async createTask(taskData: ScheduledTaskCreate): Promise<ScheduledTaskResponse> {
    return apiService.post<ScheduledTaskResponse>(`${this.basePath}/`, taskData)
  }

  async updateTask(id: number, taskData: ScheduledTaskUpdate): Promise<ScheduledTaskResponse> {
    return apiService.put<ScheduledTaskResponse>(`${this.basePath}/${id}`, taskData)
  }

  async deleteTask(id: number): Promise<void> {
    return apiService.delete<void>(`${this.basePath}/${id}`)
  }

  async updateTaskState(id: number, stateData: TaskStateUpdateRequest): Promise<void> {
    return apiService.put<void>(`${this.basePath}/${id}/state`, stateData)
  }

  async triggerTask(id: number): Promise<void> {
    return apiService.post<void>(`${this.basePath}/${id}/trigger`)
  }

  async getStats(): Promise<SchedulerStatsResponse> {
    return apiService.get<SchedulerStatsResponse>(`${this.basePath}/stats`)
  }

  async searchTasks(keyword: string): Promise<ScheduledTaskResponse[]> {
    return apiService.get<ScheduledTaskResponse[]>(`${this.basePath}/search`, { keyword })
  }
}

export const schedulerService = new SchedulerService()
export default schedulerService