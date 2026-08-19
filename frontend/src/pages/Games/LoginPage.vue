<script setup lang="ts">
import { Head, router } from "@inertiajs/vue3";
import { computed, reactive } from "vue";
import { useToast } from "@composables/toast";
import { useI18n } from "vue-i18n";
import { watch } from "vue";

interface LoginPageProps {
  error: undefined | string;
}

const { error } = defineProps<LoginPageProps>();

const i18n = useI18n();
const { create } = useToast();

watch(
  () => error,
  (newError) => {
    if (newError) {
      create({
        body: i18n.t(newError),
        variant: "danger",
        position: "bottom-start",
      });
    }
  },
);

const form = reactive({
  walletId: null,
});

function submit() {
  router.post("/games/login/", form);
}

const validateWalletId = computed(() => {
  if (form.walletId === null) return null;

  const uuidRegex = /^[0-9a-f]{32}$/i;
  return uuidRegex.test(form.walletId);
});
</script>

<template>
  <Head :title="$t('games.title')" />

  <div class="container-fixed flex flex-col items-center justify-center">
    <UiAlert variant="danger">
      <vue-markdown :source="$t('games.entry.warning')" />
    </UiAlert>

    <div class="w-full shrink-0 sm:w-1/2 md:w-5/12 lg:w-1/3 xl:w-1/4">
      <UiCard body-class="flex flex-col items-center gap-2">
        <template #header>
          <h1 class="text-center m-0">
            <iconify-icon icon="fa7-solid:dice" />
            {{ $t("games.login.title") }}
          </h1>
        </template>

        <form @submit.prevent="submit" class="flex flex-col gap-2 w-full">
          <UiFormGroup id="wallet-id-group" label-for="wallet-id-input">
            <UiInput
              id="wallet-id-input"
              v-model="form.walletId"
              :placeholder="$t('games.login.enter_wallet')"
              required
              :state="validateWalletId"
              type="password"
            />
            <UiInvalidFeedback :state="validateWalletId">
              {{ $t("games.login.error.not_valid") }}
            </UiInvalidFeedback>
          </UiFormGroup>

          <UiButton
            type="submit"
            variant="primary"
            class="w-full"
            :disabled="!validateWalletId"
          >
            {{ $t("games.login.submit") }}
          </UiButton>
        </form>

        <UiLink to="/games/">
          {{ $t("games.login.back_to_entry") }}
        </UiLink>
      </UiCard>
    </div>
  </div>
</template>
