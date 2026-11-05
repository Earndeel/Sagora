import { t } from '@lingui/core/macro';
import React from 'react';
import { toast } from 'sonner';
import { useVersionPicker } from '../../components/version-picker';
import { usePlaybackInfo } from '../queries';
import type { BaseItemDto, SourceInfo } from '../types';
import type { PlayerController } from './controller';
import { bitrateOf, learnedCap, setCap } from './bitrate-cap';
import { automaticSources } from './play';

/**
 * Quality that follows the connection, as far as single files allow: a debrid
 * version has one bitrate, so instead of a ladder within the file the player
 * moves to a lighter version at the same place when loading keeps stalling,
 * and the device remembers the bitrate that stalled so later plays start on a
 * version under it. Smooth playing raises that ceiling again.
 */

/** Stalled time within the window that calls for a lighter version. */
const STALL_BUDGET_MS = 8_000;
const WINDOW_MS = 90_000;
/** After the first frame or a jump, loading is expected, not a sign of a slow line. */
const GRACE_MS = 8_000;
/** A move of the position this far beyond the clock is a seek. */
const JUMP_MS = 3_000;
/** Lighter versions tried per play. */
const MAX_DOWNS = 3;
/** The replacement carries at most this share of the stalled version's bitrate. */
const LIGHTER = 0.65;
/** This long without a stall lets the device try heavier versions again. */
const SMOOTH_MS = 10 * 60_000;

/* Lighter versions already tried, per item, so a play does not bounce back. */
const downs = new Map<string, { count: number; at: number }>();

export function useAdaptiveVersion({
  item,
  source,
  player,
  playlist,
  enabled,
}: {
  item: BaseItemDto;
  source: SourceInfo;
  player: PlayerController;
  playlist?: string;
  enabled: boolean;
}): void {
  const picker = useVersionPicker();
  const info = usePlaybackInfo(item.Id!, { enabled });
  const { started, paused, waiting } = player.state;
  const watch = React.useRef({
    stalls: [] as { at: number; ms: number }[],
    since: 0,
    calmFrom: 0,
    lastPos: 0,
    lastClock: 0,
    smoothFrom: 0,
  });

  // A seek, or the first frame, opens a grace period and resets the calm clock.
  React.useEffect(() => {
    if (!enabled) return;
    const w = watch.current;
    const now = Date.now();
    w.calmFrom = now + GRACE_MS;
    w.smoothFrom = now;
    w.lastPos = player.playhead.positionMs;
    w.lastClock = now;
    return player.playhead.subscribe(() => {
      const at = Date.now();
      const pos = player.playhead.positionMs;
      if (Math.abs(pos - w.lastPos - (at - w.lastClock)) > JUMP_MS) {
        w.calmFrom = at + GRACE_MS;
        w.smoothFrom = at;
      }
      w.lastPos = pos;
      w.lastClock = at;
    });
  }, [enabled, started, source.Id, player.playhead]);

  React.useEffect(() => {
    if (!enabled || !started || paused) return;
    const w = watch.current;
    if (!waiting) {
      if (w.since) {
        w.stalls.push({ at: Date.now(), ms: Date.now() - w.since });
        w.since = 0;
      }
      // Smooth for long enough: this bitrate suits the line, so let heavier ones back in.
      const timer = setTimeout(() => {
        const bps = bitrateOf(source);
        const cap = learnedCap();
        if (bps && cap && bps * 1.25 > cap) setCap(bps * 1.25);
      }, Math.max(0, w.smoothFrom + SMOOTH_MS - Date.now()));
      return () => clearTimeout(timer);
    }
    if (Date.now() < w.calmFrom) return;
    w.since = Date.now();
    const timer = setInterval(() => {
      const now = Date.now();
      const stalled =
        w.stalls
          .filter((s) => now - s.at < WINDOW_MS)
          .reduce((sum, s) => sum + s.ms, 0) + (w.since ? now - w.since : 0);
      if (stalled < STALL_BUDGET_MS) return;
      clearInterval(timer);
      const run = downs.get(item.Id!);
      const count = run && now - run.at < 3 * 3600_000 ? run.count : 0;
      const bps = bitrateOf(source);
      if (count >= MAX_DOWNS || !bps) return;
      const lighter = automaticSources(info.data).find(
        (s) =>
          s.Id !== source.Id &&
          !s.aiostreams?.ytId &&
          (bitrateOf(s) ?? Infinity) <= bps * LIGHTER
      );
      if (!lighter) return;
      downs.set(item.Id!, { count: count + 1, at: now });
      setCap(bps * 0.8);
      w.stalls = [];
      w.since = 0;
      toast.info(t`The connection is slow, switching to a lighter version…`);
      picker.play(item, {
        version: lighter.Id!,
        startMs: player.playhead.positionMs,
        replace: true,
        playlist,
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [enabled, started, paused, waiting, source, info.data, item, picker, player.playhead, playlist]);
}
