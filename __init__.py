#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = __init__.py                           |
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
#-------------------------------------------------
from . import texture_mixer_icon as tm_icon
from . import texture_mixer_property as tm_property
from . import texture_mixer_operators as tm_operators
from . import texture_mixer_ui as tm_ui
from .texture_mixer_debug import Debug
#-------------------------------------------------
#endregion [IMPORT]

#region [BLENDER INFO]
#-------------------------------------------------
bl_info = {
    "name": "Texture Mixer",
    "author": "Candra Agung Prasetyo",
    "description": "Layer-based PBR mixing and texture management",
    "blender": (4, 5, 0),
    "version": (0, 1, 0),
    "location": "View3D > Sidebar > Texture Mixer",
    "warning": "",
    "doc_url": "https://github.com/CandraAP/texture_mixer",
    "category": "Material",
}
#-------------------------------------------------
#endregion [BLENDER INFO]

#region [REGISTRATION][__init__.py]
#-------------------------------------------------
def register():
    tm_icon.need_to_register()
    tm_property.need_to_register()
    tm_operators.need_to_register()
    tm_ui.need_to_register()
    Debug.LogSuper("Addon registered successfully!")
    print()
#-------------------------------------------------
def unregister():     
    tm_ui.need_to_unregister()
    tm_operators.need_to_unregister()
    tm_property.need_to_unregister()
    tm_icon.need_to_unregister()
    Debug.LogSuper("Addon unregistered successfully!")
    print()
#-------------------------------------------------
if __name__ == "__main__":
    register()
#-------------------------------------------------
#endregion [REGISTRATION][__init__.py]