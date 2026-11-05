import { storage } from '../storage';
import type { SourceInfo } from '../types';

/**
 * The bitrate this device last stalled at (see adaptive.ts), remembered for a
 * week so that plays start on a version the connection can carry.
 */
const CAP_KEY = 'sagora-adaptive-cap';
const CAP_LIFE_MS = 7 * 24 * 3600_000;

interface Cap {
  bps: number;
  at: number;
}

export function bitrateOf(source: SourceInfo): number | null {
  if (source.Bitrate && source.Bitrate > 0) return source.Bitrate;
  const seconds = source.RunTimeTicks ? source.RunTimeTicks / 1e7 : 0;
  return source.Size && seconds > 0 ? (source.Size * 8) / seconds : null;
}

/** The bitrate this device last stalled at, while it is recent. */
export function learnedCap(): number | null {
  const cap = storage.get<Cap>(CAP_KEY);
  if (!cap || Date.now() - cap.at > CAP_LIFE_MS) return null;
  return cap.bps;
}

export function setCap(bps: number | null) {
  storage.set(CAP_KEY, bps ? { bps, at: Date.now() } : null);
}

/** The ranked versions with those over the device's ceiling moved after the rest. */
export function fittingFirst(sources: SourceInfo[]): SourceInfo[] {
  const cap = learnedCap();
  if (!cap) return sources;
  const fits = (s: SourceInfo) => (bitrateOf(s) ?? 0) <= cap;
  return [...sources.filter(fits), ...sources.filter((s) => !fits(s))];
}

