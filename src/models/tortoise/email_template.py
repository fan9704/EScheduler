from tortoise import fields, models
from typing import Dict, Any


class EmailTemplate(models.Model):
    """Email 模板模型"""
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255, unique=True, description="模板名稱")
    description = fields.TextField(null=True, description="模板描述")
    
    # 模板內容
    subject_template = fields.CharField(max_length=500, description="主旨模板")
    body_template = fields.TextField(description="內容模板 (純文字)")
    html_template = fields.TextField(null=True, description="HTML 模板")
    
    # 模板變數定義
    variables = fields.JSONField(description="模板變數定義 (變數名稱、類型、預設值等)")
    
    # 預設設定
    default_sender = fields.CharField(max_length=255, null=True, description="預設寄件人")
    default_cc = fields.JSONField(null=True, description="預設副本收件人列表")
    default_bcc = fields.JSONField(null=True, description="預設密件副本收件人列表")
    
    # 狀態管理
    is_active = fields.BooleanField(default=True, description="是否啟用")
    is_system_template = fields.BooleanField(default=False, description="是否為系統模板")
    
    # 使用統計
    usage_count = fields.IntField(default=0, description="使用次數")
    last_used_at = fields.DatetimeField(null=True, description="最後使用時間")
    
    # 時間戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "email_templates"
        
    def __str__(self):
        return f"EmailTemplate({self.name})"
    
    def get_variable_names(self) -> list:
        """取得模板中定義的變數名稱列表"""
        if not self.variables:
            return []
        return [var.get('name') for var in self.variables if var.get('name')]
    
    def validate_variables(self, provided_vars: Dict[str, Any]) -> Dict[str, str]:
        """驗證提供的變數是否符合模板要求"""
        errors = {}
        
        if not self.variables:
            return errors
            
        for var_def in self.variables:
            var_name = var_def.get('name')
            var_type = var_def.get('type', 'string')
            is_required = var_def.get('required', False)
            
            if is_required and var_name not in provided_vars:
                errors[var_name] = f"必填變數 '{var_name}' 未提供"
                continue
                
            if var_name in provided_vars:
                value = provided_vars[var_name]
                if var_type == 'email' and value:
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, str(value)):
                        errors[var_name] = f"變數 '{var_name}' 不是有效的 email 格式"
                elif var_type == 'number' and value is not None:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors[var_name] = f"變數 '{var_name}' 必須是數字"
                        
        return errors


class EmailTemplateUsage(models.Model):
    """Email 模板使用記錄"""
    id = fields.IntField(primary_key=True)
    template = fields.ForeignKeyField("models.EmailTemplate", related_name="usage_records")
    task = fields.ForeignKeyField("models.ScheduledTask", related_name="email_template_usages", null=True)
    
    # 使用時的變數值
    variables_used = fields.JSONField(description="使用時提供的變數值")
    
    # 實際發送的內容 (渲染後)
    rendered_subject = fields.CharField(max_length=500, description="渲染後的主旨")
    rendered_body = fields.TextField(description="渲染後的內容")
    rendered_html = fields.TextField(null=True, description="渲染後的 HTML")
    
    # 發送資訊
    recipients = fields.JSONField(description="收件人列表")
    cc_recipients = fields.JSONField(null=True, description="副本收件人列表")
    bcc_recipients = fields.JSONField(null=True, description="密件副本收件人列表")
    sender = fields.CharField(max_length=255, description="寄件人")
    
    # 發送結果
    is_successful = fields.BooleanField(description="是否發送成功")
    error_message = fields.TextField(null=True, description="錯誤訊息")
    
    # 時間戳
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "email_template_usages"
        
    def __str__(self):
        return f"EmailTemplateUsage({self.template.name} - {self.created_at})"