import { plural } from '@lingui/core/macro';
import React from 'react';
import { BiMoviePlay } from 'react-icons/bi';
import { Button, IconButton } from '@aiostreams/ui/button';
import { navigate, to } from '../lib/paths';
import { enterTrailerFullscreen } from '../lib/playback/fullscreen';
import { trailersOf, usePrefetchTrailer } from '../lib/playback/trailers';
import { expandTeaser } from '../lib/teaser';
import type { BaseItemDto } from '../lib/types';

export function TrailerButton({
  item,
  compact,
  teaserKey,
}: {
  item: BaseItemDto;
  compact?: boolean;
  /** The page's teaser, which goes full screen where it is instead of starting over. */
  teaserKey?: string;
}) {
  const trailers = React.useMemo(() => trailersOf(item), [item]);
  const prefetch = usePrefetchTrailer();
  if (!trailers.length) return null;
  const play = (index: number) => navigate(to.trailer(item.Id!, index));
  const count = trailers.length;
  const label = plural(count, { one: 'Trailer', other: 'Trailers' });
  // Straight to a video: the page's teaser full screen, or the first trailer,
  // whose player steps through the others.
  const open = () => {
    if (teaserKey && expandTeaser(teaserKey)) return;
    enterTrailerFullscreen();
    play(0);
  };
  return (
    <>
      {compact ? (
        <IconButton
          data-ui="item-action"
          data-name="trailer"
          intent="gray-subtle"
          className="rounded-full"
          icon={<BiMoviePlay />}
          aria-label={label}
          onClick={open}
        />
      ) : (
        <Button
          data-ui="item-action"
          data-name="trailer"
          intent="gray-outline"
          className="rounded-full"
          leftIcon={<BiMoviePlay className="text-lg" />}
          onFocus={() => prefetch(trailers[0].url)}
          onPointerEnter={() => prefetch(trailers[0].url)}
          onClick={open}
        >
          {label}
        </Button>
      )}
    </>
  );
}
