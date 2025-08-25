<template>
  <v-card>
    <v-card-title>間隔設置</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model.number="rateValue"
            type="number"
            label="間隔數值"
            variant="outlined"
            density="compact"
            :min="1"
            :rules="[rules.required, rules.positive]"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="rateUnit"
            :items="unitOptions"
            label="時間單位"
            variant="outlined"
            density="compact"
          />
        </v-col>
      </v-row>
      
      <v-divider class="my-4" />
      
      <div class="mb-3">
        <div class="text-caption text-medium-emphasis mb-2">預覽表達式</div>
        <v-code class="text-body-2">
          rate({{ rateValue }} {{ rateUnit }})
        </v-code>
      </div>
      
      <div class="mb-3">
        <div class="text-caption text-medium-emphasis mb-2">描述</div>
        <div class="text-body-2">
          {{ description }}
        </div>
      </div>
      
      <v-btn
        color="primary"
        block
        size="large"
        :disabled="!isValid"
        @click="generateExpression"
      >
        <v-icon class="mr-2">mdi-creation</v-icon>
        生成 Rate 表達式
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RateExpressionRequest, TimeUnit } from '@/models/schedule_helper'

const emit = defineEmits<{
  generate: [request: RateExpressionRequest]
}>()

const rateValue = ref(5)
const rateUnit = ref<TimeUnit>(TimeUnit.MINUTES)

const unitOptions = [
  { title: '秒', value: 'seconds' },
  { title: '分鐘', value: 'minutes' },
  { title: '小時', value: 'hours' },
  { title: '天', value: 'days' },
]

const rules = {
  required: (value: any) => !!value || '此欄位為必填',
  positive: (value: number) => value > 0 || '數值必須大於0',
}

const description = computed(() => {
  const unitMap: Record<string, string> = {
    seconds: '秒',
    minutes: '分鐘',
    hours: '小時',
    days: '天',
  }
  
  return `每${rateValue.value}${unitMap[rateUnit.value] || rateUnit.value}執行一次`
})

const isValid = computed(() => {
  return rateValue.value > 0 && rateUnit.value
})

const generateExpression = () => {
  if (isValid.value) {
    console.log('生成 Rate 表達式:', { value: rateValue.value, unit: rateUnit.value }) // 調試用
    emit('generate', {
      value: rateValue.value,
      unit: rateUnit.value,
    })
  }
}
</script>