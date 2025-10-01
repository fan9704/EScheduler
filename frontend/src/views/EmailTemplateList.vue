<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h5">Email 模板管理</span>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="router.push('/email-templates/create')"
            >
              新增模板
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- 搜索和過濾 -->
            <v-row class="mb-4">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="searchQuery"
                  label="搜索模板"
                  variant="outlined"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                  density="compact"
                />
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="statusFilter"
                  label="狀態篩選"
                  :items="statusOptions"
                  variant="outlined"
                  clearable
                  density="compact"
                />
              </v-col>
            </v-row>

            <!-- 模板列表 -->
            <v-data-table
              :headers="headers"
              :items="filteredTemplates"
              :loading="loading"
              item-value="id"
              class="elevation-1"
            >
              <!-- 狀態欄位 -->
              <template #item.is_active="{ item }">
                <v-chip
                  :color="item.is_active ? 'success' : 'error'"
                  size="small"
                  variant="flat"
                >
                  {{ item.is_active ? '啟用' : '停用' }}
                </v-chip>
              </template>

              <!-- 變數欄位 -->
              <template #item.variables="{ item }">
                <v-tooltip>
                  <template #activator="{ props }">
                    <v-chip
                      v-bind="props"
                      size="small"
                      variant="outlined"
                      color="primary"
                    >
                      {{ item.variables.length }} 個變數
                    </v-chip>
                  </template>
                  <div>
                    <div v-for="variable in item.variables" :key="variable.name">
                      <strong>{{ variable.name }}</strong> ({{ variable.type }})
                      <span v-if="variable.required" class="text-red">*</span>
                    </div>
                  </div>
                </v-tooltip>
              </template>

              <!-- 使用次數 -->
              <template #item.usage_count="{ item }">
                <v-chip
                  :color="item.usage_count > 0 ? 'success' : 'grey'"
                  size="small"
                  variant="outlined"
                >
                  {{ item.usage_count }}
                </v-chip>
              </template>

              <!-- 最後使用時間 -->
              <template #item.last_used_at="{ item }">
                <span v-if="item.last_used_at">
                  {{ formatDateTime(item.last_used_at) }}
                </span>
                <span v-else class="text-grey">從未使用</span>
              </template>

              <!-- 操作欄位 -->
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  color="info"
                  variant="text"
                  @click="previewTemplate(item.id)"
                  title="預覽"
                />
                <v-btn
                  icon="mdi-content-copy"
                  size="small"
                  color="secondary"
                  variant="text"
                  @click="duplicateTemplate(item)"
                  title="複製"
                />
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  color="primary"
                  variant="text"
                  @click="editTemplate(item.id)"
                  title="編輯"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  variant="text"
                  @click="confirmDelete(item)"
                  title="刪除"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 刪除確認對話框 -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>確認刪除</v-card-title>
        <v-card-text>
          確定要刪除模板「{{ templateToDelete?.name }}」嗎？此操作無法復原。
          <v-alert
            v-if="templateToDelete?.usage_count && templateToDelete.usage_count > 0"
            type="warning"
            variant="outlined"
            class="mt-3"
          >
            此模板已被使用 {{ templateToDelete.usage_count }} 次，刪除後可能影響相關任務。
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">取消</v-btn>
          <v-btn
            color="error"
            @click="deleteTemplate"
            :loading="deleting"
          >
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 複製模板對話框 -->
    <v-dialog v-model="duplicateDialog" max-width="500">
      <v-card>
        <v-card-title>複製模板</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="duplicateName"
            label="新模板名稱"
            variant="outlined"
            :rules="[v => !!v || '請輸入模板名稱']"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="duplicateDialog = false">取消</v-btn>
          <v-btn
            color="primary"
            @click="confirmDuplicate"
            :loading="duplicating"
            :disabled="!duplicateName"
          >
            複製
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


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
import { useRouter } from 'vue-router';
import { useEmailTemplateStore } from '@/stores/email_template';
import type { EmailTemplateResponse } from '@/models/email_template';

const router = useRouter();
const emailStore = useEmailTemplateStore();

const headers = ref<Array<{
  title: string;
  key: string;
  align?: 'start' | 'center' | 'end';
}>>([
  {title:"ID",key:"id",align:"center"},
  {title:"模板名稱",key:"name",align:"center"},
  {title:"描述",key:"description",align:"center"},
  {title:"主題模板",key:"subject_template",align:"center"},
  {title:"狀態",key:"is_active",align:"center"},
  {title:"操作",key:"actions",align:"center"}
])

const statusOptions = ref([
  {title:"全部",value:null},
  {title:"啟用",value:true},
  {title:"停用",value:false}
])
// 響應式數據
const searchQuery = ref('');
const statusFilter = ref<boolean | null>(null);
const deleteDialog = ref(false);
const duplicateDialog = ref(false);
const templateToDelete = ref<EmailTemplateResponse | null>(null);
const templateToDuplicate = ref<EmailTemplateResponse | null>(null);
const duplicateName = ref('');
const deleting = ref(false);
const duplicating = ref(false);

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const loading = computed(() => emailStore.loading);
const templates = computed(() => emailStore.templates);

const filteredTemplates = computed(() => {
  let filtered = templates.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(template =>
      template.name.toLowerCase().includes(query) ||
      template.description?.toLowerCase().includes(query) ||
      template.subject_template.toLowerCase().includes(query)
    );
  }

  if (statusFilter.value !== null) {
    filtered = filtered.filter(template => template.is_active === statusFilter.value);
  }

  return filtered;
});

// 方法
function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-TW');
}

async function refreshTemplates() {
  try {
    await emailStore.fetchTemplates();
  } catch (error) {
    showSnackbar('重新整理失敗', 'error');
  }
}

function previewTemplate(templateId: number) {
  router.push(`/email-templates/${templateId}/preview`);
}

function editTemplate(templateId: number) {
  router.push(`/email-templates/${templateId}/edit`);
}

function duplicateTemplate(template: EmailTemplateResponse) {
  templateToDuplicate.value = template;
  duplicateName.value = `${template.name} (副本)`;
  duplicateDialog.value = true;
}

async function confirmDuplicate() {
  if (!templateToDuplicate.value || !duplicateName.value) return;

  duplicating.value = true;
  try {
    const duplicateData = {
      ...templateToDuplicate.value,
      name: duplicateName.value,
      is_active: false // 新複製的模板預設為停用
    };
    delete (duplicateData as any).id;
    delete (duplicateData as any).usage_count;
    delete (duplicateData as any).last_used_at;
    delete (duplicateData as any).created_at;
    delete (duplicateData as any).updated_at;

    await emailStore.createTemplate(duplicateData);
    showSnackbar('模板複製成功', 'success');
    duplicateDialog.value = false;
    templateToDuplicate.value = null;
    duplicateName.value = '';
  } catch (error) {
    showSnackbar('模板複製失敗', 'error');
  } finally {
    duplicating.value = false;
  }
}

function confirmDelete(template: EmailTemplateResponse) {
  templateToDelete.value = template;
  deleteDialog.value = true;
}

async function deleteTemplate() {
  if (!templateToDelete.value) return;

  deleting.value = true;
  try {
    await emailStore.deleteTemplate(templateToDelete.value.id);
    showSnackbar('模板刪除成功', 'success');
    deleteDialog.value = false;
    templateToDelete.value = null;
  } catch (error) {
    showSnackbar('模板刪除失敗', 'error');
  } finally {
    deleting.value = false;
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
  await refreshTemplates();
});
</script>

<style scoped>
</style>