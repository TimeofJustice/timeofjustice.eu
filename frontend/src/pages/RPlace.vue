<script setup lang="ts">
import { onMounted, ref } from "vue";
import axios from "@node_modules/axios";
import { faArrowsToDot, faEyeDropper, faPalette } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { faMaximize } from "@fortawesome/free-solid-svg-icons";
import { Head } from "@node_modules/@inertiajs/vue3";

const fieldPanZoom = ref<HTMLCanvasElement | null>(null);
const cursorImage = ref<HTMLImageElement | null>(null);
const playerCount = ref(1);
const coordinates = ref({ x: 500, y: 500 });
const fullscreen = ref(false);
const canvasContainer = ref<HTMLDivElement | null>(null);
const started = ref(false);
const disconnected = ref(false);
const chunkNumber = ref(0);
const loadedChunks = ref(0);

const colors = [
  '#6d001a',
  '#ff4500',
  '#ffd635',
  '#00a368',
  '#7eed56',
  '#009eaa',
  '#2450a4',
  '#51e9f4',
  '#6a5cff',
  '#811e9f',
  '#e4abff',
  '#ff3881',
  '#6d482f',
  '#ffb470',
  '#515252',
  '#d4d7d9',
  '#be0039',
  '#ffa800',
  '#fff8b8',
  '#00cc78',
  '#00756f',
  '#00ccc0',
  '#3690ea',
  '#493ac1',
  '#94b3ff',
  '#b44ac0',
  '#de107f',
  '#ff99aa',
  '#9c6926',
  '#000000',
  '#898d90',
  '#ffffff'
];
const customColor = ref('#000000');
const selectedColor = ref(colors[0]);
const paintFunction = ref<() => void>(() => {
  console.error('Paint function not set');
});
const pickColorFunction = ref<() => void>(() => {
  console.error('Pick color function not set');
});
const recenterFunction = ref<() => void>(() => {
  console.error('Recenter function not set');
});

type Chunk = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  paintCell: (x: number, y: number, color: string) => void;
  getColor: (x: number, y: number) => string;
};

const setUpCanvas = (canvas: HTMLCanvasElement, cursor: HTMLImageElement) => {
  const setUpCanvasSize = () => {
    const parent = canvas.parentElement;
    if (!parent) {
      console.error('Canvas parent element not found');
      return;
    }
    const oldWidth = canvas.width;
    const oldHeight = canvas.height;
    const newWidth = parent.clientWidth - (parseFloat(getComputedStyle(parent).paddingLeft) || 0) - (parseFloat(getComputedStyle(parent).paddingRight) || 0);
    const newHeight = parent.clientHeight - (parseFloat(getComputedStyle(parent).paddingTop) || 0) - (parseFloat(getComputedStyle(parent).paddingBottom) || 0);
    const deltaWidth = newWidth - oldWidth;
    const deltaHeight = newHeight - oldHeight;
    canvas.width = newWidth;
    canvas.height = newHeight;

    return {
      deltaWidth,
      deltaHeight,
    };
  };
  setUpCanvasSize();

  const rectWidth = 1000;
  const rectHeight = 1000;
  const cellSize = 10;

  const numberOfChunks = 5;
  const chunkWidth = rectWidth / numberOfChunks;
  const chunkHeight = rectHeight / numberOfChunks;

  const view = {
    x: (canvas.width - rectWidth) / 2,
    y: (canvas.height - rectHeight) / 2,
    scale: 0.1,
    highlightedCell: { x: 500, y: 500 },
    chunks: [] as Chunk[],
    apply(ctx: CanvasRenderingContext2D) {
      ctx.setTransform(this.scale, 0, 0, this.scale, this.x, this.y);
    },
    pan(amount: { x: number; y: number }) {
      this.x += amount.x;
      this.y += amount.y;
    },
    recenter() {
      if (!this.highlightedCell) return;
      this.centerCell(this.highlightedCell.x, this.highlightedCell.y);
    },
    centerCell(x: number, y: number) {
      const targetX = (canvas.width / 2) - ((x * cellSize * this.scale) + (cellSize * this.scale / 2));
      const targetY = (canvas.height / 2) - ((y * cellSize * this.scale) + (cellSize * this.scale / 2));
      const duration = 300;
      const startX = this.x;
      const startY = this.y;
      const startTime = performance.now();

      const animate = (now: number) => {
        const elapsed = Math.min((now - startTime) / duration, 1);
        this.x = startX + (targetX - startX) * elapsed;
        this.y = startY + (targetY - startY) * elapsed;
        draw();
        if (elapsed < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    },
    scaleAt(at: { x: number; y: number }, amount: number) {
      const oldScale = this.scale;
      this.scale *= amount;
      this.scale = Math.max(0.1, Math.min(this.scale, 10));
      this.x = at.x - ((at.x - this.x) * (this.scale / oldScale));
      this.y = at.y - ((at.y - this.y) * (this.scale / oldScale));
    },
    initChunks() {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          if (entry.target === canvasContainer.value) {
            const delta = setUpCanvasSize();
            draw();
            if (delta === undefined) return;
            this.x += delta.deltaWidth / 2;
            this.y += delta.deltaHeight / 2;
          }
        }
      });

      resizeObserver.observe(canvasContainer.value!);

      for (let i = 0; i < numberOfChunks; i++) {
        for (let j = 0; j < numberOfChunks; j++) {
          const offscreenCanvas = document.createElement('canvas');
          offscreenCanvas.width = chunkWidth + 1;
          offscreenCanvas.height = chunkHeight + 1;
          const offscreenCtx = offscreenCanvas.getContext('2d')!;

          offscreenCtx.fillStyle = 'white';
          offscreenCtx.fillRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);

          const paintCell = (x: number, y: number, color: string) => {
            offscreenCtx.fillStyle = color;
            if (x === offscreenCanvas.width - 2 && y === offscreenCanvas.height - 2) {
              offscreenCtx.fillRect(x, y, 2, 2);
            } else if (x === offscreenCanvas.width - 2) {
              offscreenCtx.fillRect(x, y, 2, 1);
            } else if (y === offscreenCanvas.height - 2) {
              offscreenCtx.fillRect(x, y, 1, 2);
            } else {
              offscreenCtx.fillRect(x, y, 1, 1);
            }
          };

          const getColor = (x: number, y: number) => {
            function rgbToHex(r: number, g: number, b: number) {
              if (r > 255 || g > 255 || b > 255)
                throw "Invalid color component";
              return ((r << 16) | (g << 8) | b).toString(16);
            }

            var p = offscreenCtx.getImageData(x, y, 1, 1).data;
            var hex = "#" + ("000000" + rgbToHex(p[0], p[1], p[2])).slice(-6);
            return hex;
          };

          this.chunks.push({
            canvas: offscreenCanvas,
            ctx: offscreenCtx,
            paintCell: paintCell,
            getColor: getColor
          });
        }
      }
    },
    loadChunks() {
      const numberOfRequestedChunks = 4;
      const chunkWidth = rectWidth / numberOfRequestedChunks;
      const chunkHeight = rectHeight / numberOfRequestedChunks;
      chunkNumber.value = numberOfRequestedChunks * numberOfRequestedChunks;

      const loadNextChunk = (i: number) => {
        console.log(`Loading chunk ${i + 1}/${numberOfRequestedChunks * numberOfRequestedChunks}`);

        if (i >= numberOfRequestedChunks * numberOfRequestedChunks) return;

        const chunkX = (i % numberOfRequestedChunks) * (chunkWidth);
        const chunkY = Math.floor(i / numberOfRequestedChunks) * (chunkHeight);

        axios.post(`/r-place/api/load_chunk/${chunkX}/${chunkY}/${chunkWidth}/`)
          .then(response => {
            const data = response.data;
            this.loadChunk(data.cells);
          })
          .catch(error => {
            console.error(`Error loading chunk ${i}:`, error);
          })
          .finally(() => {
            loadedChunks.value++;

            if (i < numberOfRequestedChunks * numberOfRequestedChunks - 1) {
              setTimeout(() => loadNextChunk(i + 1), 100);
            } else {
              console.log('All chunks loaded');
              started.value = true;
              draw();
            }
          });
      };
      loadNextChunk(0);
    },
    loadChunk(cells: { x: number; y: number; color: string }[]) {
      cells.forEach(cell => {
        const chunkX = Math.floor(cell.x / chunkWidth);
        const chunkY = Math.floor(cell.y / chunkHeight);
        const localX = cell.x % chunkWidth;
        const localY = cell.y % chunkHeight;

        const chunkIndex = (chunkY * numberOfChunks) + chunkX;
        if (chunkIndex < 0 || chunkIndex >= this.chunks.length) return;

        const chunk = this.chunks[chunkIndex];
        chunk.paintCell(localX, localY, cell.color);
      });
    },
    drawCell(x: number, y: number, color: string) {
      const chunkX = Math.floor(x / chunkWidth);
      const chunkY = Math.floor(y / chunkHeight);
      const localX = x % chunkWidth;
      const localY = y % chunkHeight;

      const chunkIndex = (chunkY * numberOfChunks) + chunkX;
      if (chunkIndex < 0 || chunkIndex >= this.chunks.length) return;

      const chunk = this.chunks[chunkIndex];
      chunk.paintCell(localX, localY, color);
    },
    pickColor(x: number, y: number) {
      const chunkX = Math.floor(x / chunkWidth);
      const chunkY = Math.floor(y / chunkHeight);
      const localX = x % chunkWidth;
      const localY = y % chunkHeight;

      const chunkIndex = (chunkY * numberOfChunks) + chunkX;
      if (chunkIndex < 0 || chunkIndex >= this.chunks.length) return null;

      const chunk = this.chunks[chunkIndex];
      return chunk.getColor(localX, localY);
    },
    click(e: MouseEvent) {
      const bounds = canvas.getBoundingClientRect();
      const pos = {
        x: Math.floor((e.clientX - bounds.left - this.x) / (cellSize * this.scale)),
        y: Math.floor((e.clientY - bounds.top - this.y) / (cellSize * this.scale))
      }
      if (pos.x < 0 || pos.x >= rectWidth || pos.y < 0 || pos.y >= rectHeight) return;
      this.highlightCell(pos.x, pos.y);
      return pos;
    },
    highlightCell(x: number, y: number) {
      this.highlightedCell = { x, y };
      this.centerCell(x, y);
      coordinates.value = { x, y };
    },
    paintCell() {
      const color = selectedColor.value;
      if (!this.highlightedCell) return;
      chatSocket.send(JSON.stringify({
        type: 'cell_update',
        x: this.highlightedCell.x,
        y: this.highlightedCell.y,
        color: color
      }));
    }
  };
  view.initChunks();
  paintFunction.value = () => {
    view.paintCell();
  };
  pickColorFunction.value = () => {
    const color = view.pickColor(view.highlightedCell.x, view.highlightedCell.y);
    if (color) {
      if (!colors.includes(color)) {
        customColor.value = color;
      }
      selectedColor.value = color;
    }
  };
  recenterFunction.value = () => {
    view.recenter();
  };

  const draw = () => {
    const ctx = canvas.getContext('2d')!;
    ctx.imageSmoothingEnabled = false;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();

    view.apply(ctx);

    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, rectWidth * cellSize, rectHeight * cellSize);

    for (let i = 0; i < view.chunks.length; i++) {
      const chunk = view.chunks[i];
      const chunkX = (i % numberOfChunks) * chunkWidth;
      const chunkY = Math.floor(i / numberOfChunks) * chunkHeight;
      ctx.drawImage(
        chunk.canvas,
        ((chunkX * 10)),
        ((chunkY * 10)),
        ((chunkWidth + 1) * 10),
        ((chunkHeight + 1) * 10)
      );
    }

    // Remove pixel that are only for rounding issues
    ctx.clearRect(10000, -10, 20, (canvas.height * 10) + 20);
    ctx.clearRect(-10, 10000, (canvas.width * 10) + 20, 20);

    if (view.scale > 3) {
      const alpha = Math.min(1, (view.scale - 3) / 2);
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = 'rgb(144,144,144)';
      ctx.lineWidth = 0.1;
      for (let x = 0; x < rectWidth * cellSize; x += cellSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, rectHeight * cellSize);
        ctx.stroke();
      }
      for (let y = 0; y < rectHeight * cellSize; y += cellSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(rectWidth * cellSize, y);
        ctx.stroke();
      }
      ctx.restore();
    }

    ctx.drawImage(cursor,
      view.highlightedCell.x * cellSize - 0.1,
      view.highlightedCell.y * cellSize - 0.1,
      cellSize + 0.2,
      cellSize + 0.2
    );
  };
  draw();

  let isDragging = false;
  let lastMouse = { x: 0, y: 0 };
  const mouseDown = { x: 0, y: 0 };

  canvas.addEventListener('click', (e) => {
    if (
      Math.abs(mouseDown.x - e.clientX) >= 30 ||
      Math.abs(mouseDown.y - e.clientY) >= 30
    ) {
      e.stopPropagation();
    }
  }, true);

  canvas.addEventListener('click', (e) => {
    view.click(e);
    draw();
  }, false);

  canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    lastMouse = { x: e.clientX, y: e.clientY };
    mouseDown.x = e.clientX;
    mouseDown.y = e.clientY;
  });

  canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    lastMouse = { x: e.clientX, y: e.clientY };
    mouseDown.x = e.clientX;
    mouseDown.y = e.clientY;

    const onMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const dx = e.clientX - lastMouse.x;
        const dy = e.clientY - lastMouse.y;
        view.pan({ x: dx, y: dy });
        lastMouse = { x: e.clientX, y: e.clientY };
        draw();
      }
      e.stopPropagation();
    };

    const onMouseUp = () => {
      isDragging = false;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  });

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mouse = {
      x: (e.clientX - rect.left),
      y: (e.clientY - rect.top)
    };
    const zoomFactor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    view.scaleAt(mouse, zoomFactor);
    draw();
  });

  const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";

  const chatSocket = new WebSocket(
    ws_scheme
    + '://'
    + window.location.host
    + '/ws/r-place/'
  );
  chatSocket.onopen = () => {
    console.log('WebSocket connection established');
    view.loadChunks();
  };
  chatSocket.onmessage = (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    if (data.type === 'cell_update') {
      const cell = data.cell;
      view.drawCell(cell.x, cell.y, cell.color);
      draw();
    } else if (data.type === 'player_update') {
      playerCount.value = data.count;
    }
  };
  chatSocket.onclose = () => {
    console.log('WebSocket connection closed');
    disconnected.value = true;
    started.value = false;
  };
};

onMounted(() => {
  if (!fieldPanZoom.value || !cursorImage.value) {
    console.error('Canvas element not found');
    return;
  }
  const canvas = fieldPanZoom.value;
  if (!(canvas instanceof HTMLCanvasElement)) {
    console.error('fieldPanZoom is not a canvas element');
    return;
  }
  setUpCanvas(canvas, cursorImage.value);
});
</script>

<template>
  <Head :title="$t('r_place.title')" />

  <div class="container-xxl h-100 overflow-hidden mb-2" :class="{ 'fullscreen': fullscreen }" ref="canvasContainer">
    <div class="w-100 rounded overflow-hidden position-relative h-100">
      <Transition>
        <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center bg-dark" v-if="!started || disconnected"
             :class="{ 'bg-opacity-75': disconnected }">
          <BProgress :max="chunkNumber" class="col-5" v-if="!started && !disconnected">
            <BProgressBar :value="loadedChunks" striped animated>
              <small>{{ Math.round((loadedChunks / chunkNumber) * 100) }}%</small>
            </BProgressBar>
          </BProgress>

          <BButton class="button text-light d-flex flex-column justify-content-center align-items-center rounded-0" to="/r-place/" v-if="disconnected">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.disconnected.title") }}</span>
            <span>{{ $t("r_place.canvas.disconnected.description") }}</span>
          </BButton>
        </div>
      </Transition>

      <canvas width="1000" height="1000" ref="fieldPanZoom" class="field bg-grey-200"></canvas>

      <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column justify-content-end pe-none">
        <div class="position-absolute top-0 end-0 p-2">
          <button class="button button-small text-light" @click="fullscreen = !fullscreen; ">
            <font-awesome-icon :icon="faMaximize"/>
          </button>
        </div>
        <div class="d-flex justify-content-center align-items-center gap-2 p-2 position-relative" v-if="started">
          <button class="button button-small text-light" @click="recenterFunction()">
            <font-awesome-icon :icon="faArrowsToDot"/>
          </button>
          <button class="button button-big text-light d-flex flex-column justify-content-center align-items-center" @click="paintFunction()">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.place_pixel") }}</span>
            <span>X: {{coordinates.x}} Y: {{coordinates.y}}</span>
          </button>
          <button class="button button-small text-light" @click="pickColorFunction()">
            <font-awesome-icon :icon="faEyeDropper"/>
          </button>
          <div class="position-absolute bottom-0 end-0 p-2 text-black fw-bold">
            {{ $t('r_place.canvas.players_online', {"player_count": playerCount}) }}
          </div>
        </div>
        <div class="colors" :class="{ active: started }">
          <div class="d-flex justify-content-center align-items-center gap-1">
            <div class="colors-container">
              <div class="col color" :class="{ active: selectedColor === color }" :style="{ backgroundColor: color }" @click="selectedColor = color" v-for="color in colors"></div>
            </div>
            <div class="position-relative">
              <BInput type="color" v-model="customColor" class="color color-big" :class="{ active: selectedColor === customColor && !colors.includes(selectedColor) }"
                      @blur="selectedColor = customColor" />
              <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center pe-none">
                <font-awesome-icon :icon="faPalette"/>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="d-none">
    <img :src="require('@assets/images/Cursor.png')" ref="cursorImage" />
  </div>
</template>

<style scoped lang="scss">
@import "@/assets/scss/colors.scss";

canvas {
  image-rendering: pixelated;
}

.fullscreen {
  max-width: 100%;
}

.container-xxl {
  transition: max-width .5s ease-in-out, height .5s ease-in-out;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}

.colors {
  display: flex;
  justify-content: center;
  align-items: center;

  width: 100%;
  height: 0;
  min-height: 0;
  max-height: 8rem;
  margin-bottom: -2px;

  background: $lightgray-200;
  border-top: 2px solid $black;

  transition: height .5s ease-in-out, min-height .5s ease-in-out;

  pointer-events: all;
  overflow: hidden;

  &.active {
    height: 25%;
    min-height: 4rem;
  }
}

.colors-container {
  display: grid;
  grid-template-rows: repeat(2, fit-content(100%));
  grid-template-columns: repeat(16, fit-content(100%));
  grid-gap: 0.25rem;
}

.color {
  position: relative;

  width: 2.5rem;
  height: 2.5rem;

  cursor: pointer;

  border: 2px solid $black;

  transition: border .2s ease-in-out, transform .2s ease-in-out;

  &:hover {
    border: 2px solid $gray-10;
  }

  &-big {
    height: 5.25rem;
    width: 5.25rem;

    border-radius: 0;
    padding: 0;
  }

  &.active {
    border: 4px solid $black;
    transform: scale(1.05);
  }
}

input[type=color]::-webkit-color-swatch {
  border-radius: 0;
}

.button {
  display: flex;
  justify-content: center;
  align-items: center;

  width: 12rem;
  padding: 0.5rem;

  background: $gray-500;
  border: 2px solid $black;

  pointer-events: all;

  &-small {
    width: auto;
  }

  &:hover {
    border: 2px solid $gray-10;
  }
}
</style>