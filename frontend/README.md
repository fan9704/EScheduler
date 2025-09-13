# 🧩 前端開發指南

本文件提供專案開發時需遵循的步驟與規範，確保程式碼品質與團隊協作一致性。

---

## 📦 開發環境設定

1. **安裝 Node.js 與 pnpm**

- Node.js 版本：請使用 LTS 版本
- 安裝 pnpm：
   
```bash
npm install -g pnpm
```

2. **安裝專案依賴**

```bash
pnpm install
```

3. 設定 Git Hooks（使用 Husky）

- 初始化 Husky

```shell
pnpm exec husky init
```

- 安裝 pre-commit、commit-msg hook（如已設定可略過）

```shell
pnpm exec husky add .husky/pre-commit "pnpm lint-staged"
pnpm exec husky add .husky/commit-msg "pnpm commitlint --edit \$1"
```

## 🧹 程式碼規範

專案使用以下工具確保程式碼一致性：

- ESLint：檢查語法與程式風格錯誤
- Prettier：統一程式碼格式
- @typescript-eslint：支援 TypeScript 語法檢查
- Vue 3 ESLint Plugin：針對 Vue 組件的最佳實踐檢查

### 常用指令

- 執行 ESLint 檢查

```shell
pnpm eslint --ext .ts,.vue src
```

- 執行 Prettier 格式化

```shell
pnpm prettier --write src
```

- 自動檢查並修正

```shell
pnpm lint
```

## ✍️ 開發流程

1. 建立分支
    - 開發前從 develop 分支切出新的 feature 分支：

```shell
git checkout develop
git pull
git checkout -b feat/<feature-name>
```

2. 撰寫程式碼
    - 使用 TypeScript 撰寫 Vue 3 元件
    - 遵守 ESLint 與 Prettier 規範
3. 提交程式碼
    - 確保程式碼經過 Lint 檢查：

```shell
pnpm lint
```

4. 使用符合 Conventional Commit
    - 格式的提交訊息：
        - feat: 新增任務建立頁面
        - fix: 修正日期選擇器無法顯示
        - chore: 更新依賴套件
5. 發送 Pull Request
   - 將 feature 分支推送至遠端並建立 PR，指向 develop 分支
6. 通過 Code Review 後合併 

## 🧪 測試

```shell
pnpm test
```

## ✅ 提交前檢查清單

- 程式碼通過 ESLint 與 Prettier
- 所有變更均有清楚 commit 訊息
- 單元測試全部通過
- 通過 Code Review

## 📚 附註
　　
- 請避免直接推送至 main 或 develop 分支
- 有任何設定或規範異動，需更新此文件並通知團隊成員
- 