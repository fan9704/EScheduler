<template>
  <v-card>
    <v-card-title>表達式驗證</v-card-title>
    <v-card-text>
      <v-textarea
        v-model="expression"
        label="排程表達式"
        placeholder="輸入 cron 或 rate 表達式，例如：cron(0 9 * * 1-5) 或 rate(5 minutes)"
        variant="outlined"
        rows="3"
        :rules="[rules.required]"
      />
      
      <v-btn
        color="primary"
        block
        class="mb-4"
        :loading="loading"
        :disabled="!expression.trim()"
        @click="validateExpression"
      >
        驗證表達式
      </v-btn>
      
      <v-alert
        v-if="validationResult"
        :type="validationResult.valid ? 'success' : 'error'"
        :title="validationResult.valid ? '表達式有效' : '表達式無效'"
        class="mb-4"
      >
        <div v-if="validationResult.valid">
          <div class="mb-2">
            <strong>類型：</strong> {{ validationResult.type?.toUpperCase() }}
          </div>
          <div class="mb-2">
            <strong>描述：</strong> {{ validationResult.description }}
          </div>
          <div v-if="validationResult.next_runs?.length">
            <strong>接下來的執行時間：</strong>
            <ul class="mt-1">
              <li v-for="time in validationResult.next_runs" :key="time">
                {{ time }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else>
          {{ validationResult.error }}
        </div>
      </v-alert>
      
      <!-- 常用範例 -->
      <v-expansion-panels class="mt-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <v-icon class="mr-2">mdi-lightbulb-outline</v-icon>
            常用範例
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item
                v-for="example in examples"
                :key="example.expression"
                @click="useExample(example.expression)"
              >
                <v-list-item-title>
                  <v-code class="text-caption">{{ example.expression }}</v-code>
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ example.description }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { ScheduleValidationRequest } from "@/models/schedule_helper";
import { useScheduleHelperStore } from "@/stores/schedule_helper";

const props = defineProps<{
	initialExpression?: string;
}>();

const emit = defineEmits<{
	validate: [request: ScheduleValidationRequest];
}>();

const scheduleHelperStore = useScheduleHelperStore();
const { validationResult, loading } = scheduleHelperStore;

const expression = ref("");

// 監聽初始表達式
watch(
	() => props.initialExpression,
	(newExpression) => {
		if (newExpression) {
			expression.value = newExpression;
			validateExpression();
		}
	},
	{ immediate: true },
);

const rules = {
	required: (value: string) => !!value.trim() || "請輸入表達式",
};

const examples = [
	{
		expression: "cron(0 9 * * 1-5)",
		description: "工作日早上9點執行",
	},
	{
		expression: "rate(5 minutes)",
		description: "每5分鐘執行一次",
	},
	{
		expression: "cron(0 */2 * * *)",
		description: "每2小時執行一次",
	},
	{
		expression: "rate(1 hour)",
		description: "每小時執行一次",
	},
	{
		expression: "cron(0 0 1 * *)",
		description: "每月1號午夜執行",
	},
	{
		expression: "rate(30 seconds)",
		description: "每30秒執行一次",
	},
];

const validateExpression = async () => {
	if (expression.value.trim()) {
		const request = { expression: expression.value.trim() };
		await scheduleHelperStore.validateExpression(request);
		emit("validate", request);
	}
};

const useExample = (exampleExpression: string) => {
	expression.value = exampleExpression;
	validateExpression();
};
</script>