import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { 
  EmailTemplateResponse, 
  EmailTemplateCreate, 
  EmailTemplateUpdate,
  EmailTemplatePreview,
  EmailTemplateListParams,
  EmailSendRequest,
  EmailTaskCreate,
  EmailTaskUpdate,
  EmailTaskResponse
} from '@/models/email_template';
import { emailTemplateService, emailTaskService } from '@/services/email_template';
import schedulerService from '@/services/scheduler';

export const useEmailTemplateStore = defineStore('emailTemplate', () => {
  // State
  const templates = ref<EmailTemplateResponse[]>([]);
  const currentTemplate = ref<EmailTemplateResponse | null>(null);
  const emailTasks = ref<EmailTaskResponse[]>([]);
  const currentEmailTask = ref<EmailTaskResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeTemplates = computed(() => 
    templates.value.filter(template => template.is_active)
  );

  const templateById = computed(() => (id: number) => 
    templates.value.find(template => template.id === id)
  );

  // Actions
  async function fetchTemplates(params?: EmailTemplateListParams) {
    loading.value = true;
    error.value = null;
    try {
      templates.value = await emailTemplateService.listTemplates(params);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取模板列表失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getTemplate(id: number) {
    loading.value = true;
    error.value = null;
    try {
      currentTemplate.value = await emailTemplateService.getTemplate(id);
      return currentTemplate.value;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取模板失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createTemplate(data: EmailTemplateCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newTemplate = await emailTemplateService.createTemplate(data);
      templates.value.push(newTemplate);
      return newTemplate;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '創建模板失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateTemplate(id: number, data: EmailTemplateUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updatedTemplate = await emailTemplateService.updateTemplate(id, data);
      const index = templates.value.findIndex(t => t.id === id);
      if (index !== -1) {
        templates.value[index] = updatedTemplate;
      }
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = updatedTemplate;
      }
      return updatedTemplate;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新模板失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteTemplate(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await emailTemplateService.deleteTemplate(id);
      templates.value = templates.value.filter(t => t.id !== id);
      if (currentTemplate.value?.id === id) {
        currentTemplate.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刪除模板失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function previewTemplate(previewData: EmailTemplatePreview | { template_id: number; variables: Record<string, any> }) {
    loading.value = true;
    error.value = null;
    try {
        return await emailTemplateService.previewTemplate(previewData as EmailTemplatePreview);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '預覽模板失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // 移除 previewTemplateContent 方法，因為現在統一使用 previewTemplate

  async function sendEmail(data: EmailSendRequest) {
    loading.value = true;
    error.value = null;
    try {
      return await emailTemplateService.sendEmail(data);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '發送郵件失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Email Task Actions
  async function fetchEmailTasks() {
    loading.value = true;
    error.value = null;
    try {
      emailTasks.value = await emailTaskService.getEmailTasks();
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取 Email 任務列表失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getEmailTask(id: number) {
    loading.value = true;
    error.value = null;
    try {
      currentEmailTask.value = await emailTaskService.getEmailTask(id);
      return currentEmailTask.value;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '獲取 Email 任務失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createEmailTask(data: EmailTaskCreate) {
    loading.value = true;
    error.value = null;
    try {
      const newTask = await emailTaskService.createEmailTask(data);
      emailTasks.value.push(newTask);
      return newTask;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '創建 Email 任務失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateEmailTask(id: number, data: EmailTaskUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updatedTask = await emailTaskService.updateEmailTask(id, data);
      const index = emailTasks.value.findIndex(t => t.id === id);
      if (index !== -1) {
        emailTasks.value[index] = updatedTask;
      }
      if (currentEmailTask.value?.id === id) {
        currentEmailTask.value = updatedTask;
      }
      return updatedTask;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '更新 Email 任務失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteEmailTask(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await emailTaskService.deleteEmailTask(id);
      emailTasks.value = emailTasks.value.filter(t => t.id !== id);
      if (currentEmailTask.value?.id === id) {
        currentEmailTask.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刪除 Email 任務失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function executeEmailTask(id: number) {
    loading.value = true;
    error.value = null;
    try {
      await schedulerService.triggerTask(id);
    } catch (err) {
      error.value = err instanceof Error ? err.message : '執行 Email 任務失敗';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  return {
    // State
    templates,
    currentTemplate,
    emailTasks,
    currentEmailTask,
    loading,
    error,
    
    // Getters
    activeTemplates,
    templateById,
    
    // Actions
    fetchTemplates,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    previewTemplate,
    sendEmail,
    fetchEmailTasks,
    getEmailTask,
    createEmailTask,
    updateEmailTask,
    deleteEmailTask,
    executeEmailTask,
    clearError
  };
});