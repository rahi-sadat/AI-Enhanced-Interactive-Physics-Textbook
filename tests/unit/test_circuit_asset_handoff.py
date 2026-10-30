"""Asset handoff integrity checks with tiny local bytes and no network or model loading."""
import zipfile

import pytest

from scripts import circuit_assets


@pytest.fixture
def assets(tmp_path, monkeypatch):
    root = tmp_path/'author'
    root.mkdir()
    monkeypatch.setattr(circuit_assets, 'ROOT', root)
    monkeypatch.setattr(circuit_assets, 'MANIFEST', root/'requirements/circuit-assets-v1.json')
    for i, name in enumerate(circuit_assets.FILES):
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes([i+1])*40)
    circuit_assets.main(['--write-manifest'])
    archive = tmp_path/'assets.zip'
    circuit_assets.main(['--export', str(archive)])
    target = tmp_path/'friend'
    target.mkdir()
    manifest = target/'requirements/circuit-assets-v1.json'
    manifest.parent.mkdir()
    manifest.write_bytes(circuit_assets.MANIFEST.read_bytes())
    monkeypatch.setattr(circuit_assets, 'ROOT', target)
    monkeypatch.setattr(circuit_assets, 'MANIFEST', manifest)
    return root, target, archive


def test_asset_roundtrip_and_idempotent_restore(assets):
    author, friend, archive = assets
    assert circuit_assets.main(['--restore', str(archive)]) == 0
    for name in circuit_assets.FILES:
        assert (friend/name).read_bytes() == (author/name).read_bytes()
    assert circuit_assets.main(['--restore', str(archive)]) == 0


def test_existing_different_weights_are_preserved_before_any_writes(assets):
    _, friend, archive = assets
    protected = friend/circuit_assets.FILES[-1]
    protected.parent.mkdir(parents=True)
    protected.write_bytes(b'existing work')
    with pytest.raises(ValueError, match='protected'):
        circuit_assets.main(['--restore', str(archive)])
    assert protected.read_bytes() == b'existing work'
    assert not (friend/circuit_assets.FILES[0]).exists()


def test_unexpected_archive_paths_are_rejected(assets, tmp_path):
    _, friend, archive = assets
    malicious = tmp_path/'bad.zip'
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(malicious, 'w') as target:
        for name in source.namelist():
            target.writestr(name, source.read(name))
        target.writestr('../outside.pt', b'no')
    with pytest.raises(ValueError, match='unexpected'):
        circuit_assets.main(['--restore', str(malicious)])
    assert not (friend/circuit_assets.FILES[0]).exists()
