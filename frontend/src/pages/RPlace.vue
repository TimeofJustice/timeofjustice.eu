<script setup lang="ts">
import { onMounted, ref } from 'vue';

const fieldPanZoom = ref<HTMLCanvasElement | null>(null);

const setUpCanvas = (canvas: HTMLCanvasElement) => {
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
  });

  const init = () => {
    const ctx = canvas.getContext('2d');
    if (ctx) {
      let isDragging = false;
      let offsetX = 0;
      let offsetY = 0;
      let startX = 0;
      let startY = 0;
      let scale = 1;

      const drawBackground = () => {
        ctx.fillStyle = 'lightgray';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      };

      const rectWidth = 1000;
      const rectHeight = 1000;

      const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];

// Wir teilen das große Spielfeld in mehrere Chunks auf und speichern sie im Array `chunks`
type Chunk = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  render: (random: boolean) => void;
};

const chunks: Chunk[] = [];
const numberOfChunksX = 10;
const numberOfChunksY = 10;
const chunkWidth = rectWidth / numberOfChunksX;
const chunkHeight = rectHeight / numberOfChunksY;

for (let i = 0; i < numberOfChunksX; i++) {
  for (let j = 0; j < numberOfChunksY; j++) {
    const offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = chunkWidth;
    offscreenCanvas.height = chunkHeight;
    const offscreenCtx = offscreenCanvas.getContext('2d')!;

    const renderFieldToOffscreen = (random: boolean) => {
      for (let x = 0; x < chunkWidth; x++) {
        for (let y = 0; y < chunkHeight; y++) {
          if (random) {
            offscreenCtx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
          } else {
            offscreenCtx.fillStyle = colors[((i * chunkWidth + x) + (j * chunkHeight + y)) % colors.length];
          }

          offscreenCtx.fillRect(x, y, 1, 1);
        }
      }
    };
    renderFieldToOffscreen(false);

    chunks.push({
      canvas: offscreenCanvas,
      ctx: offscreenCtx,
      render: renderFieldToOffscreen
    });
  }
}

      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        chunk.render(false);
      }

const drawRect = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground();
  ctx.save();
  ctx.scale(scale, scale);

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const chunkX = (i % numberOfChunksX) * chunkWidth;
    const chunkY = Math.floor(i / numberOfChunksX) * chunkHeight;
    ctx.drawImage(
      chunk.canvas,
      ((chunkX * 100) + offsetX),
      ((chunkY * 100) + offsetY),
      (chunkWidth * 100),
      (chunkHeight * 100)
    );
  }

  ctx.restore();
};

      canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        const rect = canvas.getBoundingClientRect();
        startX = e.clientX - rect.left - offsetX;
        startY = e.clientY - rect.top - offsetY;
      });

      canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
          const rect = canvas.getBoundingClientRect();
          offsetX = e.clientX - rect.left - startX;
          offsetY = e.clientY - rect.top - startY;
          drawRect();
        }
      });

      canvas.addEventListener('mouseup', () => {
        isDragging = false;
      });

      canvas.addEventListener('mouseleave', () => {
        isDragging = false;
      });

      canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = 0.1;
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left - offsetX) / scale;
        const mouseY = (e.clientY - rect.top - offsetY) / scale;

        const newScale = scale + (e.deltaY < 0 ? zoomFactor : -zoomFactor);
        const clampedScale = Math.min(Math.max(newScale, 0.5), 3); // Limit zoom between 0.5x and 3x

        offsetX -= (mouseX * (clampedScale - scale));
        offsetY -= (mouseY * (clampedScale - scale));
        scale = clampedScale;

        drawRect();
      });

      drawRect();

// Intervall zum Zeichnen des Rechtecks
      const drawInterval = setInterval(() => {
        const chunk = chunks[0];
        chunk.render(true);
        drawRect();
      }, 5000);
    }
  }

  init();
};

onMounted(() => {
  if (!fieldPanZoom.value) {
    console.error('Canvas element not found');
    return;
  }
  const canvas = fieldPanZoom.value;
  if (!(canvas instanceof HTMLCanvasElement)) {
    console.error('fieldPanZoom is not a canvas element');
    return;
  }
  setUpCanvas(canvas);
});
</script>

<template>
  <div class="container-xxl h-100 overflow-hidden pb-2">
    <canvas width="1000" height="1000" ref="fieldPanZoom" class="field"></canvas>
  </div>
</template>

<style scoped lang="scss">
canvas {
  image-rendering: pixelated;
}
</style>