export interface RateExpressionRequest {
  value: number
  unit: TimeUnit
}

export interface CronExpressionRequest {
  minute: string
  hour: string
  day: string
  month: string
  weekday: string
}

export interface QuickScheduleRequest {
  type: string
  time?: string
  weekdays?: number[]
  interval?: number
  unit?: string
}

export interface ScheduleExpressionResponse {
  expression: string
  type: ScheduleType
  description: string
  next_runs: string[]
}

export interface ScheduleValidationRequest {
  expression: string
}

export interface ScheduleValidationResponse {
  valid: boolean
  type?: ScheduleType
  description?: string
  error?: string
  next_runs?: string[]
}

export interface ScheduleTemplateResponse {
  name: string
  description: string
  expression: string
  type: ScheduleType
  category: string
}

export interface CronHelpResponse {
  field: CronField
  description: string
  range: string
  special_chars: string[]
  examples: Array<{ value: string; description: string }>
}

export enum ScheduleType {
  CRON = 'cron',
  RATE = 'rate',
}

export enum TimeUnit {
  SECOND = 'second',
  SECONDS = 'seconds',
  MINUTE = 'minute',
  MINUTES = 'minutes',
  HOUR = 'hour',
  HOURS = 'hours',
  DAY = 'day',
  DAYS = 'days',
}

export enum CronField {
  MINUTE = 'minute',
  HOUR = 'hour',
  DAY = 'day',
  MONTH = 'month',
  WEEKDAY = 'weekday',
}