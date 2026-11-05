import { t } from '@lingui/core/macro';
import React from 'react';
import { LuPlay, LuVolume2, LuVolumeX, LuX } from 'react-icons/lu';
import { cn } from '@aiostreams/ui/core/styling';
import { useItem } from '../lib/queries';
import { settings, useSetting } from '../lib/settings';
import { trailersOf, useTrailerPlayback } from '../lib/playback/trailers';
import {
  registerTeaserScreen,
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
/** A cinema-wide trailer is enlarged to its picture, past its black bands, and only this much more. */
const PICTURE_OVERSCAN = 1.03;
/** Wider than this, YouTube's black bands above and below would still show at EMBED_OVERSCAN. */
const BANDED_FROM = (EMBED_W / EMBED_H) * EMBED_OVERSCAN;
/** The sound rises over this once the teaser shows, never as the page opens. */
const FADE_IN_MS = 3000;
/** Full screen, asked for with a click: the sound comes quickly. */
const FULL_FADE_IN_MS = 600;
const FADE_STEPS = 20;

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
  // Full screen from the trailer button: the same player, carrying on.
  const screen = React.useRef<HTMLDivElement | null>(null);
  const [full, setFull] = React.useState(false);
  React.useEffect(() => {
    const follow = () =>
      setFull(!!screen.current && document.fullscreenElement === screen.current);
    document.addEventListener('fullscreenchange', follow);
    return () => document.removeEventListener('fullscreenchange', follow);
  }, []);
  // A trailer its owner keeps off other sites gives way to the next one.
  const refused = React.useCallback(() => {
    if (index + 1 < Math.min(trailers.length, MAX_TRIES)) setIndex(index + 1);
    else setOver(true);
  }, [index, trailers.length]);
  const turn = useTeaserTurn(
    teaserKey,
    enabled && allowed && (active || full) && !!trailer && !over,
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
      registerTeaserScreen(teaserKey, null);
    },
    [teaserKey]
  );
  const attach = React.useCallback(
    (el: HTMLDivElement | null) => {
      screen.current = el;
      registerTeaserScreen(teaserKey, el);
    },
    [teaserKey]
  );

  if (!shown || playback.data!.kind === 'external') return null;
  const found = playback.data!;
  const events = {
    onPlaying: () => setPlaying(true),
    onEnded: () => {
      if (document.fullscreenElement === screen.current)
        void document.exitFullscreen().catch(() => undefined);
      setPlaying(false);
      setOver(true);
      latest.current.onEnded?.();
    },
    onFailed: refused,
    full,
  };
  return (
    <div
      ref={attach}
      aria-hidden={!full}
      data-ui="teaser"
      data-playing={playing || undefined}
      data-full={full || undefined}
      className={cn(
        'pointer-events-none absolute inset-0 overflow-hidden [container-type:size]',
        'opacity-0 transition-opacity duration-700 ease-out data-[playing]:opacity-100',
        'data-[full]:pointer-events-auto data-[full]:bg-black data-[full]:opacity-100',
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
  /** Full screen: whole picture, sound on, its own pause and close. */
  full: boolean;
}

/** Raises a volume from where it is to 100 in steps; returns the stop. */
function fadeIn(
  from: number,
  ms: number,
  set: (volume: number) => void
): () => void {
  let volume = from;
  const step = Math.max(1, (100 - from) / FADE_STEPS);
  set(volume);
  const timer = setInterval(() => {
    volume = Math.min(100, volume + step);
    set(volume);
    if (volume >= 100) clearInterval(timer);
  }, ms / FADE_STEPS);
  return () => clearInterval(timer);
}

/** Over a full-screen teaser: a click pauses or resumes, and a close button. */
function FullControls({
  paused,
  onToggle,
}: {
  paused: boolean;
  onToggle(): void;
}) {
  return (
    <div
      data-ui="teaser-full-controls"
      className="absolute inset-0 z-[1] cursor-pointer"
      onClick={onToggle}
    >
      {paused && (
        <span className="absolute left-1/2 top-1/2 flex size-20 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-black/50 text-4xl text-white">
          <LuPlay />
        </span>
      )}
      <button
        type="button"
        data-ui="teaser-full-close"
        aria-label={t`Close`}
        title={t`Close`}
        onClick={(e) => {
          e.stopPropagation();
          void document.exitFullscreen().catch(() => undefined);
        }}
        className="absolute end-6 top-6 flex size-11 items-center justify-center rounded-full border border-white/40 bg-black/40 text-xl text-white backdrop-blur-sm hover:border-white hover:bg-black/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--ring]"
      >
        <LuX />
      </button>
    </div>
  );
}

// Covers its box like the artwork, a little enlarged to keep the player's
// edges out of sight.
const COVER =
  'absolute start-1/2 top-1/2 h-[max(100cqh,56.25cqw)] w-[max(100cqw,177.78cqh)] -translate-x-1/2 -translate-y-1/2 scale-[1.2] rtl:translate-x-1/2 border-0';

/* Each trailer's picture width over height, measured once. */
const ratios = new Map<string, Promise<number>>();

/** How tall the picture is in one of YouTube's 4:3 stills of the video, black bands left out. */
function pictureRatio(src: string): Promise<number | null> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onerror = () => resolve(null);
    img.onload = () => {
      try {
        const w = 160;
        const h = Math.round((img.naturalHeight / img.naturalWidth) * w);
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
        ctx.drawImage(img, 0, 0, w, h);
        const { data } = ctx.getImageData(0, 0, w, h);
        // A row is picture once any pixel in it is more than near black.
        const lit = (y: number) => {
          for (let x = 0; x < w; x++) {
            const i = (y * w + x) * 4;
            if (Math.max(data[i], data[i + 1], data[i + 2]) > 40) return true;
          }
          return false;
        };
        let top = 0;
        while (top < h && !lit(top)) top++;
        let bottom = h - 1;
        while (bottom > top && !lit(bottom)) bottom--;
        resolve(bottom > top ? w / (bottom - top + 1) : null);
      } catch {
        resolve(null);
      }
    };
    img.src = src;
  });
}

/**
 * The trailer's picture ratio, 16:9 until known: three stills from its start,
 * middle and end, the lightest one, as a dark scene looks like black bands.
 */
function useVideoRatio(id: string): number {
  const [ratio, setRatio] = React.useState(EMBED_W / EMBED_H);
  React.useEffect(() => {
    let current = true;
    let known = ratios.get(id);
    if (!known) {
      known = Promise.all(
        [1, 2, 3].map((n) => pictureRatio(`https://i.ytimg.com/vi/${id}/hq${n}.jpg`))
      ).then((found) => {
        const sure = found.filter((r): r is number => r !== null);
        return sure.length ? Math.min(...sure, 2.4) : EMBED_W / EMBED_H;
      });
      ratios.set(id, known);
    }
    void known.then((r) => current && setRatio(r));
    return () => {
      current = false;
    };
  }, [id]);
  return ratio;
}

function YouTubeTeaser({
  id,
  onPlaying,
  onEnded,
  onFailed,
  full,
}: { id: string } & TeaserEvents) {
  const frame = React.useRef<HTMLIFrameElement>(null);
  const box = React.useRef<HTMLDivElement>(null);
  const [scale, setScale] = React.useState(0);
  const ratio = useVideoRatio(id);
  const [muted] = useTeaserMuted();
  const [heard, setHeard] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [paused, setPaused] = React.useState(false);
  const volume = React.useRef(0);
  const latest = React.useRef({ onPlaying, onEnded, onFailed, muted, full });
  latest.current = { onPlaying, onEnded, onFailed, muted, full };
  // What the player last reported, and whether the teaser has been shown.
  const report = React.useRef({
    state: -1,
    time: 0,
    quality: '',
    shown: false,
    failed: false,
    captionsOff: false,
  });

  // Laid out at 1920×1080 whatever the box, then scaled down to cover it,
  // or full screen to show the whole picture. A cinema-wide trailer covers
  // it with its picture, leaving YouTube's black bands above and below out.
  React.useLayoutEffect(() => {
    const el = box.current;
    if (!el) return;
    const fit = () => {
      const w = el.clientWidth / EMBED_W;
      const h = el.clientHeight / EMBED_H;
      if (full) setScale(Math.min(w, h));
      else if (ratio > BANDED_FROM)
        setScale(
          Math.max(w, el.clientHeight / (EMBED_W / ratio)) * PICTURE_OVERSCAN
        );
      else setScale(Math.max(w, h) * EMBED_OVERSCAN);
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(el);
    return () => observer.disconnect();
  }, [full, ratio]);

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
        // Silent until it shows; the sound then rises (below).
        command('mute');
        command('setPlaybackQuality', ['hd1080']);
      }
      // Captions load with playback, so they are taken off once it starts.
      if (state === 1 && !now.captionsOff) {
        now.captionsOff = true;
        command('unloadModule', ['captions']);
        command('unloadModule', ['cc']);
        command('setOption', ['captions', 'track', {}]);
      }
      if (data.event === 'onError') latest.current.onFailed();
      // A trailer that exists only below 720p gives way to the next one.
      const levels = info.availableQualityLevels ?? [];
      if (
        !now.shown &&
        !now.failed &&
        !latest.current.full &&
        levels.length &&
        !levels.some((level) => HD_QUALITIES.has(level))
      ) {
        now.failed = true;
        latest.current.onFailed();
      }
      // Full screen was asked for: it shows as soon as it plays.
      if (
        !now.shown &&
        now.state === 1 &&
        (latest.current.full ||
          (now.time >= CHROME_HIDDEN_S && HD_QUALITIES.has(now.quality)))
      ) {
        now.shown = true;
        setRevealed(true);
        latest.current.onPlaying();
      }
      if (state === 1) setPaused(false);
      if (state === 2) setPaused(true);
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

  // Sound only once the teaser shows (or full screen), rising rather than all at once.
  const audible = heard && (full || (revealed && !muted));
  React.useEffect(() => {
    if (!audible) {
      if (heard) command('mute');
      volume.current = 0;
      return;
    }
    command('unMute');
    return fadeIn(volume.current, full ? FULL_FADE_IN_MS : FADE_IN_MS, (v) => {
      volume.current = v;
      command('setVolume', [Math.round(v)]);
    });
  }, [audible, full, heard, command]);

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
      {full && (
        <FullControls
          paused={paused}
          onToggle={() => command(paused ? 'playVideo' : 'pauseVideo')}
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
  full,
}: { url: string } & TeaserEvents) {
  const video = React.useRef<HTMLVideoElement>(null);
  const [muted] = useTeaserMuted();
  const [revealed, setRevealed] = React.useState(false);
  const [paused, setPaused] = React.useState(false);
  const audible = full || (revealed && !muted);
  React.useEffect(() => {
    const el = video.current;
    if (!el) return;
    if (!audible) {
      el.muted = true;
      el.volume = 0;
      return;
    }
    el.muted = false;
    return fadeIn(el.volume * 100, full ? FULL_FADE_IN_MS : FADE_IN_MS, (v) => {
      el.volume = v / 100;
    });
  }, [audible, full]);
  return (
    <>
      <video
        ref={video}
        data-ui="teaser-video"
        src={url}
        muted
        autoPlay
        playsInline
        preload="auto"
        disablePictureInPicture
        onPlaying={() => {
          setRevealed(true);
          setPaused(false);
          onPlaying();
        }}
        onPause={() => setPaused(true)}
        onEnded={onEnded}
        onError={onFailed}
        className={
          full
            ? 'absolute inset-0 h-full w-full object-contain'
            : cn(COVER, 'object-cover')
        }
      />
      {full && (
        <FullControls
          paused={paused}
          onToggle={() => {
            const el = video.current;
            if (el) void (el.paused ? el.play() : el.pause());
          }}
        />
      )}
    </>
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
