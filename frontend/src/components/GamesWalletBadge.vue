<script setup lang="ts">
import { useWallet } from "@composables/wallet";
import GamesAvatar from "@components/GamesAvatar.vue";

const { wallet, balance, isLoaded, openSettings } = useWallet();
</script>

<template>
  <UiDropdown
    align="end"
    toggle-class="p-0 rounded-full after:hidden"
    menu-class="min-w-48"
    variant="tertiary"
    v-if="isLoaded"
  >
    <template #button-content>
      <GamesAvatar :avatar="wallet.avatar" size="md" />
    </template>

    <div class="px-4 py-1">
      <strong class="block truncate">
        {{ wallet.name }}
        <span class="font-normal opacity-60">#{{ wallet.publicId }}</span>
      </strong>

      <span class="flex items-center gap-1 tabular-nums">
        <iconify-icon icon="fa7-solid:coins" />
        {{ balance }} TJTs
      </span>
    </div>

    <hr class="my-2 border-hairline" />

    <UiDropdownItem @click="openSettings">
      <iconify-icon icon="fa7-solid:edit" class="mr-1" />
      {{ $t("games.main.settings") }}
    </UiDropdownItem>

    <hr class="my-2 border-hairline" />

    <UiDropdownItem to="/logout/" class="text-danger hover:text-danger">
      <iconify-icon icon="fa7-solid:sign-out" class="mr-1" />
      {{ $t("games.main.logout") }}
    </UiDropdownItem>
  </UiDropdown>
</template>
