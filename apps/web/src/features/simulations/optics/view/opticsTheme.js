/** optics/view/opticsTheme.js - Design tokens for the optics p5.js canvas. */
export const THEME = {
  axis:         { stroke: 'rgba(255,255,255,0.25)', weight: 1, dash: [6, 4] },
  lens:         { stroke: '#60a5fa', weight: 2.5, glow: '#60a5fa', apertureH: 200 },
  mirror:       { stroke: '#a78bfa', weight: 3, glow: '#a78bfa', fill: 'rgba(167,139,250,0.1)' },
  prism:        { stroke: '#38bdf8', weight: 2, fill: 'rgba(56,189,248,0.12)', glow: '#38bdf8' },
  normal:       { stroke: 'rgba(255,255,255,0.4)', weight: 1.2, dash: [5, 4] },
  angleArc:     { stroke: '#fbbf24', weight: 1.5, fill: 'rgba(251,191,36,0.18)' },
  angleText:    { fill: '#fbbf24', size: 12 },
  object:       { stroke: '#4ade80', fill: '#4ade80', weight: 2.5, glow: '#4ade80', glowBlur: 12 },
  imageReal:    { stroke: '#fb923c', fill: '#fb923c', weight: 2,   glow: '#fb923c', glowBlur: 10 },
  imageVirtual: { stroke: 'rgba(251,146,60,0.55)', fill: 'rgba(251,146,60,0.55)', weight: 1.5, dash: [6, 4] },
  rays: ['#38bdf8', '#f472b6', '#a78bfa', '#34d399', '#f87171'],
  virtual: { alpha: 0.45, dash: [8, 5] },
  focal:      { fill: '#fbbf24', radius: 5 },
  focalLabel: { fill: '#fbbf24', size: 12 },
};

