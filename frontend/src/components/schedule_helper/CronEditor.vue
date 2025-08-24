<template>
  <v-card>
    <v-card-title>Cron 表達式編輯器</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="cronFields.minute"
            :items="minuteOptions"
            label="分鐘 (0-59)"
            variant="outlined"
            density="compact"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="cronFields.hour"
            :items="hourOptions"
            label="小時 (0-23)"
            variant="outlined"
            density="compact"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="cronFields.day"
            :items="dayOptions"
            label="日 (1-31)"
            variant="outlined"
            density="compact"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="cronFields.month"
            :items="monthOptions"
            label="月 (1-12)"
            variant="outlined"
            density="compact"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="cronFields.weekday"
            :items="weekdayOptions"
            label="星期 (0-7)"
            variant="outlined"
            density="compact"
          />
        </v-col>
      </v-row>
      
      <v-divider class="my-4" />
      
      <div class="mb-3">
        <div class="text-caption text-medium-emphasis mb-2">預覽表達式</div>
        <v-code class="text-body-2">
          cron({{ cronExpression }})
        </v-code>
      </div>
      
      <v-btn
        color="primary"
        block
        size="large"
        @click="generateExpression"
      >
        <v-icon class="mr-2">mdi-creation</v-icon>
        生成 Cron 表達式
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CronExpressionRequest } from '@/models/schedule_helper'

const emit = defineEmits<{
  generate: [request: CronExpressionRequest]
}>()

const cronFields = ref({
  minute: '*',
  hour: '*',
  day: '*',
  month: '*',
  weekday: '*',
})

const minuteOptions = [
  { title: '每分鐘', value: '*' },
  { title: '每5分鐘', value: '*/5' },
  { title: '每10分鐘', value: '*/10' },
  { title: '每15分鐘', value: '*/15' },
  { title: '每30分鐘', value: '*/30' },
  { title: '第0分鐘', value: '0' },
  { title: '第30分鐘', value: '30' },
]

const hourOptions = [
  { title: '每小時', value: '*' },
  { title: '每2小時', value: '*/2' },
  { title: '每6小時', value: '*/6' },
  { title: '每12小時', value: '*/12' },
  { title: '上午9點', value: '9' },
  { title: '下午6點', value: '18' },
  { title: '工作時間 (9-17)', value: '9-17' },
]

const dayOptions = [
  { title: '每天', value: '*' },
  { title: '每月1號', value: '1' },
  { title: '每月15號', value: '15' },
  { title: '每月最後一天', value: 'L' },
  { title: '1號和15號', value: '1,15' },
]

const monthOptions = [
  { title: '每月', value: '*' },
  { title: '1月', value: '1' },
  { title: '6月', value: '6' },
  { title: '12月', value: '12' },
  { title: '第一季 (1-3月)', value: '1-3' },
  { title: '第四季 (10-12月)', value: '10-12' },
]

const weekdayOptions = [
  { title: '每天', value: '*' },
  { title: '週一', value: '1' },
  { title: '週五', value: '5' },
  { title: '週末', value: '0,6' },
  { title: '工作日 (週一到週五)', value: '1-5' },
]

const cronExpression = computed(() => {
  return `${cronFields.value.minute} ${cronFields.value.hour} ${cronFields.value.day} ${cronFields.value.month} ${cronFields.value.weekday}`
})

const generateExpression = () => {
  console.log('生成 Cron 表達式:', cronFields.value) // 調試用
  emit('generate', cronFields.value)
}
</script>