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
const walletPhrase = ref<string | null>(null);
const revealReason = ref<string | null>(null);

const showToast = (message: string, variant: "success" | "danger") => {
  create({ body: i18n.t(message), variant, position: "bottom-start" });
};

/**
 * The phrase is the only credential, so the server hands it over just once,
 * while the wallet is new, and never puts it in the page props.
 */
const loadRecoveryPhrase = () => {
  axios
    .get("/games/api/user/wallet-phrase/")
    .then((response) => {
      walletPhrase.value = response.data.walletPhrase;
      revealReason.value = response.data.reason;
    })
    .catch(() => {
      walletPhrase.value = null;
      revealReason.value = null;
    });
};

const copyPhrase = () => {
  if (!walletPhrase.value) return;

  navigator.clipboard
    .writeText(walletPhrase.value)
    .then(() => showToast("games.main.copy_phrase", "success"))
    .catch(() => showToast("games.main.copy_phrase_error", "danger"));
};

const form = reactive<{ name: string; avatarId: number | null }>({
  name: "",
  avatarId: null,
});

// Reset from the store on every opening, so the form never shows a stale name
// or avatar after a change made elsewhere.
watch(
  settingsOpen,
  (open) => {
    if (!open) return;

    form.name = wallet.name;
    form.avatarId = wallet.avatar?.id ?? null;

    loadRecoveryPhrase();
  },
  // The store can open the settings while signing in, before this component
  // mounts; without `immediate` the form would come up blank.
  { immediate: true },
);

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

      showToast("games.main.settings_success", "success");

      settingsOpen.value = false;
    })
    .catch((error) => {
      showToast(
        error.response?.data?.error ?? "games.main.errors.invalid_request",
        "danger",
      );
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

    <!-- First thing in the modal, and only ever rendered while the server is
         still willing to hand the phrase over: this is the one chance to
         write it down. -->
    <UiAlert variant="warning" class="mb-0" v-if="walletPhrase">
      <h4 class="mt-0 mb-2">{{ $t("games.main.wallet_phrase") }}</h4>

      <p class="mb-2" v-if="revealReason === 'migrated'">
        {{ $t("games.main.wallet_phrase_migrated") }}
      </p>

      <div class="flex items-center gap-2">
        <code
          class="grow rounded-md border border-hairline bg-field px-3 py-2 break-all select-all"
        >
          {{ walletPhrase }}
        </code>

        <UiButton
          variant="tertiary"
          :title="$t('games.main.copy_wallet_phrase')"
          @click="copyPhrase"
          square
        >
          <iconify-icon icon="iconamoon:copy-duotone" />
        </UiButton>
      </div>

      <small class="mt-2 block">
        {{ $t("games.main.wallet_phrase_hint") }}
      </small>
    </UiAlert>

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
          :error="$t('games.main.settings_invalid')"
        />
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
