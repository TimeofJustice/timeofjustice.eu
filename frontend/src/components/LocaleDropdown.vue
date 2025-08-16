<script setup lang="ts">
import { LOCALES } from "@configurations/locales.ts";

const changeLocale = (lang: string) => {
  localStorage.setItem("lang", lang);
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
      @click="
        $i18n.locale = locale.code;
        changeLocale(locale.code);
      "
    >
      <i :class="locale.icon" class="rounded-1" /> {{ locale.name }}
    </BDropdownItemButton>
  </BDropdown>
</template>
