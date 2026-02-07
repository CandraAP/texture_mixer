# Texture Mixer

<p align="left">
  <a href="https://www.patreon.com/c/candraap"><img src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white" /></a>
  <a href="https://ko-fi.com/candraap"><img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" /></a>
</p>

Texture Mixer is a layer-based texturing toolset for Blender. It automates the creation of complex node groups to allow for multi-channel painting and mask management.

> [!WARNING]
> **Experimental Status:** This addon is currently in active development (Alpha). All features, node structures, and workflows are subject to change in future updates. Please use with caution on production files and always keep backups!

---

🚀 ## Features
- **Non-Destructive Layer Stack:** Manage your PBR materials using layers instead of messy node webs.
- **Single-Channel Painting:** Paint Base Color, Metallic, Roughness, and more individually.
- **Multi-Channel Painting:** Paint Base Color, Metallic, Roughness, and more simultaneously.
- **Dynamic Masking:** Stack paintable and procedural masks on any layer.
- **Export Pipeline:** Bake your layers into production-ready texture sets with channel packing.

🛠 ## Installation
- Download the repository as a `.zip` file.
- In **Blender 5.0+**, go to `Edit > Preferences > Get Extensions`.
- Click the arrow in the top right and select `Install from Disk...`
- Select the downloaded `.zip` and enable **Texture Mixer**.

📖 ## Usage Overview
- **Open N-Panel:** After installation, find the Texture Mixer tab in the 3D View Sidebar (N).
- **Initialize:** Create a new Layer Manager for your active/selected mesh. *(Note: This will replace the current material with the TM structure).*
- **Add Layers:** Choose between **Paint Layers** (manual painting) or **Fill Layers** (procedural/texture inputs).
- **Painting:** Enter the custom Multi-Channel mode to affect multiple PBR slots in a single stroke.
- **Baking:** Use the Export tab to flatten your layers into final maps.

---

### 🧡 Support the Development
If you find this tool useful and want to support its development, consider becoming a patron or buying me a coffee!

[![Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/c/candraap) 
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/candraap)

---

# 📺 Feature Demos

| Feature | Preview |
| :--- | :--- |
| **Initialization** <br> Setup the layer manager for your mesh. | <video src="https://github.com/user-attachments/assets/58f73bd1-b1ab-4397-bd32-ceeeec39ea09" width="400" autoplay loop muted playsinline></video> |
| **Channel Management** <br> Quickly toggle PBR channels. | <video src="https://github.com/user-attachments/assets/23ce6535-9b23-4907-a24c-15f463ac95bf" width="400" autoplay loop muted playsinline></video> |
| **Fill Layers** <br> Create and configure procedural layers. | <video src="https://github.com/user-attachments/assets/dbba0f20-f746-48fc-8ece-ba9688573ac2" width="400" autoplay loop muted playsinline></video> <br> <video src="https://github.com/user-attachments/assets/f00e3041-fb9b-4d1d-8939-6ee2427bca7a" width="400" autoplay loop muted playsinline></video> |
| **Masking System** <br> Create and setup dynamic masks. | <video src="https://github.com/user-attachments/assets/2e75593a-652a-46fd-9ca3-b75c24144766" width="400" autoplay loop muted playsinline></video> |
| **Multi-Channel Paint** <br> Paint multiple PBR slots at once. | <video src="https://github.com/user-attachments/assets/cedf4d05-931a-4c58-9dfd-ac505ed7b7ed" width="400" autoplay loop muted playsinline></video> |
| **Baking & Export** <br> Flatten layers to texture maps. | <video src="https://github.com/user-attachments/assets/2353e849-2350-4ff0-99b3-df68511bb366" width="400" autoplay loop muted playsinline></video> |
| **Advanced Features** <br> Dynamic resolution & Multi-profiles. | <video src="https://github.com/user-attachments/assets/0cec4887-2c06-46fe-a1b5-f5bfe6604c6b" width="400" autoplay loop muted playsinline></video> <br> <video src="https://github.com/user-attachments/assets/6e501042-42a3-4756-90eb-845e9dbffcce" width="400" autoplay loop muted playsinline></video> |
