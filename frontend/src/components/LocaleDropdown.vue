<script setup lang="ts">
import { LOCALES } from "@configurations/locales.ts";
import { router } from "@inertiajs/vue3";
import { useI18n } from "@node_modules/vue-i18n";

const i18n = useI18n();

const changeLocale = (lang: string) => {
  if (lang === i18n.locale.value) return;

  i18n.locale.value = lang;

  // Persist language selection
  document.cookie = `django_language=${lang};path=/;max-age=31536000`;

  // Reload only props with inertia
  router.reload();
};
</script>

<template>
  <BDropdown variant="ghost">
    <template #button-content>
      <i
        :class="LOCALES.find((locale) => locale.code === $i18n.locale)?.icon"
        class="rounded-1"
      />
    </template>

    <BDropdownItemButton
      v-for="locale in LOCALES"
      :key="locale.code"
      @click="changeLocale(locale.code)"
    >
      <i :class="locale.icon" class="rounded-1" /> {{ locale.name }}
    </BDropdownItemButton>
  </BDropdown>
</template>
