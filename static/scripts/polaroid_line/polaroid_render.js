// ═══════════════════════════════════════════
// TRIPPING — polaroid_render.js
// Renderer — wire, polaroids, petals, scroll
// Depends on: polaroid_data.js (loaded first)
// ═══════════════════════════════════════════

const WIRE_Y_RATIO = 0.20
const PHOTO_W      = 115
const PHOTO_H      = 115
const PHOTO_W_P    = 86
const PHOTO_H_P    = 112
const CAPTION_H    = 30
const SPACING      = 165
const PAD_X        = 110
const SCROLL_STEP  = 340

let _assets    = []
let _onOpen    = null
let _scrollX   = 0
let _maxScroll = 0

// ── PUBLIC API ──
// assets: [{ media_path, media_type, title, members }]
// onOpen: fn(members, index) — called on polaroid click
function initPolaroidLine(assets, onOpen) {
  console.log('asset',assets)
  _assets = assets
  _onOpen = onOpen
  _spawnPetals()
  _render()
}

// ── PETALS ──
function _spawnPetals() {
  const container = document.getElementById('petals')
  for (let i = 0; i < 22; i++) {
    const el     = document.createElement('div')
    el.className = 'petal'
    const left  = Math.random() * 100
    const dur   = 5 + Math.random() * 8
    const delay = Math.random() * 12
    const drift = (Math.random() - 0.5) * 120
    const rot   = Math.random() * 720 - 360
    const op    = (0.1 + Math.random() * 0.15).toFixed(2)
    el.innerHTML = PETAL_SVGS[i % PETAL_SVGS.length].replace(/VAR/g, op)
    el.style.cssText = `
      left: ${left}vw;
      --pd: ${dur}s;
      --pdelay: ${delay}s;
      --px: ${drift}px;
      --pr: ${rot}deg;
      --po: ${op};
    `
    container.appendChild(el)
  }
}

// ── RENDER ──
function _render() {
  const scene  = document.getElementById('scene')
  const H      = window.innerHeight
  const count  = _assets.length
  const totalW = PAD_X * 2 + (count - 1) * SPACING + PHOTO_W + 60

  scene.style.width = totalW + 'px'
  _maxScroll = Math.max(0, totalW - window.innerWidth)
  _scrollX   = 0
  scene.style.transform = 'translateX(0px)'

  scene.querySelectorAll('.polaroid').forEach(e => e.remove())
  document.getElementById('arrows').innerHTML = ''

  _renderWire(totalW, H)
  const clusterPts = _renderPolaroids(scene, H)
  _renderArrows(clusterPts)
  _updateButtons()
}

function _renderWire(totalW, H) {
  const svg   = document.getElementById('wire-svg')
  const wireY = H * WIRE_Y_RATIO
  const count = _assets.length

  svg.setAttribute('width',   totalW)
  svg.setAttribute('viewBox', `0 0 ${totalW} ${H * 0.65}`)

  const pts = []
  for (let i = 0; i <= count + 2; i++) {
    const x = (i / (count + 2)) * (totalW + 40) - 20
    const y = wireY + Math.sin(i * 0.8) * 11 + Math.cos(i * 0.4) * 4
    pts.push([x, y])
  }

  const wirePath = pts.map((p, i) => {
    if (i === 0) return `M${p[0]},${p[1]}`
    const px = pts[i-1]
    return `Q${(px[0]+p[0])/2},${(px[1]+p[1])/2} ${p[0]},${p[1]}`
  }).join(' ')

  document.getElementById('wire-path').setAttribute('d', wirePath)
  document.getElementById('wire-shadow-path').setAttribute('d', wirePath)
}

function _renderPolaroids(scene, H) {
  const wireY      = H * WIRE_Y_RATIO
  const clusterPts = []

  _assets.forEach((asset, i) => {
    const cx      = PAD_X + i * SPACING
    const wireYi  = wireY + Math.sin(i * 0.8) * 11 + Math.cos(i * 0.4) * 4
    const port    = (i % 5 === 2) || (i % 7 === 4)
    const pW      = port ? PHOTO_W_P : PHOTO_W
    const pH      = port ? PHOTO_H_P : PHOTO_H
    const rot     = _rot(i)
    const drop    = _drop(i)
    const tapeRot = (Math.random() * 6 - 3).toFixed(1)

    const el = document.createElement('div')
    el.className = 'polaroid swinging'
    el.style.cssText = `
      left: ${cx - pW / 2}px;
      top:  ${wireYi + drop}px;
      width: ${pW}px;
      height: ${pH + CAPTION_H}px;
      --base-rot: rotate(${rot}deg);
      --swing-dur: ${3.2 + (i % 4) * 0.85}s;
      --drop-delay: ${i * 0.055}s;
    `

    // ── media ──
    const inner = document.createElement('div')
    inner.style.cssText = `width:${pW-12}px;height:${pH}px;overflow:hidden;position:relative;`

    if (asset.media_path) {
      if (asset.media_type === 'video') {
        const vid = document.createElement('video')
        vid.src = asset.media_path
        vid.muted = true
        vid.preload = 'metadata'
        vid.style.cssText = `width:100%;height:100%;object-fit:cover;`
        inner.appendChild(vid)
        const play = document.createElement('div')
        play.className = 'polaroid-play'
        el.appendChild(play)
      } else {
        const img = document.createElement('img')
        img.src = asset.media_path
        img.style.cssText = `width:100%;height:100%;object-fit:cover;`
        inner.appendChild(img)
      }
    } else {
      const empty = document.createElement('div')
      empty.className = 'polaroid-empty'
      inner.appendChild(empty)
    }

    el.appendChild(inner)

    // ── tape ──
    const tape = document.createElement('div')
    tape.className = 'tape'
    tape.style.setProperty('--tape-rot', `${tapeRot}deg`)
    el.appendChild(tape)

    // ── label ──
    const label = document.createElement('div')
    label.className = 'polaroid-label'
    label.textContent = asset.title || ''
    el.appendChild(label)

    // ── badge ──
    if (asset.members && asset.members.length > 1) {
      const badge = document.createElement('div')
      badge.className = 'polaroid-badge'
      badge.textContent = asset.members.length
      el.appendChild(badge)
    }

    el.addEventListener('click', () => {
      if (_onOpen) _onOpen(asset.members || [asset], 0)
    })

    scene.appendChild(el)

    clusterPts.push({
      cx,
      cy: wireYi + drop + (pH + CAPTION_H) / 2,
      members: asset.members?.length || 1
    })
  })

  return clusterPts
}

function _renderArrows(clusterPts) {
  const arrowG = document.getElementById('arrows')
  for (let i = 0; i < clusterPts.length - 1; i++) {
    const a = clusterPts[i], b = clusterPts[i+1]
    if (a.members > 1 || b.members > 1) {
      const mx   = (a.cx + b.cx) / 2
      const my   = Math.min(a.cy, b.cy) - 50
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      path.setAttribute('d',            `M${a.cx},${a.cy} Q${mx},${my} ${b.cx},${b.cy}`)
      path.setAttribute('fill',         'none')
      path.setAttribute('stroke',       '#6a5a40')
      path.setAttribute('stroke-width', '1.1')
      path.setAttribute('opacity',      '0.5')
      path.setAttribute('stroke-dasharray', '4 3')
      path.setAttribute('marker-end',   'url(#arrowhead)')
      arrowG.appendChild(path)
    }
  }
}

// ── SCROLL ──
function scrollLine(dir) {
  _scrollX = Math.max(0, Math.min(_maxScroll, _scrollX + dir * SCROLL_STEP))
  document.getElementById('scene').style.transform = `translateX(${-_scrollX}px)`
  _updateButtons()
}

function _updateButtons() {
  document.getElementById('btn-left').classList.toggle('hidden',  _scrollX <= 0)
  document.getElementById('btn-right').classList.toggle('hidden', _scrollX >= _maxScroll)
}

// ── DRAG (mouse) ──
let _drag = false, _dx0 = 0, _sx0 = 0

document.getElementById('line-outer').addEventListener('mousedown', e => {
  _drag = true; _dx0 = e.clientX; _sx0 = _scrollX
  document.body.style.cursor = 'grabbing'
})
document.addEventListener('mousemove', e => {
  if (!_drag) return
  _scrollX = Math.max(0, Math.min(_maxScroll, _sx0 - (e.clientX - _dx0)))
  document.getElementById('scene').style.transform = `translateX(${-_scrollX}px)`
  _updateButtons()
})
document.addEventListener('mouseup', () => {
  _drag = false
  document.body.style.cursor = ''
})

// ── DRAG (touch) ──
let _tx0 = 0, _tsc0 = 0
document.getElementById('line-outer').addEventListener('touchstart', e => {
  _tx0 = e.touches[0].clientX; _tsc0 = _scrollX
}, { passive: true })
document.getElementById('line-outer').addEventListener('touchmove', e => {
  _scrollX = Math.max(0, Math.min(_maxScroll, _tsc0 - (e.touches[0].clientX - _tx0)))
  document.getElementById('scene').style.transform = `translateX(${-_scrollX}px)`
  _updateButtons()
}, { passive: true })

// ── HELPERS ──
function _rot(i)  { return [-7, 3, -5, 8, -2, 11, -8, 4, -10, 6, -4, 9][i % 12] }
function _drop(i) { return [8, 5, 95, 10, 105, 6, 12, 98, 5, 88, 7, 102][i % 12] }

window.addEventListener('resize', _render)

// ── INIT ──
initPolaroidLine(_assetsArray, (members, idx) => {
  console.log('open viewer', members, idx)
  // openPolaroidViewer(members, idx)  ← hook into your viewer
})

function setUpPolaroidLine(asset){
  initPolaroidLine(asset, (members, idx) => {
  console.log('open viewer', members, idx)
  // openPolaroidViewer(members, idx)  ← hook into your viewer
})
}