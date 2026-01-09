<script setup lang="ts">
import QuizBackground from "@/components/Quiz/QuizBackground.vue";
import { useToast } from "bootstrap-vue-next";
import { Head, router } from "@inertiajs/vue3";
import { ref, computed, reactive } from "vue";
import axios from "@node_modules/axios";
import { useI18n } from "vue-i18n";

// Form state
const selectedForm = ref<"join" | "create">("join");
const isLoading = ref(false);
const form = reactive({
  playerName: "",
  lobbyCode: "",
});

// Validation
const validatePlayerName = computed(() => {
  if (form.playerName === "") return null;
  return (
    form.playerName.trim().length > 0 && form.playerName.trim().length <= 50
  );
});

const validateJoinCode = computed(() => {
  if (form.lobbyCode.length === 0) return null;
  return (
    form.lobbyCode.length === 6 &&
    /^[A-Z0-9]{6}$/.test(form.lobbyCode.toUpperCase())
  );
});

const i18n = useI18n();
const { create } = useToast();

const showToast = (message: string, variant: "success" | "danger") => {
  create?.({
    body: message,
    variant: variant,
    interval: 5000,
    position: "bottom-start",
    noProgress: true,
  });
};

const joinGame = () => {
  axios
    .post(`/quiz/join`, form)
    .then((response) => {
      // Save player ID as cookie
      document.cookie = `quiz_player_id=${response.data.player_id}; path=/; max-age=${
        60 * 60 * 24 * 1
      }`;
      // Redirect to lobby
      router.visit(`/quiz/${response.data.lobby_code}`);
    })
    .catch((error) => {
      showToast(i18n.t("quiz.error." + error.response.data.message), "danger");
    });
};

const createGame = () => {
  axios
    .post(`/quiz/create`, { playerName: form.playerName })
    .then((response) => {
      // Save player ID as cookie
      document.cookie = `quiz_player_id=${response.data.player_id}; path=/; max-age=${
        60 * 60 * 24 * 1
      }`;
      // Redirect to lobby
      router.visit(`/quiz/${response.data.lobby_code}`);
    })
    .catch((error) => {
      showToast(i18n.t("quiz.error." + error.response.data.message), "danger");
    });
};
</script>

<template>
  <Head :title="$t('quiz.title')" />

  <div
    class="quiz-lobby-page h-100 fullscreen overflow-hidden position-relative"
  >
    <QuizBackground
      primary-color="hsl(185, 75%, 50%)"
      secondary-color="hsl(215, 85%, 60%)"
    />

    <div class="container-xxl d-flex flex-column h-100">
      <BCard
        class="lobby-container rounded-4 col-12 col-md-8 col-lg-6 p-0 p-md-3 m-auto"
        body-class="d-flex flex-column gap-2"
      >
        <div class="lobby-header text-center">
          <span class="fs-1 fw-bold">{{ $t("quiz.title") }}</span>
          <div class="text-accent">{{ $t("quiz.lobby.subtitle") }}</div>
        </div>

        <BForm
          class="d-flex flex-column gap-2 pt-1"
          v-if="selectedForm === 'join'"
        >
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
              v-model="form.lobbyCode"
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
            :disabled="isLoading || !validatePlayerName || !validateJoinCode"
            @click.prevent="joinGame"
          >
            <BSpinner small class="me-2" v-if="isLoading" />
            {{
              isLoading
                ? $t("quiz.lobby.joining")
                : $t("quiz.lobby.join_button")
            }}
          </BButton>

          <div class="text-center mt-2">
            <iconify-icon icon="fa6-solid:plus" class="me-1" />
            <a href="#" @click.prevent="selectedForm = 'create'">{{
              $t("quiz.lobby.or_create_game")
            }}</a>
          </div>
        </BForm>

        <BForm class="d-flex flex-column gap-2 pt-1" v-else>
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
            @click.prevent="createGame"
          >
            <BSpinner small class="me-2" v-if="isLoading" />
            {{
              isLoading
                ? $t("quiz.lobby.creating")
                : $t("quiz.lobby.create_game")
            }}
          </BButton>

          <div class="text-center mt-2">
            <iconify-icon icon="fa6-solid:door-open" class="me-1" />
            <a href="#" @click.prevent="selectedForm = 'join'">{{
              $t("quiz.lobby.or_join_game")
            }}</a>
          </div>
        </BForm>
      </BCard>
    </div>
  </div>

  <BToastOrchestrator />
</template>

<style scoped lang="scss">
.quiz-lobby-page {
  background-color: rgba(7, 28, 57, 1);
}

.lobby-header {
  span {
    background-image: linear-gradient(
      90deg,
      hsl(222, 84%, 60%),
      hsl(212, 78%, 71%)
    );
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

.btn-primary {
  background: linear-gradient(90deg, hsl(222, 84%, 60%), hsl(212, 78%, 71%));
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
  --bs-border-color: rgb(67, 119, 239);
  --bs-nav-tabs-link-active-bg: rgba(67, 119, 239, 0.4);
  --bs-nav-tabs-link-active-color: rgba(
    var(--bs-accent-rgb),
    var(--bs-text-opacity, 1)
  );
  --bs-nav-tabs-link-active-border-color: var(--bs-border-color)
    var(--bs-border-color) var(--bs-border-color);
  --bs-nav-tabs-link-hover-border-color: transparent;
  --bs-nav-tabs-border-width: 2px;
}

.lobby-tabs .form-control {
  --bs-border-color: rgb(67, 119, 239);
}
</style>
