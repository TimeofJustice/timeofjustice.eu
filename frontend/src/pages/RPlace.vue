<script setup lang="ts">
import { onMounted, ref } from "vue";

const fieldPanZoom = ref<HTMLCanvasElement | null>(null);
const cursorImage = ref<HTMLImageElement | null>(null);

const setUpCanvas = (canvas: HTMLCanvasElement, cursor: HTMLImageElement) => {
  const setUpCanvasSize = () => {
    const parent = canvas.parentElement;
    if (!parent) {
      console.error('Canvas parent element not found');
      return;
    }
    canvas.width = canvas.parentElement.clientWidth - (parseFloat(getComputedStyle(canvas.parentElement).paddingLeft) || 0) - (parseFloat(getComputedStyle(canvas.parentElement).paddingRight) || 0);
    canvas.height = canvas.parentElement.clientHeight - (parseFloat(getComputedStyle(canvas.parentElement).paddingTop) || 0) - (parseFloat(getComputedStyle(canvas.parentElement).paddingBottom) || 0);
  };
  setUpCanvasSize();

  window.addEventListener('resize', () => {
    setUpCanvasSize();
    draw();
  });

  const rectWidth = 1000;
  const rectHeight = 1000;
  const cellSize = 10;

  const numberOfChunksX = 10;
  const numberOfChunksY = 10;
  const chunkWidth = rectWidth / numberOfChunksX;
  const chunkHeight = rectHeight / numberOfChunksY;

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
      for (let i = 0; i < numberOfChunksX; i++) {
        for (let j = 0; j < numberOfChunksY; j++) {
          const offscreenCanvas = document.createElement('canvas');
          offscreenCanvas.width = chunkWidth;
          offscreenCanvas.height = chunkHeight;
          const offscreenCtx = offscreenCanvas.getContext('2d')!;

          offscreenCtx.fillStyle = 'white';
          offscreenCtx.fillRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);

          const paintCell = (x: number, y: number, color: string) => {
            offscreenCtx.fillStyle = color;
            offscreenCtx.fillRect(x, y, 1, 1);
          };

          this.chunks.push({
            canvas: offscreenCanvas,
            ctx: offscreenCtx,
            paintCell: paintCell
          });
        }
      }
    },
    drawCell(x: number, y: number, color: string) {
      const chunkX = Math.floor(x / chunkWidth);
      const chunkY = Math.floor(y / chunkHeight);
      const localX = x % chunkWidth;
      const localY = y % chunkHeight;

      const chunkIndex = (chunkY * numberOfChunksX) + chunkX;
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
      return pos;
    },
    highlightCell(x: number, y: number) {
      this.highlightedCell = { x, y };
      this.centerCell(x, y);
    }
  };
  view.initChunks();

  setInterval(() => {
    const randomX = Math.floor(Math.random() * rectWidth);
    const randomY = Math.floor(Math.random() * rectHeight);
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    view.drawCell(randomX, randomY, randomColor);
    draw();
  }, 100);

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
      const chunkX = (i % numberOfChunksX) * chunkWidth;
      const chunkY = Math.floor(i / numberOfChunksX) * chunkHeight;
      ctx.drawImage(
        chunk.canvas,
        ((chunkX * 10)),
        ((chunkY * 10)),
        (chunkWidth * 10),
        (chunkHeight * 10)
      );
    }

    if (view.scale > 3) {
      ctx.strokeStyle = 'rgba(0,0,0,1)';
      ctx.lineWidth = 0.5;
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
    }

    ctx.drawImage(cursor,
      (view.highlightedCell.x * cellSize - 0.5),
      (view.highlightedCell.y * cellSize - 0.5),
      cellSize + 1,
      cellSize + 1
    );
  };

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

  draw();
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
  <div class="container-xxl h-100 overflow-hidden pb-2">
    <canvas width="1000" height="1000" ref="fieldPanZoom" class="field bg-grey-200"></canvas>
    <img :src="require('@assets/images/Cursor.png')" alt="cursor" class="cursor" ref="cursorImage" />
  </div>
</template>

<style scoped lang="scss">
canvas {
  image-rendering: pixelated;
}
</style>