<script setup lang="ts">
import { Head } from "@inertiajs/vue3";
import { ref, computed, reactive } from "vue";

// Form state
const isLoading = ref(false);
const form = reactive({
  playerName: "",
  joinCode: "",
});

// Validation
const validatePlayerName = computed(() => {
  if (form.playerName === "") return null;
  return (
    form.playerName.trim().length > 0 && form.playerName.trim().length <= 50
  );
});

const validateJoinCode = computed(() => {
  if (form.joinCode.length === 0) return null;
  return (
    form.joinCode.length === 6 &&
    /^[A-Z0-9]{6}$/.test(form.joinCode.toUpperCase())
  );
});
</script>

<template>
  <Head :title="$t('quiz.title')" />

  <div class="quiz-lobby-page h-100 fullscreen">
    <div class="container-xxl d-flex flex-column h-100">
      <BCard
        class="lobby-container rounded-4 col-12 col-md-8 col-lg-6 p-0 p-md-3 m-auto"
        body-class="d-flex flex-column gap-2"
      >
        <div class="lobby-header text-center">
          <span class="fs-1 fw-bold">{{ $t("quiz.title") }}</span>
          <div class="text-accent">{{ $t("quiz.lobby.subtitle") }}</div>
        </div>

        <BTabs fill class="lobby-tabs">
          <BTab>
            <template #title>
              <iconify-icon icon="fa6-solid:door-open" />
              {{ $t("quiz.lobby.join") }}
            </template>

            <BForm class="d-flex flex-column gap-2 pt-1">
              <BFormGroup
                :label="$t('quiz.lobby.enter_player_name')"
                label-for="player-name"
              >
                <BFormInput
                  id="player-name"
                  v-model="form.playerName"
                  :placeholder="$t('quiz.lobby.player_name_placeholder')"
                  maxlength="50"
                  :state="validatePlayerName"
                  :disabled="isLoading"
                  required
                >
                </BFormInput>
                <BFormInvalidFeedback :state="validatePlayerName">
                  {{ $t("quiz.lobby.player_name_help") }}
                </BFormInvalidFeedback>
              </BFormGroup>
              <BFormGroup
                :label="$t('quiz.lobby.enter_code')"
                label-for="join-code"
              >
                <BFormInput
                  id="join-code"
                  v-model="form.joinCode"
                  :placeholder="$t('quiz.lobby.code_placeholder')"
                  maxlength="6"
                  :state="validateJoinCode"
                  class="text-uppercase"
                  required
                >
                </BFormInput>
                <BFormInvalidFeedback :state="validateJoinCode">
                  {{ $t("quiz.lobby.code_help") }}
                </BFormInvalidFeedback>
              </BFormGroup>

              <BButton
                type="submit"
                variant="primary"
                :disabled="
                  isLoading || !validatePlayerName || !validateJoinCode
                "
              >
                <BSpinner small class="me-2" v-if="isLoading" />
                {{
                  isLoading
                    ? $t("quiz.lobby.joining")
                    : $t("quiz.lobby.join_button")
                }}
              </BButton>
            </BForm>
          </BTab>

          <BTab>
            <template #title>
              <iconify-icon icon="fa6-solid:plus" />
              {{ $t("quiz.lobby.create") }}
            </template>

            <BForm class="d-flex flex-column gap-2 pt-1">
              <BFormGroup
                :label="$t('quiz.lobby.enter_player_name')"
                label-for="player-name"
              >
                <BFormInput
                  id="player-name"
                  v-model="form.playerName"
                  :placeholder="$t('quiz.lobby.player_name_placeholder')"
                  maxlength="50"
                  :state="validatePlayerName"
                  :disabled="isLoading"
                  required
                >
                </BFormInput>
                <BFormInvalidFeedback :state="validatePlayerName">
                  {{ $t("quiz.lobby.player_name_help") }}
                </BFormInvalidFeedback>
              </BFormGroup>

              <BButton
                type="submit"
                variant="primary"
                :disabled="isLoading || !validatePlayerName"
              >
                <BSpinner small class="me-2" v-if="isLoading" />
                {{
                  isLoading
                    ? $t("quiz.lobby.creating")
                    : $t("quiz.lobby.create_game")
                }}
              </BButton>
            </BForm>
          </BTab>
        </BTabs>
      </BCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.quiz-lobby-page {
  background-image: linear-gradient(
    135deg,
    hsl(222, 84%, 60%),
    hsl(164, 79%, 71%)
  );
  background-size: 400% 400%;
  animation: gradientRotate 15s ease infinite;
}

@keyframes gradientRotate {
  0% {
    background-position: 0% 50%;
  }
  25% {
    background-position: 100% 50%;
  }
  50% {
    background-position: 100% 0%;
  }
  75% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.lobby-container {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.lobby-header {
  span {
    background-image: linear-gradient(
      90deg,
      hsl(222, 84%, 60%),
      hsl(164, 79%, 71%)
    );
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

.btn-primary {
  background: linear-gradient(90deg, hsl(222, 84%, 60%), hsl(164, 79%, 71%));
  border: none;
  font-weight: 600;
  transition: filter 0.3s ease;

  &:hover {
    filter: brightness(0.95);
  }
}
</style>

<style lang="scss">
.lobby-tabs .nav-tabs {
  --bs-border-color: hsl(222, 84%, 60%);
  --bs-nav-tabs-link-active-bg: transparent;
  --bs-nav-tabs-link-active-color: rgba(
    var(--bs-accent-rgb),
    var(--bs-text-opacity, 1)
  );
  --bs-nav-tabs-link-active-border-color: var(--bs-border-color)
    var(--bs-border-color) transparent;
  --bs-nav-tabs-link-hover-border-color: transparent;

  border-bottom: 0 !important;

  & .nav-link:not(.active) {
    border-bottom: var(--bs-nav-tabs-border-width) solid
      var(--bs-nav-tabs-border-color);
  }
}

.lobby-tabs .form-control {
  --bs-border-color: hsl(222, 84%, 60%);
}
</style>
