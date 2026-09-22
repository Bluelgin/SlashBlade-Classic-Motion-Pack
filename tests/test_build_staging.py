from pathlib import Path
import tempfile
import unittest

from scripts.build_pack import prepare_pack


class BuildStagingTests(unittest.TestCase):
    def test_prepare_pack_keeps_only_static_mcmeta(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / 'pack'
            pack.mkdir()
            mcmeta = b'{"pack":{"pack_format":15,"description":"test"}}'
            (pack / 'pack.mcmeta').write_bytes(mcmeta)
            (pack / 'stale.txt').write_text('old build')
            nested = pack / 'assets/slashblade/combostate'
            nested.mkdir(parents=True)
            (nested / 'motion.vmd').write_bytes(b'stale')

            result = prepare_pack(pack)

            self.assertEqual(result, pack)
            self.assertEqual((pack / 'pack.mcmeta').read_bytes(), mcmeta)
            self.assertEqual(
                {p.relative_to(pack).as_posix() for p in pack.rglob('*') if p.is_file()},
                {'pack.mcmeta'},
            )

    def test_prepare_pack_fails_without_static_mcmeta(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / 'pack'
            pack.mkdir()
            (pack / 'stale.txt').write_text('old build')
            with self.assertRaises(FileNotFoundError):
                prepare_pack(pack)


if __name__ == '__main__':
    unittest.main()
