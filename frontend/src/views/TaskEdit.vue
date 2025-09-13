<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">編輯任務</h1>
        <p class="text-body-2 text-medium-emphasis">編輯現有的排程任務</p>
      </v-col>
    </v-row>

    <!-- 載入狀態 -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" />
        <div class="mt-2">載入任務資料中...</div>
      </v-col>
    </v-row>

    <!-- 任務表單 -->
    <TaskForm
      v-else-if="taskData"
      :key="formKey"
      :initial-data="formData"
      :loading="submitting"
      @submit="handleSubmit"
      @cancel="handleCancel"
      @open-schedule-wizard="handleOpenScheduleWizard"
    />

    <!-- 錯誤狀態 -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- 排程表達式精靈對話框 -->
    <ScheduleWizardDialog
      v-model="showScheduleWizard"
      @expression-created="handleExpressionCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

import { useSchedulerStore } from '@/stores/scheduler';
import TaskForm from '@/components/scheduler/TaskForm.vue';
import ScheduleWizardDialog from '@/components/schedule_helper/ScheduleWizardDialog.vue';
import type { ScheduledTaskCreate, ScheduledTaskResponse } from '@/models/scheduler';

const router = useRouter();
const route = useRoute();
const schedulerStore = useSchedulerStore();

const loading = ref(true);
const submitting = ref(false);
const error = ref('');
const showScheduleWizard = ref(false);
const taskData = ref<ScheduledTaskResponse | null>(null);
const formData = ref<Partial<ScheduledTaskCreate>>({});
const formKey = ref(0); // 用於強制重新渲染表單

const taskId = computed(() => {
  const id = route.params.id;
  return Array.isArray(id) ? parseInt(id[0]) : parseInt(id as string);
});

// 載入任務資料
onMounted(async () => {
  try {
    loading.value = true;
    error.value = '';

    const task = await schedulerStore.fetchTask(taskId.value);
    taskData.value = task;

    // 設置表單初始數據
    formData.value = {
      name: task.name,
      description: task.description,
      schedule_expression: task.schedule_expression,
      timezone: task.timezone,
      target_type: task.target_type as any,
      target_arn: task.target_arn,
      target_input: task.target_input,
      max_retry_attempts: task.max_retry_attempts,
      retry_policy: task.retry_policy,
      dead_letter_config: task.dead_letter_config,
    };

    formKey.value++; // 觸發表單重新渲染
  } catch (err) {
    console.error('載入任務失敗:', err);
    error.value = '載入任務資料失敗，請稍後重試';
  } finally {
    loading.value = false;
  }
});

const handleSubmit = async (taskUpdateData: ScheduledTaskCreate) => {
  try {
    submitting.value = true;
    await schedulerStore.updateTask(taskId.value, taskUpdateData);
    router.push('/tasks');
  } catch (error) {
    console.error('更新任務失敗:', error);
  } finally {
    submitting.value = false;
  }
};

const handleCancel = () => {
  router.push('/tasks');
};

const handleOpenScheduleWizard = (currentFormData: Partial<ScheduledTaskCreate>) => {
  console.log('TaskEdit: 打開排程精靈，暫存數據:', currentFormData);
  // 暫存當前表單數據
  formData.value = { ...currentFormData };
  showScheduleWizard.value = true;
};

const handleExpressionCreated = (expression: string) => {
  console.log('TaskEdit: 收到表達式:', expression);
  console.log('TaskEdit: 當前表單數據:', formData.value);

  // 將生成的表達式設置到表單數據中
  formData.value = {
    ...formData.value,
    schedule_expression: expression,
  };

  // 強制重新渲染表單以確保數據更新
  formKey.value++;

  // 關閉精靈對話框
  showScheduleWizard.value = false;

  console.log('TaskEdit: 更新後的表單數據:', formData.value);
};
</script>
