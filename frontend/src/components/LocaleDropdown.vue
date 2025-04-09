<script setup lang="ts">
const langs = [
  { code: "en", text: "English", flag: "fi fi-uk" },
  { code: "de", text: "Deutsch", flag: "fi fi-de" },
  {code: "yoda", text: "Yoda", flag: "fi fi-yoda"},
];

const changeLocale = (lang: string) => {
  localStorage.setItem('lang', lang);
};
</script>

<template>
  <BDropdown class="dropdown-ghost">
    <template #button-content>
      <i :class="langs.find(lang => lang.code === $i18n.locale)?.flag" class="rounded-1"></i>
    </template>

    <BDropdownItemButton v-for="lang in langs" :key="lang.code" @click="$i18n.locale = lang.code; changeLocale(lang.code)">
      <i :class="lang.flag" class="rounded-1"></i> {{ lang.text }}
    </BDropdownItemButton>
  </BDropdown>
</template>