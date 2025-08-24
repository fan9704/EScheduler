import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// 導入色彩配置
import colorSchema from '@/assets/styles/color-schema.json'

const { colors } = colorSchema.theme

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: colors.primary.main,
          secondary: colors.secondary.main,
          background: colors.background.default,
          surface: colors.background.paper,
          'on-surface': colors.text.primary,
          'on-primary': '#ffffff',
          'on-secondary': '#ffffff',
          success: colors.success,
          warning: colors.warning,
          error: colors.error,
          info: colors.info,
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: colors.primary.main,
          secondary: colors.secondary.main,
          background: colorSchema.theme.dark.background.default,
          surface: colorSchema.theme.dark.background.paper,
          'on-surface': colorSchema.theme.dark.text.primary,
          'on-primary': '#ffffff',
          'on-secondary': '#ffffff',
          success: colors.success,
          warning: colors.warning,
          error: colors.error,
          info: colors.info,
        },
      },
    },
  },
})