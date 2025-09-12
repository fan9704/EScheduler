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
              <v-item v-for="template in webhookTemplates" v-slot="{ isSelected, toggle }" :key="template.id" >
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
                  style="margin-top: 0px"
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
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, reactive, onMounted } from "vue";
import type {
  ScheduledTaskCreate,
  ScheduledTaskResponse,
  TargetType,
} from "@/models/scheduler";
import { TaskState } from "@/models/scheduler";
import DiscordIcon from "@/assets/icons/discord.webp"
import SlackIcon from "@/assets/icons/slack.webp"
import TeamsIcon from "@/assets/icons/teams.webp"
import TelegramIcon from "@/assets/icons/telegram.webp"
const props = defineProps<{
  initialData?: ScheduledTaskResponse | Partial<ScheduledTaskCreate>;
  loading?: boolean;
}>();

const emit = defineEmits<{
  submit: [data: ScheduledTaskCreate];
  cancel: [];
  "open-schedule-wizard": [formData: Partial<ScheduledTaskCreate>];
}>();

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
const httpHeadersText = ref("");
const httpHeadersError = ref("");
const httpBodyText = ref("");
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
// 組合 headers 物件
const getHeadersObject = () => {
  const obj: Record<string, string> = {};
  headerRows.value.forEach((row) => {
    if (row.key) obj[row.key] = row.value;
  });
  return obj;
};

const webhookTemplates = [
  {
    "id": 1,
    "name": "Discord",
    "image": DiscordIcon,
    "body":{
      "content": "Hello from EScheduler!",
      "username": "EScheduler Bot",
      "avatar_url": "https://private-user-images.githubusercontent.com/76801598/481695339-a4761d01-3fba-46c1-b58a-8575651da82c.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTc2NDY1MTEsIm5iZiI6MTc1NzY0NjIxMSwicGF0aCI6Ii83NjgwMTU5OC80ODE2OTUzMzktYTQ3NjFkMDEtM2ZiYS00NmMxLWI1OGEtODU3NTY1MWRhODJjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA5MTIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwOTEyVDAzMDMzMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQxN2VmOWM1ZjQyYjQzNDc4MDU2MTFlYTA5YmVmMzYwMmZkYTZkYmI4YmM2NzRiZTZhNDg3MmM5YTJmZjYyNjYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.744R28_DppAth7R01DVR7KO7WxF4LfQGtZ3WCottNfk",
      "embeds": [
        {
          "title": "Task Notification",
          "description": "This is a notification from your scheduled task.",
          "color": 5814783
        }
      ],
      "allow_mentions": {
        "parse": ["users", "roles", "everyone"]
      }
    }
  },
  {
    "id": 2,
    "name": "Slack",
    "image": SlackIcon,
    "body":{}
  },
  {
    "id": 3,
    "name": "Microsoft Teams",
    "image": TeamsIcon,
    "body":{}
  },
  {
    "id": 4,
    "name": "Telegram",
    "image": TelegramIcon,
    "body":{}
  }
]
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

const rules = {
  required: (value: any) => !!value || "此欄位為必填",
};

// 監聽初始數據變化
watch(
  () => props.initialData,
  (newData) => {
    console.log("TaskForm 收到新的 initialData:", newData);
    if (newData) {
      nextTick(() => {
        formData.value = {
          name: newData.name || "",
          description: newData.description || "",
          schedule_expression: newData.schedule_expression || "",
          timezone: newData.timezone || "Asia/Taipei",
          target_type: (newData.target_type as TargetType) || "http",
          target_arn: newData.target_arn || "",
          target_input: newData.target_input || {},
          max_retry_attempts: newData.max_retry_attempts || 3,
          state:
            newData.state !== undefined ? newData.state : TaskState.ENABLED,
        };
        // HTTP 類型時分解 method/headers/body
        if (formData.value.target_type === "http") {
          httpMethod.value = newData.target_input?.method || "GET";
          httpHeadersText.value = newData.target_input?.headers
            ? JSON.stringify(newData.target_input.headers, null, 2)
            : "";
          httpBodyText.value = newData.target_input?.body
            ? JSON.stringify(newData.target_input.body, null, 2)
            : "";
        } else {
          targetInputText.value = JSON.stringify(
            newData.target_input || {},
            null,
            2
          );
        }
        console.log("TaskForm 更新後的 formData:", formData.value);
      });
    }
  },
  { immediate: true, deep: true }
);

// 監聽 HTTP 欄位變化
watch(
  [httpMethod, headerRows, httpBodyText],
  ([method, headers, body]) => {
    if (formData.value.target_type === "http") {
      let bodyObj = {};
      if (body.trim()) {
        try {
          bodyObj = JSON.parse(body);
        } catch (e) {}
      }
      formData.value.target_input = {
        method,
        headers: getHeadersObject(),
        body: bodyObj,
      };
    }
  },
  { deep: true }
);

// 監聽 target_input 變化 (非 HTTP 類型)
watch(targetInputText, (newValue) => {
  if (formData.value.target_type !== "http") {
    targetInputError.value = "";
    try {
      formData.value.target_input = newValue ? JSON.parse(newValue) : {};
    } catch (error: any) {
      targetInputError.value = "JSON 格式錯誤: " + error.message;
    }
  }
});

const openScheduleWizard = () => {
  console.log("TaskForm 點擊排程精靈按鈕，當前數據:", formData.value);
  emit("open-schedule-wizard", { ...formData.value });
};

const handleSubmit = async () => {
  const { valid } = await formRef.value.validate();
  // 檢查 JSON 欄位錯誤
  if (formData.value.target_type === "http") {
    if (httpHeadersError.value || httpBodyError.value) return;
  } else {
    if (targetInputError.value) return;
  }
  if (valid) {
    const payload = {
      ...formData.value,
    };
    console.log("TaskForm 提交數據:", payload);
    emit("submit", payload);
  }
};

// 🔥 新增：設置排程表達式的方法
const setScheduleExpression = (expression: string) => {
  console.log("TaskForm.setScheduleExpression 被調用，表達式:", expression);
  formData.value.schedule_expression = expression;

  // 使用 nextTick 確保 DOM 更新
  nextTick(() => {
    console.log(
      "TaskForm.setScheduleExpression 完成，當前 formData:",
      formData.value
    );
  });
};
const formatJSON = () =>{
  if (!httpBodyText.value) return;
  const parsed = JSON.parse(httpBodyText.value);
  httpBodyText.value= JSON.stringify(parsed, null, 2);
}
// 🔥 暴露方法給父組件
defineExpose({
  setScheduleExpression,
});

onMounted(() => {
  formatJSON();
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