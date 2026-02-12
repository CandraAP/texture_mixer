# Changelog
---

## [0.1.1-alpha] - 2026-02-12
### Added
- None (Initial Release).

### Fixed
- None (Initial Release).

### Changed
- None (Initial Release).

### Removed
- Developer debugging tool.

### Known Issues
- Layer Performance: Stacking a high number of layers (typically 8+) will significantly degrade viewport performance. This is due to the nature of "live" shader node composition. A completely different workflow with significantly better performance and memory usage is currently in development.
- Viewport Rendering: Viewport textures may occasionally appear black. Frequent saving of the .blend file is recommended to ensure data is packed and refreshed.
- Multi-Channel Painting: 'Smear' and 'Mask' brushes are currently unsupported in Multi-Channel mode.
- Multi-Channel Painting: Painting is currently limited to Solid Colors; texture-based sampling and stencils are planned for a future update.
- Multi-Channel Painting: Pressure-sensitive toggles for Size and Strength are disabled to prevent stability issues during the Alpha phase.
- Multi-Channel Painting: Native Blender 'Stroke' settings are only partially supported due to custom parameter overrides.
- Multi-Channel Painting: Native Blender Undo is not supported. A dedicated, robust undo system is a high-priority feature for the next update.

---

## [0.1.0-alpha] - 2026-02-07
### Added
- None (Initial Release).

### Fixed
- None (Initial Release).

### Changed
- None (Initial Release).

### Removed
- None (Initial Release).

### Known Issues
- Layer Performance: Stacking a high number of layers (typically 8+) will significantly degrade viewport performance. This is due to the nature of "live" shader node composition. A completely different workflow with significantly better performance and memory usage is currently in development.
- Viewport Rendering: Viewport textures may occasionally appear black. Frequent saving of the .blend file is recommended to ensure data is packed and refreshed.
- Multi-Channel Painting: 'Smear' and 'Mask' brushes are currently unsupported in Multi-Channel mode.
- Multi-Channel Painting: Painting is currently limited to Solid Colors; texture-based sampling and stencils are planned for a future update.
- Multi-Channel Painting: Pressure-sensitive toggles for Size and Strength are disabled to prevent stability issues during the Alpha phase.
- Multi-Channel Painting: Native Blender 'Stroke' settings are only partially supported due to custom parameter overrides.
- Multi-Channel Painting: Native Blender Undo is not supported. A dedicated, robust undo system is a high-priority feature for the next update.

---