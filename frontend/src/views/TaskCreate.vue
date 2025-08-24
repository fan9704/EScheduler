<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">創建任務</h1>
        <p class="text-body-2 text-medium-emphasis">創建新的排程任務</p>
      </v-col>
    </v-row>
    
    <TaskForm @submit="handleSubmit" @cancel="handleCancel" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSchedulerStore } from '@/stores/scheduler'
import TaskForm from '@/components/scheduler/TaskForm.vue'
import type { ScheduledTaskCreate } from '@/models/scheduler'

const router = useRouter()
const schedulerStore = useSchedulerStore()

const handleSubmit = async (taskData: ScheduledTaskCreate) => {
  try {
    await schedulerStore.createTask(taskData)
    router.push('/tasks')
  } catch (error) {
    console.error('創建任務失敗:', error)
  }
}

const handleCancel = () => {
  router.push('/tasks')
}
</script>