<script setup lang="ts">
import LeaderboardPosition from "@/components/Quiz/LeaderboardPosition.vue";
import { QuizPlayer } from "@/types/Quiz/QuizPlayer";
import { ref } from "vue";

interface LeaderboardScreenProps {
  players: QuizPlayer[];
}

const { players } = defineProps<LeaderboardScreenProps>();
const listOfPlayers = ref<QuizPlayer[]>([]);

listOfPlayers.value = [...players];

function sort() {
  requestAnimationFrame(() => {
    listOfPlayers.value.sort((a, b) => b.score - a.score);
  });
}

function add() {
  const id = listOfPlayers.value.length;
  listOfPlayers.value.push(
    new QuizPlayer(
      id,
      `Player ${id + 1}`,
      "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnppNjQzdHQzcjJjdjF6OHRlNTN5bDh3OWtlb3o0ZzZkeWY4ODZ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/InqLhljsiZrn1Bdhzq/giphy.gif",
    ),
  );
  sort();
}

function remove(item: QuizPlayer) {
  const i = listOfPlayers.value.indexOf(item);
  if (i > -1) {
    listOfPlayers.value.splice(i, 1);
  }
}
</script>

<template>
  <div
    class="inner-screen d-flex flex-column flex-md-row justify-content-between gap-3 col-12 overflow-hidden overflow-y-auto"
  >
    <div class="col-12 col-md-4 d-flex flex-column justify-content-center">
      <span class="fs-1 fw-bold">Invite your friends</span>
      <div class="d-flex flex-column gap-3 mt-3">
        <div class="fs-5 d-flex flex-column gap-1">
          <div>
            Share
            <span class="fw-bold user-select-all">
              https://timeofjustice.eu/quiz/
            </span>
            with your friends and enter...
          </div>
          <div class="session-code">156DSF</div>
        </div>
      </div>
    </div>

    <div class="d-flex flex-column col-12 col-md-6 gap-2">
      <span class="fs-1 fw-bold text-center">Players</span>

      <div class="d-flex flex-column gap-2">
        <TransitionGroup
          tag="div"
          name="leaderboard-fade"
          class="d-flex flex-column gap-2 position-relative"
        >
          <LeaderboardPosition
            v-for="player in listOfPlayers"
            :key="player.id"
            :name="player.name"
            :score="player.score"
            @click="remove(player)"
            :url="player.image"
          />
        </TransitionGroup>
      </div>

      <div class="d-flex justify-content-evenly gap-2">
        <BButton @click="add">Add Player</BButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.leaderboard-fade-move,
.leaderboard-fade-enter-active,
.leaderboard-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

.leaderboard-fade-enter-from,
.leaderboard-fade-leave-to {
  opacity: 0;
  margin-bottom: -0.5rem;
}

.leaderboard-fade-enter-from {
  transform: translateX(-50px);
}

.leaderboard-fade-leave-to {
  transform: translateX(50px);
}

.leaderboard-fade-leave-active {
  height: 0%;
  width: 100%;
}

.inner-screen {
  max-height: 100%;
}

.session-code {
  background-image: linear-gradient(90deg, #0b2c33, #063d49);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;

  font-size: 4rem;
  font-weight: bold;
  letter-spacing: 0.5rem;

  user-select: all;
}
</style>
