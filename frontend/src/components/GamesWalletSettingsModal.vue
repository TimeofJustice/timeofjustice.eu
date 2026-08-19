<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import axios from "axios";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";
import { useWallet } from "@composables/wallet";

import GamesAvatarGrid from "@components/GamesAvatarGrid.vue";

const i18n = useI18n();
const { create } = useToast();
const { wallet, settingsOpen, setName, setAvatar } = useWallet();

const saving = ref(false);

const form = reactive<{ name: string; avatarId: number | null }>({
  name: "",
  avatarId: null,
});

// Reset from the store on every opening, so the form never shows a stale name
// or avatar after a change made elsewhere.
watch(settingsOpen, (open) => {
  if (!open) return;

  form.name = wallet.name;
  form.avatarId = wallet.avatar?.id ?? null;
});

const validateName = computed(() => /^[a-zA-Z0-9]{3,32}$/.test(form.name));

const save = () => {
  if (!validateName.value || saving.value) return;

  saving.value = true;

  axios
    .post("/games/api/user/update/", {
      name: form.name,
      avatarId: form.avatarId,
    })
    .then((response) => {
      setName(response.data.name);
      setAvatar(response.data.avatar);

      create({
        body: i18n.t("games.main.settings_success"),
        variant: "success",
        position: "bottom-start",
      });

      settingsOpen.value = false;
    })
    .catch((error) => {
      create({
        body: i18n.t(
          error.response?.data?.error ?? "games.main.errors.invalid_request",
        ),
        variant: "danger",
        position: "bottom-start",
      });
    })
    .finally(() => {
      saving.value = false;
    });
};
</script>

<template>
  <UiModal
    v-model="settingsOpen"
    header-class="justify-between items-center"
    body-class="flex flex-col gap-4"
    size="lg"
    scrollable
    centered
  >
    <template #header>
      <h2 class="m-0">{{ $t("games.main.settings") }}</h2>

      <UiButton
        variant="tertiary"
        class="text-light"
        @click="settingsOpen = false"
        square
      >
        <iconify-icon icon="ep:close-bold" />
      </UiButton>
    </template>

    <form @submit.prevent="save" class="flex w-full flex-col gap-4">
      <UiFormGroup
        id="wallet-name-group"
        label-for="wallet-name-input"
        :label="$t('games.main.name')"
      >
        <UiInput
          id="wallet-name-input"
          v-model="form.name"
          :placeholder="$t('games.main.name')"
          required
          :state="validateName"
        />
        <UiInvalidFeedback :state="validateName">
          {{ $t("games.main.settings_invalid") }}
        </UiInvalidFeedback>
      </UiFormGroup>

      <UiFormGroup id="wallet-avatar-group" :label="$t('games.main.avatar')">
        <GamesAvatarGrid v-model="form.avatarId" :disabled="saving" />
      </UiFormGroup>

      <UiButton
        type="submit"
        variant="primary"
        class="w-full"
        :disabled="!validateName || saving"
      >
        {{ $t("general.save") }}
      </UiButton>
    </form>
  </UiModal>
</template>
