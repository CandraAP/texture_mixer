<p align="center">
  <img width="35%" height="35%" src="https://github.com/user-attachments/assets/09d68518-2e1b-4b98-9777-4ec821684d2a" />
</p>

# <p align="center">Texture Mixer</p>

<p align="center">
  <a href="https://www.patreon.com/c/candraap"><img src="https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white" /></a>
  <a href="https://ko-fi.com/candraap"><img src="https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white" /></a>
  <img src="https://img.shields.io/badge/Blender-5.0+-orange?style=for-the-badge&logo=blender&logoColor=white" />
</p>

<p align="center">
  <strong>A non-destructive, layer-based texturing toolset for Blender.</strong><br>
  Automate complex node groups for multi-channel painting and professional mask management.
</p>

---

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

## ⚖️ Disclaimer & License

### **A Note from the Developer**
**Texture Mixer** is my first venture into Blender addon development. Coming from C++ & C# background, I am still navigating the nuances of the Blender Python API. 
- Much of the current architecture is the result of heavy **trial and error** to bridge the gap between pure data processing and Blender’s internal systems.
- You may encounter unpolished performance or "crawler" speeds in certain complex scenarios as I work toward more optimized, buffer-based solutions. 
- I appreciate your patience and feedback as I continue to learn and refine the engine!

### **Disclaimer**
**Texture Mixer** is currently in **Alpha**. While every effort is made to ensure stability, this software is provided "as-is," without warranty of any kind. 
- **Use at your own risk.**
- The author is not responsible for any data loss, file corruption, or hardware damage resulting from the use of this addon.
- **Always keep backups** of your `.blend` files before initializing Texture Mixer on a production model.

### **License**
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. 
- You are free to use, modify, and distribute this software.
- Any derivative works must also be licensed under the GPL-3.0.
- See the [LICENSE](LICENSE) file for the full legal text.

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
