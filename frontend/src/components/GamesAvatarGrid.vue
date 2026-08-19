<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { useWallet } from "@composables/wallet";

import GamesAvatar from "@components/GamesAvatar.vue";

interface GamesAvatarGridProps {
  disabled?: boolean;
}

const { disabled = false } = defineProps<GamesAvatarGridProps>();

/**
 * The picked avatar's id. Selection only — persisting is left to the parent, so
 * the games settings can save it together with the name.
 */
const selected = defineModel<number | null>();

const i18n = useI18n();
const { create } = useToast();
const { avatars, loadAvatars } = useWallet();

const loading = ref(avatars.value.length === 0);

onMounted(() => {
  loadAvatars()
    .catch(() => {
      create({
        body: i18n.t("games.main.errors.invalid_request"),
        variant: "danger",
        position: "bottom-start",
      });
    })
    .finally(() => {
      loading.value = false;
    });
});
</script>

<template>
  <div class="flex items-center justify-center py-4" v-if="loading">
    <iconify-icon icon="fa6-solid:spinner" class="animate-spin text-2xl" />
  </div>

  <p class="m-0 text-center text-accent" v-else-if="avatars.length === 0">
    {{ $t("games.main.avatar_empty") }}
  </p>

  <div
    class="grid grid-cols-4 gap-3 sm:grid-cols-5"
    :class="{ 'pointer-events-none opacity-60': disabled }"
    v-else
  >
    <button
      type="button"
      class="aspect-square cursor-pointer rounded-full border-2 p-0 transition-transform duration-150 hover:scale-105 focus-visible:scale-105"
      :class="
        avatar.id === selected
          ? 'border-accent'
          : 'border-transparent hover:border-light'
      "
      :title="avatar.name"
      :aria-pressed="avatar.id === selected"
      @click="selected = avatar.id"
      v-for="avatar in avatars"
      :key="avatar.id"
    >
      <GamesAvatar :avatar="avatar" size="lg" />
    </button>
  </div>
</template>
