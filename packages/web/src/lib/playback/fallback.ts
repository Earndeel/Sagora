import { t } from '@lingui/core/macro';
import React from 'react';
import { toast } from 'sonner';
import { useVersionPicker } from '../../components/version-picker';
import { usePlaybackInfo } from '../queries';
import { settings, useSetting } from '../settings';
import type { BaseItemDto, SourceInfo } from '../types';
import type { PlayerController } from './controller';
import { automaticSources } from './play';

/**
 * Moves on to the item's next version when the one playing fails for real:
 * an error from the player (the stream can't be fetched, decoded or played)
 * or nothing shown after a while. Waiting for data once playing is buffering,
 * not a failure. It keeps the position, tries each version once and stops
 * after a few, leaving the error and the version list to the user.
 */

/** Versions tried on their own after the first, per play. */
const MAX_AUTO = 2;
/** How long a version may take to show its first frame. */
const START_LIMIT_MS = 30_000;
/** A play's record lasts this long, so playing the item again starts afresh. */
const RUN_MS = 20 * 60_000;

interface Run {
  tried: Set<string>;
  auto: number;
  at: number;
}

const runs = new Map<string, Run>();

function runFor(itemId: string): Run {
  const known = runs.get(itemId);
  if (known && Date.now() - known.at < RUN_MS) return known;
  const run = { tried: new Set<string>(), auto: 0, at: Date.now() };
  runs.set(itemId, run);
  return run;
}

export function useVersionFallback({
  item,
  source,
  player,
  startMs,
  playlist,
  enabled,
}: {
  item: BaseItemDto;
  source: SourceInfo;
  player: PlayerController;
  startMs: number;
  playlist?: string;
  /** Off for downloads and trailers, which have no other version. */
  enabled: boolean;
}): { pending: boolean } {
  const [allowed] = useSetting(settings.playback.autoFallback);
  const picker = useVersionPicker();
  const info = usePlaybackInfo(item.Id!, { enabled: enabled && allowed });
  const [pending, setPending] = React.useState(false);
  const [late, setLate] = React.useState(false);
  const { started, paused, error } = player.state;

  React.useEffect(() => {
    if (!enabled || !source.Id) return;
    const run = runFor(item.Id!);
    run.tried.add(source.Id);
    run.at = Date.now();
  }, [enabled, item.Id, source.Id]);

  React.useEffect(() => {
    setLate(false);
    if (!enabled || started || paused || error) return;
    const timer = setTimeout(() => setLate(true), START_LIMIT_MS);
    return () => clearTimeout(timer);
  }, [enabled, started, paused, error]);

  const failed = !!error || (late && !started);
  React.useEffect(() => {
    if (!failed || !enabled || !allowed || pending) return;
    const run = runFor(item.Id!);
    if (run.auto >= MAX_AUTO) return;
    const next = automaticSources(info.data).find(
      (s) => s.Id && !run.tried.has(s.Id) && !s.aiostreams?.ytId
    );
    if (!next) return;
    run.auto++;
    run.tried.add(next.Id!);
    setPending(true);
    const at = started ? player.playhead.positionMs : startMs;
    toast.info(
      late && !error
        ? t`This version is taking too long to start, trying another one…`
        : t`This version didn't play, trying another one…`
    );
    picker.play(item, {
      version: next.Id!,
      startMs: at,
      replace: true,
      playlist,
    });
  }, [
    failed,
    enabled,
    allowed,
    pending,
    info.data,
    item,
    started,
    startMs,
    playlist,
    picker,
    player.playhead,
    late,
    error,
  ]);

  return { pending };
}
