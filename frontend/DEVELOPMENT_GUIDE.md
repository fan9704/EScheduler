# 前端開發準則

---

## 環境需求

- Node.js >=22
- pnpm >=9
- IDE VSCode/WebStorm

## 專案結構

```txt
EScheduler/
│── frontend/     # Vue3 + Vite + pnpm + Biome
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   ├── biome.json
│   └── tsconfig.json
│
└── backend/      # FastAPI / Python 3.12 (uv)
```


### VSCode 開發環境

建議安裝以下套件

- [Vue(Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)
- [Vite](https://marketplace.visualstudio.com/items?itemName=antfu.vite)
- [Biome](https://marketplace.visualstudio.com/items?itemName=biomejs.biome)

### Webstorm 開發環境

- [Vue](https://plugins.jetbrains.com/plugin/9442-vue-js)
- [Vite](https://plugins.jetbrains.com/plugin/20011-vite)
- [Biome](https://plugins.jetbrains.com/plugin/22761-biome)

## 開發流程

```shell
# 進入專案
cd frontend
# 安裝套件
pnpm i
# 啟動開發伺服器
pnpm dev
# 格式化與檢察
pnpm biome:check
# 建置專案
pnpm build
# 最後 Commit 你的修改
```