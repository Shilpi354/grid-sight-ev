export function formatNumber(val: number | null | undefined, decimals: number = 0): string {
  if (val === null || val === undefined || Number.isNaN(val)) {
    return 'N/A';
  }
  return val.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatCompactIndian(val: number | null | undefined): string {
  if (val === null || val === undefined || Number.isNaN(val)) {
    return 'N/A';
  }
  if (val >= 10_000_000) {
    return `${(val / 10_000_000).toFixed(2)} Cr`;
  }
  if (val >= 100_000) {
    return `${(val / 100_000).toFixed(2)} L`;
  }
  if (val >= 1_000) {
    return `${(val / 1_000).toFixed(1)}k`;
  }
  return val.toLocaleString('en-IN');
}

export function getChoroplethColor(
  value: number | null | undefined,
  thresholds: number[],
  palette: string[]
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '#e2e8f0';
  }
  for (let i = 0; i < thresholds.length; i++) {
    if (value <= thresholds[i]) {
      return palette[i];
    }
  }
  return palette[palette.length - 1];
}

// Editorial cartographic palettes calibrated for clean light Positron basemap
export const PALETTE_TEAL_EMERALD = ['#e6f4f1', '#b2dfdb', '#80cbc4', '#26a69a', '#0f766e', '#064e3b'];
export const PALETTE_AMBER_RED = ['#f0fdf4', '#bbf7d0', '#fed7aa', '#fb923c', '#ea580c', '#b91c1c'];
export const PALETTE_INDIGO_CYAN = ['#f8fafc', '#cbd5e1', '#94a3b8', '#64748b', '#334155', '#0f172a'];
