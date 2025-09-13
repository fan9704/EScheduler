<template>
  <v-app-bar elevation="1" class="border-b">
    <v-app-bar-nav-icon @click="$emit('toggle-drawer')" />

    <v-app-bar-title>
      <span class="font-weight-bold">EScheduler</span>
      <span class="text-caption text-medium-emphasis ml-2">排程任務管理系統</span>
    </v-app-bar-title>

    <v-spacer />

    <v-btn icon="mdi-theme-light-dark" variant="text" @click="toggleTheme" />
  </v-app-bar>
</template>

<script setup lang="ts">
import { useTheme } from 'vuetify';

defineEmits<{
  'toggle-drawer': [];
}>();

const theme = useTheme();

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark';
};
</script>
