// ═══════════════════════════════════════════
// TRIPPING — polaroid_data.js
// Data layer — assets, petal SVGs, demo data
// ═══════════════════════════════════════════

// ── PETAL SVG TEMPLATES ──
// Replace VAR at runtime with opacity value
const PETAL_SVGS = [
  // cherry blossom
  `<svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="9" cy="5" rx="4" ry="6" fill="rgba(210,170,150,VAR)" transform="rotate(0,9,9)"/>
    <ellipse cx="9" cy="5" rx="4" ry="6" fill="rgba(210,170,150,VAR)" transform="rotate(72,9,9)"/>
    <ellipse cx="9" cy="5" rx="4" ry="6" fill="rgba(210,170,150,VAR)" transform="rotate(144,9,9)"/>
    <ellipse cx="9" cy="5" rx="4" ry="6" fill="rgba(210,170,150,VAR)" transform="rotate(216,9,9)"/>
    <ellipse cx="9" cy="5" rx="4" ry="6" fill="rgba(210,170,150,VAR)" transform="rotate(288,9,9)"/>
  </svg>`,
  // single petal
  `<svg width="14" height="20" viewBox="0 0 14 20" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="7" cy="10" rx="5" ry="9" fill="rgba(190,155,130,VAR)"/>
  </svg>`,
  // leaf
  `<svg width="16" height="12" viewBox="0 0 16 12" xmlns="http://www.w3.org/2000/svg">
    <path d="M8,1 Q14,6 8,11 Q2,6 8,1Z" fill="rgba(120,100,70,VAR)"/>
  </svg>`,
]

// ── HELPERS ──
const _imgs = (ids) => ids.map(id => ({
  media_path: `https://picsum.photos/seed/${id}/400/400`,
  media_type: 'image',
  title: ''
}))

// ── DEMO ASSETS ──
// Replace with real API data in production:
// const assets = await fetch('/api/trip/medias').then(r => r.json())
// const demoAssets = [
//   { media_path: 'https://picsum.photos/seed/dalatmtn/400/500',     media_type: 'image', title: 'da lat',    members: _imgs(['dalatmtn','dalatflower','dalatfall']) },
//   { media_path: 'https://picsum.photos/seed/hoianlantern/400/400', media_type: 'image', title: 'hoi an',    members: _imgs(['hoianlantern','hoianboat']) },
//   { media_path: 'https://picsum.photos/seed/saigon99/400/400',     media_type: 'image', title: 'saigon',    members: _imgs(['saigon99','saigonnight','saigonstreet','saigonfood','saigonroof']) },
//   { media_path: 'https://picsum.photos/seed/mekong12/400/500',     media_type: 'image', title: 'mekong',    members: _imgs(['mekong12']) },
//   { media_path: 'https://picsum.photos/seed/halong88/400/400',     media_type: 'image', title: 'ha long',   members: _imgs(['halong88','halongkayak','halongcave']) },
//   { media_path: 'https://picsum.photos/seed/hanoiold/400/400',     media_type: 'image', title: 'hanoi',     members: _imgs(['hanoiold','hanoilake','hanoifood','hanoitrain']) },
//   { media_path: 'https://picsum.photos/seed/ninh55/400/500',       media_type: 'image', title: 'ninh binh', members: _imgs(['ninh55','ninhboat']) },
//   { media_path: 'https://picsum.photos/seed/hue2024/400/400',      media_type: 'image', title: 'hue',       members: _imgs(['hue2024','huecitadel','hueriver']) },
//   { media_path: 'https://picsum.photos/seed/danang77/400/400',     media_type: 'image', title: 'da nang',   members: _imgs(['danang77','danangbridge','danangbeach','danangmkt']) },
//   { media_path: 'https://picsum.photos/seed/muine33/400/500',      media_type: 'image', title: 'mui ne',    members: _imgs(['muine33','muinesand']) },
//   { media_path: 'https://picsum.photos/seed/phuquoc1/400/400',     media_type: 'image', title: 'phu quoc',  members: _imgs(['phuquoc1','phuquocsunset','phuquocsnorkel','phuquocmarket','phuquocnight','phuquocbeach']) },
//   { media_path: 'https://picsum.photos/seed/sapa44/400/500',       media_type: 'image', title: 'sapa',      members: _imgs(['sapa44','saparice','sapamist']) },
//   { media_path: 'https://picsum.photos/seed/catba22/400/400',      media_type: 'image', title: 'cat ba',    members: _imgs(['catba22','catbajungle']) },
//   { media_path: 'https://picsum.photos/seed/binhba55/400/400',     media_type: 'image', title: 'binh ba',   members: _imgs(['binhba55','binhbabeach','binhbacoral']) },
// ]
