<template>
  <v-navigation-drawer
    v-model="localDrawer"
    :rail="rail"
    permanent
    class="border-e"
  >
    <v-list density="compact" nav>
      <v-list-item
        v-for="route in navigationRoutes"
        :key="route.name"
        :prepend-icon="route.meta?.icon"
        :title="route.meta?.title"
        :value="route.name"
        :to="route.path"
      />
    </v-list>
    
    <template #append>
      <div class="pa-2">
        <v-btn
          icon
          variant="text"
          @click="rail = !rail"
        >
          <v-icon>{{ rail ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const rail = ref(false)

const localDrawer = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// 過濾出需要在導航中顯示的路由
const navigationRoutes = computed(() => 
  router.getRoutes().filter(route => 
    route.meta?.title && 
    route.meta?.icon && 
    !route.path.includes(':') && // 排除動態路由
    route.name !== 'NotFound'
  )
)
</script>