<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { computed, reactive, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useToast } from "@composables/toast";

interface WalletLoginPageProps {
  error: string | null;
  /** Where to land once a wallet is active. */
  next: string;
}

const { error, next } = defineProps<WalletLoginPageProps>();

const i18n = useI18n();
const { create } = useToast();

watch(
  () => error,
  (newError) => {
    if (!newError) return;

    create({
      body: i18n.t(newError),
      variant: "danger",
      position: "bottom-start",
    });
  },
);

const form = reactive({
  phrase: null as string | null,
});

/**
 * A loose check for "looks like a phrase". The exact word count lives on the
 * server, and older wallets were issued shorter phrases, so this only rules
 * out obvious typos.
 */
const validatePhrase = computed(() => {
  if (form.phrase === null) return null;

  const words = form.phrase.split(/[^a-zA-Z]+/).filter(Boolean);

  return words.length >= 4;
});

function submit() {
  router.post("/login/", { ...form, next });
}

function register() {
  router.post("/register/", { next });
}
</script>

<template>
  <Head :title="$t('games.entry.title')" />

  <div class="container-fixed flex flex-col items-center justify-center">
    <div class="w-full shrink-0 sm:w-1/2 md:w-5/12 lg:w-1/3 xl:w-1/4">
      <UiCard body-class="flex flex-col gap-4">
        <template #header>
          <h1 class="m-0 text-center">
            <iconify-icon icon="fa-solid:wallet" />
            {{ $t("games.entry.title") }}
          </h1>
        </template>

        <UiButton variant="primary" class="w-full" @click="register">
          {{ $t("games.entry.enter_with_new_wallet") }}
        </UiButton>

        <div class="flex items-center gap-2 text-accent">
          <hr class="grow border-light/25" />
          {{ $t("games.login.or") }}
          <hr class="grow border-light/25" />
        </div>

        <form @submit.prevent="submit" class="flex w-full flex-col gap-2">
          <UiFormGroup
            id="wallet-phrase-group"
            label-for="wallet-phrase-input"
            :label="$t('games.login.title')"
          >
            <UiInput
              id="wallet-phrase-input"
              v-model="form.phrase"
              :placeholder="$t('games.login.enter_wallet')"
              required
              :state="validatePhrase"
              :error="$t('games.login.error.not_valid')"
              type="password"
            />
          </UiFormGroup>

          <UiButton
            type="submit"
            variant="secondary"
            class="w-full"
            :disabled="!validatePhrase"
          >
            {{ $t("games.login.submit") }}
          </UiButton>
        </form>
      </UiCard>
    </div>
  </div>
</template>
