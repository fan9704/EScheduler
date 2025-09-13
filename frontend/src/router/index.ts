import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

// 頁面組件
import Dashboard from '@/views/Dashboard.vue';
import TaskList from '@/views/TaskList.vue';
import TaskCreate from '@/views/TaskCreate.vue';
import TaskEdit from '@/views/TaskEdit.vue';
import ScheduleHelper from '@/views/ScheduleHelper.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '儀表板',
      icon: 'mdi-view-dashboard',
    },
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskList,
    meta: {
      title: '任務列表',
      icon: 'mdi-clock-outline',
    },
  },
  {
    path: '/tasks/create',
    name: 'TaskCreate',
    component: TaskCreate,
    meta: {
      title: '創建任務',
      icon: 'mdi-plus-circle-outline',
    },
  },
  {
    path: '/tasks/:id/edit',
    name: 'TaskEdit',
    component: () => import('@/views/TaskEdit.vue'),
    meta: {
      title: '編輯任務',
    },
  },
  {
    path: '/schedule-helper',
    name: 'ScheduleHelper',
    component: ScheduleHelper,
    meta: {
      title: '排程助手',
      icon: 'mdi-help-circle-outline',
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '頁面不存在',
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 路由守衛
router.beforeEach((to, from, next) => {
  // 設置頁面標題
  if (to.meta?.title) {
    document.title = `${to.meta.title} - EScheduler`;
  } else {
    document.title = 'EScheduler';
  }

  next();
});

export default router;
