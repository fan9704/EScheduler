<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12" md="8">
        <h1 class="text-h4 font-weight-bold">排程任務</h1>
        <p class="text-body-2 text-medium-emphasis">管理和監控您的排程任務</p>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center justify-end">
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          to="/tasks/create"
          class="mr-2"
        >
          創建任務
        </v-btn>
        <v-btn
          icon="mdi-refresh"
          variant="outlined"
          @click="refreshTasks"
        />
      </v-col>
    </v-row>
    
    <!-- 搜索和篩選 -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchKeyword"
          prepend-inner-icon="mdi-magnify"
          label="搜索任務"
          variant="outlined"
          density="compact"
          clearable
          @keyup.enter="searchTasks"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="狀態篩選"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="typeFilter"
          :items="typeOptions"
          label="類型篩選"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
    </v-row>
    
    <!-- 任務列表 -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="filteredTasks"
        :loading="loading"
        item-value="id"
        class="elevation-0"
      >
        <template #item.state="{ item }">
          <v-chip
            :color="getStateColor(item.state)"
            size="small"
            variant="flat"
          >
            {{ getStateText(item.state) }}
          </v-chip>
        </template>
        
        <template #item.target_type="{ item }">
          <v-chip
            size="small"
            variant="outlined"
          >
            {{ item.target_type.toUpperCase() }}
          </v-chip>
        </template>
        
        <template #item.next_execution_time="{ item }">
          <span v-if="item.next_execution_time" class="text-caption">
            {{ formatDateTime(item.next_execution_time) }}
          </span>
          <span v-else class="text-caption text-medium-emphasis">-</span>
        </template>
        
        <template #item.actions="{ item }">
          <div class="d-flex gap-1">
            <v-btn
              icon="mdi-play"
              size="small"
              variant="text"
              color="success"
              @click="triggerTask(item.id)"
            />
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="editTask(item.id)"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteTask(item.id)"
            />
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSchedulerStore } from '@/stores/scheduler'
import { TaskState } from '@/models/scheduler'
import dayjs from 'dayjs'

const router = useRouter()
const schedulerStore = useSchedulerStore()

const searchKeyword = ref('')
const statusFilter = ref('')
const typeFilter = ref('')

const { tasks, loading } = schedulerStore

const headers = [
  { title: '任務名稱', key: 'name', sortable: true },
  { title: '狀態', key: 'state', sortable: true },
  { title: '類型', key: 'target_type', sortable: true },
  { title: '排程表達式', key: 'schedule_expression', sortable: false },
  { title: '下次執行', key: 'next_execution_time', sortable: true },
  { title: '執行次數', key: 'execution_count', sortable: true },
  { title: '操作', key: 'actions', sortable: false, width: 120 },
]

const statusOptions = [
  { title: '啟用', value: TaskState.ENABLED },
  { title: '禁用', value: TaskState.DISABLED },
  { title: '暫停', value: TaskState.PAUSED },
]

const typeOptions = [
  { title: 'HTTP', value: 'http' },
  { title: 'Webhook', value: 'webhook' },
  { title: 'RabbitMQ', value: 'rabbitmq' },
  { title: 'Email', value: 'email' },
]

const filteredTasks = computed(() => {
  let result = tasks
  
  if (searchKeyword.value) {
    result = result.filter(task => 
      task.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchKeyword.value.toLowerCase()))
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(task => task.state === statusFilter.value)
  }
  
  if (typeFilter.value) {
    result = result.filter(task => task.target_type === typeFilter.value)
  }
  
  return result
})

const getStateColor = (state: string) => {
  switch (state) {
    case TaskState.ENABLED:
      return 'success'
    case TaskState.DISABLED:
      return 'error'
    case TaskState.PAUSED:
      return 'warning'
    default:
      return 'default'
  }
}

const getStateText = (state: string) => {
  switch (state) {
    case TaskState.ENABLED:
      return '啟用'
    case TaskState.DISABLED:
      return '禁用'
    case TaskState.PAUSED:
      return '暫停'
    default:
      return state
  }
}

const formatDateTime = (dateTime: string) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

const refreshTasks = async () => {
  await schedulerStore.fetchTasks()
}

const searchTasks = async () => {
  if (searchKeyword.value.trim()) {
    await schedulerStore.searchTasks(searchKeyword.value.trim())
  } else {
    await schedulerStore.fetchTasks()
  }
}

const triggerTask = async (id: number) => {
  try {
    await schedulerStore.triggerTask(id)
    // 顯示成功消息
  } catch (error) {
    // 顯示錯誤消息
  }
}

const editTask = (id: number) => {
  router.push(`/tasks/${id}/edit`)
}

const deleteTask = async (id: number) => {
  // 顯示確認對話框
  if (confirm('確定要刪除這個任務嗎？')) {
    try {
      await schedulerStore.deleteTask(id)
      // 顯示成功消息
    } catch (error) {
      // 顯示錯誤消息
    }
  }
}

onMounted(() => {
  schedulerStore.fetchTasks()
})
</script>