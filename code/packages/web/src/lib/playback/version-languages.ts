import { plural } from '@lingui/core/macro';
import React from 'react';
import { useVersionPicker } from '../../components/version-picker';
import { LANGUAGES, languageName } from '../languages';
import { usePlaybackInfo } from '../queries';
import type { BaseItemDto, SourceInfo } from '../types';
import type { PlayerController, Track } from './controller';
import { playableSources } from './play';

/**
 * Choosing the spoken language among the item's versions, as a dub menu: a
 * browser can't switch a file's own audio tracks, and many versions carry one
 * language only. A pick plays the best-ranked version in that language from
 * the same point, a version with that language alone first, since a player
 * that can't switch tracks plays a file's first one.
 */

/* eslint-disable lingui/no-unlocalized-strings -- the addon's own labels */
const NOT_LANGUAGES = new Set([
  'Multi',
  'Dual Audio',
  'Dubbed',
  'Unknown',
  'Original',
]);
/* eslint-enable lingui/no-unlocalized-strings */

const spoken = (source: SourceInfo) =>
  ((source.aiostreams?.languages ?? []) as string[]).filter(
    (l) => !NOT_LANGUAGES.has(l)
  );

function label(name: string): string {
  const known = LANGUAGES.find((l) => l.name === name);
  const shown = known ? languageName(known) : name;
  return shown.charAt(0).toLocaleUpperCase() + shown.slice(1);
}

export interface VersionLanguages {
  options: Track[];
  value: string | null;
  onSelect(id: string | null): void;
}

export function useVersionLanguages({
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
}): VersionLanguages | undefined {
  const picker = useVersionPicker();
  const info = usePlaybackInfo(item.Id!, { enabled });
  const playhead = player.playhead;
  return React.useMemo(() => {
    if (!enabled) return undefined;
    const versions = playableSources(info.data).filter(
      (s) => s.Id && !s.aiostreams?.ytId
    );
    // In the versions' own order, which is the configuration's ranking.
    const byLanguage = new Map<string, SourceInfo[]>();
    for (const version of versions)
      for (const language of spoken(version))
        byLanguage.set(language, [
          ...(byLanguage.get(language) ?? []),
          version,
        ]);
    if (byLanguage.size < 2) return undefined;
    const current = spoken(source);
    const options = [...byLanguage.entries()].map(([name, list]) => {
      const count = list.length;
      return {
        id: name,
        label: label(name),
        detail: plural(count, { one: '# version', other: '# versions' }),
      };
    });
    return {
      options,
      value: current.length === 1 ? current[0] : null,
      onSelect(name) {
        if (!name) return;
        const list = byLanguage.get(name) ?? [];
        const others = list.filter((s) => s.Id !== source.Id);
        const next = others.find((s) => spoken(s).length === 1) ?? others[0];
        if (!next) return;
        picker.play(item, {
          version: next.Id!,
          startMs: playhead.positionMs,
          replace: true,
          playlist,
        });
      },
    };
  }, [enabled, info.data, source, item, picker, playhead, playlist]);
}
