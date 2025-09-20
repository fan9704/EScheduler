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
            <span class="text-h5">編輯 Email 模板</span>
            <v-spacer />
            <v-btn
              color="success"
              prepend-icon="mdi-content-save"
              @click="saveTemplate"
              :loading="saving"
              :disabled="!valid"
            >
              儲存
            </v-btn>
          </v-card-title>

          <v-card-text v-if="!loading">
            <v-form ref="form" v-model="valid">
              <v-row>
                <!-- 基本資訊 -->
                <v-col cols="12" md="6">
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title>基本資訊</v-card-title>
                    <v-card-text>
                      <v-text-field
                        v-model="formData.name"
                        label="模板名稱 *"
                        :rules="nameRules"
                        variant="outlined"
                        class="mb-3"
                      />
                      
                      <v-textarea
                        v-model="formData.description"
                        label="描述"
                        variant="outlined"
                        rows="3"
                        class="mb-3"
                      />

                      <v-switch
                        v-model="formData.is_active"
                        label="啟用模板"
                        color="success"
                        inset
                      />
                    </v-card-text>
                  </v-card>
                </v-col>

                <!-- 預設設定 -->
                <v-col cols="12" md="6">
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title>預設設定</v-card-title>
                    <v-card-text>
                      <v-text-field
                        v-model="formData.default_sender"
                        label="預設寄件者"
                        type="email"
                        variant="outlined"
                        class="mb-3"
                      />
                      
                      <v-combobox
                        v-model="formData.default_cc"
                        label="預設副本 (CC)"
                        multiple
                        chips
                        variant="outlined"
                        class="mb-3"
                      />
                      
                      <v-combobox
                        v-model="formData.default_bcc"
                        label="預設密件副本 (BCC)"
                        multiple
                        chips
                        variant="outlined"
                      />
                    </v-card-text>
                  </v-card>
                </v-col>

                <!-- 模板內容 -->
                <v-col cols="12">
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title>模板內容</v-card-title>
                    <v-card-text>
                      <v-text-field
                        v-model="formData.subject_template"
                        label="主旨模板 *"
                        :rules="subjectRules"
                        variant="outlined"
                        class="mb-3"
                      />

                      <v-tabs v-model="contentTab" class="mb-4">
                        <v-tab value="text">純文字內容</v-tab>
                        <v-tab value="html">HTML 內容</v-tab>
                      </v-tabs>

                      <v-tabs-window v-model="contentTab">
                        <v-tabs-window-item value="text">
                          <v-textarea
                            v-model="formData.body_template"
                            label="純文字內容 *"
                            :rules="bodyRules"
                            variant="outlined"
                            rows="10"
                            placeholder="輸入您的 Email 內容模板..."
                          />
                        </v-tabs-window-item>
                        
                        <v-tabs-window-item value="html">
                          <v-textarea
                            v-model="formData.html_template"
                            label="HTML 內容"
                            variant="outlined"
                            rows="10"
                            placeholder="輸入您的 HTML Email 模板..."
                          />
                        </v-tabs-window-item>
                      </v-tabs-window>
                    </v-card-text>
                  </v-card>
                </v-col>

                <!-- 模板變數 -->
                <v-col cols="12">
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title class="d-flex align-center">
                      模板變數
                      <v-spacer />
                      <v-btn
                        color="primary"
                        size="small"
                        prepend-icon="mdi-plus"
                        @click="addVariable"
                      >
                        新增變數
                      </v-btn>
                    </v-card-title>
                    <v-card-text>
                      <div v-if="formData.variables?.length === 0" class="text-center text-grey py-4">
                        尚未定義任何變數
                      </div>
                      
                      <v-row
                        v-for="(variable, index) in formData.variables"
                        :key="index"
                        class="mb-3"
                      >
                        <v-col cols="12" md="3">
                          <v-text-field
                            v-model="variable.name"
                            label="變數名稱"
                            variant="outlined"
                            density="compact"
                            :rules="[v => !!v || '請輸入變數名稱']"
                          />
                        </v-col>
                        <v-col cols="12" md="2">
                          <v-select
                            v-model="variable.type"
                            :items="variableTypes"
                            label="類型"
                            variant="outlined"
                            density="compact"
                          />
                        </v-col>
                        <v-col cols="12" md="3">
                          <v-text-field
                            v-model="variable.description"
                            label="描述"
                            variant="outlined"
                            density="compact"
                          />
                        </v-col>
                        <v-col cols="12" md="2">
                          <v-text-field
                            v-model="variable.default_value"
                            label="預設值"
                            variant="outlined"
                            density="compact"
                          />
                        </v-col>
                        <v-col cols="12" md="1">
                          <v-switch
                            v-model="variable.required"
                            label="必填"
                            density="compact"
                            inset
                          />
                        </v-col>
                        <v-col cols="12" md="1" class="d-flex align-center">
                          <v-btn
                            icon="mdi-delete"
                            size="small"
                            color="error"
                            variant="text"
                            @click="removeVariable(index)"
                          />
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>

                <!-- 預覽 -->
                <v-col cols="12">
                  <v-card variant="outlined">
                    <v-card-title class="d-flex align-center">
                      模板預覽
                      <v-spacer />
                      <v-btn
                        color="primary"
                        size="small"
                        @click="generatePreview"
                        :loading="previewing"
                      >
                        生成預覽
                      </v-btn>
                    </v-card-title>
                    <v-card-text>
                      <div v-if="previewData">
                        <div class="mb-4">
                          <div class="text-subtitle-2 text-grey mb-2">主旨</div>
                          <v-card variant="outlined" class="pa-3">
                            <div class="text-body-1">{{ previewData.subject }}</div>
                          </v-card>
                        </div>
                        <div class="mb-4">
                          <div class="text-subtitle-2 text-grey mb-2">HTML 內容</div>
                          <v-card variant="outlined" class="pa-3">
                            <div v-html="previewData.body" class="border pa-3"></div>
                          </v-card>
                        </div>
                      </div>
                      <div v-else class="text-center text-grey py-4">
                        點擊「生成預覽」查看模板效果
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-text v-else>
            <div class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <div class="mt-2">載入中...</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 成功/錯誤提示 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEmailTemplateStore } from '@/stores/email_template';
import type { EmailTemplateUpdate, EmailTemplateResponse, EmailTemplatePreviewResponse } from '@/models/email_template';

const route = useRoute();
const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const form = ref();
const valid = ref(false);
const loading = ref(true);
const saving = ref(false);
const previewing = ref(false);
const contentTab = ref('text');
const previewData = ref<EmailTemplatePreviewResponse | null>(null);
const template = ref<EmailTemplateResponse | null>(null);

const formData = ref<EmailTemplateUpdate>({
  name: '',
  description: '',
  subject_template: '',
  body_template: '',
  html_template: '',
  variables: [],
  default_sender: '',
  default_cc: [],
  default_bcc: [],
  is_active: true
});

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const templateId = computed(() => Number(route.params.id));

// 常量
const variableTypes = [
  { title: '字串', value: 'string' },
  { title: '數字', value: 'number' },
  { title: '布林值', value: 'boolean' },
  { title: '日期', value: 'date' },
  { title: 'Email', value: 'email' },
  { title: 'URL', value: 'url' }
];

const nameRules = [
  (v: string) => !!v || '請輸入模板名稱',
  (v: string) => v.length <= 255 || '模板名稱不能超過 255 個字元'
];

const subjectRules = [
  (v: string) => !!v || '請輸入主旨模板',
  (v: string) => v.length <= 500 || '主旨模板不能超過 500 個字元'
];

const bodyRules = [
  (v: string) => !!v || '請輸入內容模板'
];

// 方法
function addVariable() {
  if (!formData.value.variables) {
    formData.value.variables = [];
  }
  formData.value.variables.push({
    name: '',
    type: 'string',
    description: '',
    required: false,
    default_value: '',
    validation_rules: {}
  });
}

function removeVariable(index: number) {
  if (formData.value.variables) {
    formData.value.variables.splice(index, 1);
  }
}

async function generatePreview() {
  if (!formData.value.subject_template || (!formData.value.body_template && !formData.value.html_template)) {
    showSnackbar('請先填寫主旨和內容模板', 'warning');
    return;
  }
  
  previewing.value = true;
  try {
    // 生成示例變數值
    const sampleVariables: Record<string, any> = {};
    formData.value.variables?.forEach(variable => {
      if (variable.name) {
        switch (variable.type) {
          case 'string':
            sampleVariables[variable.name] = variable.default_value || `示例${variable.name}`;
            break;
          case 'number':
            sampleVariables[variable.name] = variable.default_value || 123;
            break;
          case 'boolean':
            sampleVariables[variable.name] = variable.default_value !== undefined ? variable.default_value : true;
            break;
          case 'date':
            sampleVariables[variable.name] = variable.default_value || new Date().toISOString().split('T')[0];
            break;
          case 'email':
            sampleVariables[variable.name] = variable.default_value || 'example@example.com';
            break;
          case 'url':
            sampleVariables[variable.name] = variable.default_value || 'https://example.com';
            break;
          default:
            sampleVariables[variable.name] = variable.default_value || `示例${variable.name}`;
        }
      }
    });

    // 統一使用 html_template 方式預覽
    previewData.value = await emailStore.previewTemplate({
      subject_template: formData.value.subject_template,
      body_template: formData.value.body_template,
      html_template: formData.value.html_template,
      variables: sampleVariables
    });
    
    showSnackbar('預覽生成成功', 'success');
  } catch (error) {
    console.error('預覽生成失敗:', error);
    showSnackbar('預覽生成失敗，請檢查模板語法', 'error');
  } finally {
    previewing.value = false;
  }
}

async function loadTemplate() {
  try {
    loading.value = true;
    template.value = await emailStore.getTemplate(templateId.value);
    
    if (template.value) {
      // 填充表單數據
      formData.value = {
        name: template.value.name,
        description: template.value.description || '',
        subject_template: template.value.subject_template,
        body_template: template.value.body_template,
        html_template: template.value.html_template || '',
        variables: [...(template.value.variables || [])],
        default_sender: template.value.default_sender || '',
        default_cc: template.value.default_cc || [],
        default_bcc: template.value.default_bcc || [],
        is_active: template.value.is_active
      };
    }
  } catch (error) {
    console.error('載入模板失敗:', error);
    showSnackbar('載入模板失敗', 'error');
    await router.push('/email-templates');
  } finally {
    loading.value = false;
  }
}

async function saveTemplate() {
  if (!form.value?.validate() || !template.value) return;

  saving.value = true;
  try {
    await emailStore.updateTemplate(template.value.id, formData.value);
    showSnackbar('模板更新成功', 'success');
    router.push('/email-templates');
  } catch (error) {
    console.error('更新模板失敗:', error);
    showSnackbar('更新模板失敗', 'error');
  } finally {
    saving.value = false;
  }
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = {
    show: true,
    message,
    color
  };
}

// 生命週期
onMounted(() => {
  loadTemplate();
});
</script>

<style scoped>
.border {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>