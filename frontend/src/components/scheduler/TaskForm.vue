<template>
  <v-form ref="formRef" @submit.prevent="handleSubmit">
    <v-card>
      <v-card-title>{{ isEdit ? "編輯任務" : "創建任務" }}</v-card-title>
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

          <!-- 排程表達式輸入區域 -->
          <v-col cols="12">
            <div class="d-flex gap-2">
              <v-text-field
                v-model="formData.schedule_expression"
                label="排程表達式"
                variant="outlined"
                density="compact"
                :rules="[rules.required]"
                placeholder="例如：cron(0 9 * * 1-5) 或 rate(5 minutes)"
                required
                class="flex-grow-1"
              />
              <v-btn
                color="primary"
                variant="outlined"
                size="large"
                @click="openScheduleWizard"
              >
                <v-icon class="mr-2">mdi-wizard-hat</v-icon>
                排程精靈
              </v-btn>
            </div>
            <div class="text-caption text-medium-emphasis mt-1">
              使用排程精靈可以輕鬆創建 Cron 或 Rate 表達式
            </div>
            <!-- 顯示表達式狀態 -->
            <div v-if="formData.schedule_expression" class="mt-2">
              <v-chip size="small" color="success" variant="outlined">
                <v-icon class="mr-1" size="16">mdi-check</v-icon>
                已設置：{{ formData.schedule_expression }}
              </v-chip>
            </div>
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
          <v-col cols="12" md="3">
            <v-text-field
              v-model="formData.timezone"
              label="時區"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="12" v-if="formData.target_type === 'webhook'" class="pa-6">
            <h2>選擇 Webhook Template</h2>
            <v-item-group v-model="selectedWebhookTemplate" mandatory class="d-flex">
              <v-item v-for="template in webhook_template" v-slot="{ isSelected, toggle }" :key="template.id" >
                <v-card @click="toggle" class="cursor-pointer ma-2 pa-2" :class="isSelected? 'selected-card' : ''" style="flex:1;display: flex;">
                  <v-img @click="httpBodyText = JSON.stringify(template.body); formatJSON()" :src="template.image" height="100px">
                    {{ template.name }}
                  </v-img>
                </v-card>
              </v-item>
            </v-item-group>
          </v-col>
          <!-- HTTP 類型時顯示 Method、Header、Body -->
          <template v-if="formData.target_type === 'http' || formData.target_type === 'webhook'">
            <v-col cols="12" md="3" v-if="formData.target_type === 'http'">
              <v-select
                v-model="httpMethod"
                :items="httpMethodOptions"
                label="HTTP Method"
                variant="outlined"
                density="compact"
                :rules="[rules.required]"
                required
              />
            </v-col>
            <v-col cols="12" md="12" v-if="formData.target_type === 'http'">
              <div style="position: relative">
                <div
                  class="font-weight-bold"
                  style="position: absolute; top: -24px; left: 0"
                >
                  HTTP Headers
                </div>
                <div
                  v-for="(row, idx) in headerRows"
                  :key="idx"
                  class="d-flex align-center mb-2"
                  style="margin-top: 0"
                >
                  <v-combobox
                    v-model="row.key"
                    :items="commonHeaders"
                    label="Key"
                    variant="outlined"
                    density="compact"
                    class="mr-2"
                    clearable
                    hide-details
                    style="max-width: 220px"
                    filterable
                    solo
                  />
                  <v-text-field
                    v-model="row.value"
                    label="Value"
                    variant="outlined"
                    density="compact"
                    hide-details
                    style="max-width: 220px"
                  />
                  <v-btn
                    icon="mdi-delete"
                    @click="headerRows.splice(idx, 1)"
                    v-if="headerRows.length > 1"
                    size="small"
                    variant="text"
                  />
                </div>
                <v-btn
                  color="primary"
                  variant="text"
                  @click="headerRows.push({ key: '', value: '' })"
                  size="small"
                >
                  <v-icon>mdi-plus</v-icon> 新增 Header
                </v-btn>
              </div>
            </v-col>
            <v-col cols="12">
              <div class="font-weight-bold" style="margin-bottom: 8px">
                HTTP Body (JSON)
              </div>
              <Codemirror
                v-model:value="httpBodyText"
                :options="cmOptions"
                height="400"
                ref="cmRef"
              >
              </Codemirror>
              <v-btn @click="formatJSON()">Format JSON</v-btn>
            </v-col>
          </template>
          <!-- Email 類型時顯示 Email 特定欄位 -->
          <template v-else-if="formData.target_type === 'email'">
            <!-- Email 設定方式選擇 -->
            <v-col cols="12">
              <v-divider class="my-4" />
              <div class="text-h6 mb-3">Email 設定</div>
              <v-radio-group v-model="emailMode" inline>
                <v-radio label="使用模板" value="template" />
                <v-radio label="直接設定" value="direct" />
              </v-radio-group>
            </v-col>

            <!-- 模板模式 -->
            <template v-if="emailMode === 'template'">
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedTemplateId"
                  label="選擇 Email 模板"
                  :items="enhancedTemplateOptions"
                  variant="outlined"
                  :loading="templatesLoading"
                  @update:model-value="onTemplateChange"
                  clearable
                />
              </v-col>
              
              <v-col cols="12" md="6" v-if="selectedTemplate">
                <v-btn
                  color="primary"
                  variant="outlined"
                  @click="previewTemplate"
                  :loading="previewLoading"
                  prepend-icon="mdi-eye"
                >
                  預覽模板
                </v-btn>
              </v-col>

              <!-- 創建新模板提示 -->
              <v-col cols="12" v-if="selectedTemplateId === 'create_new'">
                <v-card variant="outlined" color="primary">
                  <v-card-text class="d-flex align-center">
                    <v-icon class="mr-3" color="primary">mdi-information</v-icon>
                    <div class="flex-grow-1">
                      <div class="text-subtitle-1 font-weight-medium">創建新的 Email 模板</div>
                      <div class="text-body-2 text-medium-emphasis">
                        點擊下方按鈕跳轉到模板創建頁面，創建完成後可回到此處選擇使用。
                      </div>
                    </div>
                    <v-btn
                      color="primary"
                      variant="elevated"
                      @click="navigateToCreateTemplate"
                      prepend-icon="mdi-plus"
                    >
                      創建模板
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- 模板變數設定 -->
              <v-col cols="12" v-if="selectedTemplate && selectedTemplate.variables.length > 0">
                <v-divider class="my-2" />
                <div class="text-subtitle-1 mb-3">模板變數設定</div>
                <v-row>
                  <v-col 
                    cols="12" 
                    md="6" 
                    v-for="variable in selectedTemplate.variables" 
                    :key="variable.name"
                  >
                    <v-text-field
                      v-model="templateVariables[variable.name]"
                      :label="variable.name"
                      :placeholder="variable.default_value"
                      :hint="variable.description"
                      variant="outlined"
                      density="compact"
                      :required="variable.required"
                      :rules="variable.required ? [rules.required] : []"
                    />
                  </v-col>
                </v-row>
              </v-col>
            </template>

            <!-- 直接設定模式 -->
            <template v-else>
              <v-col cols="12">
                <v-text-field
                  v-model="directEmailData.subject"
                  label="郵件主旨"
                  variant="outlined"
                  :rules="[rules.required]"
                  required
                />
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="directEmailData.body"
                  label="郵件內容"
                  variant="outlined"
                  :rules="[rules.required]"
                  rows="6"
                  required
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="directEmailData.sender"
                  label="寄件人 Email"
                  variant="outlined"
                  type="email"
                  hint="留空則使用系統預設"
                />
              </v-col>
            </template>

            <!-- 收件人設定 -->
            <v-col cols="12">
              <v-divider class="my-4" />
              <div class="text-h6 mb-3">收件人設定</div>
            </v-col>
            
            <v-col cols="12">
              <v-combobox
                v-model="emailRecipients"
                label="收件人"
                variant="outlined"
                multiple
                chips
                :rules="[rules.required, rules.emailList]"
                required
                hint="輸入 Email 地址後按 Enter 新增"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-combobox
                v-model="emailCC"
                label="副本收件人 (CC)"
                variant="outlined"
                multiple
                chips
                :rules="[rules.emailList]"
                hint="可選，輸入 Email 地址後按 Enter 新增"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-combobox
                v-model="emailBCC"
                label="密件副本收件人 (BCC)"
                variant="outlined"
                multiple
                chips
                :rules="[rules.emailList]"
                hint="可選，輸入 Email 地址後按 Enter 新增"
              />
            </v-col>
          </template>
          <!-- 其他類型維持原本 target_input 輸入 -->
          <template v-else>
            <v-col cols="12">
              <v-textarea
                v-model="targetInputText"
                label="目標輸入參數 (JSON)"
                variant="outlined"
                rows="4"
                placeholder='{"method": "GET", "headers": {"Accept": "application/json"}}'
                :error-messages="targetInputError ? [targetInputError] : []"
              />
            </v-col>
          </template>
          <!-- 新增啟用開關 -->
          <v-col cols="12" md="6">
            <v-switch
              v-model="formData.state"
              :value="formData.state"
              :false-value="TaskState.DISABLED"
              :color="formData.state === TaskState.ENABLED ? 'success' : 'grey'"
              label="啟用任務"
              inset
            />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="outlined" @click="$emit('cancel')"> 取消 </v-btn>
        <v-btn color="primary" type="submit" :loading="loading">
          {{ isEdit ? "更新" : "創建" }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>

  <!-- 模板預覽對話框 -->
  <v-dialog v-model="previewDialog" max-width="800">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-eye</v-icon>
        模板預覽
      </v-card-title>
      <v-card-text v-if="templatePreview">
        <div class="mb-4">
          <div class="text-subtitle-1 font-weight-bold mb-2">主旨：</div>
          <div class="text-body-1 pa-3 bg-grey-lighten-4 rounded">
            {{ templatePreview.subject }}
          </div>
        </div>
        <div class="mb-4">
          <div class="text-subtitle-1 font-weight-bold mb-2">內容：</div>
          <div class="text-body-1 pa-3 bg-grey-lighten-4 rounded" style="white-space: pre-wrap;">
            {{ templatePreview.body }}
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="previewDialog = false">關閉</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, reactive, ref, watch} from "vue";
import {useRouter} from "vue-router";
import type {ScheduledTaskCreate, ScheduledTaskResponse, TargetType,} from "@/models/scheduler";
import {TaskState} from "@/models/scheduler";
import {webhook_template} from "@/templates/webhook";
import {useEmailTemplateStore} from "@/stores/email_template";
import type {EmailTemplatePreviewResponse} from "@/models/email_template";
import Codemirror from "codemirror-editor-vue3";

const props = defineProps<{
	initialData?: ScheduledTaskResponse | Partial<ScheduledTaskCreate>;
	loading?: boolean;
}>();

const emit = defineEmits<{
	submit: [data: ScheduledTaskCreate];
	cancel: [];
	"open-schedule-wizard": [formData: Partial<ScheduledTaskCreate>];
}>();

// Router
const router = useRouter();

// Email 相關 store
const emailStore = useEmailTemplateStore();

const formRef = ref();
const targetInputText = ref("");
const targetInputError = ref("");
const cmRef = ref();
const cmOptions = reactive({
	mode: "application/json",
	theme: "tomorrow-night-bright",
	lineNumbers: true,
	lineWiseCopyCut: true,
	gutters: ["CodeMirror-lint-markers"],
	autoCloseBrackets: true,
	matchBrackets: true,
	lint: true,
});

// HTTP Method 欄位
const httpMethod = ref("GET");
const httpMethodOptions = ["GET", "POST", "PUT", "DELETE", "PATCH"];
const httpBodyText = ref(JSON.stringify(props.initialData?.target_input) || "");
const httpBodyError = ref("");

// HTTP Headers 欄位
const headerRows = ref([{ key: "", value: "" }]);
const commonHeaders = [
	"Authorization",
	"Host",
	"Accept-Language",
	"Accept-Encoding",
	"Cookie",
	"Cache-Control",
	"Content-Length",
	"Content-Type",
	"Accept",
	"Referer",
	"User-Agent",
	"WWW-Authenticate",
	"Proxy-Authenticate",
	"Proxy-Authorization",
	"Age",
];

// Email 相關欄位
const emailMode = ref<'template' | 'direct'>('template');
const selectedTemplateId = ref<number | string | null>(null);
const templateVariables = ref<Record<string, any>>({});
const templatePreview = ref<EmailTemplatePreviewResponse | null>(null);
const previewDialog = ref(false);
const previewLoading = ref(false);
const templatesLoading = ref(false);
const emailRecipients = ref<string[]>([]);
const emailCC = ref<string[]>([]);
const emailBCC = ref<string[]>([]);

const directEmailData = ref({
  subject: '',
  body: '',
  sender: ''
});

// 組合 headers 物件
const getHeadersObject = () => {
	const obj: Record<string, string> = {};
	headerRows.value.forEach((row) => {
		if (row.key) obj[row.key] = row.value;
	});
	return obj;
};

const selectedWebhookTemplate = ref(null);
const formData = ref({
	name: "",
	description: "",
	schedule_expression: "",
	timezone: "Asia/Taipei",
	target_type: "http" as TargetType,
	target_arn: "",
	target_input: {} as Object,
	max_retry_attempts: 3,
	state: TaskState.ENABLED,
});

const isEdit = computed(() => {
	return !!(props.initialData && "id" in props.initialData);
});

const targetTypeOptions = [
	{ title: "HTTP", value: "http" },
	{ title: "Webhook", value: "webhook" },
	{ title: "RabbitMQ", value: "rabbitmq" },
	{ title: "Email", value: "email" },
];

// Email 相關計算屬性
const templates = computed(() => emailStore.templates || []);
const selectedTemplate = computed(() => 
  typeof selectedTemplateId.value === 'number'
    ? templates.value.find(t => t.id === selectedTemplateId.value)
    : null
);

const templateOptions = computed(() =>
  templates.value
    .filter(t => t.is_active)
    .map(t => ({
      title: t.name,
      value: t.id,
      subtitle: t.description
    }))
);

// 增強的模板選項，包含創建新模板選項
const enhancedTemplateOptions = computed(() => [
  ...templateOptions.value,
  { 
    title: "➕ 創建新模板", 
    value: "create_new",
    subtitle: "創建一個新的 Email 模板"
  }
]);

const rules = {
	required: (value: any) => !!value || "此欄位為必填",
  emailList: (value: string[]) => {
    if (!value || value.length === 0) return true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return value.every(email => emailRegex.test(email)) || "請輸入有效的 Email 地址";
  }
};

// Email 相關方法
const onTemplateChange = async () => {
  if (selectedTemplateId.value === 'create_new') {
    // 當選擇創建新模板時，不需要載入模板數據
    return;
  }
  
  if (typeof selectedTemplateId.value === 'number') {
    const template = selectedTemplate.value;
    if (template) {
      // 初始化模板變數
      templateVariables.value = {};
      template.variables.forEach(variable => {
        if (variable.default_value) {
          templateVariables.value[variable.name] = variable.default_value;
        }
      });
    }
  } else {
    templateVariables.value = {};
  }
};

// 導航到創建模板頁面
const navigateToCreateTemplate = () => {
  // 在新標籤頁中打開模板創建頁面，這樣用戶不會丟失當前的表單數據
  const routeData = router.resolve('/email-templates/create');
  window.open(routeData.href, '_blank');
  
  // 重置選擇，讓用戶可以重新選擇
  selectedTemplateId.value = null;
};

const previewTemplate = async () => {
  if (!selectedTemplate.value) return;
  
  previewLoading.value = true;
  try {
    const variables = templateVariables.value;
    templatePreview.value = await emailStore.previewTemplate({
      "template_id": selectedTemplate.value.id,
      "variables": variables
    });
    previewDialog.value = true;
  } catch (error) {
    console.error('預覽模板失敗:', error);
  } finally {
    previewLoading.value = false;
  }
};

// JSON 格式化函數
const formatJSON = () => {
  try {
    const parsed = JSON.parse(httpBodyText.value);
    httpBodyText.value = JSON.stringify(parsed, null, 2);
    httpBodyError.value = "";
  } catch (error) {
    httpBodyError.value = "無效的 JSON 格式";
  }
};

// 監聽 HTTP 欄位變化
watch([httpMethod, headerRows], () => {
  if (formData.value.target_type === "http") {
    formData.value.target_input = {
      method: httpMethod.value,
      headers: getHeadersObject(),
      body: httpBodyText.value ? JSON.parse(httpBodyText.value) : {},
    };
  }
}, { deep: true });

// 監聽目標輸入變化
watch(targetInputText, (newValue) => {
  if (formData.value.target_type !== "http" && formData.value.target_type !== "webhook" && formData.value.target_type !== "email") {
    try {
      formData.value.target_input = newValue ? JSON.parse(newValue) : {};
      targetInputError.value = "";
    } catch (error) {
      targetInputError.value = "無效的 JSON 格式";
    }
  }
});

const openScheduleWizard = () => {
  emit("open-schedule-wizard", formData.value);
};

const handleSubmit = async () => {
  if (!formRef.value?.validate()) return;

  try {
    const payload = { ...formData.value };
    
    // 根據目標類型設置 target_input
    if (formData.value.target_type === "http") {
      payload.target_input = {
        method: httpMethod.value,
        headers: getHeadersObject(),
        body: httpBodyText.value ? JSON.parse(httpBodyText.value) : {},
      };
    } else if (formData.value.target_type === "webhook") {
      payload.target_input = httpBodyText.value ? JSON.parse(httpBodyText.value) : {};
    } else if (formData.value.target_type === "email") {
      // Email 類型的 target_input
      if (emailMode.value === 'template' && selectedTemplate.value) {
        payload.target_input = {
          use_template: true,
          template_id: selectedTemplate.value.id,
          template_variables: templateVariables.value,
          recipients: emailRecipients.value,
          cc: emailCC.value.length > 0 ? emailCC.value : undefined,
          bcc: emailBCC.value.length > 0 ? emailBCC.value : undefined,
        };
      } else {
        payload.target_input = {
          use_template: false,
          subject: directEmailData.value.subject,
          body: directEmailData.value.body,
          sender: directEmailData.value.sender || undefined,
          recipients: emailRecipients.value,
          cc: emailCC.value.length > 0 ? emailCC.value : undefined,
          bcc: emailBCC.value.length > 0 ? emailBCC.value : undefined,
        };
      }
    } else {
      payload.target_input = targetInputText.value ? JSON.parse(targetInputText.value) : {};
    }
    
    emit("submit", payload);
  } catch (error: any) {
    console.error("表單提交失敗:", error);
  }
};

const setScheduleExpression = (expression: string) => {
  formData.value.schedule_expression = expression;
};

// 監聽 initialData 變化
watch(
  () => props.initialData,
  (newData) => {
    if (newData) {
      Object.assign(formData.value, newData);
      
      // 如果是 HTTP 類型，解析 target_input
      if (newData.target_type === "http" && newData.target_input) {
        const input = newData.target_input as any;
        httpMethod.value = input.method || "GET";
        httpBodyText.value = JSON.stringify(input.body || {}, null, 2);
        
        // 設置 headers
        if (input.headers) {
          headerRows.value = Object.entries(input.headers).map(([key, value]) => ({
            key,
            value: value as string,
          }));
        }
      } else if (newData.target_type === "webhook" && newData.target_input) {
        httpBodyText.value = JSON.stringify(newData.target_input, null, 2);
      } else if (newData.target_type === "email" && newData.target_input) {
        // 處理 Email 類型的初始數據
        const emailInput = newData.target_input as any;
        if (emailInput.use_template) {
          emailMode.value = 'template';
          selectedTemplateId.value = emailInput.template_id;
          templateVariables.value = emailInput.template_variables || {};
        } else {
          emailMode.value = 'direct';
          directEmailData.value = {
            subject: emailInput.subject || '',
            body: emailInput.body || '',
            sender: emailInput.sender || ''
          };
        }
        emailRecipients.value = emailInput.recipients || [];
        emailCC.value = emailInput.cc || [];
        emailBCC.value = emailInput.bcc || [];
      } else {
        targetInputText.value = JSON.stringify(newData.target_input || {}, null, 2);
      }
    }
  },
  { immediate: true, deep: true }
);

// 監聽 formData 變化
watch(
  formData,
  () => {
    // 可以在這裡添加其他邏輯
  },
  { deep: true }
);

// 監聽目標類型變化，載入 Email 模板
watch(() => formData.value.target_type, async (newType) => {
  if (newType === 'email') {
    templatesLoading.value = true;
    try {
      await emailStore.fetchTemplates();
    } catch (error) {
      console.error('載入 Email 模板失敗:', error);
    } finally {
      templatesLoading.value = false;
    }
  }
});

// 組件掛載時載入 Email 模板（如果需要）
onMounted(async () => {
  if (formData.value.target_type === 'email') {
    templatesLoading.value = true;
    try {
      await emailStore.fetchTemplates();
    } catch (error) {
      console.error('載入 Email 模板失敗:', error);
    } finally {
      templatesLoading.value = false;
    }
  }
});

// 暴露方法給父組件
defineExpose({
  setScheduleExpression,
});
</script>

<style scoped>
.selected-card {
  outline: 4px solid #1976d2;
  outline-offset: -4px;
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.2);
  transition: 2ms;
}
</style>