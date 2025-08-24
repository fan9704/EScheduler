<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">編輯任務</h1>
        <p class="text-body-2 text-medium-emphasis">修改排程任務配置</p>
      </v-col>
    </v-row>
    
    <TaskForm
      v-if="currentTask"
      :initial-data="currentTask"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
    
    <v-card v-else-if="loading" class="pa-8">
      <div class="text-center">
        <v-progress-circular indeterminate />
        <div class="mt-2">載入中...</div>
      </div>
    </v-card>
    
    <v-card v-else class="pa-8">
      <div class="text-center">
        <v-icon size="64" color="error">mdi-alert-circle-outline</v-icon>
        <div class="text-h6 mt-2">任務不存在</div>
        <v-btn class="mt-4" to="/tasks">返回任務列表</v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSchedulerStore } from '@/stores/scheduler'
import TaskForm from '@/components/scheduler/TaskForm.vue'
import type { ScheduledTaskUpdate } from '@/models/scheduler'

const route = useRoute()
const router = useRouter()
const schedulerStore = useSchedulerStore()

const { currentTask, loading } = schedulerStore

const taskId = Number(route.params.id)

const handleSubmit = async (taskData: ScheduledTaskUpdate) => {
  try {
    await schedulerStore.updateTask(taskId, taskData)
    router.push('/tasks')
  } catch (error) {
    console.error('更新任務失敗:', error)
  }
}

const handleCancel = () => {
  router.push('/tasks')
}

onMounted(() => {
  if (taskId) {
    schedulerStore.fetchTask(taskId)
  }
})
</script>