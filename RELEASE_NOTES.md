# Release Notes

## 1.5.1

Release date: 2026-05-06

### Added

- Multilingual UI foundation for English, Simplified Chinese, and Russian
- Central branding constants in `core/branding.py`
- New release-ready `homeassistantDesk` application naming and packaging flow
- Formalized project README and release notes

### Changed

- Unified repository, runtime, and packaging branding as `homeassistantDesk`
- Updated Windows executable naming, installer naming, and Linux packaging naming
- Updated tray text, welcome text, notifications, settings text, and editor text for unified branding
- Updated build metadata version to `1.5.1`
- Hardened the Windows PyInstaller build flow to avoid checksum and timestamp rewrite failures on some systems

### Verified

- Python source compilation via `python -m py_compile`
- Local dependency installation from `requirements.txt`
- Windows executable build via `python build_exe.py`

### Output

- `dist/homeassistantDesk.exe`
