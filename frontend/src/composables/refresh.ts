import { onBeforeUnmount, onMounted, watch } from "vue";
import { router } from "@inertiajs/vue3";

/**
 * How long the tab has to have been away before coming back is worth a request.
 * Short enough that a glance at another window is free, long enough that a real
 * absence is caught.
 */
const AWAY_THRESHOLD = 15_000;

export interface RefreshOnReturnOptions {
  /**
   * Skips the refresh while this is true. For anything the incoming data would
   * pull out from under the user: an open dialog, a half-filled form.
   */
  paused?: () => boolean;
  /**
   * Runs once the new props have arrived.
   *
   * `router.reload` keeps the page component mounted, so anything a page copied
   * out of its props at setup is still the old copy and has to be taken again
   * here. Pages that read their props directly need nothing.
   */
  onRefreshed?: () => void;
}

/**
 * Fetches the page again when the tab is returned to.
 *
 * A tab left open overnight is showing yesterday: the server decides what
 * "today" is, and it decided that when the page was first rendered. Coming back
 * to the tab is the moment to ask again.
 */
export const useRefreshOnReturn = ({
  paused,
  onRefreshed,
}: RefreshOnReturnOptions = {}) => {
  let hiddenAt: number | null = null;
  let renderedOn = new Date().toDateString();
  let inFlight = false;
  /** A refresh that came due while paused, waiting for the way to clear. */
  let owed = false;

  const refresh = () => {
    if (inFlight) return;

    inFlight = true;

    router.reload({
      onSuccess: () => {
        renderedOn = new Date().toDateString();
        onRefreshed?.();
      },
      onFinish: () => {
        inFlight = false;
      },
    });
  };

  /**
   * Held rather than dropped when the way is blocked: returning to a tab with a
   * dialog open is exactly when the page is most likely to be a day out of
   * date, and there is no second visibility change coming to ask again.
   */
  const attempt = () => {
    if (paused?.()) {
      owed = true;
      return;
    }

    owed = false;
    refresh();
  };

  if (paused) {
    watch(paused, (isPaused) => {
      if (!isPaused && owed) attempt();
    });
  }

  const onVisibilityChange = () => {
    if (document.hidden) {
      hiddenAt = Date.now();
      return;
    }

    const awayFor = hiddenAt === null ? 0 : Date.now() - hiddenAt;
    hiddenAt = null;

    // The clock rolling over counts however brief the absence was: that is the
    // case where the page is not merely stale but wrong about what day it is.
    const newDay = new Date().toDateString() !== renderedOn;

    if (awayFor >= AWAY_THRESHOLD || newDay) attempt();
  };

  onMounted(() =>
    document.addEventListener("visibilitychange", onVisibilityChange),
  );

  onBeforeUnmount(() =>
    document.removeEventListener("visibilitychange", onVisibilityChange),
  );
};
