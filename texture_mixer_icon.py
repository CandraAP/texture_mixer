#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_icon.py                 |
#----------------------------------------------------
# A Blender user since 2.49b from Indonesia! ########
#----------------------------------------------------
############| D.I.Yogyakarta, Indonesia |############
#----------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#region [IMPORT]
#-------------------------------------------------
import bpy
import os
from bpy.utils import previews
from typing import Optional, Dict
from .texture_mixer_debug import Debug
#-------------------------------------------------
debug_id = "TextureMixer_Icon_Loader"
#endregion [IMPORT]

#region [ICON]
TM_Icon_Custom_Icons: Dict[str, previews.ImagePreviewCollection] = {}
TM_Icon_Collection_Name = "TextureMixerIcons"
TM_Icon_Custom_Directory = "assets/icons/"
TM_Icon_Mapping = {
    "texture_mixer_logo_big.png": 'TM_LOGO_BIG',
    "texture_mixer_mask_fill_black.png":'TM_MASK_FILL_BLACK',
    "texture_mixer_mask_fill_white.png":'TM_MASK_FILL_WHITE',
}

def TM_Icon_Get_Icon(icon_name: str) -> int:
    """TM_Icon_Get_Icon"""
    if TM_Icon_Collection_Name in TM_Icon_Custom_Icons:
        pcoll = TM_Icon_Custom_Icons[TM_Icon_Collection_Name]
        if icon_name in pcoll:
            return pcoll[icon_name].icon_id
    return 0
#endregion [ICON]

#region [Included Classes & Property To Register]
#-------------------------------------------------
def need_to_register():
    pcoll = previews.new()
    addon_dir = os.path.dirname(__file__)
    icon_dir = os.path.join(addon_dir, TM_Icon_Custom_Directory)
    #---------------------------------------------    
    if not os.path.isdir(icon_dir):
        Debug.LogError(f"Icon directory not found at {icon_dir}",f"{debug_id}")
        need_to_unregister() 
        return
    #---------------------------------------------        
    for filename, icon_name in TM_Icon_Mapping.items():
        image_path = os.path.join(icon_dir, filename)        
        if os.path.exists(image_path):
            try:
                pcoll.load(icon_name, image_path, 'IMAGE') 
                Debug.Log(f"Loaded icon {icon_name} from {filename}",f"{debug_id}")
            except Exception as e:
                Debug.LogError(f"Failed to loading icon {filename} as {icon_name}: {e}",f"{debug_id}")
        else:
            Debug.LogWarning(f"Icon file not found {image_path}",f"{debug_id}")
    TM_Icon_Custom_Icons[TM_Icon_Collection_Name] = pcoll
#-------------------------------------------------
def need_to_unregister():
    if TM_Icon_Collection_Name in TM_Icon_Custom_Icons:
        previews.remove(TM_Icon_Custom_Icons[TM_Icon_Collection_Name])
        del TM_Icon_Custom_Icons[TM_Icon_Collection_Name]
#-------------------------------------------------
#endregion [Included Classes & Property To Register]