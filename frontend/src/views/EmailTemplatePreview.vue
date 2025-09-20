<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="router.back()"
              class="me-2"
            />
            <span class="text-h5">預覽 Email 模板</span>
            <v-spacer />
            <v-btn
              color="primary"
              prepend-icon="mdi-pencil"
              @click="editTemplate"
              variant="outlined"
            >
              編輯模板
            </v-btn>
          </v-card-title>

          <v-card-text v-if="!loading">
            <v-row>
              <!-- 模板基本資訊 -->
              <v-col cols="12">
                <v-card variant="outlined" class="mb-4">
                  <v-card-title class="text-h6 font-weight-bold">
                    <v-icon class="me-2" color="primary">mdi-information</v-icon>
                    模板資訊
                  </v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <div class="text-subtitle-2 text-medium-emphasis mb-1">模板名稱</div>
                        <div class="text-h6 font-weight-medium">{{ template?.name }}</div>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="text-subtitle-2 text-medium-emphasis mb-1">狀態</div>
                        <v-chip
                          :color="template?.is_active ? 'success' : 'error'"
                          size="small"
                          variant="flat"
                          class="font-weight-medium"
                        >
                          <v-icon 
                            :icon="template?.is_active ? 'mdi-check-circle' : 'mdi-close-circle'" 
                            size="small" 
                            class="me-1"
                          />
                          {{ template?.is_active ? '啟用' : '停用' }}
                        </v-chip>
                      </v-col>
                      <v-col cols="12" v-if="template?.description">
                        <div class="text-subtitle-2 text-medium-emphasis mb-1">描述</div>
                        <div class="text-body-1">{{ template.description }}</div>
                      </v-col>
                      <v-col cols="12" md="6" v-if="template?.created_at">
                        <div class="text-subtitle-2 text-medium-emphasis mb-1">創建時間</div>
                        <div class="text-body-2">{{ formatDateTime(template.created_at) }}</div>
                      </v-col>
                      <v-col cols="12" md="6" v-if="template?.updated_at">
                        <div class="text-subtitle-2 text-medium-emphasis mb-1">更新時間</div>
                        <div class="text-body-2">{{ formatDateTime(template.updated_at) }}</div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- 變數設定 -->
              <v-col cols="12" md="4" v-if="template && template.variables.length > 0">
                <v-card variant="outlined" class="mb-4 h-100">
                  <v-card-title class="d-flex align-center text-h6 font-weight-bold">
                    <v-icon class="me-2" color="primary">mdi-variable</v-icon>
                    模板變數
                    <v-spacer />
                    <v-btn
                      color="primary"
                      size="small"
                      @click="generatePreview"
                      :loading="previewing"
                      variant="elevated"
                    >
                      <v-icon class="me-1">mdi-refresh</v-icon>
                      更新預覽
                    </v-btn>
                  </v-card-title>
                  <v-card-text>
                    <v-form @submit.prevent="generatePreview">
                      <div
                        v-for="variable in template.variables"
                        :key="variable.name"
                        class="mb-4"
                      >
                        <v-text-field
                          v-model="variableValues[variable.name]"
                          :label="`${variable.name} ${variable.required ? '*' : ''}`"
                          :hint="variable.description"
                          :required="variable.required"
                          :type="variable.type === 'number' ? 'number' : 'text'"
                          variant="outlined"
                          density="compact"
                          :placeholder="variable.default_value"
                          clearable
                        />
                      </div>
                    </v-form>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- 預覽內容 -->
              <v-col :cols="template && template.variables.length > 0 ? 8 : 12">
                <v-card variant="outlined" class="h-100">
                  <v-card-title class="text-h6 font-weight-bold">
                    <v-icon class="me-2" color="primary">mdi-eye</v-icon>
                    預覽內容
                  </v-card-title>
                  <v-card-text>
                    <v-tabs v-model="previewTab" class="mb-4" color="primary">
                      <v-tab value="text" prepend-icon="mdi-text">純文字</v-tab>
                      <v-tab value="html" prepend-icon="mdi-language-html5">HTML</v-tab>
                    </v-tabs>

                    <v-tabs-window v-model="previewTab">
                      <!-- 純文字預覽 -->
                      <v-tabs-window-item value="text">
                        <div class="mb-6">
                          <div class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center">
                            <v-icon class="me-2" color="primary">mdi-email-outline</v-icon>
                            主旨
                          </div>
                          <v-card variant="outlined" class="pa-4 bg-grey-lighten-5">
                            <div class="text-body-1 font-weight-medium">
                              {{ previewData?.subject || template?.subject_template }}
                            </div>
                          </v-card>
                        </div>
                        <div>
                          <div class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center">
                            <v-icon class="me-2" color="primary">mdi-text-box-outline</v-icon>
                            內容
                          </div>
                          <v-card variant="outlined" class="pa-4 bg-grey-lighten-5">
                            <pre class="text-body-2 ma-0" style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;">{{ previewData?.body || template?.body_template }}</pre>
                          </v-card>
                        </div>
                      </v-tabs-window-item>

                      <!-- HTML 預覽 -->
                      <v-tabs-window-item value="html">
                        <div class="mb-6">
                          <div class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center">
                            <v-icon class="me-2" color="primary">mdi-email-outline</v-icon>
                            主旨
                          </div>
                          <v-card variant="outlined" class="pa-4 bg-grey-lighten-5">
                            <div class="text-body-1 font-weight-medium">
                              {{ previewData?.subject || template?.subject_template }}
                            </div>
                          </v-card>
                        </div>
                        <div>
                          <div class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center">
                            <v-icon class="me-2" color="primary">mdi-language-html5</v-icon>
                            HTML 內容
                          </div>
                          <v-card variant="outlined" class="pa-2">
                            <iframe
                              :srcdoc="previewData?.body || template?.html_template"
                              style="width: 100%; height: 500px; border: none; border-radius: 4px;"
                              sandbox="allow-same-origin"
                            />
                          </v-card>
                        </div>
                      </v-tabs-window-item>
                    </v-tabs-window>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>

          <!-- 載入狀態 -->
          <v-card-text v-else>
            <div class="text-center py-12">
              <v-progress-circular 
                indeterminate 
                color="primary" 
                size="64"
                width="4"
              />
              <div class="mt-4 text-h6 text-medium-emphasis">載入模板中...</div>
              <div class="text-body-2 text-medium-emphasis">請稍候</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 錯誤提示 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="4000"
      location="top"
    >
      <div class="d-flex align-center">
        <v-icon 
          :icon="snackbar.color === 'error' ? 'mdi-alert-circle' : 'mdi-check-circle'" 
          class="me-2"
        />
        {{ snackbar.message }}
      </div>
      <template #actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          關閉
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEmailTemplateStore } from '@/stores/email_template';
import type { EmailTemplateResponse, EmailTemplatePreviewResponse } from '@/models/email_template';

const route = useRoute();
const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const loading = ref(true);
const previewing = ref(false);
const previewTab = ref('text');
const template = ref<EmailTemplateResponse | null>(null);
const previewData = ref<EmailTemplatePreviewResponse | null>(null);
const variableValues = ref<Record<string, any>>({});

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const templateId = computed(() => Number(route.params.id));

// 格式化日期時間
const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 方法
async function loadTemplate() {
  try {
    loading.value = true;
    template.value = await emailStore.getTemplate(templateId.value);
    
    // 初始化變數值
    if (template.value?.variables) {
      template.value.variables.forEach(variable => {
        variableValues.value[variable.name] = variable.default_value || '';
      });
    }
    
    // 生成初始預覽
    await generatePreview();
  } catch (error) {
    console.error('載入模板失敗:', error);
    showSnackbar('載入模板失敗，請稍後重試', 'error');
    router.push('/email-templates');
  } finally {
    loading.value = false;
  }
}

async function generatePreview() {
  if (!template.value) return;
  
  try {
    previewing.value = true;
    previewData.value = await emailStore.previewTemplate({
      subject_template: template.value.subject_template,
      body_template: template.value.body_template,
      html_template: template.value.html_template,
      variables: variableValues.value
    });
  } catch (error) {
    console.error('生成預覽失敗:', error);
    showSnackbar('生成預覽失敗，請檢查變數設定', 'error');
  } finally {
    previewing.value = false;
  }
}

function editTemplate() {
  router.push(`/email-templates/${templateId.value}/edit`);
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = {
    show: true,
    message,
    color
  };
}

// 監聽變數值變化，自動更新預覽（防抖）
let previewTimeout: NodeJS.Timeout;
watch(variableValues, () => {
  if (template.value) {
    clearTimeout(previewTimeout);
    previewTimeout = setTimeout(() => {
      generatePreview();
    }, 500); // 500ms 防抖
  }
}, { deep: true });

// 生命週期
onMounted(() => {
  loadTemplate();
});
</script>

<style scoped>
iframe {
  background: white;
}

pre {
  overflow-x: auto;
  max-width: 100%;
}

.gap-2 > * {
  margin: 2px;
}
</style>