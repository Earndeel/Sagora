import { t } from '@lingui/core/macro';
import React from 'react';
import { LuVolume2, LuVolumeX } from 'react-icons/lu';
import { cn } from '@aiostreams/ui/core/styling';
import { useItem } from '../lib/queries';
import { settings, useSetting } from '../lib/settings';
import { trailersOf, useTrailerPlayback } from '../lib/playback/trailers';
import {
  setSounding,
  teasersAllowed,
  useSounding,
  useTeaserMuted,
  useTeaserTurn,
} from '../lib/teaser';
import type { BaseItemDto } from '../lib/types';

/** How long a teaser may take to start before the artwork stays. */
const START_LIMIT_MS = 9000;
const HANDSHAKE_MS = 250;

/**
 * A title's first trailer, muted, over its artwork once it has played for a
 * moment. Nothing shows until a frame plays, so a missing, refused or slow
 * trailer leaves the artwork as it was. It stops as soon as it is unmounted,
 * made inactive or loses the turn to another teaser.
 */
export function Teaser({
  item,
  teaserKey,
  active,
  delayMs,
  priority = 0,
  onPlaying,
  onEnded,
  className,
}: {
  item: BaseItemDto;
  /** Who plays it: `hero`, `follow` or the card's. */
  teaserKey: string;
  active: boolean;
  delayMs: number;
  /** A card's preview comes before the hero. */
  priority?: number;
  onPlaying?(playing: boolean): void;
  onEnded?(): void;
  className?: string;
}) {
  const [enabled] = useSetting(settings.interface.teasers);
  const [allowed] = React.useState(teasersAllowed);
  const details = useItem(item.Id ?? '');
  const trailer = trailersOf(details.data ?? item)[0];
  const [over, setOver] = React.useState(false);
  const turn = useTeaserTurn(
    teaserKey,
    enabled && allowed && active && !!trailer && !over,
    priority
  );
  const [due, setDue] = React.useState(false);
  React.useEffect(() => {
    setDue(false);
    if (!turn) return;
    const timer = setTimeout(() => setDue(true), delayMs);
    return () => clearTimeout(timer);
  }, [turn, delayMs, trailer?.url]);
  const playback = useTrailerPlayback(due ? trailer?.url : undefined);
  const [playing, setPlaying] = React.useState(false);
  const latest = React.useRef({ onPlaying, onEnded });
  latest.current = { onPlaying, onEnded };

  const shown = turn && due && !!playback.data;
  React.useEffect(() => {
    if (!shown) setPlaying(false);
  }, [shown]);
  React.useEffect(() => {
    if (!shown || playing) return;
    // A trailer that never plays gives way to the artwork for good.
    const timer = setTimeout(() => setOver(true), START_LIMIT_MS);
    return () => clearTimeout(timer);
  }, [shown, playing]);
  React.useEffect(() => {
    latest.current.onPlaying?.(playing);
    setSounding(teaserKey, playing);
  }, [playing, teaserKey]);
  React.useEffect(
    () => () => {
      latest.current.onPlaying?.(false);
      setSounding(teaserKey, false);
    },
    [teaserKey]
  );

  if (!shown || playback.data!.kind === 'external') return null;
  const found = playback.data!;
  const events = {
    onPlaying: () => setPlaying(true),
    onEnded: () => {
      setPlaying(false);
      setOver(true);
      latest.current.onEnded?.();
    },
    onFailed: () => setOver(true),
  };
  return (
    <div
      aria-hidden
      data-ui="teaser"
      data-playing={playing || undefined}
      className={cn(
        'pointer-events-none absolute inset-0 overflow-hidden [container-type:size]',
        'opacity-0 transition-opacity duration-700 ease-out data-[playing]:opacity-100',
        className
      )}
    >
      {found.kind === 'embed' ? (
        <YouTubeTeaser id={found.id} {...events} />
      ) : (
        <VideoTeaser url={found.url} {...events} />
      )}
    </div>
  );
}

interface TeaserEvents {
  onPlaying(): void;
  onEnded(): void;
  onFailed(): void;
}

// Covers its box like the artwork, a little enlarged to keep the player's
// edges out of sight.
const COVER =
  'absolute start-1/2 top-1/2 h-[max(100cqh,56.25cqw)] w-[max(100cqw,177.78cqh)] -translate-x-1/2 -translate-y-1/2 scale-[1.2] rtl:translate-x-1/2 border-0';

function YouTubeTeaser({
  id,
  onPlaying,
  onEnded,
  onFailed,
}: { id: string } & TeaserEvents) {
  const frame = React.useRef<HTMLIFrameElement>(null);
  const [muted] = useTeaserMuted();
  const [heard, setHeard] = React.useState(false);
  const latest = React.useRef({ onPlaying, onEnded, onFailed, muted });
  latest.current = { onPlaying, onEnded, onFailed, muted };

  const post = React.useCallback(
    (message: object) => {
      frame.current?.contentWindow?.postMessage(
        JSON.stringify({ ...message, id, channel: 'widget' }),
        '*'
      );
    },
    [id]
  );
  const command = React.useCallback(
    (func: string, args: unknown[] = []) =>
      post({ event: 'command', func, args }),
    [post]
  );

  React.useEffect(() => {
    const receive = (e: MessageEvent) => {
      if (e.source !== frame.current?.contentWindow) return;
      let data: { event?: string; info?: unknown };
      try {
        data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
      } catch {
        return;
      }
      setHeard(true);
      const state =
        data.event === 'onStateChange'
          ? data.info
          : data.event === 'infoDelivery'
            ? (data.info as { playerState?: number } | undefined)?.playerState
            : undefined;
      if (data.event === 'onReady' && !latest.current.muted) command('unMute');
      if (data.event === 'onError') latest.current.onFailed();
      if (state === 1) latest.current.onPlaying();
      if (state === 0) latest.current.onEnded();
    };
    addEventListener('message', receive);
    return () => removeEventListener('message', receive);
  }, [command]);

  // The player only reports once it is listened to, which it may miss early on.
  React.useEffect(() => {
    if (heard) return;
    const timer = setInterval(() => post({ event: 'listening' }), HANDSHAKE_MS);
    return () => clearInterval(timer);
  }, [heard, post]);

  React.useEffect(() => {
    if (heard) command(muted ? 'mute' : 'unMute');
  }, [muted, heard, command]);

  const origin = encodeURIComponent(location.origin);
  return (
    <iframe
      ref={frame}
      data-ui="teaser-embed"
      title=""
      tabIndex={-1}
      src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&mute=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&playsinline=1&rel=0&enablejsapi=1&origin=${origin}`}
      allow="autoplay; encrypted-media"
      referrerPolicy="strict-origin-when-cross-origin"
      onLoad={() => post({ event: 'listening' })}
      className={COVER}
    />
  );
}

function VideoTeaser({
  url,
  onPlaying,
  onEnded,
  onFailed,
}: { url: string } & TeaserEvents) {
  const [muted] = useTeaserMuted();
  return (
    <video
      data-ui="teaser-video"
      src={url}
      muted={muted}
      autoPlay
      playsInline
      preload="auto"
      disablePictureInPicture
      onPlaying={onPlaying}
      onEnded={onEnded}
      onError={onFailed}
      className={cn(COVER, 'object-cover')}
    />
  );
}

/** Turns the sound of `teaserKey`'s teaser on or off while it plays. */
export function TeaserSoundButton({
  teaserKey,
  className,
}: {
  teaserKey: string;
  className?: string;
}) {
  const [muted, setMuted] = useTeaserMuted();
  const sounding = useSounding();
  if (sounding !== teaserKey) return null;
  const label = muted ? t`Turn the sound on` : t`Turn the sound off`;
  return (
    <button
      type="button"
      data-ui="teaser-sound"
      data-muted={muted || undefined}
      data-nav="skip"
      aria-label={label}
      title={label}
      onClick={(e) => {
        e.stopPropagation();
        setMuted(!muted);
      }}
      onPointerDown={(e) => e.stopPropagation()}
      className={cn(
        'flex size-9 items-center justify-center rounded-full border border-white/40 bg-black/40 text-lg text-white backdrop-blur-sm',
        'duration-300 animate-in fade-in-0 hover:border-white hover:bg-black/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--ring]',
        className
      )}
    >
      {muted ? <LuVolumeX /> : <LuVolume2 />}
    </button>
  );
}
