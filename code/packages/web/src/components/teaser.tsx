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

/** How long a teaser may take to show before the artwork stays: load, YouTube's chrome, HD. */
const START_LIMIT_MS = 15000;
/** Trailers tried in turn when one refuses to play here, as many do. */
const MAX_TRIES = 3;
const HANDSHAKE_MS = 250;
/**
 * YouTube shows its title, logo and a play/pause glyph over the first seconds
 * of an embed even without controls; the teaser stays hidden until they fade.
 */
const CHROME_HIDDEN_S = 4;
/** Below 720p a teaser looks worse than the artwork it replaces. */
const HD_QUALITIES = new Set(['hd720', 'hd1080', 'hd1440', 'hd2160', 'highres']);
/** The size the embed lays itself out at: YouTube picks its quality from it. */
const EMBED_W = 1920;
const EMBED_H = 1080;
/** Enlarged past the box to keep the player's edges out of sight. */
const EMBED_OVERSCAN = 1.2;

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
  onLoading,
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
  /** While its player loads out of sight, before it shows or gives up. */
  onLoading?(loading: boolean): void;
  onEnded?(): void;
  className?: string;
}) {
  const [enabled] = useSetting(settings.interface.teasers);
  const [allowed] = React.useState(teasersAllowed);
  const details = useItem(item.Id ?? '');
  const trailers = trailersOf(details.data ?? item);
  const [index, setIndex] = React.useState(0);
  const trailer = trailers[index];
  const [over, setOver] = React.useState(false);
  // A trailer its owner keeps off other sites gives way to the next one.
  const refused = React.useCallback(() => {
    if (index + 1 < Math.min(trailers.length, MAX_TRIES)) setIndex(index + 1);
    else setOver(true);
  }, [index, trailers.length]);
  const turn = useTeaserTurn(
    teaserKey,
    enabled && allowed && active && !!trailer && !over,
    priority
  );
  const [due, setDue] = React.useState(false);
  React.useEffect(() => {
    setDue(false);
    if (!turn) return;
    // Only the first waits: the next ones replace one that would have shown.
    const timer = setTimeout(() => setDue(true), index ? 0 : delayMs);
    return () => clearTimeout(timer);
  }, [turn, delayMs, trailer?.url, index]);
  const playback = useTrailerPlayback(due ? trailer?.url : undefined);
  const [playing, setPlaying] = React.useState(false);
  const latest = React.useRef({ onPlaying, onLoading, onEnded });
  latest.current = { onPlaying, onLoading, onEnded };

  const shown = turn && due && !!playback.data;
  React.useEffect(() => {
    if (shown && playback.data?.kind === 'external') refused();
    if (due && playback.isError) refused();
  }, [shown, due, playback.data, playback.isError, refused]);
  React.useEffect(() => {
    if (!shown) setPlaying(false);
  }, [shown]);
  React.useEffect(() => {
    if (!shown || playing) return;
    // A trailer that never plays gives way to the next, then to the artwork.
    const timer = setTimeout(refused, START_LIMIT_MS);
    return () => clearTimeout(timer);
  }, [shown, playing, refused]);
  React.useEffect(() => {
    latest.current.onPlaying?.(playing);
    setSounding(teaserKey, playing);
  }, [playing, teaserKey]);
  const loading = shown && !playing && !over;
  React.useEffect(() => {
    latest.current.onLoading?.(loading);
  }, [loading]);
  React.useEffect(
    () => () => {
      latest.current.onPlaying?.(false);
      latest.current.onLoading?.(false);
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
    onFailed: refused,
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
        <YouTubeTeaser key={found.id} id={found.id} {...events} />
      ) : (
        <VideoTeaser key={found.url} url={found.url} {...events} />
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
  const box = React.useRef<HTMLDivElement>(null);
  const [scale, setScale] = React.useState(0);
  const [muted] = useTeaserMuted();
  const [heard, setHeard] = React.useState(false);
  const latest = React.useRef({ onPlaying, onEnded, onFailed, muted });
  latest.current = { onPlaying, onEnded, onFailed, muted };
  // What the player last reported, and whether the teaser has been shown.
  const report = React.useRef({
    state: -1,
    time: 0,
    quality: '',
    shown: false,
    failed: false,
  });

  // Laid out at 1920×1080 whatever the box, then scaled down to cover it.
  React.useLayoutEffect(() => {
    const el = box.current;
    if (!el) return;
    const fit = () =>
      setScale(
        Math.max(el.clientWidth / EMBED_W, el.clientHeight / EMBED_H) *
          EMBED_OVERSCAN
      );
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

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
      const info =
        data.event === 'infoDelivery' || data.event === 'initialDelivery'
          ? ((data.info ?? {}) as {
              playerState?: number;
              currentTime?: number;
              playbackQuality?: string;
              availableQualityLevels?: string[];
            })
          : {};
      const state =
        data.event === 'onStateChange'
          ? (data.info as number | undefined)
          : info.playerState;
      const now = report.current;
      if (typeof state === 'number') now.state = state;
      if (typeof info.currentTime === 'number') now.time = info.currentTime;
      if (info.playbackQuality) now.quality = info.playbackQuality;
      if (data.event === 'onReady') {
        if (!latest.current.muted) command('unMute');
        command('setPlaybackQuality', ['hd1080']);
        command('unloadModule', ['captions']);
      }
      if (data.event === 'onError') latest.current.onFailed();
      // A trailer that exists only below 720p gives way to the next one.
      const levels = info.availableQualityLevels ?? [];
      if (
        !now.shown &&
        !now.failed &&
        levels.length &&
        !levels.some((level) => HD_QUALITIES.has(level))
      ) {
        now.failed = true;
        latest.current.onFailed();
      }
      if (
        !now.shown &&
        now.state === 1 &&
        now.time >= CHROME_HIDDEN_S &&
        HD_QUALITIES.has(now.quality)
      ) {
        now.shown = true;
        latest.current.onPlaying();
      }
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
    <div ref={box} className="absolute inset-0">
      {scale > 0 && (
        <iframe
          ref={frame}
          data-ui="teaser-embed"
          title=""
          tabIndex={-1}
          src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&mute=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&playsinline=1&rel=0&cc_load_policy=0&vq=hd1080&enablejsapi=1&origin=${origin}`}
          allow="autoplay; encrypted-media"
          referrerPolicy="strict-origin-when-cross-origin"
          onLoad={() => post({ event: 'listening' })}
          style={{
            width: EMBED_W,
            height: EMBED_H,
            transform: `translate(-50%, -50%) scale(${scale})`,
          }}
          className="absolute left-1/2 top-1/2 max-w-none border-0"
        />
      )}
    </div>
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
