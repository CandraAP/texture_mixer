#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_property.py             |
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
import bpy.utils
from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import FloatVectorProperty
from bpy.props import IntVectorProperty
from bpy.props import EnumProperty
from bpy.props import PointerProperty
from bpy.props import CollectionProperty
from .texture_mixer_debug import Debug
#-------------------------------------------------
#endregion [IMPORT]

#region [ ADDON DATA ]
class Addon_Data():
    #-------------------------------------------------
    m_addon_name                    = "Texture Mixer"
    m_addon_descriptions            = "Texturing tools addon for Blender"
    m_addon_version                 = "0.1.0"
    m_addon_status                  = "-ALPHA"
    m_package_id                    = __package__.replace(".", "_")
    #-------------------------------------------------
    m_addon_id_stamp                = f"{__package__.lower()}_property_id"
    m_addon_is_canvas               = f"{__package__.lower()}_is_canvas"
    #-------------------------------------------------
    m_author_name                   = "Candra Agung Prasetyo"
    m_author_email                  = "yuyevon777@gmail.com"
    #-------------------------------------------------
    m_supported_file_image_type     = "*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga;*.exr"
    #-------------------------------------------------
    m_ui_panel_category              = f"{m_addon_name}"
    m_ui_panel_label_user_welcome    = f"{m_ui_panel_category} | Info"
    m_ui_panel_label_user_settings   = f"{m_ui_panel_category} | Manager"
    m_ui_panel_label_layer_settings  = f"{m_ui_panel_category} | Layer"
    m_ui_panel_label_brush_settings  = f"{m_ui_panel_category} | Brush"
    m_ui_panel_label_export_settings = f"{m_ui_panel_category} | Export"
    #-------------------------------------------------
    m_ui_enable_support              = True
    #-------------------------------------------------
#endregion [ ADDON DATA ]

#region [ENUMS]
TM_BSDF_Shader_Type_Items = [
    ('ShaderNodeBsdfPrincipled', "Principled BSDF", "Use Principled BSDF shader"),
    ('ShaderNodeBsdfDiffuse', "Diffuse BSDF", "Use Diffuse BSDF shader"),
    # support another shader types in the future...
]

TM_Resolution_Preset_Items = [
    ('R_128',"128 x 128", "Set default resolution to 128 x 128 pixels"),
    ('R_256',"256 x 256", "Set default resolution to 256 x 256 pixels"),
    ('R_512',"512 x 512", "Set default resolution to 512 x 512 pixels"),
    ('R_1024',"1024 x 1024", "Set default resolution to 1024 x 1024 pixels"),
    ('R_2048',"2048 x 2048", "Set default resolution to 2048 x 2048 pixels"),
    # ('R_4096',"4096 x 4096", "Set default resolution to 4096 x 4096 pixels"),   # <-- heavy, Approx 2+ GB of RAM per layer!
    # ('R_8192',"8192 x 8192", "Set default resolution to 8192 x 8192 pixels"),   # <-- Super heavy, Approx 6+ GB of RAM per layer!
    # more resolution presets...
]

TM_Node_Type_Items = [
    ('LAYER_PAINTABLE', "Paintable Layer", "Layer for direct painting/editing"),
    ('LAYER_PRESERVED', "Preserved Layer", "Layer using a procedural/fill value"),
    ('GROUP', "Group", "Container for nested layers"),
    # more layer types...
]

TM_Mask_Type_Items = [    
    ('MASK_PAINTABLE', "Paintable Mask", "Mask layer for direct painting/editing"),
    ('MASK_PRESERVED', "Preserved Mask", "Mask layer using a procedural/fill value"),
    # more mask types...
]

TM_Blending_Mode_Items = [
    ('MIX', "Mix", "Standard Alpha: Current Layer replaces Lower Layer based on Factor"),

    ('ADD', "Add", "Brightness Sum: Adds Current Layer values to Lower Layer; useful for glows"),
    ('SUBTRACT', "Subtract", "Brightness Reduction: Subtracts Current Layer from Lower Layer; useful for shadows"),
    ('MULTIPLY', "Multiply", "Darken: Multiplies Lower Layer by Current Layer; White is transparent, Black is solid"),
    ('DIVIDE', "Divide", "Contrast Boost: Divides Lower Layer by Current Layer; results in significant brightening"),

    ('DARKEN', "Darken", "Minimum: Compares both and keeps only the darkest pixels from either layer"),
    ('LIGHTEN', "Lighten", "Maximum: Compares both and keeps only the brightest pixels from either layer"),
    ('SCREEN', "Screen", "Inverse Multiply: Brightens Lower Layer using Current Layer without clipping highlights"),
    ('OVERLAY', "Overlay", "Contrast Mix: Multiplies dark areas and Screens light areas of Lower Layer"),
    ('DIFFERENCE', "Difference", "Inversion: Calculates the absolute color difference between Current and Lower layers"),
    ('EXCLUSION', "Exclusion", "Soft Inversion: Similar to Difference but with lower contrast and softer tones"),
    
    ('SOFT_LIGHT', "Soft Light", "Subtle Tint: Lower Layer is gently brightened or darkened by Current Layer"),
    ('LINEAR_LIGHT', "Linear Light", "Strong Lighting: Aggressively adjusts Lower Layer brightness based on Current Layer"),
    ('DODGE', "Color Dodge", "Vivid Lighten: Brightens Lower Layer to reflect Current Layer by decreasing contrast"),
    ('BURN', "Color Burn", "Heavy Darken: Darkens Lower Layer to reflect Current Layer by increasing contrast"),
    
    ('HUE', "Hue", "Color Type: Applies Hue of Current Layer to Saturation and Luminance of Lower Layer"),
    ('SATURATION', "Saturation", "Intensity: Applies Saturation of Current Layer to Hue and Luminance of Lower Layer"),
    ('COLOR', "Color", "Full Tint: Applies Hue and Saturation of Current Layer to Luminance of Lower Layer"),
    ('VALUE', "Value", "Luminosity: Applies Brightness of Current Layer to Hue and Saturation of Lower Layer"),
]
#endregion [ENUMS]

#region [DATA]
TM_DT_Export_Texture_Metadata = {
    'None':{
        'name'          : 'None',
        'init'          : 'none',
        'color_space'   : 'None', 
        'item'          : ('None', "Map (None)", "None"),
        'channel'       : [('None', "None", "None")],
        'channel_rgb'   : None,
        'shader_output' : None,
        'socket_output' : None,
        'bake_type'     : None,
        'bake_cycles_samples'           : 0,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },

    'Black':{
        'name'          : 'Black',
        'init'          : 'black',
        'color_space'   : 'None', 
        'item'          : ('Black', "Black", "Black Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")],
        'channel_rgb'   : {'r'},
        'shader_output' : None,
        'socket_output' : None,
        'bake_type'     : None,
        'bake_cycles_samples'           : 0,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },

    'White':{
        'name'          : 'White',
        'init'          : 'white',
        'color_space'   : 'None', 
        'item'          : ('White', "White", "White Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")],
        'channel_rgb'   : {'r'},
        'shader_output' : None,
        'socket_output' : None,
        'bake_type'     : None,
        'bake_cycles_samples'           : 0,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
                       
    'Alpha':{
        'name'          : 'Alpha',
        'init'          : 'alpha',
        'color_space'   : 'Non-Color', 
        'item'          : ('Alpha', "Alpha", "Alpha Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")], 
        'channel_rgb'   : {'r'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Output Alpha',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
        
    'Diffuse':{
        'name'          : 'Diffuse',
        'init'          : 'diffuse',
        'color_space'   : 'sRGB', 
        'item'          : ('Diffuse', "Diffuse", "Diffuse Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('R', "(R) Red", "Red Channel"), 
                           ('G', "(G) Green", "Green Channel"), 
                           ('B', "(B) Blue", "Blue Channel")],
        'channel_rgb'   : {'r', 'g', 'b'},
        'shader_output' : 'BSDF',
        'socket_output' : 'BSDF',
        'bake_type'     : 'DIFFUSE',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : True,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, }, 
        
    'Base Color':{
        'name'          : 'Base Color',
        'init'          : 'basecolor',
        'color_space'   : 'sRGB', 
        'item'          : ('Base Color', "Base Color", "Base Color Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('R', "(R) Red", "Red Channel"), 
                           ('G', "(G) Green", "Green Channel"), 
                           ('B', "(B) Blue", "Blue Channel")],
        'channel_rgb'   : {'r', 'g', 'b'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Output Base Color',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },      
                       
    'Roughness':{
        'name'          : 'Roughness',
        'init'          : 'roughness',
        'color_space'   : 'Non-Color', 
        'item'          : ('Roughness', "Roughness", "Roughness Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")],
        'channel_rgb'   : {'r'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Output Roughness',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
                       
    'Metallic':{
        'name'          : 'Metallic',
        'init'          : 'metallic',
        'color_space'   : 'Non-Color', 
        'item'          : ('Metallic', "Metallic", "Metallic Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")],
        'channel_rgb'   : {'r'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Output Metallic',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
        
    'Normal':{
        'name'          : 'Normal',
        'init'          : 'normal',
        'color_space'   : 'Non-Color', 
        'item'          : ('Normal', "Normal", "Normal Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('R', "(R) Red", "Red Channel"), 
                           ('G', "(G) Green", "Green Channel"), 
                           ('B', "(B) Blue", "Blue Channel")],
        'channel_rgb'   : {'r', 'g', 'b'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Raster Normal',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
        
    'Processed Normal':{
        'name'          : 'Processed Normal',
        'init'          : 'processednormal',
        'color_space'   : 'Non-Color', 
        'item'          : ('Processed Normal', "Processed Normal", "Combined Bump & Normal Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('R', "(R) Red", "Red Channel"), 
                           ('G', "(G) Green", "Green Channel"), 
                           ('B', "(B) Blue", "Blue Channel")],
        'channel_rgb'   : {'r', 'g', 'b'},
        'shader_output' : 'BSDF',
        'socket_output' : 'BSDF',
        'bake_type'     : 'NORMAL',
        'bake_cycles_samples'           : 64,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
                       
    'Bump':{
        'name'          : 'Bump',
        'init'          : 'bump',
        'color_space'   : 'Non-Color',    
        'item'          : ('Bump', "Bump", "Bump Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('BW', "(BW) Greyscale", "Black and White Channel")],
        'channel_rgb'   : {'r'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Raster Bump',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },

    'Emission':{
        'name'          : 'Emission',
        'init'          : 'emission',
        'color_space'   : 'sRGB',        
        'item'          : ('Emission', "Emission", "Emission Texture Map"),
        'channel'       : [('None', "None", "None"),
                           ('R', "(R) Red", "Red Channel"), 
                           ('G', "(G) Green", "Green Channel"), 
                           ('B', "(B) Blue", "Blue Channel")],
        'channel_rgb'   : {'r', 'g', 'b'},
        'shader_output' : 'COMPOSER',
        'socket_output' : 'Output Emission Color',
        'bake_type'     : 'EMIT',
        'bake_cycles_samples'           : 32,
        'use_pass_direct'               : False,
        'use_pass_indirect'             : False,
        'use_pass_color'                : False,
        'use_pass_ambient_occlusion'    : False,
        'use_pass_shadow'               : False, },
}

TM_DT_Export_File_Type = {
    'PNG': {
        'item': ('PNG', "PNG", "Lossless compression. Supports Alpha."),
        'extension': '.png',
        'support_alpha': True,
        'bit_depths': ['8', '16']
    },
    'JPEG': {
        'item': ('JPEG', "JPG/JPEG", "Lossy compression. No Alpha support."),
        'extension': '.jpg',
        'support_alpha': False,
        'bit_depths': ['8']
    },
    'TARGA': {
        'item': ('TARGA', "TGA (Targa)", "Standard game engine format. Supports Alpha."),
        'extension': '.tga',
        'support_alpha': True,
        'bit_depths': ['8']
    },
    'TIFF': {
        'item': ('TIFF', "TIFF", "High quality uncompressed. Supports Alpha."),
        'extension': '.tif',
        'support_alpha': True,
        'bit_depths': ['8', '16']
    },
    'OPEN_EXR': {
        'item': ('OPEN_EXR', "EXR", "Professional float data. Supports Alpha."),
        'extension': '.exr',
        'support_alpha': True,
        'bit_depths': ['16', '32']
    },
    'BMP': {
        'item': ('BMP', "BMP", "Lossless but huge files. No Alpha support."),
        'extension': '.bmp',
        'support_alpha': False,
        'bit_depths': ['8']
    }
}

TM_DT_Channels_Based_On_Shader = {  
    'ShaderNodeBsdfPrincipled'  : {'Base Color', 'Normal', 'Bump', 'Metallic', 'Roughness', 'Emission'},
    'ShaderNodeBsdfDiffuse'     : {'Base Color', 'Normal', 'Bump'},      
}

TM_DT_Custom_Node_Library = {
    'SYSTEM_FOLDER' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_FOLDER',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_LAYER' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_LAYER',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_COMPOSER' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_COMPOSER',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_DEFAULT' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_DEFAULT',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_MASK' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_MASK',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_TEXTURE' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_TEXTURE',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
    'SYSTEM_TEXTURE_MAPPING' : {
        'idname'    : 'TM_PROPERTY_SYSTEM_TEXTURE_MAPPING',
        'path'      : "assets/blends/texture_mixer_library.blend"
    },
}

TM_DT_Channels_Metadata = {
    'Base Color':{
        'default_name'              : 'Base Color',
        'default_init'              : 'basecolor',
        'default_color_space'       : 'sRGB',
        'default_channel_rgba'      : {'r', 'g', 'b', 'a'},        
        'channel_color_neutral'     : (0.0, 0.0, 0.0, 1.0),
        'default_blank_canvas'      : ((0.0,0.0,0.0,0.0), True, True), 
        'default_fill_texture'      : ((1.0,1.0,1.0,1.0), True, False), 
        'default_system_sockets'    : [ ("Color", "Base Color Value"), ("Alpha", "Base Color Alpha")],
        'default_blend_node'        : 'BASE_COLOR_BLEND'
    },
    'Roughness':{
        'default_name'              : 'Roughness',
        'default_init'              : 'roughness',
        'default_color_space'       : 'Non-Color',
        'default_channel_rgba'      : {'r'},  
        'channel_color_neutral'     : (0.5, 0.5, 0.5, 1.0),
        'default_blank_canvas'      : ((0.5,0.5,0.5,1.0), False, True),
        'default_fill_texture'      : ((0.5,0.5,0.5,1.0), False, False),
        'default_system_sockets'    : [ ("Color", "Roughness Value")],
        'default_blend_node'        : 'ROUGHNESS_BLEND'
    },
    'Metallic':{
        'default_name'              : 'Metallic',
        'default_init'              : 'metallic',
        'default_color_space'       : 'Non-Color',
        'default_channel_rgba'      : {'r'},  
        'channel_color_neutral'     : (0.5,0.5,0.5, 1.0),
        'default_blank_canvas'      : ((0.5,0.5,0.5,1.0), False, True),
        'default_fill_texture'      : ((0.5,0.5,0.5,1.0), False, False),
        'default_system_sockets'    : [ ("Color", "Metallic Value")],
        'default_blend_node'        : 'METALLIC_BLEND'
    },
    'Normal':{
        'default_name'              : 'Normal',
        'default_init'              : 'normal',
        'default_color_space'       : 'Non-Color',
        'default_channel_rgba'      : {'r', 'g', 'b'},  
        'channel_color_neutral'     : (0.5, 0.5, 1.0, 1.0),
        'default_blank_canvas'      : ((0.5,0.5,1.0,1.0), False, True),
        'default_fill_texture'      : ((0.5,0.5,1.0,1.0), False, True),
        'default_system_sockets'    : [ ("Color", "Normal Value")],
        'default_blend_node'        : 'NORMAL_BLEND'
    },
    'Bump':{
        'default_name'              : 'Bump',
        'default_init'              : 'bump',
        'default_color_space'       : 'Non-Color',
        'default_channel_rgba'      : {'r'},  
        'channel_color_neutral'     : (0.5, 0.5, 0.5, 1.0),
        'default_blank_canvas'      : ((0.5,0.5,0.5,1.0), False, True),
        'default_fill_texture'      : ((0.5,0.5,0.5,1.0), False, False),
        'default_system_sockets'    : [ ("Color", "Bump Value")] ,
        'default_blend_node'        : 'BUMP_BLEND'
    },
    'Emission':{
        'default_name'              : 'Emission',
        'default_init'              : 'emission',
        'default_color_space'       : 'sRGB',
        'default_channel_rgba'      : {'r', 'g', 'b'},  
        'channel_color_neutral'     : (0.0, 0.0, 0.0, 1.0),
        'default_blank_canvas'      : ((0.0,0.0,0.0,1.0), False, True),
        'default_fill_texture'      : ((0.0,0.0,0.0,1.0), False, False),
        'default_system_sockets'    : [ ("Color", "Emission Value")],
        'default_blend_node'        : 'EMISSION_BLEND'
    },
}
#endregion [DATA]

#region [Property Logic]
def TextureMixer_Property_Get_Active_Manager(context):
    """TextureMixer_Property_Get_Active_Manager"""
    debug_id = "TextureMixer_Property_Get_Active_Manager"

    try:
        user_data = context.scene.TM_User_Data
        if not user_data:
            Debug.LogError("Failed to find user data.", debug_id)
            return None

        user_data = context.scene.TM_User_Data
        manager_collection = user_data.m_managed_tm_node_manager_collection
        if not manager_collection:
            Debug.LogWarning("No Layer Managers exist", debug_id)
            return None

        for manager in manager_collection:
            if manager.m_enable: 
                return manager
            
        Debug.LogWarning("No active Layer Manager found", debug_id)
        return None
    
    except Exception as e:
        Debug.LogError(f"{str(e)}", debug_id)
        return None

def TextureMixer_Property_Get_Active_Layer(context):
    """TextureMixer_Property_Get_Active_Layer"""
    debug_id = "TextureMixer_Property_Get_Active_Layer"
    
    try:
        active_manager = TextureMixer_Property_Get_Active_Manager(context)
        if not active_manager:
            return

        managed_layer = active_manager.m_managed_tm_node_collection
        if len(managed_layer) == 0:
            Debug.LogWarning("Create new layer first.", debug_id)
            return None

        if 0 <= active_manager.m_managed_tm_node_pointer < len(managed_layer):
            layer = managed_layer[active_manager.m_managed_tm_node_pointer]
            if layer:
                return layer
        else:
            Debug.LogWarning("Active layer pointer out of range!", debug_id)
    except Exception as e:
        Debug.LogError(f"{str(e)}", debug_id)
        return None
    
def TextureMixer_Property_Get_Material_With_Id(material_id: str) -> bpy.types.Material | None:
    """TM_Logic_Material_Get_By_Id"""
    debug_id = "TM_Logic_Material_Get_By_Id"
    stamp_id = Addon_Data.m_addon_id_stamp

    try:
        for mat in bpy.data.materials:
            if stamp_id in mat and mat[stamp_id] == material_id:
                return mat

        Debug.LogError(f"Material with ID '{material_id}' not found", debug_id)
        return None
    except Exception as e:
        Debug.LogError(f"{str(e)}", debug_id)
        return None

def TextureMixer_Property_Get_ShaderNode_With_Id(context, target_node_id:str, target_internal_node_name:str|None = None) -> bpy.types.Node | None:
    """TextureMixer_Property_Get_ShaderNode_With_Id"""
    debug_id = "TextureMixer_Property_Get_ShaderNode_With_Id"
    stamp_id = Addon_Data.m_addon_id_stamp

    try:
        active_manager = TextureMixer_Property_Get_Active_Manager(context)
        if not active_manager:
            return None
        
        active_material = TextureMixer_Property_Get_Material_With_Id(active_manager.m_managed_material_id)
        if not active_material:
            return None        
        if not active_material.use_nodes:
            Debug.LogError(f"Active material '{active_material.name}' doesnt use nodes.", debug_id)
            return None
        
        active_node_tree = active_material.node_tree

        active_node = None
        for node in active_node_tree.nodes:
            if node.get(stamp_id) == target_node_id:
                active_node = node
        if not active_node:
            Debug.LogError("Failed to find active node.", debug_id)
            return None

        if not target_internal_node_name or active_node.type != 'GROUP':
            return active_node

        internal_tree = active_node.node_tree
        if internal_tree is None:
            return None

        internal_node = internal_tree.nodes.get(target_internal_node_name)
        if internal_node is None:
            return None

        return internal_node

    except Exception as e:
        Debug.LogError(f"{str(e)}", debug_id)
        return None
#endregion [Property Logic]

#region [TM_Texture]
class TM_Texture(PropertyGroup):
    """TM_Texture"""
    m_id: StringProperty(name="Id") 
        
    m_user_texture_path: StringProperty(name="User Texture Path")  
    m_user_texture_hash: StringProperty(name="User Texture Hash")  
    m_user_texture_size: IntVectorProperty(name="User Texture Size", size=2, default=(0, 0))  

    m_preserved_texture_id: StringProperty(name="Preserved Texture Id")  
    m_preserved_texture_size: IntVectorProperty(name="Preserved Texture Size", size=2, default=(0, 0))  
    
    m_virtual_texture_id: StringProperty(name="Virtual Texture Id")     
    m_virtual_texture_size: IntVectorProperty(name="Virtual Texture Size", size=2, default=(0, 0))  

    m_shader_node_system_texture_id: StringProperty(name="Texture System Node Id")    
    m_shader_node_virtual_texture_name: StringProperty(name="Texture Virtual Node Id", default="TM_TEXTURE_VIRTUAL")  
#endregion [TM_Texture]

#region [Channels]
class TM_Channel_Data(PropertyGroup):
    """TM_Channel_Data"""
    m_name : StringProperty(name="Channel Name")

    m_tm_texture_id: StringProperty(name="TM Texture Id")  
    
    m_blending_mode: EnumProperty(name="Blending Mode", items=TM_Blending_Mode_Items, default='MIX', update=lambda self, context: tm_channel_data_update_m_blending_mode(self, context))

def tm_channel_data_update_m_blending_mode(self, context):
    if not self.m_name:
        return

    active_layer = TextureMixer_Property_Get_Active_Layer(context)
    if not active_layer:
        return
    
    layer_node_name = active_layer.m_shader_node_system_layer_id

    channel_metadata = TM_DT_Channels_Metadata.get(self.m_name)
    if not channel_metadata:
        return
    
    self_node_name = channel_metadata.get('default_blend_node')
    if not self_node_name:
        return

    blend_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, layer_node_name, self_node_name)
    if not blend_node:
        return

    if blend_node.data_type != 'RGBA':
        return

    blend_node.blend_type = self.m_blending_mode
    
class TM_Channel_Container(PropertyGroup):
    """TM_Channel_Container"""
    m_channel_basecolor: PointerProperty(type=TM_Channel_Data, name="Base Color Channel")  
    m_channel_normal: PointerProperty(type=TM_Channel_Data, name="Normal Channel")   
    m_channel_bump: PointerProperty(type=TM_Channel_Data, name="Bump Channel")  
    m_channel_metallic: PointerProperty(type=TM_Channel_Data, name="Metallic Channel")  
    m_channel_roughness: PointerProperty(type=TM_Channel_Data, name="Roughness Channel")  
    m_channel_emission: PointerProperty(type=TM_Channel_Data, name="Emission Channel")  
#endregion [Channels]

#region [Texture Export]
def tm_texture_export_get_map_items(self, context):
    items = []
    for index, data in TM_DT_Export_Texture_Metadata.items():
        items.append(data['item'])
    return items

def tm_texture_export_get_channel_items(self, context, slot_prefix):
    current_map_key = getattr(self, f"m_slot_{slot_prefix}_map")    
    if current_map_key in TM_DT_Export_Texture_Metadata:
        return TM_DT_Export_Texture_Metadata[current_map_key]['channel']
    return [('None', "None", "None")]

def tm_texture_export_get_file_type(self, context):
    items = []
    for index, data in TM_DT_Export_File_Type.items():
        items.append(data['item'])
    return items

def tm_texture_export_sync_channel_selection(self, context, slot_prefix):
    current_map = getattr(self, f"m_slot_{slot_prefix}_map")
    current_channel = getattr(self, f"m_slot_{slot_prefix}_channel")
    valid_channels = [item[0] for item in TM_DT_Export_Texture_Metadata[current_map]['channel']]
    if current_channel not in valid_channels:
        setattr(self, f"m_slot_{slot_prefix}_channel", 'None')

def tm_texture_export_name_update(self, context):
    active_manager = TextureMixer_Property_Get_Active_Manager(context)
    if not active_manager:
        return

    collection = active_manager.m_managed_tm_texture_export_collection
    new_name = self.m_name
    original_name = new_name
    suffix = 1
    
    while any(item.m_name == new_name and item.m_id != self.m_id for item in collection):
        new_name = f"{original_name}.{suffix:03d}"
        suffix += 1
    
    if new_name != self.m_name:
        self.m_name = new_name

class TM_Texture_Export(PropertyGroup):
    """TM_Texture_Export"""
    m_id            : StringProperty(name="Id") 
    m_name          : StringProperty(name="Name", update=lambda self, context: tm_texture_export_name_update(self, context))  
    m_enable        : BoolProperty(name="Enable", default=True)  

    m_slot_r_map            : EnumProperty(name="Slot R Map",       items=tm_texture_export_get_map_items, update=lambda self, context: tm_texture_export_sync_channel_selection(self, context, "r"))
    m_slot_r_channel        : EnumProperty(name="Slot R Channel",   items=lambda self, context: tm_texture_export_get_channel_items(self, context, "r"))    
    m_slot_r_invert         : BoolProperty(name="Slot R Invert",    default=False)
    m_slot_r_as_srgb        : BoolProperty(name="Slot R True = sRGB | False = Linear",   default=True)

    m_slot_g_map            : EnumProperty(name="Slot G Map",       items=tm_texture_export_get_map_items, update=lambda self, context: tm_texture_export_sync_channel_selection(self, context, "g"))
    m_slot_g_channel        : EnumProperty(name="Slot G Channel",   items=lambda self, context: tm_texture_export_get_channel_items(self, context, "g"))
    m_slot_g_invert         : BoolProperty(name="Slot G Invert",    default=False)
    m_slot_g_as_srgb        : BoolProperty(name="Slot G True = sRGB | False = Linear",   default=True)

    m_slot_b_map            : EnumProperty(name="Slot B Map",       items=tm_texture_export_get_map_items, update=lambda self, context: tm_texture_export_sync_channel_selection(self, context, "b"))
    m_slot_b_channel        : EnumProperty(name="Slot B Channel",   items=lambda self, context: tm_texture_export_get_channel_items(self, context, "b"))
    m_slot_b_invert         : BoolProperty(name="Slot B Invert",    default=False)
    m_slot_b_as_srgb        : BoolProperty(name="Slot B True = sRGB | False = Linear",   default=True)

    m_slot_a_map            : EnumProperty(name="Slot A Map",       items=tm_texture_export_get_map_items, update=lambda self, context: tm_texture_export_sync_channel_selection(self, context, "a"))
    m_slot_a_channel        : EnumProperty(name="Slot A Channel",   items=lambda self, context: tm_texture_export_get_channel_items(self, context, "a"))   
    m_slot_a_invert         : BoolProperty(name="Slot A Invert",    default=False)  
    m_slot_a_as_srgb        : BoolProperty(name="Slot A True = sRGB | False = Linear",   default=True)

    m_file_type     : EnumProperty(name="File Type",        items=tm_texture_export_get_file_type)
#endregion [Texture Export]

#region [Core]
class TM_Mask(PropertyGroup):
    """TM_Mask"""
    m_id: StringProperty(name="Id") 
    m_tm_node_host_id: StringProperty(name="Host Layer Node Id") 
    m_tm_node_manager_id: StringProperty(name="Manager Id")  
    m_tm_texture_id: StringProperty(name="TM Texture Id")  

    m_name: StringProperty(name="Name")  
    m_type: EnumProperty(name="Type", items=TM_Mask_Type_Items, default='MASK_PAINTABLE')  
    
    m_enable: BoolProperty(name="Enable", default=True, update=lambda self, context: tm_mask_update_m_enable(self, context))  
    m_opacity: FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0, subtype='PERCENTAGE', update=lambda self, context: tm_mask_update_m_opacity(self, context))  

    m_blending_mode: EnumProperty(name="Blending Mode", items=TM_Blending_Mode_Items, default='SCREEN', update=lambda self, context: tm_mask_update_m_blending_mode(self, context))  
    
    m_shader_node_system_mask_id: StringProperty(name="Texture System Id") 
    m_shader_node_blending_node_name: StringProperty(name="Blending Node Name", default="MASK_BLEND")      

def tm_mask_update_m_enable(self, context):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_mask_id)
    if not active_node:
        return
    socket_name = "Mask Enable"
    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return
    socket_input.default_value = bool(self.m_enable)

def tm_mask_update_m_opacity(self, context):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_mask_id)
    if not active_node:
        return
    socket_name = "Mask Opacity"
    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return
    socket_input.default_value = float(self.m_opacity)

def tm_mask_update_m_blending_mode(self, context):
    blend_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_mask_id, self.m_shader_node_blending_node_name)
    if not blend_node:
        return
    if blend_node.data_type != 'RGBA':
        return
    blend_node.blend_type = self.m_blending_mode

class TM_Node(PropertyGroup):
    """TM_Node"""
    m_id: StringProperty(name="Id") 
    m_group_id: StringProperty(name="Group Id")  
    m_tm_node_manager_id: StringProperty(name="Manager Id")  

    m_name: StringProperty(name="Name")  
    m_type: EnumProperty(name="Type", items=TM_Node_Type_Items, default='LAYER_PAINTABLE')
    m_blending_mode: EnumProperty(name="Blending Mode", items=TM_Blending_Mode_Items, default='SCREEN', update=lambda self, context: tm_node_update_m_blending_mode(self, context))       
    
    m_enable: BoolProperty(name="Enable", default=True, update=lambda self, context: tm_node_update_m_enable(self, context))  
    m_opacity: FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0, subtype='PERCENTAGE', update=lambda self, context: tm_node_update_m_opacity(self, context))
    
    m_channel: PointerProperty(type=TM_Channel_Container, name="Channel")
    
    m_mask_enable: BoolProperty(name="Mask Enable", default=False, update=lambda self, context: tm_node_update_m_mask_enable(self, context))
    m_managed_tm_mask_collection: CollectionProperty(type=TM_Mask, name="Mask")
    m_managed_tm_mask_pointer: IntProperty(name="Active Mask Pointer")
    
    m_shader_node_system_layer_id: StringProperty(name="Layer Shader Node") 
    m_shader_node_system_texture_mapping_id: StringProperty(name="Texture Mapping Shader Node") 
    m_shader_node_blending_node_name: StringProperty(name="Blending Node Name", default="ALPHA_BLEND") 

def tm_node_update_m_blending_mode(self, context):
    active_layer = TextureMixer_Property_Get_Active_Layer(context)
    if not active_layer:
        return
    layer_node_name = active_layer.m_shader_node_system_layer_id

    blend_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, layer_node_name, self.m_shader_node_blending_node_name)
    if not blend_node:
        return

    if blend_node.data_type != 'RGBA':
        return

    blend_node.blend_type = self.m_blending_mode

def tm_node_update_m_mask_enable(self, context):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_layer_id)
    if not active_node:
        return

    socket_name = "Mask Enable"
    if self.m_type == 'GROUP':
        socket_name = "Enable Managed Mask"

    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return
        
    socket_input.default_value = bool(self.m_mask_enable)

def tm_node_update_m_enable(self, context):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_layer_id)
    if not active_node:
        return

    socket_name = "Layer Enable"
    if self.m_type == 'GROUP':
        socket_name = "Enable Managed Folder"

    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return

    socket_input.default_value = bool(self.m_enable)

def tm_node_update_m_opacity(self, context):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_layer_id)
    if not active_node:
        return

    socket_name = "Layer Opacity"
    if self.m_type == 'GROUP':
        socket_name = "Opacity Managed Folder"

    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return
        
    socket_input.default_value = float(self.m_opacity)

class TM_Node_Manager_Data(PropertyGroup):
    """TM_Internal_Requirement"""
    m_baked_position_map_id         : StringProperty(name="Position Map Id")

    m_export_save_file_path     : StringProperty(name="Save File Path", default="", subtype='FILE_PATH')
    m_export_render_margin_size : IntProperty(name="Margin Size", default=16)

class TM_Node_Manager(PropertyGroup):
    """TM_Node_Manager"""    
    m_id                                : StringProperty(name="Id")  
 
    m_name                              : StringProperty(name="Name")  
    m_enable                            : BoolProperty(name="Enable", default=False)  
    
    m_preserved_resolution              : EnumProperty(name="Preserved Resolution", items=TM_Resolution_Preset_Items, default='R_1024')  
    m_preserved_resolution_cache        : EnumProperty(name="Preserved Resolution", items=TM_Resolution_Preset_Items, default='R_1024')  
    
    m_virtual_resolution                : EnumProperty(name="Virtual Resolution", items=TM_Resolution_Preset_Items, default='R_1024')  
    m_virtual_resolution_cache          : EnumProperty(name="Virtual Resolution", items=TM_Resolution_Preset_Items, default='R_1024')  

    m_output_resolution                 : EnumProperty(name="Output Resolution", items=TM_Resolution_Preset_Items, default='R_1024', update=lambda self, context: tm_node_manager_update_m_output_resolution(self, context))  

    m_main_shader_type                  : EnumProperty(name="Type", items=TM_BSDF_Shader_Type_Items, default='ShaderNodeBsdfPrincipled')  
    m_main_shader_type_cache            : EnumProperty(name="Type", items=TM_BSDF_Shader_Type_Items, default='ShaderNodeBsdfPrincipled')  

    m_managed_material_id               : StringProperty(name="Managed Material Name", default="")    

    m_managed_tm_texture_collection     : CollectionProperty(type=TM_Texture, name="All Managed Textures") 
    m_managed_tm_texture_pointer        : IntProperty(name="Active TM_Texture Pointer")   

    m_managed_tm_node_collection        : CollectionProperty(type=TM_Node, name="Layer")  
    m_managed_tm_node_pointer           : IntProperty(name="Active Layer Pointer")  

    m_managed_tm_texture_export_collection  : CollectionProperty(type=TM_Texture_Export, name="All Managed Textures Export")
    m_managed_tm_texture_export_pointer     : IntProperty(name="Active TM_Texture Export Pointer")  

    m_data                              : PointerProperty(type=TM_Node_Manager_Data,name="Data")
    
    m_shader_node_main_shader_id        : StringProperty(name="Main Shader Node Id")  
    m_shader_node_output_id             : StringProperty(name="Output Node Id")  
    m_shader_node_system_composer_id    : StringProperty(name="System Composer Node Id")  
    m_shader_node_system_default_id     : StringProperty(name="System Default Nod Id")  

    # active channels
    m_channel_basecolor_enable          : BoolProperty(name="Channel Base Color Enable", default=True, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Base Color", self.m_channel_basecolor_enable))  
    m_channel_metallic_enable           : BoolProperty(name="Channel Metallic Enable", default=True, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Metallic", self.m_channel_metallic_enable))  
    m_channel_roughness_enable          : BoolProperty(name="Channel Roughness Enable", default=True, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Roughness", self.m_channel_roughness_enable))  
    m_channel_bump_enable               : BoolProperty(name="Channel Bump Enable", default=False, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Bump", self.m_channel_bump_enable))  
    m_channel_normal_enable             : BoolProperty(name="Channel Normal Enable", default=True, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Normal", self.m_channel_normal_enable))  
    m_channel_emission_enable           : BoolProperty(name="Channel Emission Enable", default=False, update=lambda self, context: tm_node_manager_update_m_channel_enable(self, context, "Enable Emission", self.m_channel_emission_enable))  
  
def tm_node_manager_update_m_output_resolution(self, context):
    res_str     = self.m_output_resolution.split('_')[1]
    res_int     = int(res_str)
    max_dim     = max(res_int, res_int)    
    iterations  = int((max_dim / 1024) * 16)
    result_int  = max(4, iterations)

    self.m_data.m_export_render_margin_size = result_int

def tm_node_manager_update_m_channel_enable(self, context, socket_name:str, value:bool):
    active_node = TextureMixer_Property_Get_ShaderNode_With_Id(context, self.m_shader_node_system_composer_id)
    if not active_node:
        return

    socket_input = active_node.inputs.get(socket_name)
    if not socket_input:
        return
        
    socket_input.default_value = value
    user_data = context.scene.TM_User_Data
    user_data.m_ui_tm_paint_mode_enable = False
#endregion [Core]
   
#region [Brush]
class TM_Brush_Data(PropertyGroup):
    """TM_Brush_Data"""
    m_channel_basecolor_enable  : BoolProperty(name="Enable Base Color", default=True)  
    m_channel_normal_enable     : BoolProperty(name="Enable Normal", default=True)  
    m_channel_roughness_enable  : BoolProperty(name="Enable Roughness", default=True)  
    m_channel_metallic_enable   : BoolProperty(name="Enable Metallic", default=True)  
    m_channel_bump_enable       : BoolProperty(name="Enable Bump", default=True)  
    m_channel_emission_enable   : BoolProperty(name="Enable Emission", default=True) 
    m_channel_mask_enable       : BoolProperty(name="Enable Mask", default=True)  
    
    m_brush_basecolor_color     : FloatVectorProperty( name="Color Base Color", subtype='COLOR', size=4, default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0)
    m_brush_normal_color        : FloatVectorProperty( name="Color Normal", subtype='COLOR', size=4, default=(0.5, 0.5, 1.0, 1.0), min=0.0, max=1.0)
    m_brush_roughness_color     : FloatVectorProperty( name="Color Roughness", subtype='COLOR', size=4, default=(0.5, 0.5, 0.5, 1.0), min=0.0, max=1.0)
    m_brush_metallic_color      : FloatVectorProperty( name="Color Metallic", subtype='COLOR', size=4, default=(0.5, 0.5, 0.5, 1.0), min=0.0, max=1.0)
    m_brush_bump_color          : FloatVectorProperty( name="Color Bump", subtype='COLOR', size=4, default=(0.5, 0.5, 0.5, 1.0), min=0.0, max=1.0) 
    m_brush_emission_color      : FloatVectorProperty( name="Color Emission", subtype='COLOR', size=4, default=(0.0, 0.0, 0.0, 1.0), min=0.0, max=1.0)    
    m_brush_mask_color          : FloatVectorProperty( name="Color Mask", subtype='COLOR', size=4, default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0) 

    m_brush_basecolor_image     : PointerProperty(type=bpy.types.Image,name="Brush Base Color")
    m_brush_normal_image        : PointerProperty(type=bpy.types.Image,name="Brush Normal")
    m_brush_roughness_image     : PointerProperty(type=bpy.types.Image,name="Brush Roughness") 
    m_brush_metallic_image      : PointerProperty(type=bpy.types.Image,name="Brush Metallic")
    m_brush_bump_image          : PointerProperty(type=bpy.types.Image,name="Brush Bump")
    m_brush_emission_image      : PointerProperty(type=bpy.types.Image,name="Brush Emission")
    m_brush_mask_image          : PointerProperty(type=bpy.types.Image,name="Brush Mask")

    m_brush_basecolor_blend     : EnumProperty(name="Blending Mode Base Color", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_normal_blend        : EnumProperty(name="Blending Mode Normal", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_roughness_blend     : EnumProperty(name="Blending Mode Roughness", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_metallic_blend      : EnumProperty(name="Blending Mode Metallic", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_bump_blend          : EnumProperty(name="Blending Mode Bump", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_emission_blend      : EnumProperty(name="Blending Mode Emission", items=TM_Blending_Mode_Items, default='MIX')
    m_brush_mask_blend          : EnumProperty(name="Blending Mode Mask", items=TM_Blending_Mode_Items, default='MIX')

    m_brush_alpha_image         : PointerProperty(type=bpy.types.Image,name="Brush Alpha")
    m_brush_texture_alpha       : PointerProperty(type=bpy.types.Texture,name="Brush Texture Alpha")
    m_brush_texture_image       : PointerProperty(type=bpy.types.Texture,name="Brush Texture Image")

    m_brush_option_skip_channel     : BoolProperty(name="Skip Channel", default=True)
    m_brush_option_enable_smoothing : BoolProperty(name="Enable Smoothing", default=True)

    #region [Experimental]
    m_brush_mode                : EnumProperty(name="Brush Mode", items=[
                                    ('TM_BRUSH_PAINT', "Paint Brush", "")
                                    # ('TM_BRUSH_ERASER', "Eraser Brush", "")
                                    # add more
                                ], default='TM_BRUSH_PAINT')  
    m_brush_falloff_resolution  : IntProperty(name="Falloff Resolution", default=256, min=32, soft_max=1024)
    m_brush_falloff_hardness    : FloatProperty(name="Falloff Hardness", default=0.5, min=0.0, soft_max=1.0)
    #endregion [Experimental]

#endregion [Brush]

#region [Scene Global]
class TM_User_Data_Manager(PropertyGroup):
    """TM_User_Data_Manager"""
    m_managed_tm_node_manager_collection: CollectionProperty(type=TM_Node_Manager, name="Layer Managers")  
    m_managed_tm_node_manager_pointer: IntProperty(name="Active Layer Manager Pointer")  
    m_system_initial_id: StringProperty(name="Initial Id", default="Texture_Mixer")
    m_system_base_id: IntProperty(name="Base Id", default=0)
    m_system_counter_id: IntProperty(name="Counter For New Id", default=0)  

    m_brush_data: PointerProperty(type=TM_Brush_Data)
    m_ui_tm_paint_mode_enable: BoolProperty(default=False) 
    
    m_ui_usersettings_tabs: EnumProperty(
        name="UI User Settings Navigation",
        items=[
            ('MANAGER', "Manager", "Show Layer Manager Collection Tab", 0),
            ('CHANNEL', "Channel", "Show Channel Settings Tab", 1),
            ('OPTIONS', "", "Show Options Tab", 'SETTINGS', 2),
        ],
        default='MANAGER'
    )  

    m_ui_layer_option_tabs: EnumProperty(
        name="UI Layer Navigation",
        items=[
            ('LAYER', "Layer", "Show Layer Collection Tab", 0),
            ('MASK', "Mask", "Show Mask Collection Tab", 1),
            ('OPTIONS', "", "Show Options Tab", 'SETTINGS', 2)
        ],
        default='LAYER'
    )  

    m_ui_channel_option_tabs: EnumProperty(
        name="Channel Options",
        items=[
            ('CHANNEL', "Channels", "Show Channel Collection Tab", 0),
            ('OPTIONS', "", "Show Options Tab", 'SETTINGS', 1),
        ],
        default='CHANNEL'
    )  

    m_ui_brush_option_tabs: EnumProperty(
        name="Brush Options",
        items=[
            ('PAINT_MODE', "Channel Settings", "", 0),
            ('OPTIONS', "", "Show Options Tab", 'SETTINGS', 1),
        ],
        default='PAINT_MODE'
    )  
    
    m_ui_show_support: BoolProperty(default=True)  
    m_ui_show_layer_to_group_options: BoolProperty(default=True)  
    m_ui_show_layer_properties: BoolProperty(default=True) 
    m_ui_show_export_rgba_settings: BoolProperty(default=True)  
    m_ui_show_export_path_settings: BoolProperty(default=True)  
      
    m_ui_show_basecolor: BoolProperty(name="Show Base Color", default=True)  
    m_ui_show_normal: BoolProperty(name="Show Normal", default=True)  
    m_ui_show_bump: BoolProperty(name="Show Bump", default=True)  
    m_ui_show_metallic: BoolProperty(name="Show Metallic", default=True)  
    m_ui_show_roughness: BoolProperty(name="Show Roughness", default=True)  
    m_ui_show_emission: BoolProperty(name="Show Emission", default=True) 
  
#endregion [Scene Global]

#region [Included Classes & Property To Register]
#-------------------------------------------------
included_classes = (   
    #--------------------------------------------- 
    TM_Texture,
    #---------------------------------------------
    TM_Channel_Data,
    TM_Channel_Container,
    #---------------------------------------------
    TM_Texture_Export,
    TM_Mask,
    #---------------------------------------------
    TM_Node,
    TM_Node_Manager_Data,
    TM_Node_Manager,
    #---------------------------------------------
    TM_Brush_Data,
    #---------------------------------------------
    TM_User_Data_Manager,
    #---------------------------------------------
)
#-------------------------------------------------
def need_to_register():
    for cls in included_classes:
        bpy.utils.register_class(cls)
    #---------------------------------------------    
    Scene.TM_User_Data = PointerProperty(type=TM_User_Data_Manager)
#-------------------------------------------------
def need_to_unregister():
    if hasattr(Scene, 'TM_User_Data'): 
        delattr(bpy.types.Scene, 'TM_User_Data')
    #---------------------------------------------
    for cls in reversed(included_classes):
        bpy.utils.unregister_class(cls)
#-------------------------------------------------
#endregion [Included Classes & Property To Register]
