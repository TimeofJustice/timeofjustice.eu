<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { useWallet } from "@composables/wallet";
import GamesAvatar from "@components/GamesAvatar.vue";

const i18n = useI18n();
const { create } = useToast();
const { wallet, balance, isLoaded, openSettings, copyWalletId } = useWallet();

const copy = () => {
  copyWalletId()
    .then(() => {
      create({
        body: i18n.t("games.main.copy_wallet"),
        variant: "success",
        position: "bottom-start",
      });
    })
    .catch(() => {
      create({
        body: i18n.t("games.main.copy_wallet_error"),
        variant: "danger",
        position: "bottom-start",
      });
    });
};
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
      <strong class="block truncate">{{ wallet.name }}</strong>

      <span class="flex items-center gap-1 tabular-nums">
        <iconify-icon icon="fa7-solid:coins" />
        {{ balance }} TJTs
      </span>
    </div>

    <hr class="my-2 border-black/15" />

    <UiDropdownItem @click="openSettings">
      <iconify-icon icon="fa7-solid:edit" class="mr-1" />
      {{ $t("games.main.settings") }}
    </UiDropdownItem>

    <UiDropdownItem @click="copy">
      <iconify-icon icon="iconamoon:copy-duotone" class="mr-1" />
      {{ $t("games.main.copy_wallet_id") }}
    </UiDropdownItem>

    <hr class="my-2 border-black/15" />

    <UiDropdownItem to="/logout/" class="text-danger hover:text-danger">
      <iconify-icon icon="fa7-solid:sign-out" class="mr-1" />
      {{ $t("games.main.logout") }}
    </UiDropdownItem>
  </UiDropdown>
</template>
