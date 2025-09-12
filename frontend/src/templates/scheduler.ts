import { ExpressionTemplate } from "@/models/schedule_helper"

const expression_template:ExpressionTemplate[] = [
  {
    "id": 1,
    "name": "每分鐘",
    "type": "rate",
    "expression": "rate(1 minute)",
    "description": "每分鐘執行一次",
    "category": "常用間隔"
  },
  {
    "id": 2,
    "name": "每5分鐘",
    "type": "rate",
    "expression": "rate(5 minutes)",
    "description": "每5分鐘執行一次",
    "category": "常用間隔"
  },
  {
    "id": 3,
    "name": "每15分鐘",
    "type": "rate",
    "expression": "rate(15 minutes)",
    "description": "每15分鐘執行一次",
    "category": "常用間隔"
  },
  {
    "id": 4,
    "name": "每30分鐘",
    "type": "rate",
    "expression": "rate(30 minutes)",
    "description": "每30分鐘執行一次",
    "category": "常用間隔"
  },
  {
    "id": 5,
    "name": "每小時",
    "type": "rate",
    "expression": "rate(1 hour)",
    "description": "每小時執行一次",
    "category": "常用間隔"
  },
  {
    "id": 6,
    "name": "每天",
    "type": "rate",
    "expression": "rate(1 day)",
    "description": "每天執行一次",
    "category": "常用間隔"
  },
  {
    "id": 7,
    "name": "每天午夜",
    "type": "cron",
    "expression": "0 0 * * *",
    "description": "每天午夜12點執行",
    "category": "每日排程"
  },
  {
    "id": 8,
    "name": "每天早上9點",
    "type": "cron",
    "expression": "0 9 * * *",
    "description": "每天早上9點執行",
    "category": "每日排程"
  },
  {
    "id": 9,
    "name": "每天下午6點",
    "type": "cron",
    "expression": "0 18 * * *",
    "description": "每天下午6點執行",
    "category": "每日排程"
  },
  {
    "id": 10,
    "name": "工作日早上8點",
    "type": "cron",
    "expression": "0 8 * * 1-5",
    "description": "週一到週五早上8點執行",
    "category": "工作日排程"
  },
  {
    "id": 11,
    "name": "工作日下午5點",
    "type": "cron",
    "expression": "0 17 * * 1-5",
    "description": "週一到週五下午5點執行",
    "category": "工作日排程"
  },
  {
    "id": 12,
    "name": "工作日每小時",
    "type": "cron",
    "expression": "0 * * * 1-5",
    "description": "工作日每小時執行",
    "category": "工作日排程"
  },
  {
    "id": 13,
    "name": "週六早上10點",
    "type": "cron",
    "expression": "0 10 * * 6",
    "description": "每週六早上10點執行",
    "category": "週末排程"
  },
  {
    "id": 14,
    "name": "週日凌晨2點",
    "type": "cron",
    "expression": "0 2 * * 0",
    "description": "每週日凌晨2點執行",
    "category": "週末排程"
  },
  {
    "id": 15,
    "name": "每月1號",
    "type": "cron",
    "expression": "0 0 1 * *",
    "description": "每月1號午夜執行",
    "category": "每月排程"
  },
  {
    "id": 16,
    "name": "每月15號",
    "type": "cron",
    "expression": "0 0 15 * *",
    "description": "每月15號午夜執行",
    "category": "每月排程"
  },
  {
    "id": 17,
    "name": "每月最後一天",
    "type": "cron",
    "expression": "0 0 L * *",
    "description": "每月最後一天午夜執行",
    "category": "每月排程"
  }
]

export { expression_template }