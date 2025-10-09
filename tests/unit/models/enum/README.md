# 是否需要測試 Enum？

不需要針對 Enum 本身寫單元測試。

原因如下

- Enum 是 標準庫（enum.Enum） 功能，行為穩定且可預期；
- 你的程式沒有自定義 Enum 的邏輯（如動態值、複雜屬性、方法）；
- 單測應該聚焦在你「如何使用」Enum，而非測試 Enum 本身。

## 什麼情況要測試 Enum？

如果以下條件成立，那就值得測試：

你在 Enum 上實作了自定義方法

```python
class TaskState(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"

    def is_active(self):
        return self == TaskState.ENABLED
```

👉 這時候你就該測：

```python
def test_is_active():
    assert TaskState.ENABLED.is_active() is True
    assert TaskState.DISABLED.is_active() is False
```

你在 Enum 之間有相依邏輯
（例如某個 Enum 對應另一個設定或資料庫欄位）

## 建議測試方式（輕量檢查用）

即使不測「Enum 本身」，可以加一個簡單 sanity test：

```python
import pytest
from src.models.enums import TaskState, TargetType, ExecutionStatus, ScheduleType

def test_enum_values_are_correct():
    assert TaskState.ENABLED.value == "ENABLED"
    assert TargetType.EMAIL.value == "email"
    assert ExecutionStatus.SUCCEEDED.value == "SUCCEEDED"
    assert ScheduleType.CRON.value == "cron"
```

這樣的測試主要目的：

防止誤改 enum 值（例如 refactor 改錯大小寫）；

確保關鍵常數仍一致（特別是若有外部 API 依賴）。

## 整合測試時使用 Enum 的測試建議

你未來在測試 Model / API / Service 時，
會用到這些 Enum，例如：

```python
EmailTaskResponse(
    state=TaskState.ENABLED,
    target_type=TargetType.EMAIL,
)
```

這時測試重點應該放在：

Enum 是否正確序列化／反序列化（特別是 FastAPI/Pydantic）；

與資料庫或 API 的整合結果正確。

例如：

```python
def test_enum_serialization():
    data = {"state": "ENABLED"}
    model = EmailTaskResponse(
        id=1, name="test", schedule_expression="cron", timezone="Asia/Taipei",
        target_type="email", target_arn="arn:123", target_input={}, 
        state="ENABLED", execution_count=0, max_retry_attempts=3,
        created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z",
        use_template=False, template_id=None, template_name=None,
        recipients=[]
    )
    assert model.state == TaskState.ENABLED
```

## 實務建議總結

| 類型	| 是否需要測試|	測試重點|
| Enum 常量	|❌ 不需要	|除非你擔心值被誤改，可加 sanity test|
| Enum 自定義方法 |	✅ 需要	測邏輯正確性|
| Enum 與 Model / API 整合|	✅ 建議	測序列化、驗證與邏輯整合|
