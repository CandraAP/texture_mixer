# Changelog

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
- Layer Performance: Stacking a high number of layers (typically 8+) will significantly degrade viewport performance. This is due to the nature of "live" shader node composition.
- Viewport Rendering: Viewport textures may occasionally appear black. Frequent saving of the .blend file is recommended.
- Multi Channels Painting: 'Smear' and 'Mask' brushes are currently unsupported in Multi-Channel mode. 
- Multi Channels Painting: Multi-Channel painting is currently limited to Solid Colors, texture-based sampling and stencils are planned for a future update.
- Multi Channels Painting: Currently pressure-sensitive toggles for Size and Strength are disabled to prevent stability issues.
- Multi Channels Painting: The native 'Stroke' settings in the Texture Painting panel are only partially supported due to the addon's custom parameter overrides.
- Multi Channels Painting: Native Blender Undo is currently not supported for Multi-Channel painting. A dedicated, robust undo system is a high-priority feature for the next update.

---