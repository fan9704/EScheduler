<template>
  <v-dialog
    :model-value="modelValue"
    max-width="1200px"
    persistent
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span class="text-h5">
          <v-icon class="mr-2">mdi-wizard-hat</v-icon>
          排程表達式精靈
        </span>
        <v-btn icon="mdi-close" variant="text" @click="closeDialog" />
      </v-card-title>

      <v-card-text>
        <!-- 錯誤提示 -->
        <v-alert
          v-if="scheduleHelperStore.error"
          type="error"
          class="mb-4"
          dismissible
          @click:close="scheduleHelperStore.clearError"
        >
          {{ scheduleHelperStore.error }}
        </v-alert>

        <v-row>
          <v-col cols="12" lg="8">
            <v-card>
              <v-card-title>創建排程表達式</v-card-title>
              <v-card-text>
                <v-tabs v-model="activeTab">
                  <v-tab value="template">快速模板</v-tab>
                  <v-tab value="rate">間隔設置</v-tab>
                  <v-tab value="cron">Cron 編輯器</v-tab>
                  <v-tab value="validate">表達式驗證</v-tab>
                </v-tabs>

                <v-tabs-window v-model="activeTab" class="mt-4">
                  <v-tabs-window-item value="template">
                    <TemplateSelector @select="handleTemplateSelect" />
                  </v-tabs-window-item>

                  <v-tabs-window-item value="rate">
                    <RateEditor @generate="handleRateGenerate" />
                  </v-tabs-window-item>

                  <v-tabs-window-item value="cron">
                    <CronEditor @generate="handleCronGenerate" />
                  </v-tabs-window-item>

                  <v-tabs-window-item value="validate">
                    <ExpressionValidator
                      :initial-expression="scheduleHelperStore.currentExpression?.expression"
                      @validate="handleValidate"
                    />
                  </v-tabs-window-item>
                </v-tabs-window>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" lg="4">
            <!-- 載入狀態 -->
            <v-card v-if="scheduleHelperStore.loading" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary" />
              <div class="text-body-2 text-medium-emphasis mt-2">生成表達式中...</div>
            </v-card>

            <!-- 預覽結果 -->
            <v-card v-else-if="scheduleHelperStore.currentExpression">
              <v-card-title class="d-flex align-center">
                <v-icon class="mr-2" color="success">mdi-check-circle</v-icon>
                預覽結果
              </v-card-title>
              <v-card-text>
                <div class="mb-3">
                  <div class="text-caption text-medium-emphasis">表達式</div>
                  <v-code class="text-body-2">
                    {{ scheduleHelperStore.currentExpression.expression }}
                  </v-code>
                </div>

                <div class="mb-3">
                  <div class="text-caption text-medium-emphasis">類型</div>
                  <v-chip
                    size="small"
                    :color="
                      scheduleHelperStore.currentExpression.type === 'cron'
                        ? 'primary'
                        : 'secondary'
                    "
                    variant="flat"
                  >
                    {{ scheduleHelperStore.currentExpression.type.toUpperCase() }}
                  </v-chip>
                </div>

                <div class="mb-3">
                  <div class="text-caption text-medium-emphasis">描述</div>
                  <div class="text-body-2">
                    {{ scheduleHelperStore.currentExpression.description }}
                  </div>
                </div>

                <div v-if="scheduleHelperStore.currentExpression.next_runs?.length" class="mb-4">
                  <div class="text-caption text-medium-emphasis">接下來的執行時間</div>
                  <v-list density="compact">
                    <v-list-item
                      v-for="(time, index) in scheduleHelperStore.currentExpression.next_runs.slice(
                        0,
                        5,
                      )"
                      :key="index"
                      class="px-0"
                    >
                      <v-list-item-title class="text-body-2">
                        {{ time }}
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </div>

                <v-btn block color="primary" size="large" @click="useExpression">
                  <v-icon class="mr-2">mdi-check</v-icon>
                  使用此表達式
                </v-btn>
              </v-card-text>
            </v-card>

            <!-- 空狀態 -->
            <v-card v-else class="text-center pa-8">
              <v-icon size="64" color="grey-lighten-2"> mdi-clock-outline </v-icon>
              <div class="text-body-2 text-medium-emphasis mt-2">選擇或創建排程表達式</div>
              <div class="text-caption text-medium-emphasis mt-1">使用左側的工具來生成表達式</div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn variant="outlined" @click="closeDialog"> 取消 </v-btn>
        <v-btn
          color="primary"
          :disabled="!scheduleHelperStore.currentExpression"
          @click="useExpression"
        >
          確認使用
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import TemplateSelector from './TemplateSelector.vue';
import RateEditor from './RateEditor.vue';
import CronEditor from './CronEditor.vue';
import ExpressionValidator from './ExpressionValidator.vue';

import { useScheduleHelperStore } from '@/stores/schedule_helper';
import type {
  RateExpressionRequest,
  CronExpressionRequest,
  ScheduleValidationRequest,
} from '@/models/schedule_helper';

defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'expression-created': [expression: string];
}>();

// 直接使用 Store 實例，不要解構
const scheduleHelperStore = useScheduleHelperStore();

const activeTab = ref('template');

const handleTemplateSelect = async (expression: string) => {
  console.log('ScheduleWizardDialog: 模板選擇:', expression);
  try {
    await scheduleHelperStore.validateExpression({ expression });
    console.log('ScheduleWizardDialog: 模板驗證成功');
  } catch (error) {
    console.error('ScheduleWizardDialog: 模板驗證失敗:', error);
  }
};

const handleRateGenerate = async (request: RateExpressionRequest) => {
  console.log('ScheduleWizardDialog: 生成 Rate 表達式:', request);
  try {
    await scheduleHelperStore.generateRateExpression(request);
    console.log(
      'ScheduleWizardDialog: Rate 表達式生成成功，當前表達式:',
      scheduleHelperStore.currentExpression,
    );
  } catch (error) {
    console.error('ScheduleWizardDialog: 生成 Rate 表達式失敗:', error);
  }
};

const handleCronGenerate = async (request: CronExpressionRequest) => {
  console.log('ScheduleWizardDialog: 生成 Cron 表達式:', request);
  try {
    await scheduleHelperStore.generateCronExpression(request);
    console.log(
      'ScheduleWizardDialog: Cron 表達式生成成功，當前表達式:',
      scheduleHelperStore.currentExpression,
    );
  } catch (error) {
    console.error('ScheduleWizardDialog: 生成 Cron 表達式失敗:', error);
  }
};

const handleValidate = async (request: ScheduleValidationRequest) => {
  console.log('ScheduleWizardDialog: 驗證表達式:', request);
  try {
    await scheduleHelperStore.validateExpression(request);
    console.log('ScheduleWizardDialog: 表達式驗證成功');
  } catch (error) {
    console.error('ScheduleWizardDialog: 驗證表達式失敗:', error);
  }
};

const useExpression = () => {
  if (scheduleHelperStore.currentExpression) {
    console.log(
      'ScheduleWizardDialog: 發送表達式事件:',
      scheduleHelperStore.currentExpression.expression,
    );
    emit('expression-created', scheduleHelperStore.currentExpression.expression);
  } else {
    console.warn('ScheduleWizardDialog: 沒有可用的表達式');
  }
};

const closeDialog = () => {
  console.log('ScheduleWizardDialog: 關閉對話框');
  emit('update:modelValue', false);
  // 清除當前表達式和錯誤
  scheduleHelperStore.clearCurrentExpression();
  scheduleHelperStore.clearError();
};
</script>
