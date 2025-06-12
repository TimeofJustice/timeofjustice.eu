<script setup lang="ts">
import { onMounted, ref } from "vue";
import axios from "@node_modules/axios";

const fieldPanZoom = ref<HTMLCanvasElement | null>(null);
const cursorImage = ref<HTMLImageElement | null>(null);

const setUpCanvas = (canvas: HTMLCanvasElement, cursor: HTMLImageElement) => {
  const setUpCanvasSize = () => {
    const parent = canvas.parentElement;
    if (!parent) {
      console.error('Canvas parent element not found');
      return;
    }
    canvas.width = parent.clientWidth - (parseFloat(getComputedStyle(parent).paddingLeft) || 0) - (parseFloat(getComputedStyle(parent).paddingRight) || 0);
    canvas.height = parent.clientHeight - (parseFloat(getComputedStyle(parent).paddingTop) || 0) - (parseFloat(getComputedStyle(parent).paddingBottom) || 0);
  };
  setUpCanvasSize();

  window.addEventListener('resize', () => {
    setUpCanvasSize();
    draw();
  });

  const rectWidth = 1000;
  const rectHeight = 1000;
  const cellSize = 10;

  const numberOfChunks = 5;
  const chunkWidth = rectWidth / numberOfChunks;
  const chunkHeight = rectHeight / numberOfChunks;

  const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];

  type Chunk = {
    canvas: HTMLCanvasElement;
    ctx: CanvasRenderingContext2D;
    paintCell: (x: number, y: number, color: string) => void;
  };

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

          this.chunks.push({
            canvas: offscreenCanvas,
            ctx: offscreenCtx,
            paintCell: paintCell
          });
        }
      }
    },
    loadChunks() {
      const loadNextChunk = (i: number) => {
        const numberOfRequestedChunks = 4;
        const chunkWidth = rectWidth / numberOfRequestedChunks;
        const chunkHeight = rectHeight / numberOfRequestedChunks;
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
            if (i < numberOfRequestedChunks * numberOfRequestedChunks - 1) {
              setTimeout(() => loadNextChunk(i + 1), 100);
            } else {
              console.log('All chunks loaded');
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
    click(e: MouseEvent) {
      const bounds = canvas.getBoundingClientRect();
      const pos = {
        x: Math.floor((e.clientX - bounds.left - this.x) / (cellSize * this.scale)),
        y: Math.floor((e.clientY - bounds.top - this.y) / (cellSize * this.scale))
      }
      if (pos.x < 0 || pos.x >= rectWidth || pos.y < 0 || pos.y >= rectHeight) return;
      this.highlightCell(pos.x, pos.y);
      chatSocket.send(JSON.stringify({
        type: 'cell_update',
        x: pos.x,
        y: pos.y,
        color: colors[Math.floor(Math.random() * colors.length)]
      }));
      return pos;
    },
    highlightCell(x: number, y: number) {
      this.highlightedCell = { x, y };
      this.centerCell(x, y);
    }
  };
  view.initChunks();

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

  canvas.addEventListener('mousemove', (e) => {
    if (isDragging) {
      const dx = e.clientX - lastMouse.x;
      const dy = e.clientY - lastMouse.y;
      view.pan({ x: dx, y: dy });
      lastMouse = { x: e.clientX, y: e.clientY };
      draw();
    }
    e.stopPropagation();
  });

  canvas.addEventListener('mouseup', () => {
    isDragging = false;
  });

  canvas.addEventListener('mouseleave', () => {
    isDragging = false;
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
    console.log('WebSocket message received:', e.data);
    const data = JSON.parse(e.data);
    if (data.type === 'cell_update') {
      const cell = data.cell;
      view.drawCell(cell.x, cell.y, cell.color);
      draw();
    }
  };
  chatSocket.onclose = () => {
    console.log('WebSocket connection closed');
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
  <div class="container-xxl h-100 overflow-hidden mb-2">
    <div class="w-100 rounded overflow-hidden position-relative h-100">
      <canvas width="1000" height="1000" ref="fieldPanZoom" class="field bg-grey-200"></canvas>
      <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column justify-content-end pe-none">
        <div class="colors active">
          Test
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

  &.active {
    height: 25%;
    min-height: 4rem;
  }
}
</style>