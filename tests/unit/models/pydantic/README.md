# 🧭 是否需要測試 Pydantic 模型？

## ✅ 該測試的情境

Pydantic 本身已經是經過充分測試的框架，所以我們不需要測試「型別轉換、驗證」這些內建機制是否運作。
但以下幾種情況非常值得寫 unit test

## 測試理由	

1. 自定義 validator	例如你這裡的 @validator('type')、validate_template_usage、validate_direct_email_fields。這些是你自己的邏輯，要確保輸入錯誤時會拋出正確錯誤。
2. 欄位預設值 / 可選欄位行為	確保 optional 欄位沒有提供時仍能正確初始化。
3. 嵌套模型 (nested models)	像 List[TemplateVariable]，要確認巢狀結構能正確被解析。
4. Enum / Constraint / 限制條件	例如長度限制、最小值、最大值（min_length, ge, le）確實被執行。

## 📌 換句話說：

你不需要測試「Pydantic 會不會驗證 email 格式」，但你要測試「你在模型裡自定義的驗證規則」。