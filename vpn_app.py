#!/usr/bin/env python3
"""A lightweight terminal VPN app for managing VPN profiles and sessions.

This app does not implement a VPN protocol itself. Instead, it provides:
- local profile management (saved to JSON)
- OpenVPN config file generation
- safe shell command stubs for connect/disconnect actions
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE = Path.home() / ".vpn_app_profiles.json"


@dataclass
class VPNProfile:
    name: str
    server: str
    protocol: str = "udp"
    port: int = 1194
    username: Optional[str] = None


class VPNApp:
    def __init__(self, store_path: Path = DEFAULT_STORE) -> None:
        self.store_path = store_path
        self._profiles: Dict[str, VPNProfile] = {}
        self._load()

    def _load(self) -> None:
        if not self.store_path.exists():
            self._profiles = {}
            return

        raw = json.loads(self.store_path.read_text())
        self._profiles = {
            key: VPNProfile(**value)
            for key, value in raw.items()
        }

    def _save(self) -> None:
        payload = {name: asdict(profile) for name, profile in self._profiles.items()}
        self.store_path.write_text(json.dumps(payload, indent=2))

    def add_profile(self, profile: VPNProfile) -> None:
        self._profiles[profile.name] = profile
        self._save()

    def remove_profile(self, name: str) -> bool:
        existed = name in self._profiles
        if existed:
            del self._profiles[name]
            self._save()
        return existed

    def list_profiles(self) -> Dict[str, VPNProfile]:
        return dict(self._profiles)

    def get_profile(self, name: str) -> VPNProfile:
        if name not in self._profiles:
            raise KeyError(f"No profile named '{name}'")
        return self._profiles[name]

    def generate_openvpn_config(self, name: str, output_file: Path) -> Path:
        profile = self.get_profile(name)
        config = (
            "client\n"
            "dev tun\n"
            f"proto {profile.protocol}\n"
            f"remote {profile.server} {profile.port}\n"
            "resolv-retry infinite\n"
            "nobind\n"
            "persist-key\n"
            "persist-tun\n"
            "remote-cert-tls server\n"
            "cipher AES-256-GCM\n"
            "verb 3\n"
        )
        output_file.write_text(config)
        return output_file

    def connect(self, name: str, dry_run: bool = True) -> str:
        profile = self.get_profile(name)
        command = [
            "echo",
            f"Connecting to {profile.server}:{profile.port} via {profile.protocol}"
        ]
        if dry_run:
            return " ".join(command)
        subprocess.run(command, check=True)
        return "Connected"

    def disconnect(self, dry_run: bool = True) -> str:
        command = ["echo", "Disconnecting VPN session"]
        if dry_run:
            return " ".join(command)
        subprocess.run(command, check=True)
        return "Disconnected"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple VPN profile manager")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add or update a profile")
    add.add_argument("name")
    add.add_argument("server")
    add.add_argument("--protocol", default="udp", choices=["udp", "tcp"])
    add.add_argument("--port", type=int, default=1194)
    add.add_argument("--username", default=None)

    rm = sub.add_parser("remove", help="Remove a profile")
    rm.add_argument("name")

    sub.add_parser("list", help="List profiles")

    show = sub.add_parser("config", help="Generate an OpenVPN config")
    show.add_argument("name")
    show.add_argument("output", type=Path)

    conn = sub.add_parser("connect", help="Connect to a profile")
    conn.add_argument("name")
    conn.add_argument("--execute", action="store_true", help="Run instead of dry-run")

    disc = sub.add_parser("disconnect", help="Disconnect session")
    disc.add_argument("--execute", action="store_true", help="Run instead of dry-run")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    custom_store = os.environ.get("VPN_APP_STORE")
    app = VPNApp(Path(custom_store) if custom_store else DEFAULT_STORE)

    if args.command == "add":
        app.add_profile(
            VPNProfile(
                name=args.name,
                server=args.server,
                protocol=args.protocol,
                port=args.port,
                username=args.username,
            )
        )
        print(f"Saved profile '{args.name}'")

    elif args.command == "remove":
        removed = app.remove_profile(args.name)
        print(f"Removed '{args.name}'" if removed else f"Profile '{args.name}' not found")

    elif args.command == "list":
        profiles = app.list_profiles()
        if not profiles:
            print("No VPN profiles configured yet.")
        else:
            for name, profile in profiles.items():
                print(f"- {name}: {profile.server}:{profile.port}/{profile.protocol}")

    elif args.command == "config":
        path = app.generate_openvpn_config(args.name, args.output)
        print(f"Wrote OpenVPN config to {path}")

    elif args.command == "connect":
        print(app.connect(args.name, dry_run=not args.execute))

    elif args.command == "disconnect":
        print(app.disconnect(dry_run=not args.execute))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
