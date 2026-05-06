# homeassistantDesk

`homeassistantDesk` is a desktop companion for Home Assistant on Windows and Linux.  
It brings a configurable dashboard, tray integration, fast entity access, notifications, and multilingual UI support into a single desktop app.

## Highlights

- Desktop dashboard with drag-and-drop layout
- Real-time Home Assistant sync over WebSocket
- System tray integration
- Entity shortcuts and quick actions
- Camera, weather, climate, media, printer, mower, vacuum, and sensor support
- Multilingual UI foundation with English, Simplified Chinese, and Russian
- Windows executable build and Linux AppImage build workflow

## Supported Languages

- English
- Simplified Chinese
- Russian

Language is stored in `appearance.language` and is handled through [core/i18n.py](core/i18n.py).

## Supported Entity Types

- Automation
- Camera
- Climate
- Curtain / Cover
- Fan
- Light / Switch
- Lawn Mower
- Media Player
- Scene
- Script
- Sensor
- Sun
- Vacuum
- Weather
- 3D Printer tile

## Run From Source

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
python main.py
```

## Build

### Windows

Build the executable:

```bash
python build_exe.py
```

Expected output:

- `dist/homeassistantDesk.exe`

To build the Windows installer, compile [setup.iss](setup.iss) with Inno Setup.

### Linux

Build the AppImage:

```bash
python3 build_linux.py
```

## Repository Layout

- `core/`: config, versioning, branding, i18n, Home Assistant client helpers
- `services/`: notifications, mobile app registration, shortcuts, IPC, location
- `ui/`: dashboard, settings, widgets, overlays, themes
- `build_exe.py`: Windows packaging
- `build_linux.py`: Linux packaging

## Branding

This fork is branded as `homeassistantDesk`.

Key branding constants live in [core/branding.py](core/branding.py).

## Release Notes

Current release notes are tracked in [RELEASE_NOTES.md](RELEASE_NOTES.md).

## License

This project remains under the MIT License. See [LICENSE](LICENSE).
