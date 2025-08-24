<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-select
          v-model="selectedCategory"
          :items="categories"
          label="模板分類"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchKeyword"
          label="搜索模板"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-magnify"
          clearable
        />
      </v-col>
    </v-row>
    
    <v-row>
      <v-col
        v-for="template in filteredTemplates"
        :key="template.name"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card
          class="template-card"
          :class="{ 'selected': selectedTemplate?.name === template.name }"
          @click="selectTemplate(template)"
        >
          <v-card-title class="text-h6">
            {{ template.name }}
          </v-card-title>
          <v-card-subtitle>
            <v-chip
              size="small"
              :color="template.type === 'cron' ? 'primary' : 'secondary'"
              variant="flat"
            >
              {{ template.type.toUpperCase() }}
            </v-chip>
          </v-card-subtitle>
          <v-card-text>
            <div class="mb-2">
              <div class="text-caption text-medium-emphasis">描述</div>
              <div class="text-body-2">{{ template.description }}</div>
            </div>
            <div>
              <div class="text-caption text-medium-emphasis">表達式</div>
              <v-code class="text-caption">
                {{ template.expression }}
              </v-code>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <div v-if="filteredTemplates.length === 0" class="text-center py-8">
      <v-icon size="64" color="grey-lighten-2">
        mdi-file-search-outline
      </v-icon>
      <div class="text-h6 mt-2 text-medium-emphasis">
        沒有找到匹配的模板
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useScheduleHelperStore } from '@/stores/schedule_helper'
import type { ScheduleTemplateResponse } from '@/models/schedule_helper'

const emit = defineEmits<{
  select: [expression: string]
}>()

const scheduleHelperStore = useScheduleHelperStore()
const { templates } = scheduleHelperStore

const selectedCategory = ref('')
const searchKeyword = ref('')
const selectedTemplate = ref<ScheduleTemplateResponse | null>(null)

const categories = computed(() => {
  const cats = [...new Set(templates.map(t => t.category))]
  return cats.map(cat => ({ title: cat, value: cat }))
})

const filteredTemplates = computed(() => {
  let result = templates
  
  if (selectedCategory.value) {
    result = result.filter(t => t.category === selectedCategory.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => 
      t.name.toLowerCase().includes(keyword) ||
      t.description.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const selectTemplate = (template: ScheduleTemplateResponse) => {
  selectedTemplate.value = template
  emit('select', template.expression)
}

onMounted(() => {
  scheduleHelperStore.fetchTemplates()
})
</script>

<style scoped>
.template-card {
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.template-card.selected {
  border: 2px solid rgb(var(--v-theme-primary));
}
</style>