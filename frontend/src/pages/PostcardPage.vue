<script setup lang="ts">
import { Head } from "@node_modules/@inertiajs/vue3";
import { reactive, ref, watch } from "vue";
import axios from "@node_modules/axios";
import FullscreenLayout from "@layouts/FullscreenLayout.vue";

const baseURL = window.location;

interface PostcardDesign {
  id: number;
  pageColor: string;
  backgroundColor: string;
  stampColor: string;
  accentColor: string;
  textColor: string;
  icon: string;
}

interface Postcard {
  id: number;
  message: string;
  greetings: string;
  design: PostcardDesign;
}

interface PostcardPageProps {
  postcard?: Postcard;
  designs: PostcardDesign[];
}

const { postcard, designs } = defineProps<PostcardPageProps>();

const defaultPostcard: Postcard = {
  id: 0,
  message: "Hier könnte deine Nachricht stehen!",
  greetings: "Dein Name",
  design: {
    id: 0,
    pageColor: "#ffbaba",
    backgroundColor: "#fff",
    stampColor: "#e5b473",
    accentColor: "#e57373",
    textColor: "#333333",
    icon: "twemoji:teddy-bear",
  },
};

const activePostcard = reactive<Postcard>(postcard || defaultPostcard);

const showPostcard = ref(false);
const showOffcanvas = ref(false);

const activeDesignId = ref<number>(designs.length > 0 ? designs[0].id : 0);
const sendMessageId = ref("");

const form = reactive({
  message: "",
  greetings: "",
  designId: activeDesignId.value,
});

watch(activeDesignId, (newDesignId) => {
  form.designId = newDesignId;
});

const onSubmit = (event: SubmitEvent) => {
  event.preventDefault();
  event.stopPropagation();

  axios
    .post(`/sendy/api/send/`, form)
    .then((response) => {
      sendMessageId.value = response.data.data.id;
    })
    .catch(() => {});
};

const onReset = (event: Event) => {
  event.preventDefault();
  event.stopPropagation();

  form.message = "";
  form.greetings = "";

  sendMessageId.value = "";
};

const report = (event: MouseEvent) => {
  event.preventDefault();
  event.stopPropagation();

  axios
    .post(`/sendy/api/report/${activePostcard.id}`, form)
    .then(() => {})
    .catch(() => {});
};
</script>

<template>
  <Head :title="$t('postcard.title')" />

  <FullscreenLayout
    class="d-flex justify-content-center align-items-center pb-2 postcard-page"
    :style="{
      '--background-color': activePostcard.design.pageColor,
      '--postcard-background-color': activePostcard.design.backgroundColor,
      '--postcard-stamp-color': activePostcard.design.stampColor,
      '--postcard-accent-color': activePostcard.design.accentColor,
      '--postcard-text-color': activePostcard.design.textColor,
    }"
    style="padding-top: 4rem"
  >
    <div
      class="container-xxl postcard-wrapper"
      :class="{ show: showPostcard }"
      @click="showPostcard = !showPostcard"
    >
      <div class="postcard">
        <div class="postcard-front">
          <iconify-icon :icon="activePostcard.design.icon" />

          <div class="postcard-stamp"></div>
        </div>
        <div class="postcard-back">
          <div class="postcard-message">
            {{ activePostcard.message }}
          </div>
          <div class="postcard-sender mt-3">
            {{ activePostcard.greetings }}
          </div>

          <BButton
            variant="tertiary"
            class="btn-circle position-absolute top-0 end-0 m-2"
            @click="report"
          >
            <iconify-icon icon="fa:exclamation" />
          </BButton>
        </div>
      </div>
    </div>

    <div
      class="position-absolute bottom-0 start-0 end-0 mb-2 d-flex justify-content-center"
    >
      <BButton
        variant="primary"
        size="lg"
        class="btn-circle"
        @click="showOffcanvas = true"
      >
        <iconify-icon icon="streamline:send-email" />
      </BButton>
    </div>
  </FullscreenLayout>

  <BOffcanvas v-model="showOffcanvas" placement="end">
    <template #header>
      <BButton
        variant="tertiary"
        class="btn-square"
        :title="$t('general.close')"
        @click="showOffcanvas = false"
      >
        <iconify-icon icon="ep:close-bold" />
      </BButton>
    </template>

    <BForm
      @submit="onSubmit"
      @reset="onReset"
      class="d-flex flex-column gap-2"
      v-if="!sendMessageId"
    >
      <BFormGroup label="Deine Grußbotschaft" label-for="greetings">
        <BFormInput
          id="greetings"
          v-model="form.greetings"
          placeholder="Deine Grußbotschaft"
          required
        ></BFormInput>
      </BFormGroup>

      <BFormGroup label="Deine Nachricht" label-for="message">
        <BFormTextarea
          id="message"
          v-model="form.message"
          placeholder="Schreibe deine Nachricht hier..."
          rows="5"
          required
        ></BFormTextarea>
      </BFormGroup>

      <div>Dein Postkarten-Design:</div>

      <div
        class="d-grid gap-3"
        style="grid-template-columns: repeat(auto-fill, minmax(150px, 1fr))"
      >
        <div
          class="postcard-design"
          :class="{ active: design.id === activeDesignId }"
          :style="{
            '--background-color': design.pageColor,
            '--postcard-background-color': design.backgroundColor,
            '--postcard-stamp-color': design.stampColor,
            '--postcard-accent-color': design.accentColor,
            '--postcard-text-color': design.textColor,
          }"
          v-for="design in designs"
          :key="design.id"
          @click="activeDesignId = design.id"
        >
          <div class="postcard-front">
            <iconify-icon :icon="design.icon" />

            <div class="postcard-stamp"></div>
          </div>

          <div class="selected-overlay">
            <iconify-icon icon="fa6-solid:check" />
          </div>
        </div>
      </div>

      <BButton type="submit" variant="primary"> Senden </BButton>
    </BForm>

    <div class="d-flex flex-column gap-2" v-else>
      <span> Deine Nachricht findest du hier: </span>

      <div
        class="p-2 text-center bg-black bg-opacity-25 rounded w-100 d-flex justify-content-between align-items-center position-relative"
      >
        <BLink
          :href="`${baseURL}${sendMessageId}`"
          target="_blank"
          external
          class="flex-grow-1"
        >
          {{ baseURL }}{{ sendMessageId }}
        </BLink>

        <BButton variant="tertiary" class="btn-square">
          <iconify-icon icon="iconamoon:copy-duotone" />
        </BButton>
      </div>

      <BLink class="w-100 text-center" @click="onReset"> Zurück </BLink>
    </div>
  </BOffcanvas>
</template>

<style scoped lang="scss">
@keyframes shake {
  0% {
    transform: rotate(0);
  }
  10% {
    transform: rotate(-5deg);
  }
  20% {
    transform: rotate(5deg);
  }
  30% {
    transform: rotate(-5deg);
  }
  50% {
    transform: rotate(0);
  }
  100% {
    transform: rotate(0);
  }
}

.postcard-page {
  background: var(--background-color, #ffbaba);
}

.postcard-wrapper {
  background-color: transparent;
  width: 100%;
  height: 100%;
  max-width: 400px;
  max-height: 400px;
  perspective: 1000px;
  cursor: pointer;
  animation: shake 2s ease-in-out infinite;

  &.show {
    animation: none;
  }
}

.postcard {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
  transform-style: preserve-3d;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.18);
  border-radius: 2rem;
  transform: scale(0.8);
}

.postcard-wrapper.show .postcard {
  transform: rotateY(180deg) scale(1);
}

.postcard-design {
  background: var(--background-color, #ffbaba);
  position: relative;
  cursor: pointer;
  transition: transform 0.3s ease-in-out;
  border-radius: 1rem;
  overflow: hidden;
  padding: 0.5rem;

  &:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
}

.postcard-design .postcard-front {
  position: relative;
  border-radius: 1rem;
  font-size: 3rem;

  .postcard-stamp {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 25px;
    height: 25px;
    border-radius: 0.4rem;
  }
}

.postcard-design .selected-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(44, 44, 44, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  border: 2px solid currentColor;
  border-radius: 1rem;
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
}

.postcard-design.active .selected-overlay {
  opacity: 1;
}

.postcard-front,
.postcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 2rem;
  border: 2px dashed var(--postcard-accent-color, #e57373);
  padding: 2rem 3rem;
  box-shadow: 0 2px 8px 0 rgba(229, 115, 115, 0.08);
}

.postcard-front {
  background: var(--postcard-background-color, #fff);
  color: var(--postcard-accent-color, #333333);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 8rem;

  .postcard-stamp {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 50px;
    height: 50px;
    border-radius: 0.5rem;
    border: 2px dashed var(--postcard-stamp-color, #e5b473);
    background: color-mix(
      in srgb,
      var(--postcard-stamp-color, #e5b473) 20%,
      transparent
    );
    box-shadow: 0 2px 6px 0 rgba(229, 180, 115, 0.12);
  }
}

.postcard-back {
  background: var(--postcard-background-color, #fff);
  color: var(--postcard-text-color, #333333);
  transform: rotateY(180deg);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 1.2rem;
  padding: 2rem 2.5rem;
  gap: 1.5rem;

  .postcard-message {
    font-weight: 500;
    margin-bottom: 0.5rem;
    word-break: break-word;
    text-align: center;
    letter-spacing: 0.02em;
  }

  .postcard-sender {
    font-style: italic;
    color: var(--postcard-accent-color, #e57373);
    text-align: center;
    font-family: "Segoe Script", cursive;
    font-size: 1.1rem;
    letter-spacing: 0.04em;
  }
}
</style>
