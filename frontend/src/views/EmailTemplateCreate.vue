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
            <span class="text-h5">{{ isEdit ? '編輯' : '創建' }} Email 模板</span>
          </v-card-title>

          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="saveTemplate">
              <v-row>
                <!-- 基本資訊 -->
                <v-col cols="12">
                  <div class="text-h6 mb-3">基本資訊</div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="formData.name"
                    label="模板名稱"
                    variant="outlined"
                    :rules="nameRules"
                    required
                  />
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="formData.is_active"
                    label="啟用模板"
                    color="primary"
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="formData.description"
                    label="模板描述"
                    variant="outlined"
                    rows="2"
                  />
                </v-col>

                <!-- 郵件內容 -->
                <v-col cols="12">
                  <v-divider class="my-4" />
                  <div class="text-h6 mb-3">郵件內容</div>
                </v-col>
                
                <v-col cols="12">
                  <v-text-field
                    v-model="formData.subject_template"
                    label="主旨模板"
                    variant="outlined"
                    :rules="subjectRules"
                    required
                    hint="可使用變數，例如：{{user_name}}，您好！"
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-tabs v-model="contentTab" class="mb-3">
                    <v-tab value="text">純文字內容</v-tab>
                    <v-tab value="html">HTML 內容</v-tab>
                  </v-tabs>
                  
                  <v-window v-model="contentTab">
                    <v-window-item value="text">
                      <v-textarea
                        v-model="formData.body_template"
                        label="郵件內容模板"
                        variant="outlined"
                        :rules="bodyRules"
                        rows="8"
                        required
                        hint="可使用變數，例如：親愛的 {{user_name}}，歡迎使用我們的服務！"
                      />
                    </v-window-item>
                    
                    <v-window-item value="html">
                      <v-textarea
                        v-model="formData.html_template"
                        label="HTML 內容模板"
                        variant="outlined"
                        rows="8"
                        hint="可使用 HTML 標籤和變數，例如：<h1>歡迎 {{user_name}}</h1>"
                      />
                    </v-window-item>
                  </v-window>
                </v-col>

                <!-- 預設郵件設定 -->
                <v-col cols="12">
                  <v-divider class="my-4" />
                  <div class="text-h6 mb-3">預設郵件設定</div>
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="formData.default_sender"
                    label="預設寄件者"
                    variant="outlined"
                    type="email"
                    hint="例如：noreply@example.com"
                  />
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-combobox
                    v-model="formData.default_cc"
                    label="預設副本 (CC)"
                    variant="outlined"
                    multiple
                    chips
                    hint="輸入 Email 地址後按 Enter"
                  />
                </v-col>
                
                <v-col cols="12" md="4">
                  <v-combobox
                    v-model="formData.default_bcc"
                    label="預設密件副本 (BCC)"
                    variant="outlined"
                    multiple
                    chips
                    hint="輸入 Email 地址後按 Enter"
                  />
                </v-col>

                <!-- 模板變數 -->
                <v-col cols="12">
                  <v-divider class="my-4" />
                  <div class="text-h6 mb-3 d-flex align-center">
                    模板變數
                    <v-btn
                      color="primary"
                      variant="outlined"
                      size="small"
                      @click="addVariable"
                      class="ms-2"
                    >
                      <v-icon start>mdi-plus</v-icon>
                      新增變數
                    </v-btn>
                  </div>
                </v-col>
                
                <v-col cols="12" v-if="formData.variables.length === 0">
                  <v-alert type="info" variant="outlined">
                    {{"尚未定義任何變數。變數可以讓您的模板更加靈活，例如 \{\{user_name\}\}、\{\{order_id\}\} 等。"}}
                  </v-alert>
                </v-col>
                
                <v-col cols="12" v-for="(variable, index) in formData.variables" :key="index">
                  <v-card variant="outlined" class="mb-2">
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="3">
                          <v-text-field
                            v-model="variable.name"
                            label="變數名稱"
                            variant="outlined"
                            density="compact"
                            hint="例如：user_name"
                          />
                        </v-col>
                        
                        <v-col cols="12" md="2">
                          <v-select
                            v-model="variable.type"
                            label="類型"
                            :items="variableTypes"
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
                            hide-details
                          />
                        </v-col>
                        
                        <v-col cols="12" md="1">
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

                <!-- 預覽區域 -->
                <v-col cols="12">
                  <v-divider class="my-4" />
                  <div class="text-h6 mb-3 d-flex align-center">
                    模板預覽
                    <v-btn
                      color="primary"
                      variant="outlined"
                      size="small"
                      @click="generatePreview"
                      :loading="previewing"
                      class="ms-2"
                    >
                      生成預覽
                    </v-btn>
                  </div>
                </v-col>
                
                <v-col cols="12" v-if="previewData">
                  <v-card variant="outlined">
                    <v-card-text>
                      <div class="mb-3">
                        <strong>主旨：</strong>{{ previewData.subject }}
                      </div>
                      <div class="mb-3">
                        <strong>HTML 內容：</strong>
                        <div v-html="previewData.body" class="border pa-3 mt-2"></div>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn @click="router.back()">取消</v-btn>
            <v-btn
              color="primary"
              @click="saveTemplate"
              :loading="saving"
              :disabled="!valid"
            >
              {{ isEdit ? '更新' : '創建' }}
            </v-btn>
          </v-card-actions>
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
import type { EmailTemplateCreate, EmailTemplateUpdate, EmailTemplatePreviewResponse } from '@/models/email_template';

const route = useRoute();
const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const form = ref();
const valid = ref(false);
const saving = ref(false);
const previewing = ref(false);
const contentTab = ref('text');
const previewData = ref<EmailTemplatePreviewResponse | null>(null);

const formData = ref<EmailTemplateCreate>({
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
const isEdit = computed(() => !!route.params.id);
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
  formData.value.variables.splice(index, 1);
}

async function generatePreview() {
  if (!formData.value.subject_template || (!formData.value.body_template && !formData.value.html_template) ){
    showSnackbar('請先填寫主旨和內容模板', 'warning');
    return;
  }

  previewing.value = true;
  try {
    // 生成示例變數值
    const sampleVariables: Record<string, any> = {};
    formData.value.variables.forEach(variable => {
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
          default:
            sampleVariables[variable.name] = `示例${variable.name}`;
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

async function saveTemplate() {
  if (!form.value?.validate()) return;

  saving.value = true;
  try {
    if (isEdit.value) {
      await emailStore.updateTemplate(templateId.value, formData.value as EmailTemplateUpdate);
      showSnackbar('模板更新成功', 'success');
    } else {
      const newTemplate = await emailStore.createTemplate(formData.value);
      showSnackbar('模板創建成功', 'success');
      await router.push(`/email-templates/${newTemplate.id}/edit`);
    }
  } catch (error) {
    console.error('保存模板失敗:', error);
    showSnackbar(isEdit.value ? '模板更新失敗' : '模板創建失敗', 'error');
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
onMounted(async () => {
  if (isEdit.value) {
    try {
      const template = await emailStore.getTemplate(templateId.value);
      if (template) {
        formData.value = {
          name: template.name,
          description: template.description || '',
          subject_template: template.subject_template,
          body_template: template.body_template,
          html_template: template.html_template || '',
          variables: template.variables,
          default_sender: template.default_sender || '',
          default_cc: template.default_cc || [],
          default_bcc: template.default_bcc || [],
          is_active: template.is_active
        };
      }
    } catch (error) {
      console.error('載入模板失敗:', error);
      showSnackbar('載入模板失敗', 'error');
      router.back();
    }
  }
});
</script>

<style scoped>
.border {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>