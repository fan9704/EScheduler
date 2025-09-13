<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">排程助手</h1>
        <p class="text-body-2 text-medium-emphasis">幫助您創建正確的排程表達式</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>排程表達式生成器</v-card-title>
          <v-card-text>
            <v-tabs v-model="activeTab">
              <v-tab value="template">模板選擇</v-tab>
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
                <ExpressionValidator @validate="handleValidate" />
              </v-tabs-window-item>
            </v-tabs-window>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card v-if="currentExpression">
          <v-card-title>生成結果</v-card-title>
          <v-card-text>
            <div class="mb-3">
              <div class="text-caption text-medium-emphasis">表達式</div>
              <v-code class="text-body-2">
                {{ currentExpression.expression }}
              </v-code>
            </div>

            <div class="mb-3">
              <div class="text-caption text-medium-emphasis">描述</div>
              <div class="text-body-2">
                {{ currentExpression.description }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-medium-emphasis">接下來的執行時間</div>
              <v-list density="compact">
                <v-list-item
                  v-for="(time, index) in currentExpression.next_runs"
                  :key="index"
                  class="px-0"
                >
                  <v-list-item-title class="text-body-2">
                    {{ time }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </div>

            <v-btn block color="primary" @click="useExpression"> 使用此表達式 </v-btn>
          </v-card-text>
        </v-card>

        <v-card v-else class="text-center pa-8">
          <v-icon size="64" color="grey-lighten-2"> mdi-clock-outline </v-icon>
          <div class="text-body-2 text-medium-emphasis mt-2">選擇或創建排程表達式</div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

import { useScheduleHelperStore } from '@/stores/schedule_helper';
import TemplateSelector from '@/components/schedule_helper/TemplateSelector.vue';
import RateEditor from '@/components/schedule_helper/RateEditor.vue';
import CronEditor from '@/components/schedule_helper/CronEditor.vue';
import ExpressionValidator from '@/components/schedule_helper/ExpressionValidator.vue';
import type {
  RateExpressionRequest,
  CronExpressionRequest,
  ScheduleValidationRequest,
} from '@/models/schedule_helper';

const router = useRouter();
const scheduleHelperStore = useScheduleHelperStore();

const { currentExpression } = scheduleHelperStore;

const activeTab = ref('template');

const handleTemplateSelect = (expression: string) => {
  // 使用模板表達式進行驗證
  scheduleHelperStore.validateExpression({ expression });
};

const handleRateGenerate = (request: RateExpressionRequest) => {
  scheduleHelperStore.generateRateExpression(request);
};

const handleCronGenerate = (request: CronExpressionRequest) => {
  scheduleHelperStore.generateCronExpression(request);
};

const handleValidate = (request: ScheduleValidationRequest) => {
  scheduleHelperStore.validateExpression(request);
};

const useExpression = () => {
  if (currentExpression?.value) {
    // 跳轉到創建任務頁面，並帶上表達式
    router.push({
      path: '/tasks/create',
      query: {
        expression: currentExpression?.value.expression,
      },
    });
  }
};
</script>
