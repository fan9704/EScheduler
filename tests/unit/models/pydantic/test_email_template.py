import pytest
from pydantic import ValidationError
from src.models.pydantic.email_template import TemplateVariable, EmailTaskCreate

# -------------------------
# TemplateVariable validator
# -------------------------
def test_template_variable_type_valid():
    var = TemplateVariable(name="email", type="email")
    assert var.type == "email"

def test_template_variable_type_invalid():
    with pytest.raises(ValidationError) as exc_info:
        TemplateVariable(name="foo", type="invalid_type")
    assert "變數類型必須是" in str(exc_info.value)

# -------------------------
# EmailTaskCreate validator
# -------------------------
def test_email_task_create_use_template_without_template_id():
    with pytest.raises(ValidationError) as exc_info:
        EmailTaskCreate(
            name="Task 1",
            schedule_expression="* * * * *",
            recipients=["test@example.com"],
            use_template=True,  # 開啟模板使用
            template_id=None,   # 卻沒提供 template_id
            subject="ignored"
        )
    assert "使用模板時必須提供 template_id" in str(exc_info.value)

def test_email_task_create_direct_email_without_subject():
    with pytest.raises(ValidationError) as exc_info:
        EmailTaskCreate(
            name="Task 2",
            schedule_expression="* * * * *",
            recipients=["test@example.com"],
            use_template=False,  # 不使用模板
            subject=None         # 沒提供 subject
        )
    assert "不使用模板時必須提供 subject" in str(exc_info.value)

def test_email_task_create_valid_cases():
    task = EmailTaskCreate(
        name="Task 3",
        schedule_expression="* * * * *",
        recipients=["test@example.com"],
        use_template=True,
        template_id=1
    )
    assert task.use_template is True
    assert task.template_id == 1
