import { createI18n } from 'vue-i18n';

const messages = {
  'zh-TW': {
    // 中文翻譯
    app: {
      title: 'EScheduler',
      subtitle: '排程任務管理系統',
    },
    nav: {
      dashboard: '儀表板',
      tasks: '任務列表',
      create: '創建任務',
      helper: '排程助手',
    },
    // 更多翻譯...
  },
};

const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW',
  fallbackLocale: 'zh-TW',
  messages,
});

export default i18n;
