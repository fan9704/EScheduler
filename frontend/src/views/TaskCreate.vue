<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">創建任務</h1>
        <p class="text-body-2 text-medium-emphasis">創建新的排程任務</p>
      </v-col>
    </v-row>
    
    <TaskForm 
      ref="taskFormRef"
      @submit="handleSubmit" 
      @cancel="handleCancel"
      @open-schedule-wizard="handleOpenScheduleWizard"
    />
    
    <!-- 排程表達式精靈對話框 -->
    <ScheduleWizardDialog
      v-model="showScheduleWizard"
      @expression-created="handleExpressionCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import ScheduleWizardDialog from "@/components/schedule_helper/ScheduleWizardDialog.vue";
import type TaskForm from "@/components/scheduler/TaskForm.vue";
import type { ScheduledTaskCreate } from "@/models/scheduler";
import { useSchedulerStore } from "@/stores/scheduler";

const router = useRouter();
const schedulerStore = useSchedulerStore();

const showScheduleWizard = ref(false);
const taskFormRef = ref<InstanceType<typeof TaskForm> | null>(null);
const tempFormData = ref<Partial<ScheduledTaskCreate>>({});

const handleSubmit = async (taskData: ScheduledTaskCreate) => {
	try {
		await schedulerStore.createTask(taskData);
		router.push("/tasks");
	} catch (error) {
		console.error("創建任務失敗:", error);
	}
};

const handleCancel = () => {
	router.push("/tasks");
};

const handleOpenScheduleWizard = (
	currentFormData: Partial<ScheduledTaskCreate>,
) => {
	console.log("TaskCreate: 打開排程精靈，暫存數據:", currentFormData);
	// 暫存當前表單數據
	tempFormData.value = { ...currentFormData };
	showScheduleWizard.value = true;
};

const handleExpressionCreated = (expression: string) => {
	console.log("TaskCreate: 收到表達式:", expression);
	console.log("TaskCreate: 當前暫存數據:", tempFormData.value);

	// 關閉精靈對話框
	showScheduleWizard.value = false;

	// 直接調用 TaskForm 的方法來設置表達式
	if (taskFormRef.value) {
		taskFormRef.value.setScheduleExpression(expression);
		console.log("TaskCreate: 已調用 TaskForm.setScheduleExpression");
	} else {
		console.error("TaskCreate: taskFormRef 不存在");
	}
};
</script>