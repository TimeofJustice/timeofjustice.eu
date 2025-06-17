<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  faArrowsToDot,
  faBinoculars,
  faCheck,
  faChevronLeft,
  faChevronRight,
  faEyeDropper,
  faLayerGroup,
  faPalette,
  faSync
} from "@node_modules/@fortawesome/free-solid-svg-icons";
import { faClose, faMaximize, faMinimize } from "@fortawesome/free-solid-svg-icons";
import { Head } from "@node_modules/@inertiajs/vue3";
import axios from "@node_modules/axios";

interface PlaceState {
  playerCount: number;
  coordinates: { x: number; y: number };
  fullscreen: boolean;
  overlayScreen: boolean;
  inOverlay: boolean;
  colors: string[][];
  colorsPage: number;
  state: 'loading' | 'viewing' | 'started' | 'disconnected';
  chunks: {
    number: number;
    loaded: number;
  };
  color: {
    active: string;
    custom: string;
  }
}

function rgbToHex(r: number, g: number, b: number) {
  if (r > 255 || g > 255 || b > 255)
    throw "Invalid color component";
  return ((r << 16) | (g << 8) | b).toString(16);
}

class Overlay {
  image: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  overlayImage: HTMLCanvasElement;
  initialized: boolean = false;
  colors: string[] = [];
  x: number;
  y: number;
  width: number;
  height: number;

  constructor(image: HTMLCanvasElement, x: number, y: number) {
    this.image = image;
    this.ctx = image.getContext('2d')!;
    this.x = x;
    this.y = y;
    this.width = image.width;
    this.height = image.height;

    this.overlayImage = document.createElement('canvas');
    this.overlayImage.width = this.image.width * 5;
    this.overlayImage.height = this.image.height * 5;

    this.calculateOverlay();

    this.initialized = true;
  }
  calculateOverlay(color?: string) {
    const ctx = this.overlayImage.getContext('2d')!;
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, this.overlayImage.width, this.overlayImage.height);

    for (let x = 0; x < this.image.width; x++) {
      for (let y = 0; y < this.image.height; y++) {
        const pixelColor = this.image.getContext('2d')!.getImageData(x, y, 1, 1).data;
        const hexColor = "#" + ("000000" + rgbToHex(pixelColor[0], pixelColor[1], pixelColor[2])).slice(-6);

        if (color && hexColor !== color) continue;

        ctx.fillStyle = `rgba(${pixelColor[0]}, ${pixelColor[1]}, ${pixelColor[2]}, ${pixelColor[3] / 255})`;
        ctx.fillRect(x * 5 + 2, y * 5 + 2, 1, 1);

        if (this.initialized) continue;
        if (!this.colors.includes(hexColor)) {
          this.colors.push(hexColor);
        }
      }
    }
  }
}

class Chunk {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

  constructor(width: number, height: number) {
    this.canvas = document.createElement('canvas');
    this.canvas.width = width + 1;
    this.canvas.height = height + 1;
    this.ctx = this.canvas.getContext('2d')!;

    this.ctx.fillStyle = 'white';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  paintCell(x: number, y: number, color: string) {
    this.ctx.fillStyle = color;
    if (x === this.canvas.width - 2 && y === this.canvas.height - 2) {
      this.ctx.fillRect(x, y, 2, 2);
    } else if (x === this.canvas.width - 2) {
      this.ctx.fillRect(x, y, 2, 1);
    } else if (y === this.canvas.height - 2) {
      this.ctx.fillRect(x, y, 1, 2);
    } else {
      this.ctx.fillRect(x, y, 1, 1);
    }
  };
  getColor (x: number, y: number) {
    const p = this.ctx.getImageData(x, y, 1, 1).data;
    return "#" + ("000000" + rgbToHex(p[0], p[1], p[2])).slice(-6);
  };
}

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

const rectWidth = activeCanvas.width;
const rectHeight = activeCanvas.height;
const cellSize = 10;

const numberOfChunks = 5;
const chunkWidth = rectWidth / numberOfChunks;
const chunkHeight = rectHeight / numberOfChunks;

const placeState = ref<PlaceState>({
  playerCount: 1,
  coordinates: { x: 0, y: 0 },
  fullscreen: false,
  overlayScreen: false,
  inOverlay: false,
  colors: [colors],
  colorsPage: 0,
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

const setUpCanvasSize = (canvas: HTMLCanvasElement) => {
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

const view = {
  canvas: null as HTMLCanvasElement | null,
  cursor: null as HTMLImageElement | null,
  socket: null as WebSocket | null,
  width: 0,
  height: 0,
  position: { x: 0, y: 0 },
  scale: 0.1,
  cursorPosition: { x: 0, y: 0 },
  chunks: [] as Chunk[],
  overlay: null as Overlay | null,

  init(canvas: HTMLCanvasElement, cursor: HTMLImageElement, socket?: WebSocket) {
    this.canvas = canvas;
    this.cursor = cursor;
    this.socket = socket || null;

    this.width = canvas.width;
    this.height = canvas.height;

    this.position = { x: (canvas.width - rectWidth) / 2, y: (canvas.height - rectHeight) / 2 };
    this.cursorPosition = { x: rectWidth / 2, y: rectHeight / 2 };

    placeState.value.coordinates = {
      x: this.cursorPosition.x,
      y: this.cursorPosition.y
    };

    this.initChunks();
  },
  initChunks() {
    placeState.value.chunks.loaded = 0;
    placeState.value.chunks.number = numberOfChunks * numberOfChunks;

    for (let i = 0; i < numberOfChunks; i++) {
      for (let j = 0; j < numberOfChunks; j++) {
        this.chunks.push(new Chunk(chunkWidth, chunkHeight));
      }
    }

    this.loadChunk(0);
  },
  loadChunk(index: number) {
    if (index >= this.chunks.length) return;

    const chunkX = (index % numberOfChunks) * chunkWidth;
    const chunkY = Math.floor(index / numberOfChunks) * chunkHeight;

    axios.get(`/r-place/api/load_chunk/${chunkX}/${chunkY}/${chunkWidth}/${activeCanvas.name}/`)
      .then(response => {
        const data = response.data;
        this.drawChunk(data.cells);
      })
      .catch(error => {
        console.error(`Error loading chunk ${index}:`, error);
      })
      .finally(() => {
        placeState.value.chunks.loaded++;

        if (index < this.chunks.length - 1) {
          setTimeout(() => this.loadChunk(index + 1), 100);
        } else {
          if (activeCanvas.active) {
            placeState.value.state = 'started';
          } else {
            placeState.value.state = 'viewing';
          }

          this.refresh();
        }
      });
  },
  drawChunk(cells: { x: number; y: number; color: string }[]) {
    cells.forEach(cell => {
      this.drawCell(cell.x, cell.y, cell.color);
    });
  },
  getChunk(x: number, y: number): Chunk {
    const chunkX = Math.floor(x / chunkWidth);
    const chunkY = Math.floor(y / chunkHeight);

    const chunkIndex = (chunkY * numberOfChunks) + chunkX;
    if (chunkIndex < 0 || chunkIndex >= this.chunks.length) {
      throw new Error(`Chunk index out of bounds: ${chunkIndex}`);
    }

    return this.chunks[chunkIndex];
  },
  drawCell(x: number, y: number, color: string) {
    const chunk = this.getChunk(x, y);
    const localX = x % chunkWidth;
    const localY = y % chunkHeight;

    chunk.paintCell(localX, localY, color);
  },
  pickColor() {
    const chunk = this.getChunk(this.cursorPosition.x, this.cursorPosition.y);
    const localX = this.cursorPosition.x % chunkWidth;
    const localY = this.cursorPosition.y % chunkHeight;
    const color = chunk.getColor(localX, localY);

    if (color) {
      if (!colors.includes(color)) {
        placeState.value.color.custom = color;
      }
      placeState.value.color.active = color;
    }
  },
  paint() {
    if (!this.socket || !this.canvas) {
      console.error('Socket or canvas not initialized');
      return;
    }

    const color = placeState.value.color.active;

    this.socket.send(JSON.stringify({
      type: 'cell_update',
      x: this.cursorPosition.x,
      y: this.cursorPosition.y,
      color: color
    }));
  },
  apply(ctx: CanvasRenderingContext2D) {
    ctx.setTransform(this.scale, 0, 0, this.scale, this.position.x, this.position.y);
  },
  resize() {
    if (!this.canvas) {
      console.error('Canvas not initialized');
      return;
    }
    const delta = setUpCanvasSize(this.canvas);
    if (delta) {
      this.position.x += delta.deltaWidth / 2;
      this.position.y += delta.deltaHeight / 2;
    }
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.refresh();
  },
  pan(amount: { x: number; y: number }) {
    this.position.x += amount.x;
    this.position.y += amount.y;
  },
  scaleAt(at: { x: number; y: number }, amount: number) {
    const oldScale = this.scale;
    this.scale *= amount;
    this.scale = Math.max(0.1, Math.min(this.scale, 10));
    this.position.x = at.x - ((at.x - this.position.x) * (this.scale / oldScale));
    this.position.y = at.y - ((at.y - this.position.y) * (this.scale / oldScale));
  },
  refresh() {
    if (!this.canvas || !this.cursor) {
      console.error('Canvas or cursor image not initialized');
      return;
    }

    const ctx = this.canvas.getContext('2d')!;
    ctx.imageSmoothingEnabled = false;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.width, this.height);
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

    ctx.clearRect(rectWidth * cellSize, -cellSize * 1.5, cellSize * 1.5, (rectWidth * cellSize) + cellSize * 3);
    ctx.clearRect(-cellSize * 1.5, rectHeight * cellSize, (rectHeight * cellSize) + cellSize * 3, cellSize * 1.5);

    if (this.overlay) {
      ctx.drawImage(
        this.overlay.overlayImage,
        this.overlay.x * cellSize,
        this.overlay.y * cellSize,
        this.overlay.overlayImage.width * cellSize / 5,
        this.overlay.overlayImage.height * cellSize / 5
      );
    }

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

    ctx.drawImage(this.cursor,
      this.cursorPosition.x * cellSize - 0.1,
      this.cursorPosition.y * cellSize - 0.1,
      cellSize + 0.2,
      cellSize + 0.2
    );
  },
  center() {
    const targetX = (this.width / 2) - ((this.cursorPosition.x * cellSize * this.scale) + (cellSize * this.scale / 2));
    const targetY = (this.height / 2) - ((this.cursorPosition.y * cellSize * this.scale) + (cellSize * this.scale / 2));
    const duration = 300;
    const startX = this.position.x;
    const startY = this.position.y;
    const startTime = performance.now();

    const animate = (now: number) => {
      const elapsed = Math.min((now - startTime) / duration, 1);
      this.position.x = startX + (targetX - startX) * elapsed;
      this.position.y = startY + (targetY - startY) * elapsed;
      this.refresh();
      if (elapsed < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  },
  moveTo(x: number, y: number) {
    if (x < 0 || x >= rectWidth || y < 0 || y >= rectHeight) {
      console.warn(`Attempted to move to out-of-bounds coordinates: (${x}, ${y})`);
      return;
    }

    this.cursorPosition.x = x;
    this.cursorPosition.y = y;
    placeState.value.coordinates = { x, y };
    this.center();

    if (this.overlay && (this.overlay.x <= x && x < this.overlay.x + this.overlay.width) &&
        (this.overlay.y <= y && y < this.overlay.y + this.overlay.height)) {
      if (!placeState.value.inOverlay) {
        placeState.value.colors = [];
        for (let i = 0; i < this.overlay.colors.length; i += 32) {
          placeState.value.colors.push(this.overlay.colors.slice(i, i + 32));
        }

        placeState.value.color.active = this.overlay.colors[0];
        placeState.value.inOverlay = true;
        placeState.value.colorsPage = 0;
      }
    } else {
      placeState.value.colors = [colors];
      placeState.value.color.active = colors[0];
      placeState.value.inOverlay = false;
      placeState.value.colorsPage = 0;

      if (this.overlay) {
        this.overlay.calculateOverlay();
        this.refresh();
      }
    }
  },
  click(e: MouseEvent) {
    const bounds = this.canvas!.getBoundingClientRect();
    const pos = {
      x: Math.floor((e.clientX - bounds.left - this.position.x) / (cellSize * this.scale)),
      y: Math.floor((e.clientY - bounds.top - this.position.y) / (cellSize * this.scale))
    };
    if (pos.x < 0 || pos.x >= rectWidth || pos.y < 0 || pos.y >= rectHeight) return;
    this.moveTo(pos.x, pos.y);
    return pos;
  },
  calculateOverlay(color: string) {
    if (!this.overlay) {
      console.error('Overlay not initialized');
      return;
    }
    this.overlay.calculateOverlay(color);
    this.refresh();

    if (!colors.includes(color)) {
      placeState.value.color.custom = color;
    }
    placeState.value.color.active = color;
  }
}

let isDragging = false;
let lastMouse = { x: 0, y: 0 };
const mouseDown = { x: 0, y: 0 };

function keydownHandler(e: KeyboardEvent) {
  if (placeState.value.overlayScreen) {
    return;
  }

  if (e.key === 'ArrowUp') {
    e.preventDefault();
    view.moveTo(view.cursorPosition.x, view.cursorPosition.y - 1);
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    view.moveTo(view.cursorPosition.x, view.cursorPosition.y + 1);
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault();
    view.moveTo(view.cursorPosition.x - 1, view.cursorPosition.y);
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    view.moveTo(view.cursorPosition.x + 1, view.cursorPosition.y);
  } else if (e.key === 'r' || e.key === 'R') {
    e.preventDefault();
    view.center();
  }

  if (placeState.value.state !== 'started') return;

  if (e.key === ' ') {
    e.preventDefault();
    view.paint();
  } else if (e.key === 'c' || e.key === 'C') {
    e.preventDefault();
    view.pickColor();
  } else if (e.key === 'Tab') {
    e.preventDefault();
    const currentIndex = placeState.value.colors[placeState.value.colorsPage].indexOf(placeState.value.color.active);
    if (currentIndex === -1 || (placeState.value.inOverlay && currentIndex === placeState.value.colors[placeState.value.colorsPage].length - 1)) {
      placeState.value.color.active = placeState.value.colors[placeState.value.colorsPage][0];
    } else if (currentIndex === placeState.value.colors[placeState.value.colorsPage].length - 1 && !placeState.value.inOverlay) {
      placeState.value.color.active = placeState.value.color.custom;
    } else {
      placeState.value.color.active = placeState.value.colors[placeState.value.colorsPage][currentIndex + 1];
    }
  }
}

function clickBeforeHandler(e: MouseEvent) {
  if (
    Math.abs(mouseDown.x - e.clientX) >= 30 ||
    Math.abs(mouseDown.y - e.clientY) >= 30
  ) {
    e.stopPropagation();
  }
}

function clickAfterHandler(e: MouseEvent) {
  view.click(e);
}

function mouseDownHandler(e: MouseEvent) {
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
      view.refresh();
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
}

function wheelHandler(e: WheelEvent) {
  e.preventDefault();
  if (!canvas.value || !cursorImage.value) {
    console.error('Canvas element not found');
    return;
  }

  const rect = canvas.value.getBoundingClientRect();
  const mouse = {
    x: (e.clientX - rect.left),
    y: (e.clientY - rect.top)
  };
  const zoomFactor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
  view.scaleAt(mouse, zoomFactor);
  view.refresh();
}

function touchStartHandler(e: TouchEvent) {
  if (e.touches.length === 1) {
    isDragging = true;
    lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    mouseDown.x = e.touches[0].clientX;
    mouseDown.y = e.touches[0].clientY;
  }
}

let lastPinchDist: number | null = null;

function touchMoveHandler(e: TouchEvent) {
  if (isDragging && e.touches.length === 1) {
    const dx = e.touches[0].clientX - lastMouse.x;
    const dy = e.touches[0].clientY - lastMouse.y;
    view.pan({ x: dx, y: dy });
    lastMouse = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    view.refresh();
    e.preventDefault();
  }

  if (!canvas.value || !cursorImage.value) {
    console.error('Canvas element not found');
    return;
  }

  if (e.touches.length === 2) {
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (lastPinchDist !== null) {
      const zoomFactor = dist / lastPinchDist;
      const rect = canvas.value.getBoundingClientRect();
      const center = {
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top
      };
      view.scaleAt(center, zoomFactor);
      view.refresh();
    }
    lastPinchDist = dist;
    e.preventDefault();
  } else {
    lastPinchDist = null;
  }
}

function touchEndHandler(e: TouchEvent) {
  isDragging = false;

  if (e.touches.length < 2) {
    lastPinchDist = null;
  }

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
      view.refresh();
    }
  }
}

function touchCancelHandler() {
  isDragging = false;
}

onMounted(() => {
  if (!canvas.value || !cursorImage.value) {
    console.error('Canvas element not found');
    return;
  }
  setUpCanvasSize(canvas.value);

  const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      if (entry.target === canvasContainer.value) {
        view.resize();
      }
    }
  });

  resizeObserver.observe(canvasContainer.value!);

  // Desktop: Keyboard controls
  window.addEventListener('keydown', keydownHandler);
  // Desktop: Mouse controls
  canvas.value.addEventListener('click', clickBeforeHandler, true);
  canvas.value.addEventListener('click', clickAfterHandler, false);
  canvas.value.addEventListener('mousedown', mouseDownHandler);
  canvas.value.addEventListener('wheel', wheelHandler);

  // Mobile: Touch-controls
  canvas.value.addEventListener('touchstart', touchStartHandler, { passive: false });
  canvas.value.addEventListener('touchmove', touchMoveHandler, { passive: false });
  canvas.value.addEventListener('touchend', touchEndHandler, { passive: false });
  canvas.value.addEventListener('touchcancel', touchCancelHandler, { passive: false });

  onBeforeUnmount(() => {
    console.log('Cleaning up event listeners');
    window.removeEventListener('keydown', keydownHandler);
    canvas.value?.removeEventListener('click', clickBeforeHandler, true);
    canvas.value?.removeEventListener('click', clickAfterHandler, false);
    canvas.value?.removeEventListener('mousedown', mouseDownHandler);
    canvas.value?.removeEventListener('wheel', wheelHandler);
    canvas.value?.removeEventListener('touchstart', touchStartHandler);
    canvas.value?.removeEventListener('touchmove', touchMoveHandler);
    canvas.value?.removeEventListener('touchend', touchEndHandler);
    canvas.value?.removeEventListener('touchcancel', touchCancelHandler);
    resizeObserver.disconnect();
  });

  if (!activeCanvas.active) {
    view.init(canvas.value, cursorImage.value);
    return;
  }

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";

  const socket = new WebSocket(
    wsScheme
    + '://'
    + window.location.host
    + '/ws/r-place/'
  );
  socket.onopen = () => {
    console.log('WebSocket connection established');

    if (!canvas.value || !cursorImage.value) {
      console.error('Canvas element not found');
      return;
    }
    view.init(canvas.value, cursorImage.value, socket);
  };
  socket.onmessage = (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    if (data.type === 'cell_update') {
      const cell = data.cell;
      view.drawCell(cell.x, cell.y, cell.color);
      view.refresh();
    } else if (data.type === 'player_update') {
      placeState.value.playerCount = data.count;
    }
  };
  socket.onclose = () => {
    console.log('WebSocket connection closed');
    placeState.value.state = 'disconnected';
  };

  onBeforeUnmount(() => {
    socket.close()
  });
});

const file = ref<File | null>(null);
const previewCanvas = ref<HTMLCanvasElement | null>(null);
const sizeOnCanvasX = ref(100);
const limitSizeOnCanvasX = ref(1000);
const positionOnCanvasX = ref(0);
const positionOnCanvasY = ref(0);
const numberColors = ref(10);
const synced = ref(true);

const overlay = {
  fieldCanvas: document.createElement('canvas'),
  originalCanvas: document.createElement('canvas'),
  reducedCanvas: document.createElement('canvas'),
  resizeCanvas: document.createElement('canvas'),
  initialized: false,
  imageLoaded: false,
  x: 0,
  y: 0,
  init() {
    if (!this.fieldCanvas || !previewCanvas.value) {
      console.error('Field ord preview canvas not found');
      return;
    }

    const previewWidth = 300;
    const previewHeight = 300;
    this.fieldCanvas.width = previewWidth;
    this.fieldCanvas.height = previewHeight;

    this.loadChunks();

    this.initialized = true;
  },
  loadChunks() {
    if (!this.fieldCanvas) {
      console.error('Field canvas not found');
      return;
    }
    const ctx = this.fieldCanvas.getContext('2d');
    if (!ctx) {
      console.error('Failed to get canvas context');
      return;
    }

    const multiplierWidth = this.fieldCanvas.width / activeCanvas.width;
    const multiplierHeight = this.fieldCanvas.height / activeCanvas.height;

    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, this.fieldCanvas.width, this.fieldCanvas.height);
    for (let i = 0; i < view.chunks.length; i++) {
      const chunk = view.chunks[i];
      const chunkX = (i % numberOfChunks) * chunkWidth;
      const chunkY = Math.floor(i / numberOfChunks) * chunkHeight;
      ctx.drawImage(
        chunk.canvas,
        chunkX * multiplierWidth,
        chunkY * multiplierHeight,
        (chunkWidth + 1) * multiplierWidth,
        (chunkHeight + 1) * multiplierHeight
      );
    }
  },
  open() {
    if (!this.initialized) {
      this.init();
    }
    this.loadChunks();

    if (!previewCanvas.value || !this.reducedCanvas || !this.fieldCanvas) {
      console.error('Preview, temp or field canvas not found');
      return;
    }
    previewCanvas.value.width = this.fieldCanvas.width;
    previewCanvas.value.height = this.fieldCanvas.height;
    const ctx = previewCanvas.value.getContext('2d');
    if (!ctx) {
      console.error('Failed to get preview canvas context');
      return;
    }
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, previewCanvas.value.width, previewCanvas.value.height);
    ctx.drawImage(this.fieldCanvas, 0, 0, previewCanvas.value.width, previewCanvas.value.height);

    placeState.value.overlayScreen = true;

    if(!this.imageLoaded) return;

    this.preview();
  },
  loadImage(file: File) {
    if (!this.initialized) {
      this.init();
    }
    if (!this.originalCanvas) {
      console.error('canvas not found');
      return;
    }
    const ctx = this.originalCanvas.getContext('2d');
    if (!ctx) {
      console.error('Failed to get original canvas context');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        this.originalCanvas.width = img.width;
        this.originalCanvas.height = img.height;
        ctx.clearRect(0, 0, this.originalCanvas.width, this.originalCanvas.height);
        ctx.drawImage(img, 0, 0, img.width, img.height);
        this.imageLoaded = true;
        this.preview();
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  },
  reduceColors(amount: number) {
    if (!this.initialized) {
      this.init();
    }
    if (!this.resizeCanvas || !this.reducedCanvas) {
      console.error('Original or reduced canvas not found');
      return;
    }

    this.reducedCanvas.width = this.resizeCanvas.width;
    this.reducedCanvas.height = this.resizeCanvas.height;
    const ctx = this.reducedCanvas.getContext('2d');
    if (!ctx) {
      console.error('Failed to get resize canvas context');
      return;
    }
    ctx.imageSmoothingEnabled = false;

    const RgbQuant = require('rgbquant');
    const q = new RgbQuant({colors: amount})
    q.sample(this.resizeCanvas);
    q.palette();
    const out = q.reduce(this.resizeCanvas);

    const imageData = new ImageData(new Uint8ClampedArray(out), this.reducedCanvas.width, this.reducedCanvas.height);
    ctx.putImageData(imageData, 0, 0);
  },
  resizeImage(width: number) {
    const imgRatio = this.originalCanvas.width / this.originalCanvas.height;
    let pixelW = width;
    let pixelH = Math.round(pixelW / imgRatio);

    limitSizeOnCanvasX.value = Math.min(Math.min(1000, this.originalCanvas.width), Math.floor(1000 / pixelH * pixelW));
    if (sizeOnCanvasX.value > limitSizeOnCanvasX.value) {
      sizeOnCanvasX.value = limitSizeOnCanvasX.value;

      pixelW = limitSizeOnCanvasX.value;
      pixelH = Math.round(pixelW / imgRatio);
    }

    this.resizeCanvas.width = pixelW;
    this.resizeCanvas.height = pixelH;
    const tempCtx = this.resizeCanvas.getContext('2d');
    if (!tempCtx) {
      console.error('Failed to get temp canvas context');
      return;
    }
    tempCtx.clearRect(0, 0, this.resizeCanvas.width, this.resizeCanvas.height);
    tempCtx.drawImage(this.originalCanvas, 0, 0, pixelW, pixelH);

    this.reduceColors(Number(numberColors.value));
  },
  preview() {
    if (!this.imageLoaded) {
      synced.value = true;
      return;
    }
    if (!this.initialized) {
      this.init();
    }
    if (!previewCanvas.value || !this.reducedCanvas || !this.fieldCanvas) {
      console.error('Preview, temp or field canvas not found');
      return;
    }
    previewCanvas.value.width = this.fieldCanvas.width;
    previewCanvas.value.height = this.fieldCanvas.height;
    const ctx = previewCanvas.value.getContext('2d');
    if (!ctx) {
      console.error('Failed to get preview canvas context');
      return;
    }
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, previewCanvas.value.width, previewCanvas.value.height);
    ctx.drawImage(this.fieldCanvas, 0, 0, previewCanvas.value.width, previewCanvas.value.height);

    const previewWidth = 300;
    const previewHeight = 300;
    const multiplierWidth = previewWidth / activeCanvas.width;
    const multiplierHeight = previewHeight / activeCanvas.height;

    this.resizeImage(Number(sizeOnCanvasX.value));

    ctx.drawImage(
      this.reducedCanvas,
      0, 0, this.reducedCanvas.width, this.reducedCanvas.height,
      this.x * multiplierWidth, this.y * multiplierHeight, this.reducedCanvas.width * multiplierWidth, this.reducedCanvas.height * multiplierHeight
    );

    synced.value = true;
  },
  calculate() {
    if (!this.initialized) {
      this.init();
    }
    if (!this.reducedCanvas) {
      console.error('Reduced canvas not found');
      return;
    }
    this.preview();
    view.overlay = new Overlay(this.reducedCanvas, Number(positionOnCanvasX.value), Number(positionOnCanvasY.value));
    view.refresh();
    placeState.value.overlayScreen = false;
  }
}

watch(file, (newFile) => {
  if (!newFile) return;
  overlay.loadImage(newFile);
});

watch([positionOnCanvasX, positionOnCanvasY], ([newPositionX, newPositionY]) => {
  overlay.x = newPositionX;
  overlay.y = newPositionY;
});

watch([positionOnCanvasX, positionOnCanvasY, numberColors, sizeOnCanvasX], () => {
  synced.value = false;
});

watch(() => placeState.value.color.active, (newColor) => {
  if (placeState.value.inOverlay) {
    view.calculateOverlay(newColor);
    view.refresh();
  }
});
</script>

<template>
  <Head :title="$t('r_place.title')" />

  <div class="container-xxl h-100 overflow-hidden mb-2 place-container" :class="{ 'fullscreen': placeState.fullscreen }" ref="canvasContainer">
    <div class="w-100 rounded overflow-hidden position-relative h-100">
      <Transition>
        <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center bg-dark" v-if="placeState.state !== 'started' && placeState.state !== 'viewing'"
             :class="{ 'bg-opacity-75': placeState.state === 'disconnected' }">
          <BProgress :max="placeState.chunks.number" class="col-5" v-if="placeState.state === 'loading'">
            <BProgressBar :value="placeState.chunks.loaded" striped animated>
              <small>{{ Math.round((placeState.chunks.loaded / placeState.chunks.number) * 100) }}%</small>
            </BProgressBar>
          </BProgress>

          <BButton class="place-button text-light d-flex flex-column justify-content-center align-items-center rounded-0" to="/r-place/" v-if="placeState.state === 'disconnected'">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.disconnected.title") }}</span>
            <span>{{ $t("r_place.canvas.disconnected.description") }}</span>
          </BButton>
        </div>
      </Transition>

      <canvas width="1000" height="1000" ref="canvas" class="field bg-grey-200"></canvas>

      <div class="position-absolute top-0 bottom-0 start-0 end-0 d-flex flex-column justify-content-end pe-none">
        <div class="position-absolute top-0 end-0 p-2 d-flex flex-column gap-2 align-items-end">
          <div class="d-flex gap-2">
            <BButton class="place-button place-button-small text-light" @click="overlay.open()">
              <font-awesome-icon :icon="faLayerGroup"/>
            </BButton>
            <BButton class="place-button place-button-small text-light d-none d-xxl-flex" @click="placeState.fullscreen = !placeState.fullscreen;">
              <font-awesome-icon :icon="faMaximize" v-if="!placeState.fullscreen"/>
              <font-awesome-icon :icon="faMinimize" v-else/>
            </BButton>
          </div>
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
                {{ $t('r_place.canvas.canvas_select.ongoing') }}
              </BBadge>
            </BDropdownItem>
          </BDropdown>
        </div>
        <div class="d-flex justify-content-center align-items-center gap-2 p-2 position-relative" v-if="placeState.state === 'started'">
          <BButton class="place-button place-button-small text-light" @click="view.center()">
            <font-awesome-icon :icon="faArrowsToDot"/>
          </BButton>
          <BButton class="place-button place-button-big text-light d-flex flex-column justify-content-center align-items-center" @click="view.paint()">
            <span class="fw-bold fs-5">{{ $t("r_place.canvas.place_pixel") }}</span>
            <span>X: {{placeState.coordinates.x}} Y: {{placeState.coordinates.y}}</span>
          </BButton>
          <BButton class="place-button place-button-small text-light" @click="view.pickColor()">
            <font-awesome-icon :icon="faEyeDropper"/>
          </BButton>
          <div class="position-absolute bottom-0 end-0 p-2 text-black fw-bold d-none d-sm-block">
            {{ $t('r_place.canvas.players_online', {"player_count": placeState.playerCount}) }}
          </div>
        </div>
        <div class="place-colors-container" :class="{ active: placeState.state === 'started' }">
          <div class="d-flex justify-content-center align-items-center gap-1">
            <div @click="placeState.colorsPage = Math.max(0, placeState.colorsPage - 1)" class="place-colors-arrow" :class="{ 'opacity-0': placeState.colorsPage === 0 }" v-if="placeState.inOverlay">
              <font-awesome-icon :icon="faChevronLeft" />
            </div>
            <div class="place-colors-grid" v-for="(page, index) in placeState.colors" :key="index" v-show="placeState.colorsPage === index">
              <div class="col place-color" :class="{ active: placeState.color.active === color }" :style="{ backgroundColor: color }" @click="placeState.color.active = color" v-for="color in page"></div>
              <div class="col place-color d-flex justify-content-center align-items-center" v-for="i in (32 - page.length)" :key="i" style="background-color: white;">
                <font-awesome-icon :icon="faClose" class="text-black" />
              </div>
            </div>
            <div @click="placeState.colorsPage = Math.min(placeState.colors.length - 1, placeState.colorsPage + 1)" class="place-colors-arrow" :class="{ 'opacity-0': placeState.colorsPage === placeState.colors.length - 1 }" v-if="placeState.inOverlay">
              <font-awesome-icon :icon="faChevronRight" />
            </div>

            <div class="position-relative d-none d-sm-block" v-if="!placeState.inOverlay">
              <BInput type="color" v-model="placeState.color.custom" class="place-color place-color-big" :class="{ active: placeState.color.active === placeState.color.custom && !placeState.colors[placeState.colorsPage].includes(placeState.color.active) }"
                      @blur="placeState.color.active = placeState.color.custom" />
              <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center pe-none">
                <font-awesome-icon :icon="faPalette"/>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Transition>
        <div class="position-absolute top-0 start-0 end-0 bottom-0 d-flex justify-content-center align-items-center bg-dark bg-opacity-75 overflow-auto p-2" :class="{ 'd-none': !placeState.overlayScreen }">
          <div class="d-flex flex-column justify-content-center align-items-center gap-2 position-relative p-3 bg-grey-200 bg-opacity-100 border border-2 border-black">
            <div class="position-relative">
              <canvas ref="previewCanvas"></canvas>

              <Transition>
                <div class="position-absolute top-0 end-0 start-0 bottom-0 d-flex justify-content-center align-items-center bg-grey-200 bg-opacity-75" v-if="!synced">
                  <BButton @click="overlay.preview()" class="place-button fs-3">
                    <font-awesome-icon :icon="faSync" />
                  </BButton>
                </div>
              </Transition>
            </div>

            <BFormFile v-model="file" accept="image/*" class="place-input" />

            <BFormGroup
              :label="$t('r_place.canvas.overlay.x', { 'x': positionOnCanvasX })"
              label-for="position-x-input"
              label-class="mb-1"
              class="w-100"
            >
              <BFormInput
                id="position-x-input"
                type="range"
                v-model="positionOnCanvasX"
                min="0" :max="activeCanvas.width"
                class="place-range"
              />
            </BFormGroup>
            <BFormGroup
              :label="$t('r_place.canvas.overlay.y', { 'y': positionOnCanvasY })"
              label-for="position-y-input"
              label-class="mb-1"
              class="w-100"
            >
              <BFormInput
                id="position-y-input"
                type="range"
                v-model="positionOnCanvasY"
                min="0" :max="activeCanvas.height"
                class="place-range"
              />
            </BFormGroup>

            <BFormGroup
              :label="$t('r_place.canvas.overlay.width', { 'width': sizeOnCanvasX })"
              label-for="width-input"
              label-class="mb-1"
              class="w-100"
            >
              <BFormInput
                id="width-input"
                type="range"
                v-model="sizeOnCanvasX"
                min="1" :max="limitSizeOnCanvasX"
                class="place-range"
              />
            </BFormGroup>

            <BFormGroup
              :label="$t('r_place.canvas.overlay.colors', { 'colors': numberColors })"
              label-for="width-input"
              label-class="mb-1"
              class="w-100"
            >
              <BFormInput
                id="width-input"
                type="range"
                v-model="numberColors"
                :min="2" :max="200"
                class="place-range"
              />
            </BFormGroup>

            <div class="d-flex gap-2 w-100">
              <BButton class="place-button place-button text-light" @click="placeState.overlayScreen = false">
                <font-awesome-icon :icon="faClose" />
              </BButton>
              <BButton class="place-button place-button-big text-light flex-grow-1" @click="overlay.calculate()">
                <font-awesome-icon :icon="faCheck" />
              </BButton>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>

  <div class="d-none">
    <img :src="require('@assets/images/Cursor.png')" ref="cursorImage" />
  </div>
</template>

<style lang="scss">
@import "@/assets/scss/colors.scss";

.place-container.fullscreen {
  max-width: 100%!important;
}

.place-container {
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

.place-colors-container {
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

.place-colors-grid {
  display: grid;
  grid-template-rows: repeat(2, fit-content(100%));
  grid-template-columns: repeat(16, fit-content(100%));
  grid-gap: 0.25rem;

  @media (max-width: 992px) {
    grid-template-columns: repeat(8, fit-content(100%));
  }
}

.place-color {
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

.place-button, .place-dropdown > .btn, .place-button.btn {
  display: flex;
  justify-content: center;
  align-items: center;

  min-width: 2.25rem;
  padding: 0.5rem;

  --bs-btn-bg: $gray-500;
  --bs-btn-hover-bg: #{$gray-500};
  background: $gray-500;
  border: 2px solid $black;
  border-radius: 0;

  pointer-events: all;
  transition: border .2s ease-in-out;

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

.place-input {
  width: 100%;

  background: $gray-500!important;
  border: 2px solid $black!important;
  border-radius: 0!important;

  outline: none!important;
  transition: border .2s ease-in-out!important;

  &::-webkit-file-upload-button {
    background: $gray-300!important;
  }

  &:hover {
    border: 2px solid $gray-10!important;
  }
}

.place-range::-webkit-slider-thumb {
  background: $gray-500!important;
  border-radius: 0!important;
  border: 2px solid $black!important;
}

.place-range::-moz-range-thumb {
  background: $gray-500!important;
  border-radius: 0!important;
  border: 2px solid $black!important;
}

.place-range::-ms-thumb {
  background: $gray-500!important;
  border-radius: 0!important;
  border: 2px solid $black!important;
}

.place-range::-webkit-slider-runnable-track {
  background: $gray-500!important;
  border-radius: 0!important;
}

.place-colors-arrow {
  display: flex;
  justify-content: center;
  align-items: center;

  padding: 0.5rem;

  cursor: pointer;
  color: $black;
  opacity: 1;

  transition: opacity .2s ease-in-out;

  &:hover {
    color: $gray-10;
  }
}
</style>