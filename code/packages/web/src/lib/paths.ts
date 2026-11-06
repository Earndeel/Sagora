import type { ServerInfo } from './server-info';
import type { BaseItemDto } from './types';
import { currentHost } from './hosts';

/*
 * The app routes on the URL hash, like jellyfin-web, so it works under any
 * mount of the API. Sagora: on the website, served at the root of its own
 * address, pages have real paths instead (sagora.walter-ai.cloud/item/…). The
 * apps load the interface from a file, and the server's /jellyfin/web page can
 * sit under any mount, so they keep the hash.
 */
const WEB_MOUNT = /\/web(\/(index\.html)?)?$/i;

/** The pages of the app, which the site serves at their own address. */
export const APP_PATH =
  /^\/(history|downloads|favourites|calendar|settings|search|discover|item|person|play)?(\/|\?|$)/;

let routingOnPaths: boolean | undefined;

/** True on the website at the root of its address; decided once, at load. */
export function pathRouting(): boolean {
  return (routingOnPaths ??=
    currentHost().name === 'browser' &&
    /^https?:$/.test(window.location.protocol) &&
    !WEB_MOUNT.test(window.location.pathname));
}

/** The in-app path on screen, as `/play/x?source=…`. */
export function currentPath(): string {
  return pathRouting()
    ? window.location.pathname + window.location.search
    : window.location.hash.slice(1) || '/';
}

export const to = {
  home: '/',
  history: '/history',
  downloads: '/downloads',
  calendar: (month?: string) =>
    month ? `/calendar?month=${month}` : '/calendar',
  favourites: (kind?: string) =>
    kind ? `/favourites?kind=${kind}` : '/favourites',
  settings: (tab?: string) => (tab ? `/settings?tab=${tab}` : '/settings'),
  search: (term?: string) =>
    term ? `/search?q=${encodeURIComponent(term)}` : '/search',
  discover: (
    viewId?: string,
    opts: { genre?: string; kind?: string } = {}
  ): string => {
    if (!viewId) return '/discover';
    const params = new URLSearchParams();
    if (opts.genre) params.set('genre', opts.genre);
    if (opts.kind) params.set('kind', opts.kind);
    const query = params.toString();
    return `/discover/${viewId}${query ? `?${query}` : ''}`;
  },
  item: (itemId: string) => `/item/${itemId}`,
  person: (personId: string) => `/person/${personId}`,
  /** With `playlist`, it plays on through that playlist. */
  play: (itemId: string, sourceId: string, startMs = 0, playlist?: string) =>
    `/play/${itemId}?source=${sourceId}${startMs ? `&start=${Math.round(startMs)}` : ''}${playlist ? `&playlist=${playlist}` : ''}`,
  trailer: (itemId: string, index = 0) =>
    `/play/trailer/${itemId}${index ? `?trailer=${index}` : ''}`,
};

/** An episode has no page of its own; it opens its show at its season. */
export function itemPath(
  item: Pick<BaseItemDto, 'Id' | 'Type' | 'SeriesId' | 'SeasonId'>
): string {
  if (item.Type === 'Episode' && item.SeriesId) {
    const params = new URLSearchParams();
    if (item.SeasonId) params.set('season', item.SeasonId);
    if (item.Id) params.set('episode', item.Id);
    return `${to.item(item.SeriesId)}?${params}`;
  }
  return to.item(item.Id!);
}

/** The item's page, opening on its version list. */
export function versionsPath(
  item: Pick<BaseItemDto, 'Id' | 'Type' | 'SeriesId' | 'SeasonId'>,
  playlist?: string
): string {
  const path = itemPath(item);
  return `${path}${path.includes('?') ? '&' : '?'}pick=${item.Id}${playlist ? `&playlist=${playlist}` : ''}`;
}

export const href = (path: string) => (pathRouting() ? path : `#${path}`);

/** The in-app path an `href` of this app names, or null for any other link. */
export function appPathOf(link: string): string | null {
  if (link.startsWith('#/')) return link.slice(1);
  return pathRouting() && APP_PATH.test(link) ? link : null;
}

/** The server's configuration page, when it has one. */
/** The server's own when it names one; the hosting server's page otherwise. */
export function configureUrl(base: string, info: ServerInfo): string | null {
  const url =
    info.configureUrl ?? (__STANDALONE__ ? null : '/stremio/configure');
  return url ? new URL(url, base).href : null;
}

interface NavigateOptions {
  replace?: boolean;
  keepScroll?: boolean;
}

type Push = (path: string, opts: NavigateOptions) => void;
type Restart = (path: string) => Promise<void>;

const open = (path: string) => {
  if (pathRouting()) window.location.assign(path);
  else window.location.hash = path;
};

let push: Push = (path) => open(path);

let restart: Restart = async (path) => open(path);

export function setNavigator(fn: Push, fresh: Restart): void {
  push = fn;
  restart = fresh;
}

export function navigate(path: string, opts: NavigateOptions = {}) {
  push(path, opts);
}

/** `path` as the history's first entry, so back can't reach the pages before it. */
export function startOver(path: string): Promise<void> {
  return restart(path);
}

/** Back where the user came from, or to `fallback` on a page opened directly. */
export function goBack(fallback: string): void {
  if (window.history.length > 1) window.history.back();
  else navigate(fallback, { replace: true });
}

/** As `goBack`, but to `fallback` where back would leave the app, as after a link from another site. */
export function goBackInApp(fallback: string): void {
  if ((window.history.state?.__TSR_index ?? 0) > 0) window.history.back();
  else navigate(fallback, { replace: true });
}
