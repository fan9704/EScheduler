# 開發風格工具指南 Dev Styling Tool Guide

在 EScheduler 專案中，我們透過自動化工具鏈來確保代碼的品質、一致性與可維護性。所有貢獻者請務必遵循以下工具規範。

---

## [Ruff](https://blog.kyomind.tw/ruff/)

**「極速、全能的 Python 代碼靜態分析與格式化工具」**

* **定位**：Ruff 是一個用 Rust 編寫的高效能 Python Linter 與 Formatter，旨在取代並整合 Flake8、isort、Black 等傳統工具。
* **為什麼使用它**：效能極佳且內建超過 700 條規則，支援自動修正（`--fix`）。
* **專案實踐**：用於統一程式碼風格、排序 Import 以及攔截潛在邏輯錯誤。

---

## [MyPy](https://blog.kyomind.tw/mypy/)

**「Python 的靜態型別檢查器 (Static Type Checker)」**

* **定位**：透過分析 Type Hints（型別提示）來檢查型別錯誤。
* **為什麼使用它**：在執行前攔截 `NoneType` 或型別不匹配的 Bug，提升代碼可讀性與 IDE 補全精準度。
* **專案實踐**：Service 層與 Pydantic Model 必須通過 MyPy 的嚴格檢查。

---

## [pre-commit & Git Hooks](https://blog.kyomind.tw/pre-commit/)

**「代碼提交前的自動化守衛」**

* **定位**：管理 Git Hooks 的框架，讓腳本在執行 `git commit` 前自動觸發。
* **為什麼使用它**：確保只有通過檢查的品質代碼能進入倉庫。
* **專案實踐**：安裝後，每次提交時會自動跑一遍 Ruff 與基礎檔案檢查。

---

## [Codecov](https://docs.codecov.com/docs/code-coverage-with-python)

**「可視化的測試覆蓋率監控平台」**

* **定位**：將測試覆蓋率（Test Coverage）轉化為可視化報告，並整合於 GitHub PR 評論中。
* **為什麼使用它**：直觀顯示測試死角，並防止新 PR 導致覆蓋率下降。
* **專案實踐**：核心邏輯的覆蓋率需維持在標準以上，CI 流程會自動回傳報告。

---

## 🛠️ 開發工作流與指令使用時機

為了維持專案品質，開發時建議遵循以下流程：

### 1. 環境初始化 (僅需執行一次)
在複製專案後，必須掛載 Git Hooks，否則 `pre-commit` 不會自動生效。
* **指令**：`pre-commit install`
* **時機**：首次建立開發環境或重裝系統後。

### 2. 日日常開發循環 (撰寫程式碼時)
在寫程式的過程中，可以手動跑 Linter 來確保邏輯正確，並在寫完功能後跑測試。
* **檢查與自動修復**：`uv run ruff check . --fix`
    * **時機**：程式碼寫到一半覺得亂亂的，或是想清理未使用的 Import 時。
* **自動排版**：`uv run ruff format .`
    * **時機**：提交前確保括號、空格符合專案規範。
* **執行單元測試**：`uv run pytest`
    * **時機**：完成一個 Small Feature 或 Bugfix 後，確認沒有壞掉舊有功能。

### 3. 提交代碼前 (Commit 前的最終確認)
通常 `git commit` 會觸發自動檢查，但建議大型修改先手動跑一次全域檢查。
* **全域靜態檢查**：`uv run ruff check .` 與 `uv run mypy .`
    * **時機**：準備下 `git commit` 前。
* **產生覆蓋率報告**：`uv run pytest --cov=src --cov-report=term-missing`
    * **時機**：新增了 Service 方法，想確認單元測試是否有跑進去每一行邏輯。

---

### 🚀 開發者快速指令彙整

| 任務 | 指令 | 使用時機 |
| :--- | :--- | :--- |
| **安裝 Hook** | `pre-commit install` | **環境初始化** |
| **自動修正錯誤** | `uv run ruff check . --fix` | **隨時執行**，快速清理代碼 |
| **手動排版** | `uv run ruff format .` | **提交前**，美化程式碼結構 |
| **型別檢查** | `uv run mypy .` | **重構後**，確保介面傳參正確 |
| **執行測試** | `uv run pytest --cov=src` | **推送到 GitHub 前**，確保覆蓋率 |
| **強制執行 Hook** | `pre-commit run --all-files` | **修改了 Linter 配置後**，確保舊代碼符合新規則 |
