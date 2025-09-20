import { apiService } from './api';
import type {
  EmailTemplateCreate,
  EmailTemplateUpdate,
  EmailTemplateResponse,
  EmailTemplatePreview,
  EmailTemplatePreviewResponse,
  EmailTaskCreate,
  EmailTaskUpdate,
  EmailTaskResponse,
  EmailSendRequest,
  EmailSendResponse,
  EmailTemplateListParams
} from '@/models/email_template';

export class EmailTemplateService {
  private readonly baseUrl = '/email-templates';

  // Email Template CRUD 操作
  async createTemplate(data: EmailTemplateCreate): Promise<EmailTemplateResponse> {
    return apiService.post<EmailTemplateResponse>(this.baseUrl, data);
  }

  async listTemplates(params?: EmailTemplateListParams): Promise<EmailTemplateResponse[]> {
    return apiService.get<EmailTemplateResponse[]>(this.baseUrl, params);
  }

  async getTemplate(id: number): Promise<EmailTemplateResponse> {
    return apiService.get<EmailTemplateResponse>(`${this.baseUrl}/${id}`);
  }

  async updateTemplate(id: number, data: EmailTemplateUpdate): Promise<EmailTemplateResponse> {
    return apiService.put<EmailTemplateResponse>(`${this.baseUrl}/${id}`, data);
  }

  async deleteTemplate(id: number): Promise<void> {
    return apiService.delete<void>(`${this.baseUrl}/${id}`);
  }

  // Email Template 預覽
  async previewTemplate(previewData: EmailTemplatePreview): Promise<EmailTemplatePreviewResponse> {
    return apiService.post<EmailTemplatePreviewResponse>(
      `${this.baseUrl}/preview`,
      previewData
    );
  }

  // 立即發送 Email
  async sendEmail(data: EmailSendRequest): Promise<EmailSendResponse> {
    return apiService.post<EmailSendResponse>(`${this.baseUrl}/send`, data);
  }

}

// Email Task 相關服務（使用現有的 scheduler API）
export class EmailTaskService {
  private readonly baseUrl = '/scheduler';

  async createEmailTask(data: EmailTaskCreate): Promise<EmailTaskResponse> {
    // 轉換為 ScheduledTaskCreate 格式
    const taskData = {
      name: data.name,
      description: data.description,
      schedule_expression: data.schedule_expression,
      timezone: data.timezone,
      target_type: 'email',
      target_arn: data.recipients[0], // 使用第一個收件人作為 target_arn
      target_input: {
        use_template: data.use_template,
        template_id: data.template_id,
        template_variables: data.template_variables,
        subject: data.subject,
        body: data.body,
        html_body: data.html_body,
        recipients: data.recipients,
        cc: data.cc,
        bcc: data.bcc,
        sender: data.sender
      }
    };

    return apiService.post<EmailTaskResponse>(this.baseUrl, taskData);
  }

  async updateEmailTask(id: number, data: EmailTaskUpdate): Promise<EmailTaskResponse> {
    // 轉換為 ScheduledTaskUpdate 格式
    const taskData = {
      name: data.name,
      description: data.description,
      schedule_expression: data.schedule_expression,
      timezone: data.timezone,
      target_input: {
        use_template: data.use_template,
        template_id: data.template_id,
        template_variables: data.template_variables,
        subject: data.subject,
        body: data.body,
        html_body: data.html_body,
        recipients: data.recipients,
        cc: data.cc,
        bcc: data.bcc,
        sender: data.sender,
      },
    };

    return apiService.put<EmailTaskResponse>(`${this.baseUrl}/${id}`, taskData);
  }

  async getEmailTasks(): Promise<EmailTaskResponse[]> {
    return apiService.get<EmailTaskResponse[]>(`${this.baseUrl}?target_type=email`);
  }

  async getEmailTask(id: number): Promise<EmailTaskResponse> {
    return apiService.get<EmailTaskResponse>(`${this.baseUrl}/${id}`);
  }

  async deleteEmailTask(id: number): Promise<void> {
    return apiService.delete<void>(`${this.baseUrl}/${id}`);
  }

  async executeEmailTask(id: number): Promise<void> {
    return apiService.post<void>(`${this.baseUrl}/${id}/execute`);
  }

  async updateEmailTaskState(id: number, state: string): Promise<void> {
    return apiService.put<void>(`${this.baseUrl}/${id}/state`, { state });
  }
}

export const emailTemplateService = new EmailTemplateService();
export const emailTaskService = new EmailTaskService();