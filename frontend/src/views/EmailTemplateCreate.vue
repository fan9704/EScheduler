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
          <h1 class="text-h4 font-weight-bold">創建 Email 模板</h1>
        </div>
        <p class="text-body-2 text-medium-emphasis">創建新的 Email 模板</p>
      </v-col>
    </v-row>

    <EmailTemplateForm
      :initial-data="initialData"
      :loading="saving"
      @submit="handleSubmit"
      @cancel="handleCancel"
      @show-snackbar="showSnackbar"
    />

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
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEmailTemplateStore } from '@/stores/email_template';
import EmailTemplateForm from '@/components/email_template/EmailTemplateForm.vue';
import type { EmailTemplateCreate } from '@/models/email_template';

const route = useRoute();
const router = useRouter();
const emailStore = useEmailTemplateStore();

// 響應式數據
const saving = ref(false);

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
});

// 計算屬性
const initialData = computed(() => {
  // 可以根據查詢參數設置初始數據
  return {
    is_active: true
  };
});

// 方法
async function handleSubmit(templateData: EmailTemplateCreate) {
  saving.value = true;
  try {
    const newTemplate = await emailStore.createTemplate(templateData);
    showSnackbar('模板創建成功', 'success');
    await router.push(`/email-templates/${newTemplate.id}/edit`);
  } catch (error) {
    console.error('創建模板失敗:', error);
    showSnackbar('模板創建失敗', 'error');
  } finally {
    saving.value = false;
  }
}

function handleCancel() {
  router.back();
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = {
    show: true,
    message,
    color
  };
}
</script>
<style scoped>
.border {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>
