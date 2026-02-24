from pathlib import Path

from vpn_app import VPNApp, VPNProfile


def test_add_list_remove(tmp_path: Path):
    store = tmp_path / "profiles.json"
    app = VPNApp(store)

    app.add_profile(VPNProfile(name="work", server="vpn.example.com"))
    profiles = app.list_profiles()

    assert "work" in profiles
    assert profiles["work"].server == "vpn.example.com"

    assert app.remove_profile("work") is True
    assert app.remove_profile("work") is False


def test_generate_openvpn_config(tmp_path: Path):
    store = tmp_path / "profiles.json"
    out = tmp_path / "client.ovpn"
    app = VPNApp(store)
    app.add_profile(VPNProfile(name="lab", server="10.0.0.5", protocol="tcp", port=443))

    generated = app.generate_openvpn_config("lab", out)

    assert generated == out
    text = out.read_text()
    assert "proto tcp" in text
    assert "remote 10.0.0.5 443" in text
