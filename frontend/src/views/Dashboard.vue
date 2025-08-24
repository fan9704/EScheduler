<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">儀表板</h1>
        <p class="text-body-2 text-medium-emphasis">排程任務系統概覽</p>
      </v-col>
    </v-row>
    
    <!-- 統計卡片 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-icon size="40" color="primary" class="mr-3">
              mdi-clock-outline
            </v-icon>
            <div>
              <div class="text-h5 font-weight-bold">
                {{ stats?.total_tasks || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">
                總任務數
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-icon size="40" color="success" class="mr-3">
              mdi-check-circle-outline
            </v-icon>
            <div>
              <div class="text-h5 font-weight-bold">
                {{ stats?.enabled_tasks || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">
                啟用任務
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-icon size="40" color="warning" class="mr-3">
              mdi-pause-circle-outline
            </v-icon>
            <div>
              <div class="text-h5 font-weight-bold">
                {{ stats?.disabled_tasks || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">
                禁用任務
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-icon size="40" color="info" class="mr-3">
              mdi-play-circle-outline
            </v-icon>
            <div>
              <div class="text-h5 font-weight-bold">
                {{ stats?.total_executions_today || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">
                今日執行
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- 最近任務 -->
    <v-row>
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <span>最近任務</span>
            <v-btn
              variant="text"
              size="small"
              to="/tasks"
            >
              查看全部
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-list v-if="recentTasks.length > 0">
              <v-list-item
                v-for="task in recentTasks"
                :key="task.id"
                :to="`/tasks/${task.id}/edit`"
              >
                <template #prepend>
                  <v-avatar size="32" :color="getStateColor(task.state)">
                    <v-icon size="16" color="white">
                      {{ getStateIcon(task.state) }}
                    </v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>{{ task.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ task.description || '無描述' }}
                </v-list-item-subtitle>
                
                <template #append>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatDateTime(task.updated_at) }}
                  </div>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">
                mdi-clock-outline
              </v-icon>
              <div class="text-h6 mt-2 text-medium-emphasis">
                暫無任務
              </div>
              <v-btn
                color="primary"
                class="mt-4"
                to="/tasks/create"
              >
                創建第一個任務
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>快速操作</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item to="/tasks/create">
                <template #prepend>
                  <v-icon>mdi-plus-circle-outline</v-icon>
                </template>
                <v-list-item-title>創建新任務</v-list-item-title>
              </v-list-item>
              
              <v-list-item to="/schedule-helper">
                <template #prepend>
                  <v-icon>mdi-help-circle-outline</v-icon>
                </template>
                <v-list-item-title>排程助手</v-list-item-title>
              </v-list-item>
              
              <v-list-item @click="refreshData">
                <template #prepend>
                  <v-icon>mdi-refresh</v-icon>
                </template>
                <v-list-item-title>刷新數據</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSchedulerStore } from '@/stores/scheduler'
import { TaskState } from '@/models/scheduler'
import dayjs from 'dayjs'

const schedulerStore = useSchedulerStore()

const { tasks, stats, loading } = schedulerStore

const recentTasks = computed(() => 
  tasks.slice(0, 5).sort((a, b) => 
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )
)

const getStateColor = (state: string) => {
  switch (state) {
    case TaskState.ENABLED:
      return 'success'
    case TaskState.DISABLED:
      return 'error'
    case TaskState.PAUSED:
      return 'warning'
    default:
      return 'grey'
  }
}

const getStateIcon = (state: string) => {
  switch (state) {
    case TaskState.ENABLED:
      return 'mdi-check'
    case TaskState.DISABLED:
      return 'mdi-close'
    case TaskState.PAUSED:
      return 'mdi-pause'
    default:
      return 'mdi-help'
  }
}

const formatDateTime = (dateTime: string) => {
  return dayjs(dateTime).format('MM-DD HH:mm')
}

const refreshData = async () => {
  await Promise.all([
    schedulerStore.fetchTasks(),
    schedulerStore.fetchStats(),
  ])
}

onMounted(() => {
  refreshData()
})
</script>