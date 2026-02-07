# Texture Mixer
Texture Mixer is a layer-based texturing toolset. It automates the creation of complex node groups to allow for multi-channel painting and mask management.

🚀 Features
- Non-Destructive Layer Stack: Manage your PBR materials using layers instead of messy node webs.
- Single-Channel Painting: Paint Base Color, Metallic, Roughness, and more individually.
- Multi-Channel Painting: Paint Base Color, Metallic, Roughness, and more simultaneously.
- Dynamic Masking: Stack paintable and procedural masks on any layer.
- Export Pipeline: Bake your layers into production-ready texture sets with channel packing.

🛠 Installation
- Download the repository as a .zip file.
- In Blender 5.0+, go to Edit > Preferences > Get Extensions.
- Click the arrow in the top right and select Install from Disk...
- Select the downloaded .zip and enable Texture Mixer.

📖 Usage Overview
- Open N-Panel: After installation, find the Texture Mixer tab in the 3D View Sidebar (N).
- Initialize: Create a new Layer Manager for your active/selected mesh (Warning, will remove any attached material).
- Add Layers: Choose between Paint Layers (for manual texturing) or Fill Layers (for procedural/texture inputs).
- Painting: Enter the custom Multi-Channel/Default Blender's single channel paint mode to affect multiple/single PBR slot(s) in a single stroke.
- Baking: Use the Export tab to flatten your layers into final maps.
