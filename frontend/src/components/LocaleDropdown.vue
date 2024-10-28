<script setup lang="ts">
const langs = [
  { code: "en", text: "English", flag: "<i class=\"fi fi-us\"></i>" },
  { code: "de", text: "Deutsch", flag: "<i class=\"fi fi-de\"></i>" },
  {code: "yoda", text: "Yoda", flag: "<i class=\"fi fi-yoda\"></i>"},
];

const changeLocale = (lang: string) => {
  localStorage.setItem('lang', lang);
};
</script>

<template>
  <BDropdown class="dropdown-ghost">
    <template #button-content>
      <i v-html="langs.find(lang => lang.code === $i18n.locale)?.flag"></i>
    </template>

    <BDropdownItemButton v-for="lang in langs" :key="lang.code" @click="$i18n.locale = lang.code; changeLocale(lang.code)">
      <i v-html="lang.flag"></i> {{ lang.text }}
    </BDropdownItemButton>
  </BDropdown>
</template>