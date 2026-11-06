#!/usr/bin/env python3
"""Démonstration locale : sources fictives, aucun réseau, aucune lecture."""
from dataclasses import dataclass
from typing import FrozenSet, Iterable, Optional
import argparse

@dataclass(frozen=True)
class Source:
    name: str
    title_id: str
    season: Optional[int]
    episode: Optional[int]
    provenance: str  # public_verified, private, unknown
    transport: str
    codec: str
    resolution: int
    hdr: str
    languages: FrozenSet[str]
    cached: Optional[bool]

@dataclass(frozen=True)
class Device:
    codecs: FrozenSet[str]
    max_resolution: int
    hdr_formats: FrozenSet[str]

@dataclass(frozen=True)
class Policy:
    title_id: str
    season: Optional[int]
    episode: Optional[int]
    language: str
    enabled: bool = False
    max_attempts: int = 3


def select(sources: Iterable[Source], device: Device, policy: Policy) -> list[Source]:
    """Fail closed: origine privée/inconnue et métadonnées essentielles absentes refusées."""
    if not policy.enabled:
        return []
    eligible = []
    for s in sources:
        if s.provenance != 'public_verified' or s.transport != 'https':
            continue
        if (s.title_id, s.season, s.episode) != (policy.title_id, policy.season, policy.episode):
            continue
        if s.codec not in device.codecs or s.resolution <= 0 or s.resolution > device.max_resolution:
            continue
        if s.hdr not in device.hdr_formats or policy.language not in s.languages:
            continue
        eligible.append(s)
    # Démo : 1080p est préféré à 4K ; en vrai les poids dépendent du profil/appareil.
    return sorted(eligible, key=lambda s: (s.cached is not True, abs(s.resolution - 1080), s.name))


def simulate_attempts(candidates: Iterable[Source], failure_names: set[str], limit: int) -> list[str]:
    """Simule des échecs sans ouvrir de lien ; n'essaie jamais deux fois une source."""
    attempted, seen = [], set()
    for source in candidates:
        if len(attempted) >= max(0, min(limit, 3)):
            break
        if source.name in seen:
            continue
        seen.add(source.name)
        attempted.append(source.name)
        if source.name not in failure_names:
            break
    return attempted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enabled', action='store_true', help='active la simulation')
    args = parser.parse_args()
    d = Device(frozenset({'h264', 'h265'}), 2160, frozenset({'SDR', 'HDR10'}))
    p = Policy('demo-film', None, None, 'fr', enabled=args.enabled)
    items = [
        Source('direct-1080', 'demo-film', None, None, 'public_verified', 'https', 'h264', 1080, 'SDR', frozenset({'fr'}), True),
        Source('direct-4k', 'demo-film', None, None, 'public_verified', 'https', 'h265', 2160, 'HDR10', frozenset({'fr'}), True),
        Source('tracker-prive', 'demo-film', None, None, 'private', 'https', 'h264', 1080, 'SDR', frozenset({'fr'}), True),
        Source('origine-inconnue', 'demo-film', None, None, 'unknown', 'https', 'h264', 1080, 'SDR', frozenset({'fr'}), True),
    ]
    ranked = select(items, d, p)
    print('Mode :', 'simulation activée' if args.enabled else 'désactivé')
    print('Sources admissibles :', ', '.join(s.name for s in ranked) or 'aucune')
    print('Essais simulés :', ', '.join(simulate_attempts(ranked, {'direct-1080'}, p.max_attempts)) or 'aucun')
    print('Aucune connexion ou lecture effectuée.')

if __name__ == '__main__':
    main()
