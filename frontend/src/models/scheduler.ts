export interface ScheduledTaskCreate {
  name: string;
  description?: string;
  schedule_expression: string;
  timezone: string;
  target_type: TargetType;
  target_arn: string;
  target_input?: Record<string, any>;
  max_retry_attempts?: number;
  retry_policy?: Record<string, any>;
  dead_letter_config?: Record<string, any>;
  state?: TaskState;
}

export interface ScheduledTaskUpdate {
  name?: string;
  description?: string;
  schedule_expression?: string;
  timezone?: string;
  target_type?: TargetType;
  target_arn?: string;
  target_input?: Record<string, any>;
  state?: TaskState;
  max_retry_attempts?: number;
  retry_policy?: Record<string, any>;
  dead_letter_config?: Record<string, any>;
}

export interface ScheduledTaskResponse {
  id: number;
  name: string;
  description?: string;
  schedule_expression: string;
  timezone: string;
  target_type: string;
  target_arn: string;
  target_input?: Record<string, any>;
  state: TaskState; // 改成 TaskState enum
  last_execution_time?: string;
  next_execution_time?: string;
  execution_count: number;
  max_retry_attempts: number;
  retry_policy?: Record<string, any>;
  dead_letter_config?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TaskStateUpdateRequest {
  state: TaskState;
}

export interface SchedulerStatsResponse {
  total_tasks: number;
  enabled_tasks: number;
  disabled_tasks: number;
  total_executions_today: number;
  successful_executions_today: number;
  failed_executions_today: number;
}

export enum TaskState {
  ENABLED = 'ENABLED',
  DISABLED = 'DISABLED',
  PAUSED = 'PAUSED',
}

export enum TargetType {
  HTTP = 'http',
  WEBHOOK = 'webhook',
  RABBITMQ = 'rabbitmq',
  EMAIL = 'email',
}
