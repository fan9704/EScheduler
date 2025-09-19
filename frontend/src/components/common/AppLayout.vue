<template>
  <v-app>
    <AppSidebar v-model="drawer" />
    
    <AppHeader @toggle-drawer="drawer = !drawer" />
    
    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AppHeader from "./AppHeader.vue";
import AppSidebar from "./AppSidebar.vue";

const drawer = ref(true);
</script>