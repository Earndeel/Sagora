import importlib.util
import pathlib
import sys
import unittest

path = pathlib.Path(__file__).with_name('stremio-selection-demo.py')
spec = importlib.util.spec_from_file_location('selection_demo', path)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

class TestSelection(unittest.TestCase):
    def setUp(self):
        self.d = m.Device(frozenset({'h264'}), 1080, frozenset({'SDR'}))
        self.p = m.Policy('show', 1, 2, 'fr', enabled=True)
    def src(self, name, **kw):
        base = dict(name=name,title_id='show',season=1,episode=2,provenance='public_verified',transport='https',codec='h264',resolution=1080,hdr='SDR',languages=frozenset({'fr'}),cached=True)
        return m.Source(**(base | kw))
    def test_strict_exclusions(self):
        items = [self.src('correct'), self.src('prive',provenance='private'), self.src('inconnu',provenance='unknown'), self.src('mauvais_episode',episode=3), self.src('codec',codec='av1'), self.src('langue',languages=frozenset({'en'})), self.src('hdr',hdr='HDR10'), self.src('torrent',transport='torrent')]
        self.assertEqual([s.name for s in m.select(items,self.d,self.p)], ['correct'])
    def test_disabled_by_default(self):
        self.assertEqual(m.select([self.src('ok')],self.d,m.Policy('show',1,2,'fr')), [])
    def test_prefer_cache_and_1080(self):
        source = [self.src('b',resolution=720),self.src('a',resolution=1080),self.src('z',cached=False)]
        self.assertEqual([s.name for s in m.select(source,self.d,self.p)], ['a','b','z'])
    def test_fallback_bounded_and_no_repeat(self):
        candidates=[self.src('a'),self.src('a'),self.src('b'),self.src('c'),self.src('d')]
        self.assertEqual(m.simulate_attempts(candidates,{'a','b','c','d'},99),['a','b','c'])
        self.assertEqual(m.simulate_attempts(candidates,{'a'},3),['a','b'])
    def test_unknown_format_rejected(self):
        self.assertEqual(m.select([self.src('missing',codec='unknown')],self.d,self.p),[])

if __name__ == '__main__':
    unittest.main()
