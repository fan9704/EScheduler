// Email Template 變數定義
export interface TemplateVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'email' | 'url';
  description?: string;
  required: boolean;
  default_value?: any;
  validation_rules?: Record<string, any>;
}

// Email Template 創建請求
export interface EmailTemplateCreate {
  name: string;
  description?: string;
  subject_template: string;
  body_template: string;
  html_template?: string;
  variables: TemplateVariable[];
  default_sender?: string;
  default_cc?: string[];
  default_bcc?: string[];
  is_active: boolean;
}

// Email Template 更新請求
export interface EmailTemplateUpdate {
  name?: string;
  description?: string;
  subject_template?: string;
  body_template?: string;
  html_template?: string;
  variables?: TemplateVariable[];
  default_sender?: string;
  default_cc?: string[];
  default_bcc?: string[];
  is_active?: boolean;
}

// Email Template 回應
export interface EmailTemplateResponse {
  id: number;
  name: string;
  description?: string;
  subject_template: string;
  body_template: string;
  html_template?: string;
  variables: TemplateVariable[];
  default_sender?: string;
  default_cc?: string[];
  default_bcc?: string[];
  is_active: boolean;
  usage_count: number;
  last_used_at?: string;
  created_at: string;
  updated_at: string;
}

// Email Template 預覽請求
export interface EmailTemplatePreview {
  subject_template?: string;
  body_template?: string;
  html_template?: string;
  variables: Record<string, any>;
}

// Email Template 預覽回應
export interface EmailTemplatePreviewResponse {
  subject: string;
  body: string;
  html_body?: string;
  variables_used: string[];
}

// Email Task 創建請求
export interface EmailTaskCreate {
  name: string;
  description?: string;
  schedule_expression: string;
  timezone: string;
  use_template: boolean;
  template_id?: number;
  template_variables?: Record<string, any>;
  subject?: string;
  body?: string;
  html_body?: string;
  recipients: string[];
  cc?: string[];
  bcc?: string[];
  sender?: string;
  max_retry_attempts?: number;
  state?: TaskState;
}

// Email Task 更新請求
export interface EmailTaskUpdate {
  name?: string;
  description?: string;
  schedule_expression?: string;
  timezone?: string;
  use_template?: boolean;
  template_id?: number;
  template_variables?: Record<string, any>;
  subject?: string;
  body?: string;
  html_body?: string;
  recipients?: string[];
  cc?: string[];
  bcc?: string[];
  sender?: string;
  max_retry_attempts?: number;
  state?: TaskState;
}

// Email Task 回應
export interface EmailTaskResponse {
  id: number;
  name: string;
  description?: string;
  schedule_expression: string;
  timezone: string;
  use_template: boolean;
  template_id?: number;
  template_name?: string;
  template_variables?: Record<string, any>;
  subject?: string;
  body?: string;
  html_body?: string;
  recipients: string[];
  cc?: string[];
  bcc?: string[];
  sender?: string;
  state: TaskState;
  last_execution_time?: string;
  next_execution_time?: string;
  execution_count: number;
  max_retry_attempts: number;
  created_at: string;
  updated_at: string;
}

// Email 立即發送請求
export interface EmailSendRequest {
  use_template: boolean;
  template_id?: number;
  template_variables?: Record<string, any>;
  subject?: string;
  body?: string;
  html_body?: string;
  recipients: string[];
  cc?: string[];
  bcc?: string[];
  sender?: string;
}

// Email 發送回應
export interface EmailSendResponse {
  success: boolean;
  message: string;
  usage_id?: number;
  execution_time: number;
  data?: Record<string, any>;
}

// 從 scheduler.ts 導入需要的類型
export enum TaskState {
  ENABLED = "ENABLED",
  DISABLED = "DISABLED",
  PAUSED = "PAUSED",
}

// Email Template 使用統計
export interface EmailTemplateUsageStats {
  template_id: number;
  template_name: string;
  total_usage: number;
  successful_sends: number;
  failed_sends: number;
  last_used_at?: string;
  usage_by_day: Array<{
    date: string;
    count: number;
  }>;
}

// Email Template 列表查詢參數
export interface EmailTemplateListParams {
  is_active?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}