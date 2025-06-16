<script setup lang="ts">
import { onMounted, ref } from "vue";
import { faArrowsToDot, faBinoculars, faEyeDropper, faPalette } from "@node_modules/@fortawesome/free-solid-svg-icons";
import { faMaximize } from "@fortawesome/free-solid-svg-icons";
import { Head } from "@node_modules/@inertiajs/vue3";
import axios from "@node_modules/axios";

interface PlaceState {
  playerCount: number;
  coordinates: { x: number; y: number };
  fullscreen: boolean;
  state: 'loading' | 'started' | 'disconnected';
  chunks: {
    number: number;
    loaded: number;
  };
  color: {
    active: string;
    custom: string;
  }
}

type Chunk = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  paintCell: (x: number, y: number, color: string) => void;
  getColor: (x: number, y: number) => string;
};

interface Canvas {
  name: string;
  width: number;
  height: number;
  active: boolean;
}

interface Props {
  activeCanvas: Canvas;
  canvases: Canvas[];
}

const { activeCanvas, canvases } = defineProps<Props>();

const canvas = ref<HTMLCanvasElement | null>(null);
const cursorImage = ref<HTMLImageElement | null>(null);

const canvasContainer = ref<HTMLDivElement | null>(null);

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

const paintFunction = ref<() => void>(() => {
  console.error('Paint function not set');
});
const pickColorFunction = ref<() => void>(() => {
  console.error('Pick color function not set');
});
const recenterFunction = ref<() => void>(() => {
  console.error('Recenter function not set');
});

const placeState = ref<PlaceState>({
  playerCount: 1,
  coordinates: { x: 0, y: 0 },
  fullscreen: false,
  state: 'loading',
  chunks: {
    number: 0,
    loaded: 0
  },
  color: {
    active: '#6d001a',
    custom: '#00156b'
  }
});

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

  const rectWidth = activeCanvas.width;
  const rectHeight = activeCanvas.height;
  const cellSize = 10;

  const numberOfChunks = 5;
  const chunkWidth = rectWidth / numberOfChunks;
  const chunkHeight = rectHeight / numberOfChunks;

  const view = {
    x: (canvas.width - rectWidth) / 2,
    y: (canvas.height - rectHeight) / 2,
    scale: 0.1,
    highlightedCell: { x: rectWidth / 2, y: rectHeight / 2 },
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
            if (delta !== undefined) {
              this.x += delta.deltaWidth / 2;
              this.y += delta.deltaHeight / 2;
            }
            draw();
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
      placeState.value.chunks.number = numberOfRequestedChunks * numberOfRequestedChunks;

      const loadNextChunk = (i: number) => {
        if (i >= numberOfRequestedChunks * numberOfRequestedChunks) return;

        const chunkX = (i % numberOfRequestedChunks) * (chunkWidth);
        const chunkY = Math.floor(i / numberOfRequestedChunks) * (chunkHeight);

        axios.get(`/r-place/api/load_chunk/${chunkX}/${chunkY}/${chunkWidth}/${activeCanvas.name}/`)
          .then(response => {
            const data = response.data;
            this.loadChunk(data.cells);
          })
          .catch(error => {
            console.error(`Error loading chunk ${i}:`, error);
          })
          .finally(() => {
            placeState.value.chunks.loaded++;

            if (i < numberOfRequestedChunks * numberOfRequestedChunks - 1) {
              setTimeout(() => loadNextChunk(i + 1), 100);
            } else {
              placeState.value.state = 'started';
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
      if (x < 0 || x >= rectWidth || y < 0 || y >= rectHeight) return;

      this.highlightedCell = { x, y };
      this.centerCell(x, y);
      placeState.value.coordinates = { x, y };
    },
    paintCell() {
      const color = placeState.value.color.active;
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
        placeState.value.color.custom = color;
      }
      placeState.value.color.active = color;
    }
  };
  recenterFunction.value = () => {
    view.recenter();
  };
  placeState.value.coordinates = {
    x: view.highlightedCell.x,
    y: view.highlightedCell.y
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
    ctx.clearRect(rectWidth * cellSize, -cellSize * 1.5, cellSize * 1.5, (rectWidth * cellSize) + cellSize * 3);
    ctx.clearRect(-cellSize * 1.5, rectHeight * cellSize, (rectHeight * cellSize) + cellSize * 3, cellSize * 1.5);

    if (view.scale > 2) {
      const alpha = Math.min(1, (view.scale - 2) / 2);
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

  // Desktop: Tastatursteuerung
  window.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      view.recenter();
      draw();
    } else if (e.key === ' ') {
      e.preventDefault();
      view.paintCell();
      draw();
    } else if (e.key === 'c' || e.key === 'C') {
      e.preventDefault();
      const color = view.pickColor(view.highlightedCell.x, view.highlightedCell.y);
      if (color) {
        if (!colors.includes(color)) {
          placeState.value.color.custom = color;
        }
        placeState.value.color.active = color;
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      view.highlightCell(view.highlightedCell.x, view.highlightedCell.y - 1);
      view.centerCell(view.highlightedCell.x, view.highlightedCell.y);
      draw();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      view.highlightCell(view.highlightedCell.x, view.highlightedCell.y + 1);
      view.centerCell(view.highlightedCell.x, view.highlightedCell.y);
      draw();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      view.highlightCell(view.highlightedCell.x - 1, view.highlightedCell.y);
      view.centerCell(view.highlightedCell.x, view.highlightedCell.y);
      draw();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      view.highlightCell(view.highlightedCell.x + 1, view.highlightedCell.y);
      view.centerCell(view.highlightedCell.x, view.highlightedCell.y);
      draw();
    } else if (e.key === 'Tab') {
      e.preventDefault();
      const currentIndex = colors.indexOf(placeState.value.color.active);
      if (currentIndex === -1) {
        placeState.value.color.active = colors[0];
      } else if (currentIndex === colors.length - 1) {
        placeState.value.color.active = placeState.value.color.custom;
      } else {
        placeState.value.color.active = colors[currentIndex + 1];
      }
    }
  });

  // Desktop: Maussteuerung
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

  // Mobile: Touchsteuerung
  canvas.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isDragging = true;
      lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      mouseDown.x = e.touches[0].clientX;
      mouseDown.y = e.touches[0].clientY;
    }
  }, { passive: false });

  canvas.addEventListener('touchmove', (e) => {
    if (isDragging && e.touches.length === 1) {
      const dx = e.touches[0].clientX - lastMouse.x;
      const dy = e.touches[0].clientY - lastMouse.y;
      view.pan({ x: dx, y: dy });
      lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      draw();
      e.preventDefault();
    }
  }, { passive: false });

  canvas.addEventListener('touchend', () => {
    isDragging = false;
  }, { passive: false });

  canvas.addEventListener('touchcancel', () => {
    isDragging = false;
  }, { passive: false });

  canvas.addEventListener('touchend', (e) => {
    if (e.changedTouches.length === 1) {
      const touch = e.changedTouches[0];
      if (
        Math.abs(mouseDown.x - touch.clientX) < 30 &&
        Math.abs(mouseDown.y - touch.clientY) < 30
      ) {
        // Simuliere Klick
        const fakeEvent = {
          clientX: touch.clientX,
          clientY: touch.clientY,
          stopPropagation: () => {},
        } as MouseEvent;
        view.click(fakeEvent);
        draw();
      }
    }
  }, { passive: false });

  // Zoom (Pinch-to-zoom)
  let lastPinchDist: number | null = null;
  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (lastPinchDist !== null) {
        const zoomFactor = dist / lastPinchDist;
        const rect = canvas.getBoundingClientRect();
        const center = {
          x: (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left,
          y: (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top
        };
        view.scaleAt(center, zoomFactor);
        draw();
      }
      lastPinchDist = dist;
      e.preventDefault();
    } else {
      lastPinchDist = null;
    }
  }, { passive: false });

  canvas.addEventListener('touchend', (e) => {
    if (e.touches.length < 2) {
      lastPinchDist = null;
    }
  }, { passive: false });

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
      placeState.value.playerCount = data.count;
    }
  };
  chatSocket.onclose = () => {
    console.log('WebSocket connection closed');
    placeState.value.state = 'disconnected';
  };
};

onMounted(() => {
  if (!canvas.value || !cursorImage.value) {
    console.error('Canvas element not found');
    return;
  }
  if (!(canvas.value instanceof HTMLCanvasElement)) {
    console.error('canvas is not a canvas element');
    return;
  }
  setUpCanvas(canvas.value, cursorImage.value);
});
</script>

<template>
  <Head :title="$t('r_place.title')" />

  <div class="container-xxl h-100 overflow-hidden mb-2" :class="{ 'fullscreen': placeState.fullscreen }" ref="canvasContainer">
    <div class="w-100 rounded overflow-hidden position-relative h-100">
      <Transition>
        <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center bg-dark" v-if="placeState.state !== 'started'"
             :class="{ 'bg-opacity-75': placeState.state === 'disconnected' }">
          <BProgress :max="placeState.chunks.number" class="col-5" v-if="placeState.state === 'loading'">
            <BProgressBar :value="placeState.chunks.loaded" striped animated>
              <small>{{ Math.round((placeState.chunks.loaded / placeState.chunks.number) * 100) }}%</small>
            </BProgressBar>
          </BProgress>

          <BButton class="button text-light d-flex flex-column justify-content-center align-items-center rounded-0" to="/r-place/" v-if="placeState.state === 'disconnected'">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.disconnected.title") }}</span>
            <span>{{ $t("r_place.canvas.disconnected.description") }}</span>
          </BButton>
        </div>
      </Transition>

      <canvas width="1000" height="1000" ref="canvas" class="field bg-grey-200"></canvas>

      <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column justify-content-end pe-none">
        <div class="position-absolute top-0 end-0 p-2">
          <button class="button button-small text-light d-none d-xxl-flex" @click="placeState.fullscreen = !placeState.fullscreen;">
            <font-awesome-icon :icon="faMaximize"/>
          </button>
        </div>
        <div class="position-absolute top-0 start-0 p-2">
          <BDropdown variant="primary" class="pe-auto place-dropdown" offset="5">
            <template #button-content>
              <font-awesome-icon :icon="faBinoculars" class="me-2" />
              <span>{{ activeCanvas.name }}</span>
            </template>
            <BDropdownItem v-for="canvas in canvases" :key="canvas.name" :to="'/r-place/' + canvas.name + '/'" link-class="d-flex align-items-center justify-content-between gap-2">
              {{ canvas.name }}
              <BBadge variant="success" v-if="canvas.active">
                Ongoing
              </BBadge>
            </BDropdownItem>
          </BDropdown>
        </div>
        <div class="d-flex justify-content-center align-items-center gap-2 p-2 position-relative" v-if="placeState.state === 'started'">
          <button class="button button-small text-light" @click="recenterFunction()">
            <font-awesome-icon :icon="faArrowsToDot"/>
          </button>
          <button class="button button-big text-light d-flex flex-column justify-content-center align-items-center" @click="paintFunction()">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.place_pixel") }}</span>
            <span>X: {{placeState.coordinates.x}} Y: {{placeState.coordinates.y}}</span>
          </button>
          <button class="button button-small text-light" @click="pickColorFunction()">
            <font-awesome-icon :icon="faEyeDropper"/>
          </button>
          <div class="position-absolute bottom-0 end-0 p-2 text-black fw-bold d-none d-sm-block">
            {{ $t('r_place.canvas.players_online', {"player_count": placeState.playerCount}) }}
          </div>
        </div>
        <div class="colors" :class="{ active: placeState.state === 'started' }">
          <div class="d-flex justify-content-center align-items-center gap-1">
            <div class="colors-container">
              <div class="col color" :class="{ active: placeState.color.active === color }" :style="{ backgroundColor: color }" @click="placeState.color.active = color" v-for="color in colors"></div>
            </div>
            <div class="position-relative d-none d-sm-block">
              <BInput type="color" v-model="placeState.color.custom" class="color color-big" :class="{ active: placeState.color.active === placeState.color.custom && !colors.includes(placeState.color.active) }"
                      @blur="placeState.color.active = placeState.color.custom" />
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

<style lang="scss">
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

    @media (max-width: 576px) {
      min-height: 10rem;
    }

    @media (max-width: 992px) {
      min-height: 12rem;
    }
  }
}

.colors-container {
  display: grid;
  grid-template-rows: repeat(2, fit-content(100%));
  grid-template-columns: repeat(16, fit-content(100%));
  grid-gap: 0.25rem;

  @media (max-width: 992px) {
    grid-template-columns: repeat(8, fit-content(100%));
  }
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

  @media (max-width: 576px) {
    width: 2.25rem;
    height: 2.25rem;
  }

  &-big {
    border: 2px solid $black!important;
    height: 5.25rem!important;
    width: 5.25rem!important;

    border-radius: 0!important;
    padding: 0!important;

    outline: none!important;

    &:hover {
      border: 2px solid $gray-10!important;
    }

    &.active {
      border: 4px solid $black!important;
      transform: scale(1.05)!important;
    }
  }

  &.active {
    border: 4px solid $black;
    transform: scale(1.05);
  }
}

input[type=color]::-webkit-color-swatch {
  border-radius: 0;
}

.button, .place-dropdown > .btn, .button.btn {
  display: flex;
  justify-content: center;
  align-items: center;

  padding: 0.5rem;

  --bs-btn-bg: $gray-500;
  --bs-btn-hover-bg: #{$gray-500};
  background: $gray-500;
  border: 2px solid $black;
  border-radius: 0;

  pointer-events: all;

  &-big {
    width: 12rem;
  }

  &:hover {
    border: 2px solid $gray-10;
  }
}

.place-dropdown > .dropdown-menu {
  background: $gray-500;
  border: 2px solid $black;
  border-radius: 0;
  --bs-dropdown-link-color: #{$white};

  --bs-dropdown-link-hover-color: #{$white};
  --bs-dropdown-link-hover-bg: #{$gray-300};
}
</style>