import React from 'react';
import { useSession } from './session';
import { settings, useSetting } from './settings';
import { backdropUrl, landscapeUrl, posterUrl } from './images';
import { usePageShown } from './page-shown';
import type { BaseItemDto } from './types';

/**
 * A title's colour, taken from its artwork, tints the play buttons, progress
 * bars and a few glows while the title is on screen, as `--title-accent` on
 * the root. The background and the rest of the theme stay as they are.
 * Several places may show a title: the latest to ask wins, and the one
 * before comes back when it goes, as when an item's page closes over home.
 */

const SIDE = 40;
const BINS = 24;

const found = new Map<string, Promise<string | null>>();

/** The colour picked for an image, or null for artwork with none to speak of. */
export function accentOf(src: string): Promise<string | null> {
  let known = found.get(src);
  if (!known) {
    known = read(src).catch(() => null);
    found.set(src, known);
    if (found.size > 300) found.delete(found.keys().next().value!);
  }
  return known;
}

function read(src: string): Promise<string | null> {
  return new Promise((resolve) => {
    const img = new Image();
    // Another server's images only read back when it allows it; else no colour.
    img.crossOrigin = 'anonymous';
    img.decoding = 'async';
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = SIDE;
        canvas.height = Math.max(
          1,
          Math.round((SIDE * img.naturalHeight) / img.naturalWidth) || SIDE
        );
        const context = canvas.getContext('2d', { willReadFrequently: true });
        if (!context) return resolve(null);
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
        const { data } = context.getImageData(
          0,
          0,
          canvas.width,
          canvas.height
        );
        const rgb = pick(data);
        resolve(rgb && tune(rgb));
      } catch {
        resolve(null);
      }
    };
    img.onerror = () => resolve(null);
    img.src = src;
  });
}

type Rgb = [number, number, number];

/** The most present lively hue, averaged with its neighbours. */
export function pick(data: ArrayLike<number>): Rgb | null {
  const weight = new Float64Array(BINS);
  const sums = Array.from({ length: BINS }, () => [0, 0, 0]);
  const pixels = data.length / 4;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const v = max / 255;
    const s = max ? (max - min) / max : 0;
    if (v < 0.22 || s < 0.28) continue;
    const bin = Math.min(
      BINS - 1,
      Math.floor((hue(r, g, b, max, min) / 360) * BINS)
    );
    const w = s * s * v;
    weight[bin] += w;
    sums[bin][0] += r * w;
    sums[bin][1] += g * w;
    sums[bin][2] += b * w;
  }
  let best = -1;
  let bestWeight = 0;
  for (let bin = 0; bin < BINS; bin++) {
    const around =
      weight[bin] +
      0.5 * (weight[(bin + 1) % BINS] + weight[(bin + BINS - 1) % BINS]);
    if (around > bestWeight) {
      bestWeight = around;
      best = bin;
    }
  }
  // A few coloured pixels in a grey picture are no colour of its own.
  if (best < 0 || bestWeight < pixels * 0.012) return null;
  let total = 0;
  const rgb = [0, 0, 0];
  for (const bin of [best - 1, best, best + 1]) {
    const at = (bin + BINS) % BINS;
    const share = at === best ? 1 : 0.5;
    total += weight[at] * share;
    for (let c = 0; c < 3; c++) rgb[c] += sums[at][c] * share;
  }
  return rgb.map((c) => c / total) as Rgb;
}

function hue(r: number, g: number, b: number, max: number, min: number) {
  const d = max - min;
  if (!d) return 0;
  const h =
    max === r
      ? ((g - b) / d) % 6
      : max === g
        ? (b - r) / d + 2
        : (r - g) / d + 4;
  return (h * 60 + 360) % 360;
}

const luminance = ([r, g, b]: Rgb) => {
  const lin = (c: number) => {
    const x = c / 255;
    return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
};

function hsl([r, g, b]: Rgb): [number, number, number] {
  const max = Math.max(r, g, b) / 255;
  const min = Math.min(r, g, b) / 255;
  const l = (max + min) / 2;
  const d = max - min;
  const s = d ? d / (1 - Math.abs(2 * l - 1)) : 0;
  return [hue(r, g, b, max * 255, min * 255), s, l];
}

function rgbOf(h: number, s: number, l: number): Rgb {
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  const [r, g, b] =
    h < 60
      ? [c, x, 0]
      : h < 120
        ? [x, c, 0]
        : h < 180
          ? [0, c, x]
          : h < 240
            ? [0, x, c]
            : h < 300
              ? [x, 0, c]
              : [c, 0, x];
  return [r, g, b].map((v) => Math.round((v + m) * 255)) as Rgb;
}

/**
 * Bright enough for dark text on it and to stand out on the dark background
 * (a contrast of at least 6:1 with near black), never pale or garish.
 */
export function tune(rgb: Rgb): string {
  const [h, s0] = hsl(rgb);
  const s = Math.min(0.82, Math.max(0.45, s0));
  let l = 0.6;
  let out = rgbOf(h, s, l);
  while (luminance(out) < 0.3 && l < 0.8) out = rgbOf(h, s, (l += 0.02));
  while (luminance(out) > 0.62 && l > 0.45) out = rgbOf(h, s, (l -= 0.02));
  return `rgb(${out[0]} ${out[1]} ${out[2]})`;
}

function artwork(client: Parameters<typeof backdropUrl>[0], item: BaseItemDto) {
  return (
    backdropUrl(client, item, { maxWidth: 320 }) ??
    landscapeUrl(client, item, { maxWidth: 320 }) ??
    posterUrl(client, item, { maxWidth: 160 })
  );
}

const holders: { key: symbol; colour: string | null }[] = [];

function apply(enabled: boolean) {
  const root = document.documentElement;
  root.toggleAttribute('data-title-colours', enabled);
  const colour = enabled ? holders.at(-1)?.colour : null;
  if (colour) {
    root.style.setProperty('--title-accent', colour);
    root.setAttribute('data-title-accent', '');
  } else {
    root.removeAttribute('data-title-accent');
  }
}

/** Tints the app with `item`'s colour while the calling page is shown. */
export function useTitleAccent(item: BaseItemDto | undefined) {
  const { client } = useSession();
  const [enabled] = useSetting(settings.interface.titleColours);
  const shown = usePageShown();
  const [key] = React.useState(() => Symbol('title-accent'));
  const src = item && artwork(client, item);

  React.useEffect(() => {
    if (!shown) return;
    const holder = { key, colour: null as string | null };
    holders.push(holder);
    return () => {
      holders.splice(holders.indexOf(holder), 1);
      apply(enabled);
    };
  }, [key, shown, enabled]);

  React.useEffect(() => {
    if (!shown) return;
    let current = true;
    const holder = holders.find((h) => h.key === key);
    if (!holder) return;
    if (!enabled || !src) {
      holder.colour = null;
      apply(enabled);
      return;
    }
    void accentOf(src).then((colour) => {
      if (!current) return;
      holder.colour = colour;
      apply(enabled);
    });
    return () => {
      current = false;
    };
  }, [key, shown, enabled, src]);
}
