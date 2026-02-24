# VPN App

A lightweight Python VPN app that helps you manage VPN profiles from the command line.

## Features

- Add, list, and remove VPN connection profiles.
- Generate OpenVPN client config snippets (`.ovpn`) from saved profiles.
- Dry-run connect/disconnect commands for safe local workflows.

## Usage

```bash
python vpn_app.py add work vpn.company.com --protocol udp --port 1194
python vpn_app.py list
python vpn_app.py config work work.ovpn
python vpn_app.py connect work
python vpn_app.py disconnect
```

By default, profiles are saved to:

- `~/.vpn_app_profiles.json`

To use a custom location for profile storage:

```bash
VPN_APP_STORE=./profiles.json python vpn_app.py list
```

## Run tests

```bash
pytest -q
```
