import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ScheduledTaskResponse,
  ScheduledTaskCreate,
  ScheduledTaskUpdate,
  SchedulerStatsResponse,
  TaskStateUpdateRequest,
} from '@/models/scheduler'
import { schedulerService } from '@/services/scheduler'

export const useSchedulerStore = defineStore('scheduler', () => {
  // State
  const tasks = ref<ScheduledTaskResponse[]>([])
  const currentTask = ref<ScheduledTaskResponse | null>(null)
  const stats = ref<SchedulerStatsResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const enabledTasks = computed(() => 
    tasks.value.filter(task => task.state === 'ENABLED')
  )
  
  const disabledTasks = computed(() => 
    tasks.value.filter(task => task.state === 'DISABLED')
  )

  const pausedTasks = computed(() => 
    tasks.value.filter(task => task.state === 'PAUSED')
  )

  // Actions
  const fetchTasks = async () => {
    try {
      loading.value = true
      error.value = null
      tasks.value = await schedulerService.getTasks()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取任務列表失敗'
      console.error('Failed to fetch tasks:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchTask = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      currentTask.value = await schedulerService.getTask(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取任務詳情失敗'
      console.error('Failed to fetch task:', err)
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData: ScheduledTaskCreate) => {
    try {
      loading.value = true
      error.value = null
      const newTask = await schedulerService.createTask(taskData)
      tasks.value.push(newTask)
      return newTask
    } catch (err) {
      error.value = err instanceof Error ? err.message : '創建任務失敗'
      console.error('Failed to create task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTask = async (id: number, taskData: ScheduledTaskUpdate) => {
    try {
      loading.value = true
      error.value = null
      const updatedTask = await schedulerService.updateTask(id, taskData)
      const index = tasks.value.findIndex(task => task.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      if (currentTask.value?.id === id) {
        currentTask.value = updatedTask
      }
      return updatedTask
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新任務失敗'
      console.error('Failed to update task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      await schedulerService.deleteTask(id)
      tasks.value = tasks.value.filter(task => task.id !== id)
      if (currentTask.value?.id === id) {
        currentTask.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刪除任務失敗'
      console.error('Failed to delete task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTaskState = async (id: number, stateData: TaskStateUpdateRequest) => {
    try {
      loading.value = true
      error.value = null
      await schedulerService.updateTaskState(id, stateData)
      const task = tasks.value.find(t => t.id === id)
      if (task) {
        task.state = stateData.state
      }
      if (currentTask.value?.id === id) {
        currentTask.value.state = stateData.state
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新任務狀態失敗'
      console.error('Failed to update task state:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const triggerTask = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      await schedulerService.triggerTask(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '觸發任務失敗'
      console.error('Failed to trigger task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchStats = async () => {
    try {
      loading.value = true
      error.value = null
      stats.value = await schedulerService.getStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取統計信息失敗'
      console.error('Failed to fetch stats:', err)
    } finally {
      loading.value = false
    }
  }

  const searchTasks = async (keyword: string) => {
    try {
      loading.value = true
      error.value = null
      tasks.value = await schedulerService.searchTasks(keyword)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '搜索任務失敗'
      console.error('Failed to search tasks:', err)
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    tasks,
    currentTask,
    stats,
    loading,
    error,
    // Getters
    enabledTasks,
    disabledTasks,
    pausedTasks,
    // Actions
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
    updateTaskState,
    triggerTask,
    fetchStats,
    searchTasks,
    clearError,
  }
})