// ─────────────────────────────────────────
// polaroid_viewer.js
// Controls the split-screen polaroid viewer
// ─────────────────────────────────────────

let _images = [];   // array of image objects { url, title, timestamp, lat, lng }
let _index  = 0;

// ── OPEN VIEWER ──
function openPolaroidViewer(images, startIndex = 0) {
  _images = images;
  _index  = startIndex;

  document.body.classList.add('viewer-open');
  document.getElementById('polaroid-viewer').classList.add('open');

  _renderPolaroid();
}

// ── CLOSE VIEWER ──
function closePolaroidViewer() {
  document.body.classList.remove('viewer-open');
  document.getElementById('polaroid-viewer').classList.remove('open');
}

// ── RENDER CURRENT IMAGE ──
function _renderPolaroid() {
  const img = _images[_index];
  if (!img) return;

  document.getElementById('polaroid-img').src          = img.url;
  document.getElementById('polaroid-title').textContent = img.title      || '—';
  document.getElementById('polaroid-meta').textContent  = img.timestamp  || '';
  document.getElementById('polaroid-counter').textContent = `${_index + 1} / ${_images.length}`;
}

// ── NAV ──
function polaroidNext() {
  if (_index < _images.length - 1) {
    _index++;
    _renderPolaroid();
  }
}

function polaroidPrev() {
  if (_index > 0) {
    _index--;
    _renderPolaroid();
  }
}

// ── KEYBOARD NAV ──
document.addEventListener('keydown', (e) => {
  if (!document.body.classList.contains('viewer-open')) return;
  if (e.key === 'ArrowRight') polaroidNext();
  if (e.key === 'ArrowLeft')  polaroidPrev();
  if (e.key === 'Escape')     closePolaroidViewer();
});