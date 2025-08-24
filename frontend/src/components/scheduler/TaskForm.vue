<template>
  <v-form ref="formRef" @submit.prevent="handleSubmit">
    <v-card>
      <v-card-title>{{ isEdit ? '編輯任務' : '創建任務' }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.name"
              label="任務名稱"
              variant="outlined"
              density="compact"
              :rules="[rules.required]"
              required
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.target_type"
              :items="targetTypeOptions"
              label="目標類型"
              variant="outlined"
              density="compact"
              :rules="[rules.required]"
              required
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="formData.description"
              label="任務描述"
              variant="outlined"
              rows="2"
            />
          </v-col>
          <v-col cols="12" md="8">
            <v-text-field
              v-model="formData.schedule_expression"
              label="排程表達式"
              variant="outlined"
              density="compact"
              :rules="[rules.required]"
              required
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-btn
              variant="outlined"
              block
              to="/schedule-helper"
              target="_blank"
            >
              <v-icon class="mr-2">mdi-help-circle-outline</v-icon>
              排程助手
            </v-btn>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.target_arn"
              label="目標 URL/ARN"
              variant="outlined"
              density="compact"
              :rules="[rules.required]"
              required
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.timezone"
              label="時區"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="targetInputText"
              label="目標輸入參數 (JSON)"
              variant="outlined"
              rows="4"
              placeholder='{"method": "GET", "headers": {"Accept": "application/json"}}'
            />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="$emit('cancel')"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
        >
          {{ isEdit ? '更新' : '創建' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ScheduledTaskCreate, ScheduledTaskResponse, TargetType } from '@/models/scheduler'

const props = defineProps<{
  initialData?: ScheduledTaskResponse
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: ScheduledTaskCreate]
  cancel: []
}>()

const formRef = ref()
const targetInputText = ref('')

const formData = ref({
  name: '',
  description: '',
  schedule_expression: '',
  timezone: 'Asia/Taipei',
  target_type: 'http' as TargetType,
  target_arn: '',
  target_input: {},
  max_retry_attempts: 3,
})

const isEdit = computed(() => !!props.initialData)

const targetTypeOptions = [
  { title: 'HTTP', value: 'http' },
  { title: 'Webhook', value: 'webhook' },
  { title: 'RabbitMQ', value: 'rabbitmq' },
  { title: 'Email', value: 'email' },
]

const rules = {
  required: (value: any) => !!value || '此欄位為必填',
}

// 監聽初始數據變化
watch(
  () => props.initialData,
  (newData) => {
    if (newData) {
      formData.value = {
        name: newData.name,
        description: newData.description || '',
        schedule_expression: newData.schedule_expression,
        timezone: newData.timezone,
        target_type: newData.target_type as TargetType,
        target_arn: newData.target_arn,
        target_input: newData.target_input || {},
        max_retry_attempts: newData.max_retry_attempts,
      }
      targetInputText.value = JSON.stringify(newData.target_input || {}, null, 2)
    }
  },
  { immediate: true }
)

// 監聽 target_input 文本變化
watch(targetInputText, (newValue) => {
  try {
    formData.value.target_input = newValue ? JSON.parse(newValue) : {}
  } catch (error) {
    // JSON 格式錯誤，保持原值
  }
})

const handleSubmit = async () => {
  const { valid } = await formRef.value.validate()
  if (valid) {
    emit('submit', formData.value)
  }
}
</script>