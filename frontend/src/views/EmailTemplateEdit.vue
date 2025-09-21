<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center mb-4">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="router.back()"
            class="me-2"
          />
          <h1 class="text-h4 font-weight-bold">編輯 Email 模板</h1>
        </div>
        <p class="text-body-2 text-medium-emphasis">編輯現有的 Email 模板</p>
      </v-col>
    </v-row>

    <!-- 載入狀態 -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" />
        <div class="mt-2">載入模板資料中...</div>
      </v-col>
    </v-row>

    <!-- 模板表單 -->
    <EmailTemplateForm
      v-else-if="templateData"
      :initial-data="templateData"
      :loading="saving"
      @submit="handleSubmit"
      @cancel="handleCancel"
      @show-snackbar="showSnackbar"
    />

    <!-- 錯誤狀態 -->
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>

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
import EmailTemplateForm from '@/components/email_template/EmailTemplateForm.vue';
import type { EmailTemplateUpdate, EmailTemplateResponse } from '@/models/email_template';

const route = useRoute();
const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const templateData = ref<EmailTemplateResponse | null>(null);

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const templateId = computed(() => Number(route.params.id));

// 方法
async function loadTemplate() {
  try {
    loading.value = true;
    error.value = '';
    
    const template = await emailStore.getTemplate(templateId.value);
    templateData.value = template;
  } catch (err) {
    console.error('載入模板失敗:', err);
    error.value = '載入模板資料失敗，請稍後重試';
  } finally {
    loading.value = false;
  }
}

async function handleSubmit(templateUpdateData: EmailTemplateUpdate) {
  if (!templateData.value) return;
  
  saving.value = true;
  try {
    await emailStore.updateTemplate(templateData.value.id, templateUpdateData);
    showSnackbar('模板更新成功', 'success');
    router.push('/email-templates');
  } catch (error) {
    console.error('更新模板失敗:', error);
    showSnackbar('模板更新失敗', 'error');
  } finally {
    saving.value = false;
  }
}

function handleCancel() {
  router.push('/email-templates');
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