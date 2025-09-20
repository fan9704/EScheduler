<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h5">Email 任務管理</span>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="router.push({ name: 'TaskCreate', query: { type: 'email' } })"
            >
              新增 Email 任務
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜尋和篩選 -->
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchQuery"
                  label="搜尋任務"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="statusFilter"
                  label="狀態篩選"
                  :items="statusOptions"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="templateFilter"
                  label="模板篩選"
                  :items="templateOptions"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-btn
                  color="secondary"
                  variant="outlined"
                  @click="refreshTasks"
                  :loading="loading"
                  block
                >
                  重新整理
                </v-btn>
              </v-col>
            </v-row>

            <!-- 任務列表 -->
            <v-data-table
              :headers="headers"
              :items="filteredTasks"
              :loading="loading"
              item-value="id"
              class="elevation-1"
            >
              <!-- 狀態欄位 -->
              <template #item.state="{ item }">
                <v-chip
                  :color="getStatusColor(item.state)"
                  size="small"
                  variant="flat"
                >
                  {{ getStatusText(item.state) }}
                </v-chip>
              </template>

              <!-- 模板欄位 -->
              <template #item.template="{ item }">
                <v-chip
                  v-if="item.use_template && item.template_name"
                  color="info"
                  size="small"
                  variant="outlined"
                >
                  {{ item.template_name }}
                </v-chip>
                <span v-else class="text-grey">直接內容</span>
              </template>

              <!-- 收件人欄位 -->
              <template #item.recipients="{ item }">
                <v-tooltip v-if="item.recipients && item.recipients.length > 0">
                  <template #activator="{ props }">
                    <span v-bind="props">
                      {{ item.recipients[0] }}
                      <span v-if="item.recipients.length > 1" class="text-grey">
                        +{{ item.recipients.length - 1 }}
                      </span>
                    </span>
                  </template>
                  <div>
                    <div v-for="recipient in item.recipients" :key="recipient">
                      {{ recipient }}
                    </div>
                  </div>
                </v-tooltip>
                <span v-else class="text-grey">無收件人</span>
              </template>

              <!-- 下次執行時間 -->
              <template #item.next_execution_time="{ item }">
                <span v-if="item.next_execution_time">
                  {{ formatDateTime(item.next_execution_time) }}
                </span>
                <span v-else class="text-grey">-</span>
              </template>

              <!-- 執行次數 -->
              <template #item.execution_count="{ item }">
                <v-chip
                  :color="item.execution_count > 0 ? 'success' : 'grey'"
                  size="small"
                  variant="outlined"
                >
                  {{ item.execution_count }}
                </v-chip>
              </template>

              <!-- 操作欄位 -->
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-play"
                  size="small"
                  color="success"
                  variant="text"
                  @click="executeTask(item.id)"
                  :loading="executingTasks.has(item.id)"
                  title="立即執行"
                />
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  color="primary"
                  variant="text"
                  @click="editTask(item.id)"
                  title="編輯"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  variant="text"
                  @click="confirmDelete(item)"
                  title="刪除"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEmailTemplateStore } from '@/stores/email_template';
import type { EmailTaskResponse } from '@/models/email_template';
import { TaskState } from '@/models/email_template';

const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const searchQuery = ref('');
const statusFilter = ref<TaskState | null>(null);
const templateFilter = ref<string | null>(null);
const deleteDialog = ref(false);
const taskToDelete = ref<EmailTaskResponse | null>(null);
const executingTasks = ref(new Set<number>());

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const loading = computed(() => emailStore.loading);
const emailTasks = computed(() => emailStore.emailTasks);

const filteredTasks = computed(() => {
  let tasks = emailTasks.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    tasks = tasks.filter(task =>
      task.name.toLowerCase().includes(query) ||
      task.description?.toLowerCase().includes(query) ||
      task.recipients.some(r => r.toLowerCase().includes(query))
    );
  }

  if (statusFilter.value) {
    tasks = tasks.filter(task => task.state === statusFilter.value);
  }

  if (templateFilter.value) {
    if (templateFilter.value === 'direct') {
      tasks = tasks.filter(task => !task.use_template);
    } else if (templateFilter.value === 'template') {
      tasks = tasks.filter(task => task.use_template);
    }
  }

  return tasks;
});

const templateOptions = computed(() => [
  { title: '使用模板', value: 'template' },
  { title: '直接內容', value: 'direct' }
]);

// 常量
const headers = [
  { title: '任務名稱', key: 'name', sortable: true },
  { title: '狀態', key: 'state', sortable: true },
  { title: '模板', key: 'template', sortable: false },
  { title: '收件人', key: 'recipients', sortable: false },
  { title: '排程表達式', key: 'schedule_expression', sortable: false },
  { title: '下次執行', key: 'next_execution_time', sortable: true },
  { title: '執行次數', key: 'execution_count', sortable: true },
  { title: '操作', key: 'actions', sortable: false, width: '150px' }
];

const statusOptions = [
  { title: '啟用', value: TaskState.ENABLED },
  { title: '停用', value: TaskState.DISABLED },
  { title: '暫停', value: TaskState.PAUSED }
];

// 方法
function getStatusColor(state: TaskState): string {
  switch (state) {
    case TaskState.ENABLED:
      return 'success';
    case TaskState.DISABLED:
      return 'error';
    case TaskState.PAUSED:
      return 'warning';
    default:
      return 'grey';
  }
}

function getStatusText(state: TaskState): string {
  switch (state) {
    case TaskState.ENABLED:
      return '啟用';
    case TaskState.DISABLED:
      return '停用';
    case TaskState.PAUSED:
      return '暫停';
    default:
      return '未知';
  }
}

function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-TW');
}

async function refreshTasks() {
  try {
    await emailStore.fetchEmailTasks();
  } catch (error) {
    showSnackbar('重新整理失敗', 'error');
  }
}

async function executeTask(taskId: number) {
  executingTasks.value.add(taskId);
  try {
    await emailStore.executeEmailTask(taskId);
    showSnackbar('任務執行成功', 'success');
    await refreshTasks();
  } catch (error) {
    showSnackbar('任務執行失敗', 'error');
  } finally {
    executingTasks.value.delete(taskId);
  }
}

function editTask(taskId: number) {
  router.push(`/tasks/${taskId}/edit`);
}

function confirmDelete(task: EmailTaskResponse) {
  taskToDelete.value = task;
  deleteDialog.value = true;
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = {
    show: true,
    message,
    color
  };
}

// 生命週期
onMounted(async () => {
  await refreshTasks();
  await emailStore.fetchTemplates();
});
</script>

<style scoped>
</style>