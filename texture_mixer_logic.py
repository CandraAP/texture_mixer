#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_logic.py                |
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
import bpy_extras
import os
import array
import hashlib
import random 
import numpy as np
#-------------------------------------------------
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import barycentric_transform
#-------------------------------------------------
from . import texture_mixer_property as tm_property
#-------------------------------------------------
# from dev_tools.texture_mixer_debug import Debug
#-------------------------------------------------
stamp_id        = tm_property.Addon_Data.m_addon_id_stamp
stamp_is_canvas = tm_property.Addon_Data.m_addon_is_canvas
#-------------------------------------------------
#endregion [IMPORT]

#region [Test Dummy]
def TM_Logic_Test_Dummy(context)->bool:
    """TM_Logic_Test_Dummy|For Quick Testing Purpose"""
    # debug_id = "LogicTestDummy"

    # Debug.Separator(debug_id)
    # Debug.Log("Test dummy .start", debug_id)
    # Debug.Log("Start", debug_id)
    ##-----------------------------------------
    ##region [Testing Content] ################
    ##-----------------------------------------
    
    ##-----------------------------------------
    ##endregion [Testing Content] #############
    ##-----------------------------------------
    # Debug.Log("Test dummy .finished", debug_id)
    # Debug.Separator(debug_id)
    return True
#endregion [Test Dummy]

#region [System ID]    
def TM_Logic_ID_Get_New(context) -> str:
    """TM_Logic_ID_Get_New"""
    # base_id = 202248 # My son's birthday 08 April 2022 
    user_data = context.scene.TM_User_Data  
    if user_data.m_system_base_id == 0:
        random_base_id = random.randint(1, 999999)
        user_data.m_system_base_id = random_base_id
        if not user_data.m_system_initial_id:
            random_init_id = random.randint(1, 999999)
            user_data.m_system_initial_id = f"{random_init_id:06}"
        
    user_data.m_system_counter_id += 1
    
    valid_id = user_data.m_system_base_id + user_data.m_system_counter_id
    
    full_id = f"{user_data.m_system_initial_id}_{valid_id:06}"
    
    return full_id

def TM_Logic_ID_Get_HashMD5(filepath: str, identifier_id: str|None = None) -> str|None:
    """TM_Logic_ID_Get_HashMD5"""

    if not os.path.exists(filepath):
        return None
    
    md5_hash = hashlib.md5()
    with open(filepath, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    
    result = md5_hash.hexdigest()

    if identifier_id:
        result = f"{result}_{identifier_id}"

    return result
#endregion [ID System]

#region [Object]
def TM_Logic_Object_Get_Active_One(context)-> bpy.types.Object | None:
    """TM_Logic_Object_Get_Active_One"""

    active_object = getattr(context, 'active_object', None)

    if not active_object:
        return None

    if active_object.type != 'MESH':
        return None
    
    if active_object.data is None:
        return None

    if active_object.mode not in {'OBJECT', 'TEXTURE_PAINT'}:
        return None
    
    return active_object 
#endregion [Object]

#region [Layer Manager]
def TM_Logic_LayerManager_Create_New(context) -> tm_property.TM_Node_Manager | None:
    """TM_Logic_LayerManager_Create_New""" 

    user_data = context.scene.TM_User_Data
    user_manager_container = user_data.m_managed_tm_node_manager_collection

    new_material = TM_Logic_Material_Create_New(context)
    if not new_material:
        return None

    main_shader_nodes = TM_Logic_ShaderNode_Get_By_Id(new_material, "Principled BSDF", True)
    if not main_shader_nodes:
        return None

    new_main_shader_id = TM_Logic_ID_Get_New(context)
    main_shader_nodes.name = new_main_shader_id
    main_shader_nodes.label = ""
    main_shader_nodes[stamp_id] = new_main_shader_id
        

    output_nodes = TM_Logic_ShaderNode_Get_By_Id(new_material, "Material Output", True)
    if not output_nodes:
        return None

    new_output_id = TM_Logic_ID_Get_New(context)
    output_nodes.name = new_output_id
    output_nodes.label = ""
    output_nodes[stamp_id] = new_output_id        

    system_composer_node = TM_Logic_ShaderNode_Get_From_Library(context, new_material, 'SYSTEM_COMPOSER')
    if not system_composer_node:
        return None        

    system_default_node = TM_Logic_ShaderNode_Get_From_Library(context, new_material, 'SYSTEM_DEFAULT')
    if not system_default_node:
        return None

    new_manager = user_manager_container.add()
    if not new_manager:
        return None

    new_manager.m_id = TM_Logic_ID_Get_New(context)
    new_manager.m_name = "New Layer Manager"
    new_manager.m_enable = True
    new_manager.m_managed_material_id = new_material.get(stamp_id)
    new_manager.m_shader_node_main_shader_id = new_main_shader_id
    new_manager.m_shader_node_output_id = new_output_id
    new_manager.m_shader_node_system_composer_id = system_composer_node["NODE_GROUP"].get(stamp_id)
    new_manager.m_shader_node_system_default_id = system_default_node["NODE_GROUP"].get(stamp_id)    

    return new_manager

def TM_Logic_LayerManager_Get_Active_Manager(context) -> tm_property.TM_Node_Manager | None:
    """TM_Logic_LayerManager_Get_Active_Manager"""

    active_object = TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return None
    
    material_slots = active_object.material_slots
    if material_slots:
        if len(material_slots) == 0:
            return None
        if material_slots[0].material is None: 
            return None
        if material_slots[0].material.get(stamp_id) is None:
            return None
    else:
        return None
    
    active_material_id = material_slots[0].material.get(stamp_id)
    if not active_material_id:
        return None

    user_data = context.scene.TM_User_Data

    manager_collection = user_data.m_managed_tm_node_manager_collection
    if not manager_collection or len (manager_collection) == 0:
        return None

    for manager in manager_collection:
        if manager.m_managed_material_id == active_material_id:
            if manager.m_enable:
                return manager
            break

    return None

def TM_logic_LayerManager_Get_By_Id(context, target_manager_id: str) -> tm_property.TM_Node_Manager | None:
    """TM_logic_LayerManager_Get_By_Id"""

    user_data = context.scene.TM_User_Data
    manager_collcetion = user_data.m_managed_tm_node_manager_collection

    for manager in manager_collcetion:
        if manager.m_id == target_manager_id:
            return manager
        
    return None

def TM_Logic_LayerManager_Get_Index_By_Id(context, target_manager_id: str) -> int|None:
    """TM_Logic_LayerManager_Get_Index_By_Id"""

    user_data = context.scene.TM_User_Data
    manager_collcetion = user_data.m_managed_tm_node_manager_collection
    for index, manager in enumerate(manager_collcetion):
        if manager.m_id == target_manager_id:
            return index
    
    return None

def TM_Logic_LayerManager_Set_Active_State(context, target_manager_id: str) -> bool:
    """TM_Logic_LayerManager_Set_Active_State"""

    if not target_manager_id:
        return False
    
    active_object = TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return False

    user_data = context.scene.TM_User_Data
    active_materials = active_object.data.materials

    target_manager = None
    manager_collection = user_data.m_managed_tm_node_manager_collection
    for index,manager in enumerate(manager_collection):
        for material in active_materials:
            if material is not None and material.get(stamp_id) == manager.m_managed_material_id:
                if manager.m_id == target_manager_id:
                    target_manager = manager
                    target_manager.m_enable = True
                    user_data.m_managed_tm_node_manager_pointer = index
                    break
                else:
                    manager.m_enable = False
                break
    if not target_manager:
        return False
            
    if target_manager.m_enable:
        target_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
        if not target_material:
            return False

        active_materials[0] = target_material

    return False

def TM_Logic_LayerManager_Change_Main_Shader(context, target_manager_id: str) -> bool:
    """TM_Logic_LayerManager_Change_Main_Shader"""

    active_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not active_manager:
        return False

    if active_manager.m_main_shader_type == active_manager.m_main_shader_type_cache:
        return False

    host_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if host_material is None:
        return False

    old_main_shader_id = active_manager.m_shader_node_main_shader_id

    if not TM_Logic_ShaderNode_Remove_Node_By_Id(host_material, old_main_shader_id):
        return False

    new_shader_idname = active_manager.m_main_shader_type_cache
    
    new_main_shader = TM_Logic_ShaderNode_Create_New_By_IdName(context, host_material, new_shader_idname)        
    if new_main_shader is None:
        return False

    active_manager.m_shader_node_main_shader_id = new_main_shader.get(stamp_id)
    active_manager.m_main_shader_type = active_manager.m_main_shader_type_cache

    return True

def TM_Logic_LayerManager_Remove_By_Id(context, target_manager_id: str) -> bool:
    """TM_Logic_LayerManager_Remove_By_Id"""

    active_object = getattr(context, 'active_object', None)
    if not active_object:
        return False

    if active_object.mode != 'OBJECT':
        return False        

    user_data = context.scene.TM_User_Data

    target_manager = None
    target_manager_index = -1
    manager_collection = user_data.m_managed_tm_node_manager_collection
    for index, manager in enumerate(manager_collection):
        if manager.m_id == target_manager_id:
            target_manager = manager
            target_manager_index = index
            break
    
    if not target_manager:
        return False
    
    target_host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not target_host_material:
        return False
    
    layer_collection = target_manager.m_managed_tm_node_collection
    if len(layer_collection) > 0:
        layer_to_remove_list = []
        for layer in layer_collection:
            layer_to_remove_list.append(layer.m_id)

        for layer_id in layer_to_remove_list:
            TM_Logic_Layer_Remove_By_Id(context,target_manager.m_id, layer_id)

    TM_Logic_ShaderNode_Remove_Node_By_Id(target_host_material, target_manager.m_shader_node_system_default_id)
    TM_Logic_ShaderNode_Remove_Node_By_Id(target_host_material, target_manager.m_shader_node_system_composer_id)

    material_id = target_host_material.get(stamp_id)
    TM_Logic_Material_Remove_By_Id(context, material_id)

    user_data.m_managed_tm_node_manager_collection.remove(target_manager_index)

    new_count = len(user_data.m_managed_tm_node_manager_collection)
    if new_count == 0:
        target_manager.m_managed_tm_node_pointer = 0
    else:
        if user_data.m_managed_tm_node_manager_pointer >= new_count:
            user_data.m_managed_tm_node_manager_pointer = new_count - 1
        elif target_manager_index < user_data.m_managed_tm_node_manager_pointer:
            user_data.m_managed_tm_node_manager_pointer -= 1
    user_data.m_managed_tm_node_manager_pointer = max(0, user_data.m_managed_tm_node_manager_pointer)

    return True
#endregion [Layer Manager]

#region [Layer]
def TM_Logic_Layer_Create_New(context, layer_type: str) -> tm_property.TM_Node|None:
    """TM_Logic_Layer_Create_New"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None

    host_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return None
    
    channels_metadata = tm_property.TM_DT_Channels_Metadata

    layer_system = active_manager.m_managed_tm_node_collection

    new_id = TM_Logic_ID_Get_New(context)

    new_layer = layer_system.add()  
    new_layer.m_id = new_id
    new_layer.m_group_id = ""
    new_layer.m_tm_node_manager_id = active_manager.m_id

    for channel_name, channel_data in channels_metadata.items():
        init = channel_data['default_init']
        if hasattr(new_layer.m_channel, f"m_channel_{init}"):
            prop = getattr(new_layer.m_channel, f"m_channel_{init}", None)
            if prop:
                prop.m_name = channel_name

    new_layer.m_type = layer_type
    if new_layer.m_type == 'LAYER_PAINTABLE':
        new_layer.m_name = "New Paint Layer "
    elif new_layer.m_type == 'LAYER_PRESERVED':
        new_layer.m_name = "New Fill Layer"
    elif new_layer.m_type == 'GROUP':
        new_layer.m_name = "New Group"

    if new_layer.m_type == 'GROUP':
        system_layer_data = TM_Logic_ShaderNode_Get_From_Library(context,host_material,'SYSTEM_FOLDER')
    else:
        system_layer_data = TM_Logic_ShaderNode_Get_From_Library(context,host_material,'SYSTEM_LAYER') 
    
    if not system_layer_data:
        return None
        
    if new_layer.m_type == 'LAYER_PRESERVED':
        texture_mapping_data = TM_Logic_ShaderNode_Get_From_Library(context, host_material, 'SYSTEM_TEXTURE_MAPPING')
        if not texture_mapping_data:
            return None

        texture_mapping_node = texture_mapping_data['NODE_GROUP']
        if not texture_mapping_node:
            return None

        new_layer.m_shader_node_system_texture_mapping_id = texture_mapping_node.get(stamp_id)              

    system_layer_node = system_layer_data['NODE_GROUP']
    if not system_layer_node:
        return None

    new_layer.m_shader_node_system_layer_id = system_layer_node.get(stamp_id) 

    if new_layer.m_type == 'LAYER_PAINTABLE':
        alpha_socket =  system_layer_node.inputs.get("Base Color Alpha")
        alpha_socket.default_value = 0.0 
    
    return new_layer 

def TM_Logic_Layer_Get_Active_Layer(context) -> tm_property.TM_Node|None:
    """TM_Logic_Layer_Get_Active_Layer"""

    target_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not target_manager:
        return None

    layer_collection = target_manager.m_managed_tm_node_collection
    if len(layer_collection) == 0:
        return None

    if 0 <= target_manager.m_managed_tm_node_pointer < len(layer_collection):
        layer = layer_collection[target_manager.m_managed_tm_node_pointer]
        if layer:
            return layer

    return None

def TM_Logic_Layer_Paint_Get_Blank_Canvas(context, target_manager_id: str, target_layer_id: str, channel_name: str) -> str|None:
    """TM_Logic_Layer_Paint_Get_Blank_Canvas"""

    target_layer = TM_Logic_Layer_Get_By_Id(context, target_manager_id, target_layer_id)
    if not target_layer:
        return False
    
    if target_layer.m_type != 'LAYER_PAINTABLE':
        return False
    
    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False
    
    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False
            
    system_layer_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_layer.m_shader_node_system_layer_id)
    if not system_layer_node:
        return False
    
    supported_channels      = tm_property.TM_DT_Channels_Metadata
    channel_data            = supported_channels.get(channel_name)
    if not channel_data:
        return False
    
    channel_prop            = f"m_channel_{channel_data['default_init']}"
    channel_texture_data    = channel_data["default_blank_canvas"]
    channel_socket_pairs    = channel_data["default_system_sockets"]
    channel_color_space     = channel_data["default_color_space"]


    channel = getattr(target_layer.m_channel, channel_prop)
    if not channel:
        return False

    tm_texture                                          = TM_Logic_TMTexture_Create_New(context)
    virtual_node_name                                   = tm_texture.m_shader_node_virtual_texture_name
    system_texture_data                                 = TM_Logic_ShaderNode_Get_From_Library(context, host_material,'SYSTEM_TEXTURE', [virtual_node_name])
    system_texture_node                                 = system_texture_data['NODE_GROUP']

    tm_texture.m_shader_node_system_texture_id          = system_texture_node.get(stamp_id)
    channel.m_tm_texture_id                             = tm_texture.m_id

    resolution_preserve_texture                         = TM_Logic_Utility_Get_Resolution_From_Preset(target_manager.m_preserved_resolution)
    resolution_virtual_texture                          = TM_Logic_Utility_Get_Resolution_From_Preset(target_manager.m_virtual_resolution)

    shader_node_virtual_texture                         = system_texture_data[virtual_node_name]

    preserve_texture_image                              = TM_Logic_Image_Generate_New(context, resolution_preserve_texture, channel_texture_data[0], channel_texture_data[1], channel_texture_data[2], channel_color_space)
    virtual_texture_image                               = TM_Logic_Image_Generate_New(context, resolution_virtual_texture, channel_texture_data[0], channel_texture_data[1], channel_texture_data[2], channel_color_space)
    
    preserve_texture_image.alpha_mode                   = 'STRAIGHT'
    virtual_texture_image.alpha_mode                    = 'STRAIGHT'

    preserve_texture_image.update()
    virtual_texture_image.update()

    preserve_texture_image.pack()
    virtual_texture_image.pack()

    shader_node_virtual_texture.image                   = virtual_texture_image               
    shader_node_virtual_texture.interpolation           = 'Linear'     

    tm_texture.m_preserved_texture_size                 = resolution_preserve_texture
    tm_texture.m_virtual_texture_size                   = resolution_virtual_texture

    tm_texture.m_preserved_texture_id                   = preserve_texture_image.get(stamp_id)
    tm_texture.m_virtual_texture_id                     = virtual_texture_image.get(stamp_id)

    for pair in channel_socket_pairs:
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_texture_node, system_layer_node, pair[0], pair[1] )

    return tm_texture.m_id
    
def TM_Logic_Layer_Get_By_Id(context, target_manager_id: str, target_layer_id: str) -> tm_property.TM_Node|None:
    """TM_Logic_Layer_Get_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return None
    
    target_layer = None
    collection_layer = target_manager.m_managed_tm_node_collection
    for layer in collection_layer:
        if layer.m_id == target_layer_id:
            target_layer = layer
            break

    if not target_layer:
        return None

    return layer

def TM_Logic_Layer_Get_Index_By_Id(context, target_manager_id: str, target_layer_id: int) -> int|None:
    """TM_Logic_Layer_Get_Index_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return None
    
    collection_layer = target_manager.m_managed_tm_node_collection
    for index, layer in enumerate(collection_layer):
        if layer.m_id == target_layer_id:
            return index

    return None

def TM_Logic_Layer_Link_Disconnect_All_Sockets(context, target_manager_id: str) -> bool:
    """TM_Logic_Layer_Link_Disconnect_All_Sockets"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False

    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False

    main_shader_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_main_shader_id)
    if not main_shader_node:
        return False

    output_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_output_id)
    if not output_node:
        return False

    system_composer_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_system_composer_id)
    if not system_composer_node:
        return False
    
    system_default_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_system_default_id)
    if not system_default_node:
        return False          

    # main shader node
    if target_manager.m_main_shader_type == 'ShaderNodeBsdfPrincipled': 
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Base Color", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Metallic", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Roughness", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Alpha", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Normal", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Emission Color", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Emission Strength", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"BSDF", False)
    
    elif target_manager.m_main_shader_type == 'ShaderNodeBsdfDiffuse': 
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Color", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Roughness", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"Normal", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, main_shader_node,"BSDF", False)

    # composer node
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Base Color", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Metallic", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Roughness", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Alpha", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Bump", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Normal", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Default Emission", True)
    
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Base Color", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Metallic", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Roughness", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Alpha", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Bump", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Normal", True)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Input Emission", True)
    
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Base Color", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Metallic", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Roughness", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Alpha", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Normal", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Emission Color", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_composer_node,"Output Emission Strength", False)

    # layer node
    layer_collection = target_manager.m_managed_tm_node_collection
    for layer_index, current_layer in enumerate(layer_collection):
        if current_layer is None:
            return False

        current_layer_node = TM_Logic_ShaderNode_Get_By_Id(host_material, current_layer.m_shader_node_system_layer_id)
        if not current_layer_node:
            return False   
        
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Alpha Tetangga", True)      
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Base Color", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Metallic", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Roughness", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Alpha", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Bump", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Normal", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Emission", True)
        
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Alpha Tetangga", False)      
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Base Color", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Metallic", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Roughness", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Alpha", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Bump", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Normal", False)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Emission", False)

        if current_layer.m_type == 'GROUP':                 
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Base Color", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Metallic", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Roughness", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Alpha", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Bump", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Normal", False)
            TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Output Emission", False)
    
    # default node
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Base Color", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Metallic", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Roughness", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Alpha", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Bump", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Normal", False)
    TM_Logic_ShaderNode_Socket_Disconnector(host_material, system_default_node,"Output Emission", False)

    return True

def TM_Logic_Layer_Link_Reconnect_All_Sockets(context, target_manager_id: str) -> bool:
    """TM_Logic_Layer_Link_Reconnect_All_Sockets"""   

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False

    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False

    main_shader_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_main_shader_id)
    if not main_shader_node:
        return False

    output_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_output_id)
    if not output_node:
        return False

    system_composer_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_system_composer_id)
    if not system_composer_node:
        return False
    
    system_default_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_manager.m_shader_node_system_default_id)
    if not system_default_node:
        return False                    

    if system_composer_node:        
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Base Color", "Default Base Color")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Metallic", "Default Metallic")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Roughness", "Default Roughness")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Alpha", "Default Alpha")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Bump", "Default Bump")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Normal", "Default Normal")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Emission", "Default Emission")

        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Base Color", "Input Base Color")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Metallic", "Input Metallic")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Roughness", "Input Roughness")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Alpha", "Input Alpha")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Bump", "Input Bump")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Normal", "Input Normal")
        TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, system_composer_node,"Output Emission", "Input Emission")

    if main_shader_node:
        if target_manager.m_main_shader_type == 'ShaderNodeBsdfPrincipled':       
            TM_Logic_ShaderNode_Socket_Linker(host_material, main_shader_node, output_node,"BSDF", "Surface")
            
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Base Color", "Base Color")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Metallic", "Metallic")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Roughness", "Roughness")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Alpha", "Alpha")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Normal", "Normal")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Emission Color", "Emission Color")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Emission Strength", "Emission Strength")
        
        elif target_manager.m_main_shader_type == 'ShaderNodeBsdfDiffuse': 
            TM_Logic_ShaderNode_Socket_Linker(host_material, main_shader_node, output_node,"BSDF", "Surface")

            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Base Color", "Color")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Roughness", "Roughness")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_composer_node, main_shader_node,"Output Normal", "Normal")

    layer_collection = target_manager.m_managed_tm_node_collection
    last_index = len(layer_collection)-1
    upper_layer = None  
    upper_layer_node = None

    for layer_index, current_layer in enumerate(layer_collection):
        if current_layer is None:
            return False
        
        current_layer_node = TM_Logic_ShaderNode_Get_By_Id(host_material, current_layer.m_shader_node_system_layer_id)
        if not current_layer_node:
            return False    
        
        # set default link relationship
        if system_default_node:
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Base Color", "Input Base Color")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Metallic", "Input Metallic")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Roughness", "Input Roughness")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Alpha", "Input Alpha")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Bump", "Input Bump")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Normal", "Input Normal")
            TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Emission", "Input Emission")

            if current_layer.m_type == 'GROUP':
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Base Color", "Managed Base Color")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Metallic", "Managed Metallic")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Roughness", "Managed Roughness")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Alpha", "Managed Alpha")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Bump", "Managed Bump")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Normal", "Managed Normal")
                TM_Logic_ShaderNode_Socket_Linker(host_material, system_default_node, current_layer_node,"Output Emission", "Managed Emission")
                
                TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Managed Alpha", True)
                current_layer_node.inputs["Managed Alpha"].default_value = 0.0
            else:            
                if current_layer.m_group_id:
                    TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Alpha", True)

            if current_layer.m_type == 'LAYER_PAINTABLE':
                if layer_index != last_index:
                    TM_Logic_ShaderNode_Socket_Disconnector(host_material, current_layer_node,"Input Alpha", True)
                    current_layer_node.inputs["Input Alpha"].default_value = 0.0

        # overwrite default link
        if upper_layer is None: 
            if system_composer_node:
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Base Color", "Input Base Color")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Metallic", "Input Metallic")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Roughness", "Input Roughness")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Alpha", "Input Alpha")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Bump", "Input Bump")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Normal", "Input Normal")
                TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, system_composer_node,"Output Emission", "Input Emission")
            else:
                return False
        else:
            if upper_layer.m_type == 'GROUP':
                if current_layer.m_type == 'GROUP':                   
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha Tetangga", "Input Alpha Tetangga") 
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Base Color", "Input Base Color")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Metallic", "Input Metallic")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Roughness", "Input Roughness")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha", "Input Alpha")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Bump", "Input Bump")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Normal", "Input Normal")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Emission", "Input Emission")                                    
                else:
                    if upper_layer.m_id == current_layer.m_group_id:    
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha Tetangga", "Input Alpha Tetangga")    
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Base Color", "Managed Base Color")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Metallic", "Managed Metallic")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Roughness", "Managed Roughness")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha", "Managed Alpha")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Bump", "Managed Bump")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Normal", "Managed Normal")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Emission", "Managed Emission")
                    else:
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha Tetangga", "Input Alpha Tetangga") 
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Base Color", "Input Base Color")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Metallic", "Input Metallic")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Roughness", "Input Roughness")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha", "Input Alpha")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Bump", "Input Bump")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Normal", "Input Normal")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Emission", "Input Emission")  
            else:
                if current_layer.m_type == 'GROUP':         
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha Tetangga", "Input Alpha Tetangga") 
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Base Color", "Input Base Color")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Metallic", "Input Metallic")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Roughness", "Input Roughness")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha", "Input Alpha")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Bump", "Input Bump")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Normal", "Input Normal")
                    TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Emission", "Input Emission") 
                else:
                    if upper_layer.m_group_id and upper_layer.m_group_id != current_layer.m_group_id:
                        target_group = TM_Logic_Layer_Get_By_Id(context, target_manager.m_id, upper_layer.m_group_id)
                        target_group_node = TM_Logic_ShaderNode_Get_By_Id(host_material, target_group.m_shader_node_system_layer_id) 

                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Alpha Tetangga", "Input Alpha Tetangga")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Base Color", "Input Base Color")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Metallic", "Input Metallic")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Roughness", "Input Roughness")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Alpha", "Input Alpha")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Bump", "Input Bump")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Normal", "Input Normal")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, target_group_node,"Output Emission", "Input Emission")   
                    else:        
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha Tetangga", "Input Alpha Tetangga")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Base Color", "Input Base Color")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Metallic", "Input Metallic")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Roughness", "Input Roughness")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Alpha", "Input Alpha")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Bump", "Input Bump")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Normal", "Input Normal")
                        TM_Logic_ShaderNode_Socket_Linker(host_material, current_layer_node, upper_layer_node,"Output Emission", "Input Emission")                                     
                        
        upper_layer = current_layer
        upper_layer_node = current_layer_node
        
    return True    

def TM_Logic_Layer_Refresh_ShaderNode(context, target_manager_id: str) -> bool:
    """TM_Logic_Layer_Refresh_ShaderNode"""

    shading = TM_Logic_Utility_Viewport_Get_Shading()
    if shading:
        original_shading = shading.type
        shading.type = 'SOLID'
        
    TM_Logic_Layer_Link_Disconnect_All_Sockets(context, target_manager_id)
    TM_Logic_Layer_Link_Reconnect_All_Sockets(context, target_manager_id)

    TM_Logic_Utility_Viewport_Refresh(context)
    shading.type = original_shading
    
    return True

def TM_Logic_Layer_Remove_By_Id(context, target_manager_id: str, target_layer_id: str) -> bool:
    """TM_Logic_Layer_Remove_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False

    target_host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not target_host_material:
        return False
    
    layer_collection = target_manager.m_managed_tm_node_collection
    target_layer = None
    target_layer_index = -1
    for index, layer in enumerate(layer_collection):
        if layer.m_id == target_layer_id:
            target_layer = layer
            target_layer_index = index
            break
                
    if not target_layer:
        return False
    
    if target_layer.m_type == 'GROUP':
        group_id = target_layer.m_id            
        for i in range(target_layer_index + 1, len(layer_collection)):
            child_layer = layer_collection[i]                
            if child_layer.m_group_id == group_id:
                child_layer.m_group_id = ""
            else:
                break
    
    mask_collection = target_layer.m_managed_tm_mask_collection

    if len(mask_collection) > 0:
        mask_to_remove_list = []
        for mask in mask_collection:
            if mask.m_tm_node_host_id == target_layer.m_id:
                mask_to_remove_list.append(mask.m_id)

        for mask_id in mask_to_remove_list:
            TM_Logic_Mask_Remove_By_Id(context, target_manager_id, target_layer_id, mask_id)

    layer_channels = target_layer.m_channel

    # region [channels]
    supprted_channels = tm_property.TM_DT_Channels_Metadata.values()
    for channel in supprted_channels:
        prop = f"m_channel_{channel.get('default_init')}"
        if not prop:
            continue
        value = getattr(layer_channels, prop)
        if not value:
            continue
        if value.m_tm_texture_id:
            TM_Logic_TMTexture_Remove_By_Id(context, target_manager_id, value.m_tm_texture_id)       
    # endregion [channels]
    
    if target_layer.m_shader_node_system_texture_mapping_id:
        TM_Logic_ShaderNode_Remove_Node_By_Id(target_host_material, target_layer.m_shader_node_system_texture_mapping_id)

    if target_layer.m_shader_node_system_layer_id:
        TM_Logic_ShaderNode_Remove_Node_By_Id(target_host_material, target_layer.m_shader_node_system_layer_id)
    
    layer_name = target_layer.m_name
    layer_id = target_layer.m_id

    layer_collection.remove(target_layer_index)

    new_count = len(target_manager.m_managed_tm_node_collection)
    if new_count == 0:
        target_manager.m_managed_tm_node_pointer = 0
    else:
        if target_manager.m_managed_tm_node_pointer >= new_count:
            target_manager.m_managed_tm_node_pointer = new_count - 1
        elif target_layer_index < target_manager.m_managed_tm_node_pointer:
            target_manager.m_managed_tm_node_pointer -= 1
    target_manager.m_managed_tm_node_pointer = max(0, target_manager.m_managed_tm_node_pointer)

    return True

def TM_Logic_Layer_Paint_Mode_Get_Active_Channel_Data(context) -> list|None:
    """TM_Logic_Layer_Paint_Mode_Get_Active_Channel_Data"""

    active_layer = TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return None
    
    if active_layer.m_type != 'LAYER_PAINTABLE':     
        return None
    
    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None
    
    active_material = TM_Logic_Material_Get_Active_Material(context)
    if not active_material:
        return None
    
    channel_set = tm_property.TM_DT_Channels_Metadata.values()
    canvas_data = []   

    for set in channel_set:
        channel_name = set.get('default_name')
        channel_init = set.get('default_init')

        get_channel_data = getattr(active_layer.m_channel, f"m_channel_{channel_init}")
        get_channel_activation = getattr(active_manager, f"m_channel_{channel_init}_enable")

        if not get_channel_activation:
            continue

        texture_container_id = get_channel_data.m_tm_texture_id
        
        if not texture_container_id:
            texture_container_id = TM_Logic_Layer_Paint_Get_Blank_Canvas(context, active_manager.m_id, active_layer.m_id, channel_name)
            if not texture_container_id:
                return None
            
        texture_container = TM_Logic_TMTexture_Get_By_Id(context, active_manager.m_id, texture_container_id)
        if not texture_container:
            return None
        
        switching_to_canvas = TM_Logic_TMTexture_Switch_To_Preserved(context, active_manager.m_id, texture_container_id)
        if not switching_to_canvas:
            return None
        
        canvas_image = TM_Logic_Image_Get_By_Id(texture_container.m_preserved_texture_id)
        if not canvas_image:
            return None    
        
        if not stamp_is_canvas in canvas_image:
            canvas_image[stamp_is_canvas] = True

        canvas_data.append({
            'channel_index': -1,
            'channel_name': channel_name, 
            'channel_init': channel_init, 
            'channel_image_name': canvas_image.name,
            'channel_color_neutral': set.get('channel_color_neutral'),
            'default_color_space': set.get('default_color_space'),
            'manager_id': active_manager.m_id,
            'layer_id': active_layer.m_id,
            'channel_tmtexture_id': texture_container_id,
            'channel_image_id': texture_container.m_preserved_texture_id,
            'channel_proxy_id': texture_container.m_virtual_texture_id,
            'channel_node_system_id' : texture_container.m_shader_node_system_texture_id,
            'channel_node_texture_name' : texture_container.m_shader_node_virtual_texture_name,
        })  
    
    context.view_layer.update()
                
    return canvas_data
#endregion [Layer]

#region [MASK]
def TM_Logic_Mask_Create_New(context, mask_type: str, white_baground: bool = True) -> tm_property.TM_Mask | None:
    """TM_Logic_Mask_Create_New"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None

    host_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return None
    
    active_layer = TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return None
    
    mask_collection = active_layer.m_managed_tm_mask_collection

    new_mask = mask_collection.add()
    new_mask.m_id = TM_Logic_ID_Get_New(context)
    new_mask.m_tm_node_host_id = active_layer.m_id
    new_mask.m_tm_node_manager_id = active_manager.m_id
    new_mask.m_type = mask_type

    if new_mask.m_type == 'MASK_PAINTABLE':
        new_mask.m_name = "New Paint Mask"
    elif new_mask.m_type == 'MASK_PRESERVED':
        new_mask.m_name = "New Fill Mask"     

    mask_system_data = TM_Logic_ShaderNode_Get_From_Library(context, host_material, 'SYSTEM_MASK', [new_mask.m_shader_node_blending_node_name])
    if not mask_system_data:
        return None        
    
    new_mask_shader_node = mask_system_data['NODE_GROUP']
    new_mask_shader_node_blend = mask_system_data[new_mask.m_shader_node_blending_node_name]

    new_mask.m_shader_node_system_mask_id =  new_mask_shader_node.get(stamp_id)
    new_mask_shader_node_blend.blend_type = new_mask.m_blending_mode 

    if new_mask.m_type == 'MASK_PAINTABLE':
        tm_texture                                          = TM_Logic_TMTexture_Create_New(context)
        new_mask.m_tm_texture_id                            = tm_texture.m_id

        virtual_node_name                                   = tm_texture.m_shader_node_virtual_texture_name
        system_texture_data                                 = TM_Logic_ShaderNode_Get_From_Library(context, host_material,'SYSTEM_TEXTURE', [virtual_node_name])

        system_texture_shader_node                          = system_texture_data['NODE_GROUP']
        virtual_texture_shader_node                         = system_texture_data[virtual_node_name]

        tm_texture.m_shader_node_system_texture_id          = system_texture_shader_node.get(stamp_id)            

        resolution_preserve_texture                         = TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_preserved_resolution)
        resolution_virtual_texture                          = TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_virtual_resolution)
        
        if white_baground:
            preserve_texture_image                          = TM_Logic_Image_Generate_New(context, resolution_preserve_texture, (1.0,1.0,1.0,1.0), False, True, 'Non-Color')
            virtual_texture_image                           = TM_Logic_Image_Generate_New(context, resolution_virtual_texture, (1.0,1.0,1.0,1.0), False, True, 'Non-Color')
        else:
            preserve_texture_image                          = TM_Logic_Image_Generate_New(context, resolution_preserve_texture, (0.0,0.0,0.0,1.0), False, True, 'Non-Color')
            virtual_texture_image                           = TM_Logic_Image_Generate_New(context, resolution_virtual_texture, (0.0,0.0,0.0,1.0), False, True, 'Non-Color')
        
        preserve_texture_image.alpha_mode                   = 'STRAIGHT'
        virtual_texture_image.alpha_mode                    = 'STRAIGHT'

        preserve_texture_image.update()
        virtual_texture_image.update()

        preserve_texture_image.pack()
        virtual_texture_image.pack()

        virtual_texture_shader_node.image                   = virtual_texture_image
        virtual_texture_shader_node.interpolation           = 'Linear'

        tm_texture.m_preserved_texture_size                 = resolution_preserve_texture
        tm_texture.m_virtual_texture_size                   = resolution_virtual_texture

        tm_texture.m_preserved_texture_id                   = preserve_texture_image.get(stamp_id)
        tm_texture.m_virtual_texture_id                     = virtual_texture_shader_node.image.get(stamp_id)

        TM_Logic_ShaderNode_Socket_Linker(host_material, system_texture_shader_node, new_mask_shader_node, "Color", "Mask Texture")        
        
    new_mask_index = len(active_layer.m_managed_tm_mask_collection) - 1

    if len(active_layer.m_managed_tm_mask_collection) > 0 and new_mask_index > 0 and active_layer.m_managed_tm_mask_pointer != new_mask_index:
        active_layer.m_managed_tm_mask_collection.move(active_layer.m_managed_tm_mask_pointer, new_mask_index)   

    return new_mask

def TM_Logic_Mask_Get_Active_Mask(context,  target_manager_id: str, target_layer_id: str) -> tm_property.TM_Mask|None:
    """TM_Logic_Mask_Get_Active_Mask"""

    target_layer = TM_Logic_Layer_Get_By_Id(context, target_manager_id, target_layer_id)
    if not target_layer:
        return None
    
    mask_collection = target_layer.m_managed_tm_mask_collection
    mask_pointer = target_layer.m_managed_tm_mask_pointer
    
    if mask_pointer < 0 or mask_pointer >= len(mask_collection):
        return None
    
    active_mask = mask_collection[mask_pointer]
    if not active_mask:
        return None
    
    return active_mask

def TM_Logic_Mask_Get_By_Id(context, layer_manager_id: str, layer_id: str, mask_id: str) -> tm_property.TM_Mask|None:
    """TM_Logic_Mask_Get_By_Id"""

    target_layer = TM_Logic_Layer_Get_By_Id(context, layer_manager_id, layer_id)
    if not target_layer:
        return False     
    
    for mask in target_layer.m_managed_tm_mask_collection:
        if mask.m_id == mask_id:
            return mask
        
    return None
        
def TM_Logic_Mask_Link_Disconnect_All_Sockets(context, target_manager_id: str, target_layer_id: str)->bool:
    """TM_Logic_Mask_Link_Disconnect_All_Sockets"""

    active_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not active_manager:
        return False

    host_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return False 
    
    active_layer = TM_Logic_Layer_Get_By_Id(context, active_manager.m_id, target_layer_id)
    if not active_layer:
        return False
    
    active_mask_layer = active_layer.m_managed_tm_mask_collection
    if not active_mask_layer:
        return False
    
    for mask in active_mask_layer:
        mask_shader_node = TM_Logic_ShaderNode_Get_By_Id(host_material, mask.m_shader_node_system_mask_id)
        if not mask_shader_node:
            return False            
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, mask_shader_node, "Input Value", True)
        TM_Logic_ShaderNode_Socket_Disconnector(host_material, mask_shader_node, "Output Value", False)

    return True

def TM_Logic_Mask_Link_Reconnect_All_Sockets(context, target_manager_id: str, target_layer_id: str)->bool:
    """TM_Logic_Mask_Link_Reconnect_All_Sockets"""

    active_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not active_manager:
        return False

    host_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return False 
    
    active_layer = TM_Logic_Layer_Get_By_Id(context, active_manager.m_id, target_layer_id)
    if not active_layer:
        return False
    
    active_layer_shader_node = TM_Logic_ShaderNode_Get_By_Id(host_material, active_layer.m_shader_node_system_layer_id)
    if not active_layer_shader_node:
        return False
    
    active_mask_layer = active_layer.m_managed_tm_mask_collection
    if not active_mask_layer:
        return False

    previouse_mask_shader_node = None
    for index, mask in enumerate(active_mask_layer):
        mask_shader_node = TM_Logic_ShaderNode_Get_By_Id(host_material, mask.m_shader_node_system_mask_id)
        if not mask_shader_node:
            return False
        
        if index == 0:
            if active_layer.m_type == 'GROUP':
                TM_Logic_ShaderNode_Socket_Linker(host_material, mask_shader_node, active_layer_shader_node, "Output Value", "Managed Mask")
            else:                    
                TM_Logic_ShaderNode_Socket_Linker(host_material, mask_shader_node, active_layer_shader_node, "Output Value", "Mask Value")    
        else:                
            if previouse_mask_shader_node:
                TM_Logic_ShaderNode_Socket_Linker(host_material, mask_shader_node, previouse_mask_shader_node, "Output Value", "Input Value")   
                
        previouse_mask_shader_node = mask_shader_node

    return True

def TM_Logic_Mask_Refresh_ShaderNode(context, target_manager_id: str, target_layer_id: str) -> bool:
    """TM_Logic_Mask_Refresh_ShaderNode"""

    shading = TM_Logic_Utility_Viewport_Get_Shading()
    if shading:
        original_shading = shading.type
        shading.type = 'SOLID'
        
    TM_Logic_Mask_Link_Disconnect_All_Sockets(context, target_manager_id, target_layer_id)
    TM_Logic_Mask_Link_Reconnect_All_Sockets(context, target_manager_id, target_layer_id)

    TM_Logic_Utility_Viewport_Refresh(context)
    shading.type = original_shading
    
    return True

def TM_Logic_Mask_Remove_By_Id(context,layer_manager_id: str, layer_id: str, mask_id: str) -> bool:
    """TM_Logic_Mask_Remove_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, layer_manager_id)
    if not target_manager:
        return False
    
    target_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not target_material:
        return False

    target_layer = TM_Logic_Layer_Get_By_Id(context, layer_manager_id, layer_id)
    if not target_layer:
        return False     

    target_mask = None
    target_mask_index = -1
    for index, mask in enumerate(target_layer.m_managed_tm_mask_collection):
        if mask.m_id == mask_id:
            target_mask = mask
            target_mask_index = index
            break

    if not target_mask:
        return False

    if target_mask.m_tm_texture_id:
        TM_Logic_TMTexture_Remove_By_Id(context,target_mask.m_tm_node_manager_id, target_mask.m_tm_texture_id)

    if target_mask.m_shader_node_system_mask_id:
        TM_Logic_ShaderNode_Remove_Node_By_Id(target_material, target_mask.m_shader_node_system_mask_id)

    target_layer.m_managed_tm_mask_collection.remove(target_mask_index)
    
    new_count = len(target_layer.m_managed_tm_mask_collection)
    if new_count == 0:
        target_layer.m_managed_tm_mask_pointer = 0
    else:
        if target_layer.m_managed_tm_mask_pointer >= new_count:
            target_layer.m_managed_tm_mask_pointer = new_count - 1
        elif target_mask_index < target_layer.m_managed_tm_mask_pointer:
            target_layer.m_managed_tm_mask_pointer -= 1
    target_layer.m_managed_tm_mask_pointer = max(0, target_layer.m_managed_tm_mask_pointer)

    return True

def TM_Logic_Mask_Paint_Mode_Get_Active_Mask_Data(context) -> list|None:
    """TM_Logic_Mask_Paint_Mode_Get_Active_Mask_Data"""

    active_layer = TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return None
    
    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None
    
    active_material = TM_Logic_Material_Get_Active_Material(context)
    if not active_material:
        return None
    
    active_mask = TM_Logic_Mask_Get_Active_Mask(context, active_manager.m_id, active_layer.m_id)
    if not active_mask:
        return None
    
    canvas_data = []   
    
    texture_container_id = active_mask.m_tm_texture_id
        
    texture_container = TM_Logic_TMTexture_Get_By_Id(context, active_manager.m_id, texture_container_id)
    if not texture_container:
        return None
    
    switching_to_canvas = TM_Logic_TMTexture_Switch_To_Preserved(context, active_manager.m_id, texture_container_id)
    if not switching_to_canvas:
        return None
    
    canvas_image = TM_Logic_Image_Get_By_Id(texture_container.m_preserved_texture_id)
    if not canvas_image:
        return None    
    
    if not stamp_is_canvas in canvas_image:
            canvas_image[stamp_is_canvas] = True

    canvas_data.append({
        'channel_index': -1,
        'channel_name': "Mask", 
        'channel_init': "mask", 
        'channel_image_name': canvas_image.name,
        'channel_color_neutral': (0.0, 0.0, 0.0, 1.0),
        'default_color_space': 'Non-Color',
        'manager_id': active_manager.m_id,
        'layer_id': active_layer.m_id,
        'mask_id': active_mask.m_id,
        'channel_tmtexture_id': texture_container_id,
        'channel_image_id': texture_container.m_preserved_texture_id,
        'channel_proxy_id': texture_container.m_virtual_texture_id,
        'channel_node_system_id' : texture_container.m_shader_node_system_texture_id,
        'channel_node_texture_name' : texture_container.m_shader_node_virtual_texture_name,
    }) 
    
    context.view_layer.update()
                
    return canvas_data
#endregion [MASK]

#region [TM Texture]
def TM_Logic_TMTexture_Create_New(context, target_manager_id: str|None = None) -> tm_property.TM_Texture | None:
    """TM_Logic_TMTexture_Create_New"""

    if target_manager_id:
        target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    else:
        target_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not target_manager:
        return None

    tm_texture_collection = target_manager.m_managed_tm_texture_collection

    tm_texture = tm_texture_collection.add()
    tm_texture.m_id = TM_Logic_ID_Get_New(context)

    return tm_texture

def TM_Logic_TMTexture_Get_By_Id(context, target_manager_id: str, tm_texture_id:str) -> tm_property.TM_Texture|None:
    """TM_Logic_TMTexture_Get_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if target_manager is None:
        return None

    texture_manager = target_manager.m_managed_tm_texture_collection
    if len(texture_manager) == 0:
        return None

    for texture in texture_manager:
        if texture.m_id == tm_texture_id:
            return texture
    
    return None

def TM_Logic_TMTexture_Switch_To_Preserved(context, target_manager_id: str, target_tm_texture_id: str) -> bool:
    """TM_Logic_TMTexture_Switch_To_Preserved"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False
    
    target_tm_texture = TM_Logic_TMTexture_Get_By_Id(context, target_manager_id, target_tm_texture_id)
    if not target_tm_texture: 
        return False
    
    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False
    
    visual_node = TM_Logic_ShaderNode_Get_Group_Internal_Node(host_material, target_tm_texture.m_shader_node_system_texture_id, target_tm_texture.m_shader_node_virtual_texture_name)
    if not visual_node:
        return False
    
    preserved_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_preserved_texture_id)
    if not preserved_image:
        return False
    
    visual_node.image = preserved_image

    return True

def TM_Logic_TMTexture_Switch_To_Virtual(context, target_manager_id: str, target_tm_texture_id: str) -> bool:
    """TM_Logic_TMTexture_Switch_To_Virtual"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False
    
    target_tm_texture = TM_Logic_TMTexture_Get_By_Id(context, target_manager_id, target_tm_texture_id)
    if not target_tm_texture: 
        return False
    
    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False
    
    visual_node = TM_Logic_ShaderNode_Get_Group_Internal_Node(host_material, target_tm_texture.m_shader_node_system_texture_id, target_tm_texture.m_shader_node_virtual_texture_name)
    if not visual_node:
        return False
    
    virtual_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_virtual_texture_id)
    if not virtual_image:
        return False

    visual_node.image = virtual_image

    return True

def TM_Logic_TMTexture_Virtual_Image_Update(context, target_manager_id: str, target_tm_texture_id: str) -> bool:
    """TM_Logic_TMTexture_Virtual_Image_Update"""

    target_tm_texture = TM_Logic_TMTexture_Get_By_Id(context, target_manager_id, target_tm_texture_id)
    if not target_tm_texture: 
        return False
    
    preserved_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_preserved_texture_id)
    if not preserved_image:
        return False
    
    preserved_image.update()
    preserved_image.pack()            
    
    virtual_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_virtual_texture_id)
    if not virtual_image:
        return False
    
    if not TM_Logic_Image_Copy(preserved_image, virtual_image):
        return False

    return True

def TM_Logic_TMTexture_Set_Working_Resolution(context, target_manager_id: str) -> bool:
    """TM_Logic_TMTexture_Set_Working_Resolution"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False
    
    tm_texture_collection = target_manager.m_managed_tm_texture_collection
    if len(tm_texture_collection) == 0:
        target_manager.m_preserved_resolution = target_manager.m_preserved_resolution_cache
        return False
    
    target_resolution = TM_Logic_Utility_Get_Resolution_From_Preset(target_manager.m_preserved_resolution_cache)
    target_resolution_sum = target_resolution[0] * target_resolution[1]

    for tm_texture in tm_texture_collection:
        if tm_texture.m_user_texture_path or tm_texture.m_user_texture_hash:
            continue

        if not tm_texture.m_preserved_texture_id:
            continue

        current_resolution = tm_texture.m_preserved_texture_size
        current_resolution_sum = current_resolution[0] * current_resolution[1]

        if target_resolution_sum == current_resolution_sum:
            continue

        target_image = TM_Logic_Image_Get_By_Id(tm_texture.m_preserved_texture_id)
        if not target_image:
            continue

        result = TM_Logic_Image_Rescale(target_image, target_resolution)
        if not result:
            continue

        tm_texture.m_preserved_texture_size = target_resolution
    
    return True

def TM_Logic_TMTexture_Set_Virtual_Resolution(context, target_manager_id: str) -> bool:
    """TM_Logic_TMTexture_Set_Virtual_Resolution"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return False
    
    tm_texture_collection = target_manager.m_managed_tm_texture_collection
    if len(tm_texture_collection) == 0:
        target_manager.m_virtual_resolution = target_manager.m_virtual_resolution_cache
        return False
    
    target_resolution = TM_Logic_Utility_Get_Resolution_From_Preset(target_manager.m_virtual_resolution_cache)
    target_resolution_sum = target_resolution[0] * target_resolution[1]

    processed_hash_list = []
    for tm_texture in tm_texture_collection:            
        if not tm_texture.m_virtual_texture_id:
            continue

        source_image = TM_Logic_Image_Get_By_Id(tm_texture.m_preserved_texture_id)
        if not source_image:
            continue            

        target_image = TM_Logic_Image_Get_By_Id(tm_texture.m_virtual_texture_id)
        if not target_image:
            continue                   
        
        if tm_texture.m_user_texture_path or tm_texture.m_user_texture_hash:

            if tm_texture.m_user_texture_hash in processed_hash_list:
                continue    

            if not tm_texture.m_user_texture_hash  in processed_hash_list:
                processed_hash_list.append(tm_texture.m_user_texture_hash)

            max_resolution = tm_texture.m_preserved_texture_size 
            max_resolution_sum = max_resolution[0] * max_resolution[1]

            if target_resolution_sum > max_resolution_sum:
                target_resolution = max_resolution
                target_resolution_sum = max_resolution_sum
        
        current_resolution = tm_texture.m_virtual_texture_size
        current_resolution_sum = current_resolution[0] * current_resolution[1]

        if current_resolution_sum == target_resolution_sum:
            continue

        rescaled = TM_Logic_Image_Rescale(target_image, target_resolution)
        if not rescaled:
            continue
        tm_texture.m_virtual_texture_size = target_resolution
        
        if target_resolution_sum > current_resolution_sum:
            copy_data_from_original = TM_Logic_Image_Copy(source_image, rescaled)
            if not copy_data_from_original:
                continue
    
    return True

def TM_logic_TMTexture_Load_Image(context, target_manager_id: str, image_file_path: str, color_space: str, target_tm_texture_id:str|None = None) -> tm_property.TM_Texture|None:
    """TM_logic_TMTexture_Load_Image | color_space: 'sRGB' or 'Non-Color'"""

    if not image_file_path:
        return None
    
    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if not target_manager:
        return None        
    
    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return None   
    
    default_virtual_size = TM_Logic_Utility_Get_Resolution_From_Preset(target_manager.m_virtual_resolution)
    
    image_file_hash = TM_Logic_ID_Get_HashMD5(image_file_path, color_space)
    
    tm_manager_collection = target_manager.m_managed_tm_texture_collection

    loaded_tm_texture = None
    if len(tm_manager_collection) > 0:
        for tmtexture in tm_manager_collection:
            if tmtexture.m_user_texture_hash == image_file_hash:
                loaded_tm_texture = tmtexture
                break
    
    target_tm_texture: tm_property.TM_Texture|None = None
    preserved_image: bpy.types.Image|None = None
    virtual_image: bpy.types.Image|None = None

    if target_tm_texture_id:           
        target_tm_texture = TM_Logic_TMTexture_Get_By_Id(context, target_manager_id, target_tm_texture_id)
        if target_tm_texture: 
            if target_tm_texture.m_user_texture_hash == image_file_hash: 
                    return target_tm_texture
            else: 
                image_virtual_node = TM_Logic_ShaderNode_Get_Group_Internal_Node(host_material, 
                            target_tm_texture.m_shader_node_system_texture_id, 
                            target_tm_texture.m_shader_node_virtual_texture_name)
                
                if image_virtual_node:
                    image_virtual_node.image = None

                image_still_used = False

                for tmt in tm_manager_collection:
                    if tmt.m_id != target_tm_texture.m_id and tmt.m_user_texture_hash == target_tm_texture.m_user_texture_hash:
                        image_still_used = True
                        break

                if not image_still_used:
                    TM_Logic_Image_Remove_By_Id(target_tm_texture.m_virtual_texture_id)
                    TM_Logic_Image_Remove_By_Id(target_tm_texture.m_preserved_texture_id)                       

                target_tm_texture.m_user_texture_path = ""
                target_tm_texture.m_user_texture_hash = ""
                target_tm_texture.m_user_texture_size = (0,0)
                target_tm_texture.m_virtual_texture_size = (0,0)
                target_tm_texture.m_preserved_texture_size = (0,0)
                target_tm_texture.m_preserved_texture_id = ""
                target_tm_texture.m_virtual_texture_id = ""

    else: 
        target_tm_texture = TM_Logic_TMTexture_Create_New(context, target_manager_id) 
        
        shader_node_data = TM_Logic_ShaderNode_Get_From_Library(context, host_material,'SYSTEM_TEXTURE')
        if not shader_node_data:
            return None
            
        texture_system_node = shader_node_data['NODE_GROUP']  

        target_tm_texture.m_shader_node_system_texture_id = texture_system_node.get(stamp_id)        

    if loaded_tm_texture: 
        target_tm_texture.m_user_texture_path = loaded_tm_texture.m_user_texture_path
        target_tm_texture.m_user_texture_hash = loaded_tm_texture.m_user_texture_hash
        target_tm_texture.m_user_texture_size = loaded_tm_texture.m_user_texture_size

        target_tm_texture.m_virtual_texture_id = loaded_tm_texture.m_virtual_texture_id
        target_tm_texture.m_virtual_texture_size = loaded_tm_texture.m_virtual_texture_size

        target_tm_texture.m_preserved_texture_id = loaded_tm_texture.m_preserved_texture_id
        target_tm_texture.m_preserved_texture_size = loaded_tm_texture.m_preserved_texture_size

        preserved_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_preserved_texture_id)
        virtual_image = TM_Logic_Image_Get_By_Id(target_tm_texture.m_virtual_texture_id)
    
    if not target_tm_texture.m_user_texture_path and not target_tm_texture.m_user_texture_hash:
        image_file = bpy.data.images.load(image_file_path)
        if not image_file: 
            return None
        image_file_size = TM_Logic_Utility_Get_Nearest_Square_Resolution(image_file.size[0], image_file.size[1])        
        image_file = TM_Logic_Image_Rescale(image_file, image_file_size) 

        preserved_image_id = TM_Logic_ID_Get_New(context)
        virtual_image_id = TM_Logic_ID_Get_New(context)

        target_tm_texture.m_user_texture_path = image_file_path
        target_tm_texture.m_user_texture_hash = image_file_hash
        target_tm_texture.m_user_texture_size = image_file_size

        target_tm_texture.m_preserved_texture_id = preserved_image_id
        target_tm_texture.m_preserved_texture_size = image_file_size

        target_tm_texture.m_virtual_texture_id = virtual_image_id
        target_tm_texture.m_virtual_texture_size = default_virtual_size

        preserved_image = image_file.copy()
        preserved_image.name = preserved_image_id
        preserved_image[stamp_id] = preserved_image_id
        preserved_image.use_fake_user = True
        preserved_image.colorspace_settings.name = color_space
        if color_space == 'sRGB':
            preserved_image.alpha_mode = 'STRAIGHT'
        elif color_space == 'Non-Color':
            preserved_image.alpha_mode = 'CHANNEL_PACKED'
        preserved_image.update() 
        preserved_image.pack()

        virtual_image = image_file.copy()
        virtual_image.name = virtual_image_id
        virtual_image[stamp_id] = virtual_image_id
        virtual_image.use_fake_user = True
        virtual_image.colorspace_settings.name = color_space   
        if color_space == 'sRGB':
            virtual_image.alpha_mode = 'STRAIGHT'
        elif color_space == 'Non-Color':
            virtual_image.alpha_mode = 'CHANNEL_PACKED'     
        virtual_image.update()        
        virtual_image.pack()

        bpy.data.images.remove(image_file)                  

    if not preserved_image or not virtual_image:
        return None        
    
    texture_virtual_node = TM_Logic_ShaderNode_Get_Group_Internal_Node(host_material, 
                        target_tm_texture.m_shader_node_system_texture_id, 
                        target_tm_texture.m_shader_node_virtual_texture_name)
    texture_virtual_node.image = virtual_image
    texture_virtual_node.interpolation = 'Linear'
    
    if not loaded_tm_texture:
        default_virtual_size_sum = default_virtual_size[0] * default_virtual_size[1]

        tm_preserved_size = target_tm_texture.m_preserved_texture_size
        tm_preserved_size_sum = tm_preserved_size[0] * tm_preserved_size[1]

        if  tm_preserved_size_sum > default_virtual_size_sum:
            TM_Logic_Image_Rescale(virtual_image, default_virtual_size)
            target_tm_texture.m_virtual_texture_size = default_virtual_size
        else:
            TM_Logic_Image_Rescale(virtual_image, tm_preserved_size)
            target_tm_texture.m_virtual_texture_size = tm_preserved_size        

    return target_tm_texture 

def TM_Logic_TMTexture_Remove_By_Id(context, target_manager_id: str, tm_texture_id:str) -> bool:
    """TM_Logic_TMTexture_Remove_By_Id"""

    target_manager = TM_logic_LayerManager_Get_By_Id(context, target_manager_id)
    if target_manager is None:
        return False
    
    host_material = TM_Logic_Material_Get_By_Id(target_manager.m_managed_material_id)
    if not host_material:
        return False

    texture_manager = target_manager.m_managed_tm_texture_collection
    if len(texture_manager) == 0:
        return False

    tm_texture = None
    tmt_index = -1
    for index, texture in enumerate(texture_manager):
        if texture.m_id == tm_texture_id:
            tm_texture = texture
            tmt_index = index
            break
    
    if not tm_texture:
        return False
    
    image_hash = tm_texture.m_user_texture_hash
    
    if image_hash:
        image_still_used = False

        for tmtexture in texture_manager:
            if tmtexture.m_id != tm_texture_id and tmtexture.m_user_texture_hash == image_hash:
                image_still_used = True
                break

        if not image_still_used:
            TM_Logic_Image_Remove_By_Id(tm_texture.m_preserved_texture_id)
            TM_Logic_Image_Remove_By_Id(tm_texture.m_virtual_texture_id)  
    else:
        TM_Logic_Image_Remove_By_Id(tm_texture.m_preserved_texture_id)
        TM_Logic_Image_Remove_By_Id(tm_texture.m_virtual_texture_id)  
    
    tm_texture.m_user_texture_hash = ""       

    if tm_texture.m_shader_node_system_texture_id:
        result = TM_Logic_ShaderNode_Remove_Node_By_Id(host_material, tm_texture.m_shader_node_system_texture_id)
        if not result:
            return False

    texture_manager.remove(tmt_index)

    new_count = len(target_manager.m_managed_tm_texture_collection)
    if new_count == 0:
        target_manager.m_managed_tm_texture_pointer = 0
    else:
        if target_manager.m_managed_tm_texture_pointer >= new_count:
            target_manager.m_managed_tm_texture_pointer = new_count - 1
        elif tmt_index < target_manager.m_managed_tm_texture_pointer:
            target_manager.m_managed_tm_texture_pointer -= 1
    target_manager.m_managed_tm_texture_pointer = max(0, target_manager.m_managed_tm_texture_pointer)

    return True
#endregion [TM Texture]

#region [Image]
def TM_Logic_Image_Generate_New(context, resolution: tuple[int, int], color_rgba: tuple[float,float,float,float], use_alpha: bool = False, use_buffer: bool = False, color_space: str|None = None) -> bpy.types.Image|None:
    """TM_Logic_Image_Generate_New"""

    if resolution[0] < 64 or resolution[1] < 64:
        return None

    color = [max(0.0, min(1.0, c)) for c in color_rgba]
    pixel_count = resolution[0] * resolution[1]
    color_data = color * pixel_count

    new_id = TM_Logic_ID_Get_New(context)

    new_image = bpy.data.images.new(
        name=new_id,
        width=resolution[0],
        height=resolution[1],
        alpha=use_alpha, # true = rgba , false = rgb
        float_buffer=use_buffer # true = 32 bit, false = 8 bit
    )
    if not new_image:
        return None
    
    if color_space:
        new_image.colorspace_settings.name = color_space

    new_image.pixels.foreach_set(color_data)
    new_image.use_fake_user = True
    new_image[stamp_id] = new_id
    new_image.update()

    return new_image

def TM_Logic_Image_Get_By_Id(image_id: str) -> bpy.types.Image | None:
    """TM_Logic_Image_Get_By_Id"""

    if not image_id:
        return None

    target_image = None
    image_collection = bpy.data.images
    for image in image_collection:
        if image.get(stamp_id) == image_id:
            target_image = image
            break
    if not target_image:
        return False

    return image

def TM_Logic_Image_Rescale(target_texture: bpy.types.Image, new_resolution: tuple[int, int]) -> bpy.types.Image|None:
    """TM_Logic_Image_Rescale"""  

    if not target_texture:
        return None

    new_w, new_h = new_resolution
    old_w, old_h = target_texture.size

    if (old_w, old_h) == (new_w, new_h):
        return target_texture

    target_texture.scale(new_w, new_h)        
            
    target_texture.update()

    target_texture.pack()
    
    return target_texture

def TM_Logic_Image_Copy(source_texture: bpy.types.Image, target_texture: bpy.types.Image) -> bool:
    """TM_Logic_Image_Copy"""

    if not source_texture:
        return False        

    if not source_texture.pixels:
        return False
    
    if not target_texture:
        return False
    
    target_texture_width, target_texture_height = target_texture.size 
    source_texture_width, source_texture_height = source_texture.size

    temp_copy = None

    if (source_texture_width, source_texture_height) == ( target_texture_width, target_texture_height):
        pixel_count = target_texture_width * target_texture_height * 4
        buffer = np.empty(pixel_count, dtype=np.float32)

        source_texture.pixels.foreach_get(buffer)
        target_texture.pixels.foreach_set(buffer)

    else:
        temp_copy = source_texture.copy()
        temp_copy.name = f"tm_temp_copy_{source_texture.name}"       
        temp_copy.scale(target_texture_width, target_texture_height)
        temp_copy.update()

        pixel_count = target_texture_width * target_texture_height * 4
        buffer = np.empty(pixel_count, dtype=np.float32)

        temp_copy.pixels.foreach_get(buffer)
        target_texture.pixels.foreach_set(buffer)
                
    target_texture.update() 
    target_texture.pack()

    if temp_copy:
        bpy.data.images.remove(temp_copy)

    return True

def TM_Logic_Image_Remove_By_Id(image_id: str) -> bool:
    """TM_Logic_Image_Remove_By_Id"""

    if not image_id:
        return False
    
    target_image = TM_Logic_Image_Get_By_Id(image_id)
    if not target_image:
        return False

    bpy.data.images.remove(target_image, do_unlink=True)

    return True

def TM_Logic_Image_Has_User(target_image: bpy.types.Image) -> bool:
    """TM_Logic_Image_Has_User"""
      
    if not target_image:
        return False
    
    if not stamp_id in target_image:
        return False
    
    if target_image.users == 0:
        return False

    if target_image.users == 1 and target_image.use_fake_user:
        return False
    
    return True

def TM_Logic_Image_Is_Packed(target_image: bpy.types.Image) -> bool:
    """TM_Logic_Image_Is_Packed"""

    if target_image:
        return target_image.packed_file is not None
    return False
#endregion [Image]

#region [Material]
def TM_Logic_Material_Create_New(context) -> bpy.types.Material | None:
    """TM_Logic_Material_Create_New"""

    new_id = TM_Logic_ID_Get_New(context)
    
    new_mat = bpy.data.materials.new(name=new_id)

    if new_mat is None:
        return None

    new_mat.use_nodes = True
    new_mat.use_fake_user = True
    new_mat[stamp_id] = new_id

    return new_mat
    
def TM_Logic_Material_Get_Active_Material(context) -> bpy.types.Material | None:
    """TM_Logic_Material_Get_Active_Material"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None
    
    target_material = TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not target_material:
        return None
        
    
    if not target_material.use_nodes:
        return None        
    
    return target_material

def TM_Logic_Material_Get_By_Id(material_id: str) -> bpy.types.Material | None:
    """TM_Logic_Material_Get_By_Id"""


    for mat in bpy.data.materials:
        if stamp_id in mat and mat[stamp_id] == material_id:
            return mat

    return None

def TM_Logic_Material_Remove_By_Id(context, material_id: str) -> bool:
    """TM_Logic_Material_Remove"""

    active_object = TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return False
    
    if not material_id:
        return False

    mat_to_remove = TM_Logic_Material_Get_By_Id(material_id)
    if mat_to_remove is None:
        return False
    
    bpy.data.materials.remove(mat_to_remove, do_unlink=True)

    slots = active_object.material_slots
    if len(slots) > 0:
        indices_to_remove = []

        for i, slot in enumerate(slots):
            if i != 0 and slot.material is None:
                indices_to_remove.append(i)

        for index in reversed(indices_to_remove):
            active_object.active_material_index = index
            bpy.ops.object.material_slot_remove()

    if len(slots) > 0:
        if len(slots) == 1 and slots[0].material is None:
            bpy.ops.object.material_slot_remove()    
        else:
            another_material_id = None
            for i, slot in enumerate(slots):
                if i != 0 and slot.material and stamp_id in slot.material:
                    another_material_id = slot.material.get(stamp_id)
                    break    
            if another_material_id:
                user_data = context.scene.TM_User_Data
                manager_collection = user_data.m_managed_tm_node_manager_collection     
                for manager in manager_collection:
                    if manager.m_managed_material_id == another_material_id:
                        TM_Logic_LayerManager_Set_Active_State(context, manager.m_id)
                        break                                                       

    return True
#endregion [Material]

#region [Shader Node]
def TM_Logic_ShaderNode_Create_New_By_IdName(context, target_material: bpy.types.Material, node_bl_idname: str) -> bpy.types.Node | None:
    """TM_Logic_ShaderNode_Create_New_By_IdName"""

    if not target_material:
        return None

    if not target_material.use_nodes:
        return None

    node_tree = target_material.node_tree
    new_node = node_tree.nodes.new(node_bl_idname)

    if new_node is None:
        return None

    new_id = TM_Logic_ID_Get_New(context)
    new_node.name = new_id
    new_node.label = ""
    new_node[stamp_id] = new_id

    new_node.location = (0, 0)  

    return new_node
    
def TM_Logic_ShaderNode_Get_By_Id(target_material: bpy.types.Material, node_id: str, id_as_name:bool = False) -> bpy.types.Node | None:
    """TM_Logic_ShaderNode_Get_By_Id"""

    if not target_material:
        return None

    if not target_material.use_nodes:
        return None
    
    node_tree = target_material.node_tree

    if id_as_name:
        target_node = node_tree.nodes.get(node_id)
        if target_node:
            return target_node
    else:
        for node in node_tree.nodes:
            if node.get(stamp_id) == node_id:
                return node

    return None

def TM_Logic_ShaderNode_Get_Group_Internal_Node(target_material: bpy.types.Material, group_node_id: str, internal_node_name: str) -> bpy.types.Node | None:
    """TM_Logic_ShaderNode_Get_Group_Internal_Node"""

    if not target_material:
        return None

    if not target_material.use_nodes:
        return None

    node_tree = target_material.node_tree
    group_node = None
    for node in node_tree.nodes:
        if node.get(stamp_id) == group_node_id:
            group_node = node
            break

    if not group_node:
        return None

    if group_node.type != 'GROUP':
        return None

    internal_tree = group_node.node_tree
    if internal_tree is None:
        return None

    internal_node = internal_tree.nodes.get(internal_node_name)
    if internal_node is None:
        return None

    return internal_node

def TM_Logic_ShaderNode_Get_From_Library(context, target_material: bpy.types.Material, shader_group_default_name: str, request_internal_node_list: list[str] | None = None) -> dict[str, bpy.types.Node | bpy.types.NodeTree | None] | None:
    """TM_Logic_ShaderNode_Get_From_Library|Reference : tm_property.TM_DT_Custom_Node_Library"""

    if not target_material:
        return None

    if not target_material.use_nodes:
        return None

    node_library = tm_property.TM_DT_Custom_Node_Library

    if shader_group_default_name not in node_library:
        return None

    group_name = node_library[shader_group_default_name]['idname']
    addon_path = node_library[shader_group_default_name]['path']

    node_tree_group = bpy.data.node_groups.get(group_name)
    if not node_tree_group:
        addon_dir = os.path.dirname(__file__)
        library_path = bpy.path.abspath(os.path.join(addon_dir, addon_path))

        if not os.path.exists(library_path):
            return None

        with bpy.data.libraries.load(library_path, link=False) as (data_from, data_to):
            if group_name in data_from.node_groups:
                data_to.node_groups = [group_name]
            else:
                return None

        node_tree_group = bpy.data.node_groups.get(group_name)
        if not node_tree_group:
            return None

    new_node_tree_group_new_id = TM_Logic_ID_Get_New(context)
    group_node_instance_new_id = TM_Logic_ID_Get_New(context)

    new_node_tree_group = node_tree_group.copy()
    new_node_tree_group.name = new_node_tree_group_new_id
    new_node_tree_group[stamp_id] = new_node_tree_group_new_id

    node_tree = target_material.node_tree
    group_node_instance = node_tree.nodes.new(type='ShaderNodeGroup')
    group_node_instance.node_tree = new_node_tree_group

    group_node_instance.name = group_node_instance_new_id
    group_node_instance.label = shader_group_default_name
    group_node_instance[stamp_id] = group_node_instance_new_id
    group_node_instance.location = (0, 0)
    group_node_instance.width = 240

    result = {}
    result["NODE_GROUP"] = group_node_instance
    result["NODE_TREE"] = new_node_tree_group

    request_list = ["Group Input", "Group Output"]
    if request_internal_node_list is not None:
        request_list.extend(request_internal_node_list)

    for key in request_list:
        node = new_node_tree_group.nodes.get(key)
        if node is None:
            result[key] = None
        else:
            result[key] = node

    return result

def TM_Logic_ShaderNode_Socket_Linker(target_material: bpy.types.Material, node_from: bpy.types.Node, node_to: bpy.types.Node, output_name: str, input_name: str, replace_existing: bool = True) -> bool:
    """TM_Logic_ShaderNode_Socket_Linker"""

    if not target_material or not target_material.use_nodes:
        return False

    if not node_from or not node_to:
        return False

    node_tree = target_material.node_tree

    if node_from.id_data != node_tree or node_to.id_data != node_tree:
        return False

    if output_name not in node_from.outputs:
        return False

    if input_name not in node_to.inputs:
        return False

    output_socket = node_from.outputs[output_name]
    input_socket = node_to.inputs[input_name]

    if replace_existing and input_socket.is_linked and not input_socket.is_multi_input:
        removed_count = len(input_socket.links)
        for link in list(input_socket.links):
            node_tree.links.remove(link)

    node_tree.links.new(output_socket, input_socket)
    return True

def TM_Logic_ShaderNode_Socket_Disconnector(target_material: bpy.types.Material, target_node: bpy.types.Node, socket_name: str | None = None, is_input_socket: bool = True) -> bool:
    """TM_Logic_ShaderNode_Socket_Disconnector"""

    if socket_name is None:
        return False
    
    if not target_material or not target_material.use_nodes:
        return False
    
    if not target_node:
        return False

    node_tree = target_material.node_tree

    socket = target_node.inputs.get(socket_name) if is_input_socket else target_node.outputs.get(socket_name)
    if not socket:
        return False

    links_to_remove = list(socket.links)

    for link in links_to_remove:
        node_tree.links.remove(link)

    return True

def TM_Logic_ShaderNode_Remove_Node_By_Id(target_material: bpy.types.Material, node_id: str) -> bool:
    """TM_Logic_ShaderNode_Remove_Node_By_Id"""

    if not target_material:
        return False

    if not target_material.use_nodes:
        return False

    node_tree = target_material.node_tree
    node_to_remove = None

    for node in node_tree.nodes:
        if node.get(stamp_id) == node_id:
            node_to_remove = node
            break                

    if node_to_remove is None:
        return False

    node_type = node_to_remove.type
    node_name = node_to_remove.label
    group_data_block = None
    group_name = "None"

    if node_to_remove.type == 'GROUP' and node_to_remove.node_tree:
        group_data_block = node_to_remove.node_tree
        group_name = group_data_block.name

    node_tree.nodes.remove(node_to_remove)

    if group_data_block:
        bpy.data.node_groups.remove(group_data_block, do_unlink=True)

    return True

def TM_Logic_ShaderNode_Set_Node_Active(target_material: bpy.types.Material, target_node: bpy.types.Node) -> bool:
    """TM_Logic_ShaderNode_Set_Node_Active"""

    if not target_material:
        return False
    if not target_node:
        return False
    if not target_material.use_nodes:
        return False
    
    node_tree = target_material.node_tree
    node_tree.nodes.active = target_node
    target_node.select = True

    return True

def TM_Logic_ShaderNode_Set_Internal_Node_Active(target_material: bpy.types.Material, group_node_id: str, internal_node_name: str) -> bool:
    """TM_Logic_ShaderNode_Set_Internal_Node_Active"""

    group_node = TM_Logic_ShaderNode_Get_By_Id(target_material, group_node_id)
    if not group_node:
        return False
    
    internal_tree = group_node.node_tree
    target_node = internal_tree.nodes.get(internal_node_name)
    if not target_node:
        return False
    
    internal_tree.nodes.active = target_node
    
    target_node.select = True

    target_material.node_tree.nodes.active = group_node

    return True
#endregion [Shader Node]

#region [Texture]
def TM_Logic_Texture_Generate_New(context, target_material: bpy.types.Material, texture_name:str|None = None, texture_type: str = 'IMAGE') -> bpy.types.Texture|None:
    """TM_Logic_Texture_Generate_New"""

    new_id = TM_Logic_ID_Get_New(context)

    bpy.data.textures.new(name=new_id, type=texture_type)
    lastIndex = len(bpy.data.textures)-1
    bpy.context.tool_settings.image_paint.brush.mask_texture = bpy.data.textures[lastIndex]
    new_texture = bpy.data.textures[lastIndex]
       
    if not new_texture:
        return None

    if texture_type == 'IMAGE':
        new_texture.name = texture_name
        new_texture.extension = 'CLIP' 
        new_texture.use_interpolation = True

    new_texture[stamp_id] = new_id
    new_texture.use_fake_user = True

    return new_texture
#endregion [Texture]

#region [Brush]
def TM_Logic_Brush_Get_Falloff_LUT(context):
    """TM_Logic_Brush_Get_Falloff_LUT 
        hardness 0.0    : Very blurry/linear
        hardness 0.5    : Standard smooth
        hardness 1.0    : Almost a solid circle
        hardness 1.0+   : full jagged solid"""
    
    user_brush_data = context.scene.TM_User_Data.m_brush_data
    resolution = user_brush_data.m_brush_falloff_resolution
    hardness = user_brush_data.m_brush_falloff_hardness

    if resolution <= 0:
        return None

    lut = np.zeros(resolution, dtype=np.float32)
    for i in range(resolution):
        t = i / (resolution - 1)
        lut[i] = 1.0 - (3 * t**2 - 2 * t**3)

    if hardness > 1.0:
            return np.where(lut > 0, 1.0, 0.0)
    
    exponent = (1.0 - hardness) * 2.0 + 0.1
    new_lut = np.power(lut, exponent)

    if hardness > 0.8:
        threshold = (hardness - 0.8) * 5.0
        new_lut = np.where(lut > (1.0 - threshold), 1.0, new_lut)

    return np.clip(new_lut, 0, 1)

def TM_Logic_Brush_Get_TargetUV(evaluated_mesh, raycasthit_position, raycasthit_face_index):
    """TM_Logic_Brush_Get_TargetUV"""
    evaluated_mesh_poly     = evaluated_mesh.polygons[raycasthit_face_index]
    evaluated_mesh_uv       = evaluated_mesh.uv_layers.active.data

    tris_01_vertex_coord    = evaluated_mesh.vertices[evaluated_mesh_poly.vertices[0]].co
    tris_02_vertex_coord    = evaluated_mesh.vertices[evaluated_mesh_poly.vertices[1]].co
    tris_03_vertex_coord    = evaluated_mesh.vertices[evaluated_mesh_poly.vertices[2]].co

    tris_01_uv_coord        = Vector((evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[0]].uv.x, evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[0]].uv.y, 0))
    tris_02_uv_coord        = Vector((evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[1]].uv.x, evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[1]].uv.y, 0))
    tris_03_uv_coord        = Vector((evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[2]].uv.x, evaluated_mesh_uv[evaluated_mesh_poly.loop_indices[2]].uv.y, 0))

    projected_uv            = barycentric_transform(
        raycasthit_position, 
        tris_01_vertex_coord, tris_02_vertex_coord, tris_03_vertex_coord, 
        tris_01_uv_coord, tris_02_uv_coord, tris_03_uv_coord)

    return projected_uv
#endregion [Brush]

#region [Render]
def TM_Logic_Render_Generate_Position_Map(context) -> bpy.types.Image | None:
    """TM_Logic_Utility_Generate_Position_Map"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return None
    
    active_material = TM_Logic_Material_Get_Active_Material(context)
    if not active_material:
        return None
    
    map_resolution = TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_preserved_resolution)
    
    position_map = TM_Logic_Image_Generate_New(context, map_resolution, (0.0,0.0,0.0,0.0), True, True,'Non-Color')
    if not position_map:
        return None
    position_map.pack()
    
    if active_manager.m_data.m_baked_position_map_id:
        TM_Logic_Image_Remove_By_Id(active_manager.m_data.m_baked_position_map_id)
        active_manager.m_data.m_baked_position_map_id = ""
    
    active_manager.m_data.m_baked_position_map_id = position_map.get(stamp_id)

    current_render_engine = context.scene.render.engine
    context.scene.render.engine = 'CYCLES'
    context.scene.cycles.bake_type = 'EMIT'
    context.scene.cycles.samples = 1  
    context.scene.cycles.use_denoising = False
    context.scene.cycles.use_adaptive_sampling = False

    TM_Logic_Render_Set_GPU_Rendering(context)

    node_geo = TM_Logic_ShaderNode_Create_New_By_IdName(context, active_material, 'ShaderNodeNewGeometry')
    node_emit = TM_Logic_ShaderNode_Create_New_By_IdName(context, active_material, 'ShaderNodeEmission')
    node_tex = TM_Logic_ShaderNode_Create_New_By_IdName(context, active_material, 'ShaderNodeTexImage')
    node_out = TM_Logic_ShaderNode_Get_By_Id(active_material, active_manager.m_shader_node_output_id)

    node_tex.image = position_map

    TM_Logic_ShaderNode_Socket_Linker(active_material, node_geo, node_emit, 'Position', 'Color')
    TM_Logic_ShaderNode_Socket_Linker(active_material, node_emit, node_out, 'Emission', 'Surface')
    
    TM_Logic_ShaderNode_Set_Node_Active(active_material, node_tex)

    target_margin = TM_Logic_Render_Calc_Dilate_Iterations(map_resolution[0], map_resolution[1])

    bpy.ops.object.bake(type='EMIT', margin=target_margin, use_clear=True)

    TM_Logic_ShaderNode_Remove_Node_By_Id(active_material, node_geo.get(stamp_id))
    TM_Logic_ShaderNode_Remove_Node_By_Id(active_material, node_emit.get(stamp_id))
    TM_Logic_ShaderNode_Remove_Node_By_Id(active_material, node_tex.get(stamp_id))

    context.scene.render.engine = current_render_engine

    TM_Logic_Layer_Refresh_ShaderNode(context,active_manager.m_id)

    return position_map

def TM_Logic_Render_Calc_Dilate_Iterations(width, height) -> int:
    """TM_Logic_Render_Calc_Dilate_Iterations"""
    max_dim = max(width, height)
    
    iterations = int((max_dim / 1024) * 16)
    
    return max(4, iterations)

def TM_Logic_Render_Numpy_Add_Dilate(buffer, iterations=2):
    """TM_Logic_Render_Numpy_Add_Dilate"""

    for _ in range(iterations):
        empty_mask = buffer[:, :, 3] == 0
        shifts = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        
        for dy, dx in shifts:
            shifted = np.roll(buffer, shift=(dy, dx), axis=(0, 1))
            fill_mask = empty_mask & (shifted[:, :, 3] > 0)
            buffer[fill_mask] = shifted[fill_mask]
            empty_mask = buffer[:, :, 3] == 0
            
    return buffer

def TM_Logic_Render_Set_GPU_Rendering(context):
    """TM_Logic_Render_Set_GPU_Rendering"""

    context.scene.cycles.device = 'GPU'
    
    prefs = context.preferences.addons['cycles'].preferences

    prefs.get_devices()

    device_types = [d[0] for d in prefs.get_device_types(context)]
    
    for priority in ['OPTIX', 'CUDA', 'METAL', 'ONEAPI', 'HIP']:
        if priority in device_types:
            prefs.compute_device_type = priority
            break
            
    for device in prefs.devices:
        if device.type == 'CPU':
            device.use = False
        else:
            device.use = True
#endregion [Render]

#region [Export Texture]
def TM_Logic_Export_Template_Create_New(context) -> tm_property.TM_Texture_Export|None:
    """TM_Logic_Export_Template_Create_New"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:  
        return None
    
    new_export_template = active_manager.m_managed_tm_texture_export_collection.add()
    new_export_template.m_id = TM_Logic_ID_Get_New(context)
    new_export_template.m_name = f"Rename_Me_{new_export_template.m_id}"
    new_export_template.m_enable = True

    active_manager.m_managed_tm_texture_export_pointer = len(active_manager.m_managed_tm_texture_export_collection) - 1

    return new_export_template

def TM_Logic_Export_Template_Remove(context)->bool:
    """TM_Logic_Export_Template_Remove"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return False
    
    export_collection = active_manager.m_managed_tm_texture_export_collection
    export_pointer = active_manager.m_managed_tm_texture_export_pointer

    if not export_collection or len(export_collection) == 0:
        return False
    
    active_manager.m_managed_tm_texture_export_collection.remove(export_pointer)

    new_count = len(active_manager.m_managed_tm_texture_export_collection)
    if new_count == 0:
        active_manager.m_managed_tm_texture_export_pointer = 0
    else:
        if active_manager.m_managed_tm_texture_export_pointer >= new_count:
            active_manager.m_managed_tm_texture_export_pointer = new_count - 1
        elif export_pointer < active_manager.m_managed_tm_texture_export_pointer:
            active_manager.m_managed_tm_texture_export_pointer -= 1
    active_manager.m_managed_tm_texture_export_pointer = max(0, active_manager.m_managed_tm_texture_export_pointer)
    
    return True

def TM_Logic_Export_Get_Active_Template(context) -> tm_property.TM_Texture_Export|None:
    """TM_Logic_Export_Get_Active_Template"""

    active_manager = TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return False

    export_collection = active_manager.m_managed_tm_texture_export_collection
    export_pointer = active_manager.m_managed_tm_texture_export_pointer

    if not export_collection or len(export_collection) == 0:
        return None
    
    return export_collection[export_pointer]
#endregion [Export Texture]

#region [Utility]
def TM_Logic_Utility_Get_Resolution_From_Preset(resolution_enum_id: str) -> tuple[int, int]:
    """TM_Logic_Utility_Get_Resolution_From_Preset"""

    if not resolution_enum_id or '_' not in resolution_enum_id:
        return (1024, 1024)

    res_str = resolution_enum_id.split('_')[1]
    res_int = int(res_str)

    return (res_int, res_int)

def TM_Logic_Utility_Get_Main_Shader_Name(shader_type: str) -> str|None:
    """TM_Logic_Utility_Get_Main_Shader_Name"""

    for listed_name in tm_property.TM_BSDF_Shader_Type_Items:
        if listed_name[0] == shader_type:
            return listed_name[1]

    return None  

def TM_Logic_Utility_Viewport_Get_Shading():
    """TM_Logic_Utility_Viewport_Get_Shading"""

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    return space.shading
                
    return None
    
def TM_Logic_Utility_Viewport_Set_Shading(context, screen_space_type:str, show_overlays: bool = True, skip_show_overlays: bool = False) -> bool:
    """TM_Logic_Utility_Viewport_Set_Shading | 'WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED'"""

    screens = context.screen.areas
    for area in screens:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = screen_space_type
                    if not skip_show_overlays:
                        space.overlay.show_overlays = show_overlays
                    return True   
                
    return False

def TM_Logic_Utility_Viewport_Set_Mode(context, target_mode: str) -> bool:
    """TM_Logic_Utility_Viewport_Set_Mode | 'OBJECT','EDIT','SCULPT','VERTEX_PAINT','WEIGHT_PAINT','TEXTURE_PAINT'"""

    active_object = TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return False
    
    if active_object.mode == target_mode:
        return True
    
    bpy.ops.object.mode_set(mode=target_mode)
    return True
       
def TM_Logic_Utility_Viewport_Refresh(context) -> bool:
    """TM_Logic_Utility_Viewport_Refresh"""

    active_object = TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return False
    
    if context.view_layer.objects.active != active_object:
        context.view_layer.objects.active = active_object

    active_object.update_tag()
    context.view_layer.update()

    for area in context.screen.areas:
        if area.type in {'VIEW_3D', 'PROPERTIES', 'NODE_EDITOR'}:
            area.tag_redraw()
            space = area.spaces.active
            if space.type == 'VIEW_3D':
                original_shading = space.shading.type
                space.shading.type = 'WIREFRAME'
                space.shading.type = original_shading

    return True

def TM_Logic_Utility_Get_Nearest_Square_Resolution(width: int, height: int) -> tuple[int, int]:
    """TM_Logic_Utility_Get_Nearest_Square_Resolution"""

    max_dim = max(width, height)
    
    pow_upper = 1 << (max_dim - 1).bit_length()
    
    pow_lower = pow_upper >> 1
    
    if (pow_upper - max_dim) < (max_dim - pow_lower):
        pot = pow_upper
    else:
        pot = pow_lower
    
    result = max(pot, 32)

    return result, result

def TM_Logic_Utility_Viewport_Set_Object_Mode(target_mode: str) -> bool:
    """TM_Logic_Utility_Viewport_Set_Object_Mode | 'OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT' """

    active_object = TM_Logic_Object_Get_Active_One(bpy.context)
    if not active_object:
        return False
    
    if active_object.mode == target_mode:
        return True
    
    bpy.ops.object.mode_set(mode=target_mode)

    return True   

def TM_Logic_Utility_sRGB_To_Linear(srgb_value):
    """TM_Logic_Utility_sRGB_To_Linear"""

    if srgb_value <= 0.04045:
        return srgb_value / 12.92
    else:
        return ((srgb_value + 0.055) / 1.055) ** 2.4

def TM_Logic_Utility_Image_To_NumpyArray(image: bpy.types.Image) -> np.ndarray | None:
    """TM_Logic_Utility_Image_To_NumpyArray"""

    if not image:
        return None
    
    width, height = image.size
    buffer = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(buffer)
    return buffer

def TM_Logic_Utility_Get_Tangent_Bitangent(self, normal):
    """TM_Logic_Utility_Get_Tangent_Bitangent"""

    normal      = np.array(normal)
    up          = np.array([0.0, 0.0, 1.0])
    if np.abs(np.dot(normal, up)) > 0.999:
        up      = np.array([1.0, 0.0, 0.0])
    tangent     = np.cross(normal, up)
    tangent    /= np.linalg.norm(tangent)
    bitangent   = np.cross(normal, tangent)
    return tangent, bitangent

def TM_Logic_Utility_Mouse_RaycastHit(context, event,target_object: bpy.types.Object, ray_length:float = 10000.0, cached_matrix=None) -> tuple[bool, Vector, Vector, int]:
    """return tuple(success, position, normal, face_index)"""

    if not target_object:
        return (False, Vector((0,0,0)), Vector((0,0,1)), -1)

    coord               = (event.mouse_region_x, event.mouse_region_y)
    region              = context.region
    rv3d                = context.space_data.region_3d

    view_vector         = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin          = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    matrix_inv          = cached_matrix if cached_matrix else target_object.matrix_world.inverted()
    
    ray_origin_obj      = matrix_inv @ ray_origin
    ray_target_obj      = matrix_inv @ (ray_origin + view_vector * ray_length) 
    ray_direction_obj   = ray_target_obj - ray_origin_obj

    hit                 = target_object.ray_cast(ray_origin_obj, ray_direction_obj)
    
    return hit
#endregion [Utility]

#region [Experimental]
# def TM_Logic_Utility_Release_My_Image() -> bool:
#     """TM_Logic_Utility_Release_My_Image"""

#     if bpy.context.tool_settings.image_paint.canvas:
#         bpy.context.tool_settings.image_paint.canvas = None
    
#     for brush in bpy.data.brushes:
#         if brush.texture and brush.texture.image is not None:
#             brush.texture.image = None

#     return True

# def TM_Logic_Experimental_Get_Safe_Pixels(image_block):
#     """TM_Logic_Experimental_Get_Safe_Pixels"""

#     width, height = image_block.size
#     pixels = np.empty(width * height * 4, dtype=np.float32)
#     image_block.pixels.foreach_get(pixels)
#     return pixels.reshape((height, width, 4))

# def TM_Logic_Utility_Color_To_Non_Color_Value(non_color_value):
#     """TM_Logic_Utility_Color_To_Non_Color_Value"""

#     return non_color_value ** (1/2.2)

# def TM_Logic_Clamp_Value(value):
#     """Ensures PBR data stays in the valid 0.0 - 1.0 range."""

#     return max(0.0, min(1.0, value))

# def TM_Logic_Brush_Get_Image_Sampler(imported_image: bpy.types.Image):
#     """TM_Logic_Brush_Get_Image_Sampler"""

#     if not imported_image:
#         return None
#     w, h = imported_image.size
#     sample_buffer = np.empty(w * h * 4, dtype=np.float32)
#     imported_image.pixels.foreach_get(sample_buffer)
#     return sample_buffer.reshape((h, w, 4))
#endregion [Experimental]