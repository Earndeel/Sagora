import React from 'react';

/**
 * Teasers: a title's trailer playing muted in place of its artwork, as in
 * the hero and in a card's preview. Only one plays at a time: the highest
 * priority holds the turn, the latest among equals, and gives it back when
 * it lets go, so a card's preview takes over from the hero, which cannot take
 * it back by moving to its next title, and hands back on closing.
 */

type Listener = () => void;

const claims: { key: string; priority: number }[] = [];
const listeners = new Set<Listener>();
let muted = true;
let sounding: string | null = null;

const emit = () => listeners.forEach((l) => l());
const subscribe = (l: Listener) => {
  listeners.add(l);
  return () => void listeners.delete(l);
};

function holder(): string | undefined {
  let top: (typeof claims)[number] | undefined;
  for (const claim of claims)
    if (!top || claim.priority >= top.priority) top = claim;
  return top?.key;
}

/** True while `key` holds the only teaser's turn; asks for it while `wants`. */
export function useTeaserTurn(
  key: string,
  wants: boolean,
  priority = 0
): boolean {
  React.useEffect(() => {
    if (!wants) return;
    const claim = { key, priority };
    claims.push(claim);
    emit();
    return () => {
      claims.splice(claims.indexOf(claim), 1);
      emit();
    };
  }, [key, wants, priority]);
  return React.useSyncExternalStore(subscribe, () => wants && holder() === key);
}

export function useTeaserMuted(): [boolean, (muted: boolean) => void] {
  const value = React.useSyncExternalStore(subscribe, () => muted);
  return [
    value,
    React.useCallback((next: boolean) => {
      muted = next;
      emit();
    }, []),
  ];
}

/** The teaser now playing, which the sound buttons act on. */
export function setSounding(key: string | null, playing: boolean) {
  if (playing) sounding = key;
  else if (sounding === key) sounding = null;
  else return;
  emit();
}

export const useSounding = () =>
  React.useSyncExternalStore(subscribe, () => sounding);

/* The element of each mounted teaser, so a trailer button can take it full screen. */
const screens = new Map<string, HTMLElement>();

export function registerTeaserScreen(key: string, el: HTMLElement | null) {
  if (el) screens.set(key, el);
  else screens.delete(key);
}

/**
 * Takes `key`'s teaser full screen, where it carries on with its sound, even
 * one still getting ready out of sight. Called from the click itself, which
 * the browser requires; false when there is none or the device cannot.
 */
export function expandTeaser(key: string): boolean {
  const el = screens.get(key);
  if (!el || typeof el.requestFullscreen !== 'function') return false;
  el.requestFullscreen().catch(() => undefined);
  return true;
}

/** What the device asks for: less motion and less data mean no teasers. */
export function teasersAllowed(): boolean {
  if (typeof matchMedia === 'function') {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
  }
  const connection = (
    navigator as Navigator & {
      connection?: { saveData?: boolean; effectiveType?: string };
    }
  ).connection;
  if (connection?.saveData) return false;
  if (connection?.effectiveType && /(^|-)2g$/.test(connection.effectiveType))
    return false;
  return true;
}
