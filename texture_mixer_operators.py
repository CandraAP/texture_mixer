#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_operators.py            |
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
import bpy.utils
import bpy_extras
import math
import gpu
import blf
import time
import numpy as np
from gpu_extras.batch import batch_for_shader
from bpy_extras.io_utils import ImportHelper
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import barycentric_transform
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
#-------------------------------------------------
# from dev_tools.texture_mixer_debug import Debug
#-------------------------------------------------
# from . import texture_mixer_undo as tm_undo
#-------------------------------------------------
from . import texture_mixer_logic as tm_logic
from . import texture_mixer_property as tm_property
#-------------------------------------------------
stamp_id    = tm_property.Addon_Data.m_addon_id_stamp
# undo_manager = tm_undo.TM_Undo_Manager.instance()
#-------------------------------------------------
#endregion [IMPORT]

#region [Operator]
#-------------------------------------------------

#region [Dummy / Test]
class TM_OT_Test_Dummy(bpy.types.Operator):
    """TM_OT_Test_Dummy"""
    bl_idname       = "texture_mixer.test_dummy"
    bl_label        = "For Testing"
    bl_description  = "Just for test, placeholder & dummy"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        # debug_id = "TM_OT_Test_Dummy"

        # Debug.Separator(debug_id, "=")
        # Debug.Log("Test dummy : [START]", debug_id)

        tm_logic.TM_Logic_Test_Dummy(context)

        # Debug.Log("Test dummy : [FINISHED]", debug_id)
        # Debug.Separator(debug_id, "=")
        return {'FINISHED'}
#endregion [Dummy / Test]

#region [Layer Manager]
class TM_OT_LayerManager_Create_New(bpy.types.Operator):
    """TM_OT_LayerManager_Create_New"""
    bl_idname       = "texture_mixer.layermanager_create_new"
    bl_label        = "Add New Layer Manager"
    bl_description  = "Creates a new Blender Material and initializes the Texture Mixer layer stack data."
    bl_options      = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return tm_logic.TM_Logic_Object_Get_Active_One(context)

    def execute(self, context):      

        active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
        if not active_object:
            return {'CANCELLED'}

        new_layer_manager = tm_logic.TM_Logic_LayerManager_Create_New(context)
        if new_layer_manager is None:
            return {'CANCELLED'}

        new_material = tm_logic.TM_Logic_Material_Get_By_Id(new_layer_manager.m_managed_material_id)
        if new_material is None:
            return {'CANCELLED'}

        mat_slots = active_object.data.materials
        if len(mat_slots) == 0:
            mat_slots.append(None)
        else:                 
            for i in range(len(active_object.material_slots) - 1, -1, -1):
                slot = active_object.material_slots[i]
                mat = slot.material
                if mat is None or stamp_id not in mat:                        
                    active_object.active_material_index = i
                    bpy.ops.object.material_slot_remove()
            
            if len(mat_slots) == 0:
                mat_slots.append(None)                    

        mat_slots.append(new_material)

        tm_logic.TM_Logic_LayerManager_Set_Active_State(context, new_layer_manager.m_id)

        tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, new_layer_manager.m_id)

        tm_logic.TM_Logic_Utility_Viewport_Set_Shading(context, 'MATERIAL', True, True)

        return {'FINISHED'}
    
class TM_OT_LayerManager_Activate(bpy.types.Operator):
    """TM_OT_LayerManager_Activate"""
    bl_idname       = "texture_mixer.layermanager_activate"
    bl_label        = "Activate Layer Manager"
    bl_description  = "Activate selected layer manager"
    bl_options      = {'REGISTER', 'INTERNAL'}

    m_manager_id : StringProperty(name="Manager ID")  

    def execute(self, context):

        if not self.m_manager_id:
            return {'CANCELLED'}

        change_state_success = tm_logic.TM_Logic_LayerManager_Set_Active_State(context, self.m_manager_id)

        if change_state_success:
            tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, self.m_manager_id)
            tm_logic.TM_Logic_Utility_Viewport_Set_Shading(context, 'MATERIAL', True, True)
            tm_logic.TM_Logic_Utility_Viewport_Refresh(context)
            return {'FINISHED'}
        else:                
            return {'CANCELLED'}

class TM_OT_LayerManager_Remove(bpy.types.Operator):
    """TM_OT_LayerManager_Remove"""
    bl_idname       = "texture_mixer.layermanager_remove"
    bl_label        = "Remove Layer Manager"
    bl_description  = "Remove selected layer manager and all its components."
    bl_options      = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="This action CANNOT be undone!", icon='ERROR')
        layout.alert = False
        layout.separator()
        layout.label(text="This will permanently remove:")
        col = layout.column(align=True)
        col.label(text="• The selected Layer Manager")
        col.label(text="• All its layers, masks and shader nodes")
        col.label(text="• The associated material")
        col.label(text="• All generated images")
        layout.separator()
        layout.label(text="Are you sure?", icon='QUESTION')

    def execute(self, context):
        active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
        if not active_object:
            return {'CANCELLED'}

        user_data = context.scene.TM_User_Data
        manager_collection = user_data.m_managed_tm_node_manager_collection
        if len(manager_collection) == 0:
            return {'CANCELLED'}

        manager_to_remove = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        
        manager_name = manager_to_remove.m_name

        result = tm_logic.TM_Logic_LayerManager_Remove_By_Id(context, manager_to_remove.m_id)
        
        if not result:
            return {'CANCELLED'}

        for area in context.screen.areas:
            if area.type in {'PROPERTIES', 'VIEW_3D', 'OUTLINER'}:
                area.tag_redraw()

        return {'FINISHED'}

class TM_OT_LayerManager_Change_Main_Shader(bpy.types.Operator):
    """TM_OT_LayerManager_Change_Main_Shader"""
    bl_idname       = "texture_mixer.layermanager_change_main_shader"
    bl_label        = "Change Main Shader"
    bl_description  = "Change main shader for current active manager"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):

        target_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)

        result = tm_logic.TM_Logic_LayerManager_Change_Main_Shader(context, target_manager.m_id)

        if result:
            tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, target_manager.m_id)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class TM_OT_LayerManager_Apply_Working_Resolution(bpy.types.Operator):
    """TM_OT_LayerManager_Apply_Working_Resolution"""
    bl_idname       = "texture_mixer.layermanager_apply_working_resolution"
    bl_label        = "Apply Working Space Resolution Change"
    bl_description  = "Apply working resolution for current active manager"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):

        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}

        preserved_res = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_preserved_resolution)
        cache_res = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_preserved_resolution_cache)
        virtual_res = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_virtual_resolution)

        sum_preserved = preserved_res[0] * preserved_res[1]
        sum_cache = cache_res[0] * cache_res[1]
        sum_virtual = virtual_res[0] * virtual_res[1]

        if sum_virtual > sum_cache:
            active_manager.m_preserved_resolution_cache = active_manager.m_virtual_resolution
            self.report({'ERROR'}, "Working resolution cannot exceed preview resolution.")
            return {'CANCELLED'}

        if sum_preserved > sum_cache:
            return context.window_manager.invoke_props_dialog(self, width=400)
        
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.alert = True
        col.label(text="Warning!", icon='ERROR')
        col.alert = False
        col.label(text="Lowering resolution may cause:")
        col.label(text="- Irreversible blurring of details in the workspace.", icon='BLANK1')
        col.label(text="- Changes applied only to paint layers and masks.", icon='BLANK1')
        col.label(text="- Your imported textures will remain untouched.", icon='INFO')
        layout.separator()
        layout.label(text="Are you sure you want to proceed?")

    def execute(self, context):
        debug_id = "TM_OT_LayerManager_Apply_Working_Resolution"
    
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)

        result = tm_logic.TM_Logic_TMTexture_Set_Working_Resolution(context, active_manager.m_id)
        if not result:
            return {'CANCELLED'}

        active_manager.m_preserved_resolution = active_manager.m_preserved_resolution_cache

        tm_logic.TM_Logic_Utility_Viewport_Refresh(context)
        
        self.report({'INFO'}, "Working Resolution Applied")
        return {'FINISHED'}    

class TM_OT_LayerManager_Apply_Preview_Resolution(bpy.types.Operator):
    """TM_OT_LayerManager_Apply_Preview_Resolution"""
    bl_idname       = "texture_mixer.layermanager_apply_preview_resolution"
    bl_label        = "Apply Preview Resolution"
    bl_description  = "Apply preview resolution for current active manager"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_id = "TM_OT_LayerManager_Apply_Preview_Resolution"

        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}

        cache_res = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_virtual_resolution_cache)
        preserved_res = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(active_manager.m_preserved_resolution)

        sum_cache = cache_res[0] * cache_res[1]
        sum_preserved = preserved_res[0] * preserved_res[1]

        if sum_cache > sum_preserved:
            active_manager.m_virtual_resolution_cache = active_manager.m_preserved_resolution
            self.report({'ERROR'}, "Preview resolution cannot exceed Working resolution.")
            return {'CANCELLED'}
        
        result = tm_logic.TM_Logic_TMTexture_Set_Virtual_Resolution(context, active_manager.m_id)
        if not result:
            return {'CANCELLED'}       

        active_manager.m_virtual_resolution = active_manager.m_virtual_resolution_cache  

        tm_logic.TM_Logic_Utility_Viewport_Refresh(context)

        return {'FINISHED'}            
#endregion [Layer Manager]

#region [Layer]
class TM_OT_Layer_Create_New_Paint(bpy.types.Operator):
    """TM_OT_Layer_Create_New_Paint"""
    bl_idname       = "texture_mixer.layer_create_new_paint"
    bl_label        = "New Paint Layer"
    bl_description  = "Create a new paintable layer above the current selection"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_id = "TM_OT_Layer_Create_New_Paint"

        result = OP_Layer_Create_New(context, 'LAYER_PAINTABLE')

        return result

class TM_OT_Layer_Create_New_Fill(bpy.types.Operator):
    """TM_OT_Layer_Create_New_Fill"""
    bl_idname       = "texture_mixer.layer_create_new_fill"
    bl_label        = "New Fill Layer"
    bl_description  = "Create a new preserved/fill layer above the current selection"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        result = OP_Layer_Create_New(context, 'LAYER_PRESERVED')

        return result

class TM_OT_Layer_Create_New_Group(bpy.types.Operator):
    """TM_OT_Layer_Create_New_Group"""
    bl_idname       = "texture_mixer.layer_create_new_group"
    bl_label        = "New Layer Group"
    bl_description  = "Create a new group/folder above the current selection"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        result = OP_Layer_Create_New(context, 'GROUP')

        return result    

def OP_Layer_Create_New(context, layer_type: str):
    """OP_Layer_Create_New"""
    
    active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
    if active_manager is None:
        return {'CANCELLED'}        

    new_layer = tm_logic.TM_Logic_Layer_Create_New(context, layer_type)
    if new_layer is None:
        return {'CANCELLED'}
    
    layer_collection = active_manager.m_managed_tm_node_collection

    if layer_collection and len(layer_collection)>1:
        active_pointer = active_manager.m_managed_tm_node_pointer

        if not layer_collection:
            active_pointer = 0
        else:
            active_pointer = max(0, min(active_pointer, len(layer_collection) - 1))

        selected_layer = layer_collection[active_pointer]

        insert_index = active_pointer

        if selected_layer.m_group_id:
            if layer_type != 'GROUP':
                new_layer.m_group_id = selected_layer.m_group_id
            else:
                group_index = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager, selected_layer.m_group_id)
                if group_index is not None:
                    insert_index = group_index  

        current_new_index = len(layer_collection) - 1
        if current_new_index != insert_index:
            layer_collection.move(current_new_index, insert_index)

        active_manager.m_managed_tm_node_pointer = insert_index
        
    tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, active_manager.m_id)

    return {'FINISHED'}
    
class TM_OT_Layer_Remove(bpy.types.Operator):
    """TM_OT_Layer_Remove"""
    bl_idname       = "texture_mixer.layer_remove"
    bl_label        = "Remove Selected Layer"
    bl_description  = "Remove selected layer"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="This action CANNOT be undone!", icon='ERROR')
        layout.alert = False
        layout.separator()
        layout.label(text="This will permanently remove:")
        col = layout.column(align=True)
        col.label(text="• The selected Layer")
        col.label(text="• All its masks and shader nodes")
        col.label(text="• The associated material")
        col.label(text="• All generated images")
        layout.separator()
        layout.label(text="Are you sure?", icon='QUESTION')

    def execute(self, context): 

        active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)

        if not active_manager:
            return {'CANCELLED'}

        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
        if not active_layer:
            return {'CANCELLED'}

        result = tm_logic.TM_Logic_Layer_Remove_By_Id(context, active_manager.m_id, active_layer.m_id)

        if result:
            tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, active_manager.m_id)

        else:
            return {'CANCELLED'}

        return {'FINISHED'}

class TM_OT_Layer_Move(bpy.types.Operator):
    """TM_OT_Layer_Move"""
    bl_idname       = "texture_mixer.layer_move"
    bl_label        = "Move Layer"
    bl_description  = "Move selected layer up/down, respecting group boundaries"
    bl_options      = {'REGISTER', 'INTERNAL'}

    direction: EnumProperty(items=[('UP', "Selected layer go up.", ""), ('DOWN', "Selected layer go down.", "")])  

    def execute(self, context):

        active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}
        
        active_layers   = active_manager.m_managed_tm_node_collection
        active_pointer  = active_manager.m_managed_tm_node_pointer
        
        if active_layers and len(active_layers)>0:
            if active_pointer < 0 or active_pointer > len(active_layers)-1:
                return {'CANCELLED'}

        active_layer    = active_layers[active_pointer]

        if not active_layer:
            return {'CANCELLED'}

        if self.direction == 'UP':
            if active_pointer <= 0:
                return {'CANCELLED'}

            upper_pointer = active_pointer - 1
            upper_layer = active_layers[upper_pointer]
            
            if upper_layer is None:
                return {'CANCELLED'}

            if active_layer.m_type != 'GROUP':
                if not active_layer.m_group_id:
                    if not upper_layer.m_group_id:
                        active_layers.move(active_pointer, upper_pointer)
                        active_manager.m_managed_tm_node_pointer = upper_pointer
                    else:
                        index_group_header = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, upper_layer.m_group_id)                        
                        active_layers.move(active_pointer, index_group_header)
                        active_manager.m_managed_tm_node_pointer = index_group_header
                else:
                    if upper_layer.m_group_id == active_layer.m_group_id:
                        active_layers.move(active_pointer, upper_pointer)
                        active_manager.m_managed_tm_node_pointer = upper_pointer
            else:
                active_group_member_id: list[int] = []  
                active_group_member_id.append(active_layer.m_id)

                for index in range(active_pointer+1, len(active_layers)):
                    if active_layers[index].m_group_id == active_layer.m_id:
                        active_group_member_id.append(active_layers[index].m_id)
                    else:
                        break   

                if not upper_layer.m_group_id:
                    for index in range(len(active_group_member_id) - 1, -1, -1):
                        layer_id = active_group_member_id[index]  
                        layer_idx = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, layer_id)                              
                        active_layers.move(layer_idx, upper_pointer)
                    active_manager.m_managed_tm_node_pointer = upper_pointer
                else:
                    index_group_header = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, upper_layer.m_group_id)
                    for index in range(len(active_group_member_id) - 1, -1, -1):
                        layer_id = active_group_member_id[index]  
                        layer_idx = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, layer_id)
                        active_layers.move(layer_idx, index_group_header)
                    active_manager.m_managed_tm_node_pointer = index_group_header                        

        elif self.direction == 'DOWN':
            if active_pointer >= len(active_layers)-1:
                return {'CANCELLED'}
            
            lower_pointer = active_pointer + 1
            lower_layer = active_layers[lower_pointer]

            if lower_layer is None:
                return {'CANCELLED'}

            if active_layer.m_type != 'GROUP':
                if not active_layer.m_group_id:
                    if lower_layer.m_type != 'GROUP':
                        active_layers.move(active_pointer, lower_pointer)
                        active_manager.m_managed_tm_node_pointer = lower_pointer
                    else:
                        last_child_index = lower_pointer 
                        for i in range(lower_pointer + 1, len(active_layers)):
                            if active_layers[i].m_group_id == lower_layer.m_id:
                                last_child_index = i
                            else:
                                break
                        active_layers.move(active_pointer, last_child_index)
                        active_manager.m_managed_tm_node_pointer = last_child_index
                else:
                    if lower_layer.m_group_id == active_layer.m_group_id:
                        active_layers.move(active_pointer, lower_pointer)
                        active_manager.m_managed_tm_node_pointer = lower_pointer
            else:
                group_id_cache = active_layer.m_id
                active_group_member_id: list[int] = []  
                active_group_member_id.append(group_id_cache)

                for index in range(active_pointer+1, len(active_layers)):
                    if active_layers[index].m_group_id == group_id_cache:
                        active_group_member_id.append(active_layers[index].m_id)
                    else:
                        break  

                new_active_pointer = active_pointer + (len(active_group_member_id)-1)

                if new_active_pointer >= len(active_layers)-1:
                    return {'CANCELLED'}
                
                new_lower_pointer = new_active_pointer + 1
                new_lower_layer = active_layers[new_lower_pointer]
                                    
                if new_lower_layer.m_type != 'GROUP':
                    for lid in active_group_member_id:
                        layer_id = lid  
                        layer_idx = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, layer_id)
                        active_layers.move(layer_idx, new_lower_pointer)
                    active_manager.m_managed_tm_node_pointer = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, group_id_cache)
                else:
                    group_id_idx = new_lower_layer.m_id
                    target_index = new_lower_pointer
                    for x in range(new_lower_pointer+1, len(active_layers)):
                        if active_layers[x].m_group_id == group_id_idx:
                            target_index = x
                        else:
                            break
                    for lid in active_group_member_id:
                        layer_id = lid  
                        layer_idx = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, layer_id)
                        active_layers.move(layer_idx, target_index)
                    active_manager.m_managed_tm_node_pointer = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, group_id_cache)

        tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, active_manager.m_id)
        
        return {'FINISHED'}

class TM_OT_Layer_Join_Group(bpy.types.Operator):
    """TM_OT_Layer_Join_Group"""
    bl_idname       = "texture_mixer.layer_join_group"
    bl_label        = "Join Group"
    bl_description  = "Join selected layer to the group above or below"
    bl_options      = {'REGISTER', 'INTERNAL'}

    direction: EnumProperty(items=[('UP', "Join Group Above", ""), ('DOWN', "Join Group Below", "")])  

    def execute(self, context):

        active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}
        
        active_layers   = active_manager.m_managed_tm_node_collection
        active_pointer  = active_manager.m_managed_tm_node_pointer
        
        if active_layers and len(active_layers)>0:
            if active_pointer < 0 or active_pointer > len(active_layers)-1:
                return {'CANCELLED'}

        active_layer    = active_layers[active_pointer]
        
        if self.direction == 'UP':
            if active_pointer <= 0:
                return {'CANCELLED'}

            upper_pointer = active_pointer-1
            upper_layer = active_layers[upper_pointer]

            if upper_layer:
                if upper_layer.m_type == 'GROUP':
                    active_layer.m_group_id = upper_layer.m_id
                    active_manager.m_managed_tm_node_pointer = active_pointer
                elif upper_layer.m_type != 'GROUP' and upper_layer.m_group_id:
                    active_layer.m_group_id = upper_layer.m_group_id
                    active_manager.m_managed_tm_node_pointer = active_pointer
        
        elif self.direction == 'DOWN':
            if active_pointer >= len(active_layers)-1:
                return {'CANCELLED'}

            lower_pointer = active_pointer+1
            lower_layer = active_layers[lower_pointer]

            if lower_layer:
                if lower_layer.m_type != 'GROUP':
                    return {'CANCELLED'}
                
                new_pointer = lower_pointer
                
                active_layer.m_group_id = lower_layer.m_id

                active_layers.move(active_pointer, new_pointer)
                active_manager.m_managed_tm_node_pointer = new_pointer

        tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, active_manager.m_id)
        
        return {'FINISHED'}

class TM_OT_Layer_Exit_Group(bpy.types.Operator):
    """TM_OT_Layer_Exit_Group"""
    bl_idname       = "texture_mixer.layer_exit_group"
    bl_label        = "Join Group"
    bl_description  = "Ejecting selected layer to above or below the group"
    bl_options      = {'REGISTER', 'INTERNAL'}

    direction: EnumProperty(items=[('UP', "Exit To Above Group", ""), ('DOWN', "Exit To Below Group", "")])  

    def execute(self, context):

        active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}
        
        active_layers   = active_manager.m_managed_tm_node_collection
        active_pointer  = active_manager.m_managed_tm_node_pointer

        if active_layers and len(active_layers)>0:
            if active_pointer < 0 or active_pointer > len(active_layers)-1:
                return {'CANCELLED'}

        active_layer    = active_layers[active_pointer]

        if self.direction == 'UP':
            group_header_index = tm_logic.TM_Logic_Layer_Get_Index_By_Id(context, active_manager.m_id, active_layer.m_group_id)
            active_layers.move(active_pointer, group_header_index)
            active_layers[group_header_index].m_group_id = ""
            active_manager.m_managed_tm_node_pointer = group_header_index

        elif self.direction == 'DOWN':
            last_child_index = active_pointer

            for i in range(active_pointer + 1, len(active_layers)):
                if active_layers[i].m_group_id == active_layer.m_group_id:
                    last_child_index = i
                else:
                    break
            active_layers.move(active_pointer, last_child_index)
            active_layers[last_child_index].m_group_id = ""
            active_manager.m_managed_tm_node_pointer = last_child_index

        tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, active_manager.m_id)

        return {'FINISHED'}

class TM_OT_Layer_Load_Texture(bpy.types.Operator, ImportHelper):
    """TM_OT_Layer_Load_Texture"""
    bl_idname       = "texture_mixer.layer_load_texture"
    bl_label        = "Load Texture"
    bl_description  = "Load Texture File"
    bl_options      = {'REGISTER', 'INTERNAL'}

    filter_glob: StringProperty(
        default=tm_property.Addon_Data.m_supported_file_image_type,
        options={'HIDDEN'}
    )  

    m_channel_name: StringProperty(name="Channel Name")

    def execute(self, context):              

        result = OP_Texture_Loader(self, context)   

        return result
        
def OP_Texture_Loader(self, context):
    """OP_Texture_Loader""" 

    channel_meta = tm_property.TM_DT_Channels_Metadata[self.m_channel_name]        
    channel_color_space     = channel_meta['default_color_space']
    channel_attr_name       = f"m_channel_{channel_meta['default_init']}"
    channel_socket_pairs    = channel_meta['default_system_sockets']

    file_path = self.filepath
    if not file_path:
        return {'CANCELLED'}

    active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return {'CANCELLED'}

    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return {'CANCELLED'}
    
    if active_layer.m_type != 'LAYER_PRESERVED':
        return {'CANCELLED'}

    host_material = tm_logic.TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return {'CANCELLED'}

    layer_shader_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_layer.m_shader_node_system_layer_id)
    if not layer_shader_node:
        return {'CANCELLED'}
    
    layer_texture_mapping_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_layer.m_shader_node_system_texture_mapping_id)
    if not layer_texture_mapping_node:
        return {'CANCELLED'} 

    channel_target = None
    if hasattr(active_layer.m_channel, channel_attr_name):
        channel_target = getattr(active_layer.m_channel, channel_attr_name)
        
    if not channel_target:
        return {'CANCELLED'}
    
    tm_texture = None
    if channel_target.m_tm_texture_id:
        tm_texture = tm_logic.TM_logic_TMTexture_Load_Image(context,active_manager.m_id, file_path, channel_color_space, channel_target.m_tm_texture_id)
    else:
        tm_texture = tm_logic.TM_logic_TMTexture_Load_Image(context,active_manager.m_id, file_path, channel_color_space)  
        channel_target.m_tm_texture_id = tm_texture.m_id     
    if not tm_texture:
        return {'CANCELLED'}
    
    tm_texture_system_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, tm_texture.m_shader_node_system_texture_id)
    if not tm_texture_system_node:
        return {'CANCELLED'}

    for pair in channel_socket_pairs:
            tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, tm_texture_system_node, layer_shader_node, pair[0], pair[1] )
    
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Offset X", "Offset X")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Offset Y", "Offset Y")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Offset Z", "Offset Z")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Tiling X", "Tiling X")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Tiling Y", "Tiling Y")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Tiling Z", "Tiling Z")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Rotation X", "Rotation X")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Rotation Y", "Rotation Y")
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, layer_texture_mapping_node, tm_texture_system_node, "Output Rotation Z", "Rotation Z")
    
    return {'FINISHED'}

class TM_OT_Layer_Remove_Texture(bpy.types.Operator):
    """TM_OT_Layer_Remove_Texture"""
    bl_idname       = "texture_mixer.layer_remove_texture"
    bl_label        = "Remove Texture"
    bl_description  = "Remove Texture File"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    m_channel_name: StringProperty(name="Channel Name")

    def execute(self, context):        

        result = OP_Texture_Remover(self, context)
  
        return result

def OP_Texture_Remover(self, context):
    """OP_Texture_Remover"""

    channel_meta = tm_property.TM_DT_Channels_Metadata[self.m_channel_name] 
    attr_channel_name = f"m_channel_{channel_meta['default_init']}"

    active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return {'CANCELLED'}

    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return {'CANCELLED'}
    if active_layer.m_type != 'LAYER_PRESERVED':
        return {'CANCELLED'}

    channel_target = None
    if hasattr(active_layer.m_channel, attr_channel_name):
        channel_target = getattr(active_layer.m_channel, attr_channel_name)

    if not channel_target:
        return {'CANCELLED'}

    if not channel_target.m_tm_texture_id:
        return {'CANCELLED'}

    result = tm_logic.TM_Logic_TMTexture_Remove_By_Id(context, active_manager.m_id, channel_target.m_tm_texture_id)
    if result:
        channel_target.m_tm_texture_id = ""
        return {'FINISHED'}
    
    return {'CANCELLED'}
#endregion [Layer]

#region [Mask]
class TM_OT_Mask_Create_New_Paint_Black(bpy.types.Operator):
    """TM_OT_Mask_Create_New_Paint_Black"""
    bl_idname       = "texture_mixer.mask_create_new_paint_black"
    bl_label        = "Create New Black Mask"
    bl_description  = "Create New Black Mask (Opacity 0%)"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):

        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)

        tm_logic.TM_Logic_Mask_Create_New(context,'MASK_PAINTABLE',False)  
        tm_logic.TM_Logic_Mask_Refresh_ShaderNode(context, active_manager.m_id, active_layer.m_id)  

        return {'FINISHED'}
        
class TM_OT_Mask_Create_New_Paint_White(bpy.types.Operator):
    """TM_OT_Mask_Create_New_Paint_White"""
    bl_idname       = "texture_mixer.mask_create_new_paint_white"
    bl_label        = "Create New White Mask"
    bl_description  = "Create New White Mask (Opacity 100%)"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
                
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)

        tm_logic.TM_Logic_Mask_Create_New(context,'MASK_PAINTABLE',True)      
        tm_logic.TM_Logic_Mask_Refresh_ShaderNode(context, active_manager.m_id, active_layer.m_id)  
     
        return {'FINISHED'}
        
class TM_OT_Mask_Create_New_Preserved(bpy.types.Operator):
    """TM_OT_Mask_Create_New_Preserved"""
    bl_idname       = "texture_mixer.mask_create_new_preserved"
    bl_label        = "Create New Fill Mask"
    bl_description  = "Create New Fill Mask"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)

        tm_logic.TM_Logic_Mask_Create_New(context,'MASK_PRESERVED')    
        tm_logic.TM_Logic_Mask_Refresh_ShaderNode(context, active_manager.m_id, active_layer.m_id)       
        
        return {'FINISHED'}

class TM_OT_Mask_Move(bpy.types.Operator):
    """TM_OT_Mask_Move"""
    bl_idname       = "texture_mixer.mask_move"
    bl_label        = "Move Mask" 
    bl_description  = "Move Mask"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    direction: EnumProperty(items=[('UP', "Selected layer go up.", ""), ('DOWN', "Selected layer go down.", "")])

    def execute(self, context):

        active_manager  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}
        
        active_layer    = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
        if not active_layer:
            return {'CANCELLED'}
        
        active_mask_layer = active_layer.m_managed_tm_mask_collection
        if not active_mask_layer or not len(active_mask_layer) > 0:
            return {'CANCELLED'}
        
        current_position = active_layer.m_managed_tm_mask_pointer

        if self.direction == 'UP':
            if current_position > 0:
                upper_position = current_position - 1
                active_mask_layer.move(current_position, upper_position)
                active_layer.m_managed_tm_mask_pointer = upper_position
        else:
            if current_position < len(active_mask_layer) - 1:
                lower_position = current_position + 1
                active_mask_layer.move(current_position, lower_position)
                active_layer.m_managed_tm_mask_pointer = lower_position

        tm_logic.TM_Logic_Mask_Refresh_ShaderNode(context, active_manager.m_id, active_layer.m_id)

        return {'FINISHED'}

class TM_OT_Mask_Texture_Loader(bpy.types.Operator, ImportHelper):
    """TM_OT_Mask_Texture_Loader"""
    bl_idname       = "texture_mixer.mask_texture_loader"
    bl_label        = "Load Texture"
    bl_description  = "Load Texture File"
    bl_options      = {'REGISTER', 'INTERNAL'}

    filter_glob: StringProperty(
        default=tm_property.Addon_Data.m_supported_file_image_type,
        options={'HIDDEN'}
    )  

    def execute(self, context):        
            
        result = OP_Mask_Texture_Loader(self, context)   

        return result

def OP_Mask_Texture_Loader(self, context):
    """OP_Mask_Texture_Loader"""
    debug_id = "OP_Mask_Texture_Loader"

    file_path = self.filepath
    if not file_path:
        return {'CANCELLED'}

    active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return {'CANCELLED'}

    host_material = tm_logic.TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return {'CANCELLED'}

    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return {'CANCELLED'}
    
    mask_layer = active_layer.m_managed_tm_mask_collection
    if not mask_layer:
        return {'CANCELLED'}

    active_pointer = active_layer.m_managed_tm_mask_pointer
    if not active_pointer >= 0:
        return {'CANCELLED'}

    mask = mask_layer[active_pointer]
    if not mask:
        return {'CANCELLED'}
    
    active_mask_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, mask.m_shader_node_system_mask_id)
    if not active_mask_node:
        return {'CANCELLED'}        

    mask_tm_texture = None
    if mask.m_tm_texture_id:
        mask_tm_texture = tm_logic.TM_logic_TMTexture_Load_Image(context,active_manager.m_id, file_path,'Non-Color', mask.m_tm_texture_id)
    else:
        mask_tm_texture = tm_logic.TM_logic_TMTexture_Load_Image(context,active_manager.m_id, file_path, 'Non-Color')  
        mask.m_tm_texture_id = mask_tm_texture.m_id  
    if not mask_tm_texture:
        return {'CANCELLED'}        

    mask_tm_texture_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, mask_tm_texture.m_shader_node_system_texture_id)
    if not mask_tm_texture_node:
        return {'CANCELLED'}
    
    tm_logic.TM_Logic_ShaderNode_Socket_Linker(host_material, mask_tm_texture_node, active_mask_node, "Color", "Mask Texture")       
    
    return {'FINISHED'}

class TM_OT_Mask_Texture_Remover(bpy.types.Operator):
    """TM_OT_Mask_Texture_Remover"""
    bl_idname       = "texture_mixer.mask_texture_remover"
    bl_label        = "Remove Mask Texture"
    bl_description  = "Remove Mask Texture"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):        
        debug_id = "TM_OT_Mask_Texture_Remover"
                
        result = OP_Mask_Texture_Remover(self, context)

        return result

def OP_Mask_Texture_Remover(self, context):

    active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
    if not active_manager:
        return {'CANCELLED'}

    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return {'CANCELLED'}
    
    mask_layer = active_layer.m_managed_tm_mask_collection
    if not mask_layer:
        return {'CANCELLED'}

    active_pointer = active_layer.m_managed_tm_mask_pointer
    if not active_pointer >= 0:
        return {'CANCELLED'}

    mask = mask_layer[active_pointer]
    if not mask:
        return {'CANCELLED'}

    if not mask.m_tm_texture_id:
        return {'CANCELLED'}

    result = tm_logic.TM_Logic_TMTexture_Remove_By_Id(context, active_manager.m_id, mask.m_tm_texture_id)

    if result:
        mask.m_tm_texture_id = ""
        return {'FINISHED'}

class TM_OT_Mask_Remove(bpy.types.Operator):
    """TM_OT_Mask_Remove"""
    bl_idname       = "texture_mixer.mask_remove"
    bl_label        = "Remove Mask"
    bl_description  = "Remove Mask"
    bl_options      = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        debug_id = "TM_OT_Mask_Remove"

        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}

        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
        if not active_layer:
            return {'CANCELLED'}
        
        mask_layer = active_layer.m_managed_tm_mask_collection
        if not mask_layer:
            return {'CANCELLED'}

        active_pointer = active_layer.m_managed_tm_mask_pointer
        if not active_pointer >= 0:
            return {'CANCELLED'}

        mask = mask_layer[active_pointer]
        if not mask:
            return {'CANCELLED'}
        
        result = tm_logic.TM_Logic_Mask_Remove_By_Id(context, active_manager.m_id, active_layer.m_id, mask.m_id)

        if result:
            tm_logic.TM_Logic_Mask_Refresh_ShaderNode(context, active_manager.m_id, active_layer.m_id)
            return {'FINISHED'}            
        else:
            return {'CANCELLED'}
#endregion [Mask]

#region [Texture Painting]
class TM_OT_Enable_Texture_Painting_Mode(bpy.types.Operator):
    """TM_OT_Enable_Texture_Painting_Mode"""
    bl_idname       = "texture_mixer.enable_texture_painting_mode"
    bl_label        = "Enable Texture Painting Mode"
    bl_description  = "Enable Texture Painting Mode"
    bl_options      = {'REGISTER', 'UNDO'}

    def execute(self, context):
    
        if not tm_logic.TM_Logic_Utility_Viewport_Set_Object_Mode('TEXTURE_PAINT'):
            return {'CANCELLED'}

        if not tm_logic.TM_Logic_Utility_Viewport_Set_Shading(context,'MATERIAL', True, True):
            return {'CANCELLED'}

        return {'FINISHED'}

class TM_OT_Layer_Paint_Blender_Multi_Channel(bpy.types.Operator):
    """TM_OT_Layer_Paint_Blender_Multi_Channel"""
    bl_idname       = "texture_mixer.layer_paint_blender_multi_channel"
    bl_label        = "Texture Mixer Paint Mode"
    bl_description  = "Texture Mixer Paint Mode"
    bl_options      = {'REGISTER', 'INTERNAL'}
    
    m_show_text  : StringProperty(name="Show Text", default="")
    m_paint_type : EnumProperty(items=[('NONE', "", ""), ('COLOR', "", ""), ('ERASE', "", ""), ('UTILITY', "", "")])

    m_brush_type_color       = {'Airbrush','Paint Hard', 'Paint Hard Pressure', 'Paint Soft', 'Paint Soft Pressure', 'Paint Pixel Art', 'Fill'}
    m_brush_type_erase       = {'Erase Hard', 'Erase Hard Pressure', 'Erase Soft', 'Erase Pixel Art'}
    m_brush_type_utility     = {'Clone', 'Blur'}
    m_brush_type_unsupported = {'Smear', 'Mask'}
    
    m_enter_painting_mode = False
    m_ui_watermark_handle = None 
    m_active_channels   = [] 
    m_stroke_points     = []

    m_active_material   = None  
    m_user_data         = None   
    m_last_mouse_pos    = None  
    
    def invoke(self, context, event):
        try:            
            self.m_active_material = tm_logic.TM_Logic_Material_Get_Active_Material(context)
            if not self.m_active_material:
                return {'CANCELLED'}
            
            self.m_active_channels = tm_logic.TM_Logic_Layer_Paint_Mode_Get_Active_Channel_Data(context) 
            if not self.m_active_channels:
                return {'CANCELLED'}
            
            self.m_user_data = context.scene.TM_User_Data
            if not self.m_user_data:
                return {'CANCELLED'}
            
            self.DrawUI(context)

            blender_image_paint     = context.tool_settings.image_paint
            blender_brush           = blender_image_paint.brush

            blender_brush.use_pressure_size = False 
            blender_brush.use_pressure_strength = False

            if blender_brush.name in self.m_brush_type_color:
                self.m_paint_type = 'COLOR'
            elif blender_brush.name in self.m_brush_type_erase:
                self.m_paint_type = 'ERASE'
            elif blender_brush.name in self.m_brush_type_utility:
                self.m_paint_type = 'UTILITY'
            else:
                self.m_paint_type = 'NONE'        
            
            for channel in self.m_active_channels:
                for i, slot in enumerate(self.m_active_material.texture_paint_slots):
                    if slot.name == channel['channel_image_name']:
                        channel['channel_index'] = i
                        channel['chanel_canvas_image'] = bpy.data.images.get(channel['channel_image_name'])
                    
                        group_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(self.m_active_material, channel['channel_node_system_id'])
                        if not group_node:
                            return {'CANCELLED'}
                        
                        internal_tree = group_node.node_tree
                        if not internal_tree:
                            return {'CANCELLED'}
                        
                        target_node = internal_tree.nodes.get(channel['channel_node_texture_name'])
                        if not target_node:
                            return {'CANCELLED'}
                        
                        channel["shadernode_target_group"] = group_node
                        channel["shadernode_target_tree"]  = internal_tree
                        channel["shadernode_target_node"]  = target_node                        
                        break  

            self.m_user_data.m_ui_tm_paint_mode_enable = True

            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        except Exception as e:
            # print(f"Invoke Error: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}    
         
    def modal(self, context, event):
        try:
            if context.area:
                context.area.tag_redraw()

            allowed_keypress = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'F'} 

            if event.type in allowed_keypress or event.alt or event.shift or event.ctrl:
                return {'PASS_THROUGH'} 
            
            if event.type == 'LEFTMOUSE':
                if event.value == 'PRESS':
                    if not self.m_enter_painting_mode:
                        self.m_enter_painting_mode = True
                        self.BuildStrokeData(context, event)
                        self.PaintOnCanvas(context, True)
                    return {'RUNNING_MODAL'}        
                
                elif event.value == 'RELEASE':
                    self.m_enter_painting_mode = False
                    self.m_last_mouse_pos = None
                    return {'RUNNING_MODAL'}
                    
                return {'RUNNING_MODAL'}   

            elif event.type == 'MOUSEMOVE':   
                if self.m_enter_painting_mode:       
                    self.BuildStrokeData(context, event)
                    self.PaintOnCanvas(context, False)
                    return {'RUNNING_MODAL'}
                
                return {'PASS_THROUGH'}
            
            enable_paint_mode = self.m_user_data.m_ui_tm_paint_mode_enable
            exit_reasons = (
                not enable_paint_mode 
                or context.mode != 'PAINT_TEXTURE' 
                or event.type in {'ESC', 'RIGHTMOUSE'}
                or context.area is None 
                or context.area.type != 'VIEW_3D'
            )
            
            if exit_reasons:
                self.CleanUp(context)
                return {'FINISHED'}

            return {'RUNNING_MODAL'}
        except Exception as e:
            print(f"Modal Error: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}  
        
    def cancel(self, context):
        try:
            return {'RUNNING_MODAL'}
        except Exception as e:
            # print(f"Cancel Error: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}  
            
    def DrawUI(self, context):        
        self.m_ui_watermark_handle = bpy.types.SpaceView3D.draw_handler_add(self.DrawUI_Watermark, (context,), 'WINDOW', 'POST_PIXEL')

    def DrawUI_Watermark(self, context):
        text                    = f"TM | Multi Channels | {self.m_show_text}"
        font_id                 = 0
        font_size               = 20
        font_color              = (1.0, 1.0, 1.0)
        font_alpha              = 0.1 if self.m_enter_painting_mode else 1.0

        text_width, text_height = blf.dimensions(font_id, text)
        pos_x = (context.region.width / 2) - (text_width / 2)
        pos_y = context.region.height - (context.region.height / 10)

        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0.0, 0.0, 0.0, font_alpha) 
        blf.shadow_offset(font_id, 1, -1)

        blf.position(font_id, pos_x, pos_y, 0)
        blf.size(font_id, font_size)
        blf.color(font_id, font_color[0], font_color[1], font_color[2], font_alpha)
        blf.draw(font_id, text)

        blf.disable(font_id, blf.SHADOW)
    
    def BuildStrokeData(self, context, event):
        if self.m_paint_type == 'NONE':
            self.m_stroke_points.clear()
            return

        user_data_brush = self.m_user_data.m_brush_data 
        
        blender_image_paint     = context.tool_settings.image_paint
        blender_brush           = blender_image_paint.brush

        if bpy.app.version >= (5, 0, 0):
            blender_unified_brush   = blender_image_paint.unified_paint_settings
            brush_size_modifier     = 0.5
        elif bpy.app.version >= (4, 5, 0) and bpy.app.version < (5, 0, 0):
            blender_unified_brush   = context.tool_settings.unified_paint_settings
            brush_size_modifier     = 1.0

        blender_unified_brush.use_unified_color = True
        blender_unified_brush.use_unified_size  = True
        blender_unified_brush.use_unified_strength = True
        blender_unified_brush.use_unified_input_samples = True 

        pressure      = getattr(event,"pressure", 1.0)
        tilt_x        = getattr(event,"tilt_x", 0.0)
        tilt_y        = getattr(event,"tilt_y", 0.0)
        time          = getattr(event,"time", 0.0)
        brush_size    = blender_unified_brush.size * brush_size_modifier * pressure

        if user_data_brush.m_brush_option_enable_smoothing:
            current_pos     = (event.mouse_region_x, event.mouse_region_y)
            spacing_factor  = blender_brush.spacing / 100.0
            pixel_spacing   = max(5.0, brush_size * spacing_factor)

            if self.m_last_mouse_pos and self.m_enter_painting_mode:
                distance = math.dist(self.m_last_mouse_pos, current_pos)
                if distance > pixel_spacing:
                    steps = int(distance / pixel_spacing)
                    for i in range(1, steps):
                        delta = i / steps
                        interp_x = self.m_last_mouse_pos[0] + (current_pos[0] - self.m_last_mouse_pos[0]) * delta
                        interp_y = self.m_last_mouse_pos[1] + (current_pos[1] - self.m_last_mouse_pos[1]) * delta
                        self.m_stroke_points.append({
                            'mouse_region_x': interp_x,
                            'mouse_region_y': interp_y,
                            'pressure'      : pressure,
                            'tilt_x'        : tilt_x,
                            'tilt_y'        : tilt_y,
                            'time'          : time,
                            'size'          : brush_size,
                        })

            self.m_stroke_points.append({
                'mouse_region_x': current_pos[0],
                'mouse_region_y': current_pos[1],
                'pressure'      : pressure,
                'tilt_x'        : tilt_x,
                'tilt_y'        : tilt_y,
                'time'          : time,
                'size'          : brush_size,
            })

            self.m_last_mouse_pos = current_pos

        else:
            self.m_stroke_points.append({
                'mouse_region_x': event.mouse_region_x,
                'mouse_region_y': event.mouse_region_y,
                'pressure'      : pressure,
                'tilt_x'        : tilt_x,
                'tilt_y'        : tilt_y,
                'time'          : time,
                'size'          : brush_size
            })

    def PaintOnCanvas(self, context, is_start:bool=False):
        if not self.m_stroke_points:
            return        
        
        user_brush_data     = self.m_user_data.m_brush_data
        
        blender_image_paint     = context.tool_settings.image_paint
        blender_brush           = blender_image_paint.brush

        if bpy.app.version >= (5, 0, 0):
            blender_unified_brush   = blender_image_paint.unified_paint_settings
        elif bpy.app.version >= (4, 5, 0) and bpy.app.version < (5, 0, 0):
            blender_unified_brush   = context.tool_settings.unified_paint_settings

        stroke_batch = []
        
        for point in self.m_stroke_points:
            stroke_batch.append({
                "name"          : "stroke",
                "location"      : (0,0,0),
                "is_start"      : is_start,
                "mouse"         : (point['mouse_region_x'], point['mouse_region_y']),
                "mouse_event"   : (point['mouse_region_x'], point['mouse_region_y']),
                "pressure"      : point['pressure'],
                "x_tilt"        : point['tilt_x'],
                "y_tilt"        : point['tilt_y'],
                "time"          : point['time'],
                "size"          : point['size'],
            })

        for channel in self.m_active_channels:
            channel_name                            = channel['channel_name']
            channel_index                           = channel['channel_index']
            channel_color_neutral                   = channel['channel_color_neutral']
            channel_canvas                          = channel['chanel_canvas_image']

            channel_sn_target_group                 = channel["shadernode_target_group"]
            channel_sn_target_tree                  = channel["shadernode_target_tree"]
            channel_sn_target_node                  = channel["shadernode_target_node"] 
            
            channel_enable                          = getattr(user_brush_data, f"m_channel_{channel['channel_init']}_enable")    
            channel_color                           = getattr(user_brush_data, f"m_brush_{channel['channel_init']}_color")  
            channel_blend                           = getattr(user_brush_data, f"m_brush_{channel['channel_init']}_blend")      

            if not channel_enable and user_brush_data.m_brush_option_skip_channel:
                continue   

            if self.m_paint_type == 'COLOR' or self.m_paint_type == 'ERASE':
                
                if self.m_paint_type == 'COLOR':
                    if channel_enable: 
                        channel_color_rgb = (channel_color[0], channel_color[1], channel_color[2])
                    else:
                        channel_color_rgb = (channel_color_neutral[0], channel_color_neutral[1], channel_color_neutral[2])

                    if hasattr(blender_brush,"blend"):
                        setattr(blender_brush,"blend", channel_blend)

                else:
                    channel_color_rgb = (channel_color_neutral[0], channel_color_neutral[1], channel_color_neutral[2])
                    channel_blend     = 'MIX'

                    if channel_enable: 
                        if channel_name == 'Base Color':
                            channel_blend = 'ERASE_ALPHA'                            
                    else:
                        if channel_name == 'Base Color':
                            continue 

                    if hasattr(blender_brush,"blend"):
                        setattr(blender_brush,"blend", channel_blend)
                        
                setattr(blender_unified_brush,"color", channel_color_rgb)
                setattr(blender_unified_brush,"secondary_color", channel_color_rgb)

            setattr(self.m_active_material,"paint_active_slot", channel_index)
            setattr(blender_image_paint,"canvas", channel_canvas)

            self.m_active_material.node_tree.nodes.active        = channel_sn_target_group
            self.m_active_material.node_tree.nodes.active.select = True

            channel_sn_target_tree.nodes.active     = channel_sn_target_node
            channel_sn_target_node.select           = True

            bpy.ops.paint.image_paint(
                    'EXEC_DEFAULT', 
                    False,
                    stroke = stroke_batch)                

        self.m_stroke_points.clear()
    
    def CleanUp(self, context):
        self.m_user_data.m_ui_tm_paint_mode_enable = False     
        self.m_enter_painting_mode = False
        self.m_show_text = ""

        if self.m_ui_watermark_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.m_ui_watermark_handle, 'WINDOW')
            self.m_ui_watermark_handle = None

        if len(self.m_stroke_points) > 0:
            self.m_stroke_points.clear()

        if len(self.m_active_channels) > 0:
            for channel in self.m_active_channels:
                channel['chanel_canvas_image']      = None                
                channel["shadernode_target_group"]  = None
                channel["shadernode_target_tree"]   = None
                channel["shadernode_target_node"]   = None 

                manager_id      = channel['manager_id']                
                tmtexture_id    = channel['channel_tmtexture_id']

                tm_logic.TM_Logic_TMTexture_Virtual_Image_Update(context, manager_id, tmtexture_id)
                tm_logic.TM_Logic_TMTexture_Switch_To_Virtual(context, manager_id, tmtexture_id)
            self.m_active_channels.clear()

        if self.m_active_material:
            self.m_active_material = None

        if self.m_user_data:
            self.m_user_data = None

class TM_OT_Layer_Paint_Blender_Single_Channel(bpy.types.Operator):
    """TM_OT_Layer_Paint_Blender_Single_Channel"""
    bl_idname       = "texture_mixer.layer_paint_blender_single_channel"
    bl_label        = "Blender Paint Mode"
    bl_description  = "Blender Paint Mode"
    bl_options      = {'REGISTER', 'INTERNAL', 'UNDO'}

    m_show_text             : StringProperty(name="Show Text", default="")
    m_channel_name_target   : StringProperty(name="Channel Target", default="")

    debug_id                = "TM_OT_Layer_Paint_Blender_Single_Channel"
    
    m_active_object         = None
    m_channel_active        = []  
    m_enter_painting_mode   = False 
    m_handle                = None   

    #region [Internal]
    def invoke(self, context, event):
        try:
            self.OnGUI(context)
            return self.Start(context, event)
        except Exception as e:
            # print(f"Invoke Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}   
   
    def modal(self, context, event):  
        try:                          
            if context.area:
                context.area.tag_redraw()

            allowed_keypress = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'RIGHTMOUSE', 'F'} 

            if event.type in allowed_keypress or event.alt or event.shift or event.ctrl:
                return {'PASS_THROUGH'} 

            if context.region.type == 'UI':
                return {'PASS_THROUGH'}
            
            if event.type == 'LEFTMOUSE':
                return self.OnPointerEnter(context, event)
            
            if event.type == 'MOUSEMOVE':
                return self.OnPointerMove(context, event)
            
            active_object       = context.active_object
            enable_paint_mode   = context.scene.TM_User_Data.m_ui_tm_paint_mode_enable
            exit_reasons = (
                self.m_active_object != active_object 
                or not enable_paint_mode 
                or context.mode != 'PAINT_TEXTURE' 
                or event.type in {'ESC'}
                or context.area is None 
                or context.area.type != 'VIEW_3D'
            )
            if exit_reasons:
                return self.OnPointerExit(context) 
            return {'RUNNING_MODAL'} 
        except Exception as e:
            # print(f"Modal Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}      
    
    def cancel(self, context):
        try:
            self.CleanUp(context)        
        except Exception as e:
            # print(f"Cancel Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}              
    #endregion [Internal]

    #region [UI]
    def OnGUI(self, context):        
        self.m_handle = bpy.types.SpaceView3D.draw_handler_add(self.DrawUI, (context,), 'WINDOW', 'POST_PIXEL')

    def DrawUI(self, context):
        text                    = f"Blender | {self.m_channel_name_target} | {self.m_show_text}"
        font_id                 = 0
        font_size               = 20
        font_color              = (1.0, 1.0, 1.0)
        font_alpha              = 0.1 if self.m_enter_painting_mode else 1.0

        text_width, text_height = blf.dimensions(font_id, text)
        pos_x = (context.region.width / 2) - (text_width / 2)
        pos_y = context.region.height - (context.region.height / 10)

        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0.0, 0.0, 0.0, font_alpha) 
        blf.shadow_offset(font_id, 1, -1)

        blf.position(font_id, pos_x, pos_y, 0)
        blf.size(font_id, font_size)
        blf.color(font_id, font_color[0], font_color[1], font_color[2], font_alpha)
        blf.draw(font_id, text)

        blf.disable(font_id, blf.SHADOW)
    #endregion [UI]

    #region [Runtime]
    def Start(self, context, event):
        """[private void Start()]"""

        active_object = context.active_object 

        if self.m_active_object and self.m_active_object != active_object:
            self.CleanUp(context)  
            return {'CANCELLED'} 

        if context.area.type == 'VIEW_3D' and context.mode == 'PAINT_TEXTURE':
        
            self.m_active_object = active_object

            context.scene.TM_User_Data.m_ui_tm_paint_mode_enable = True
            
            self.BuildCanvasData(context)  
            
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}     
        
        self.CleanUp(context)  
        return {'CANCELLED'}
    
    def OnPointerEnter(self, context, event):
        if event.value == 'PRESS':
            self.m_enter_painting_mode = True
            return {'PASS_THROUGH'}        
        
        elif event.value == 'RELEASE':
            self.m_enter_painting_mode = True
            return {'PASS_THROUGH'}
            
        return {'PASS_THROUGH'}   
    
    def OnPointerMove(self, context, event):
        self.m_enter_painting_mode = False
        return {'PASS_THROUGH'}
    
    def OnPointerExit(self, context):
        """Handle exit process clean up"""
        self.CleanUp(context)
        return {'FINISHED'}
    #endregion [Runtime]

    def BuildCanvasData(self, context):     
        active_material         = tm_logic.TM_Logic_Material_Get_Active_Material(context)
        
        self.m_channel_active.clear()
        if self.m_channel_name_target == 'Mask':
            self.m_channel_active = tm_logic.TM_Logic_Mask_Paint_Mode_Get_Active_Mask_Data(context) 
        else:
            self.m_channel_active = tm_logic.TM_Logic_Layer_Paint_Mode_Get_Active_Channel_Data(context) 
                    
        for index, canvas in enumerate(self.m_channel_active):
            if canvas['channel_name'] == self.m_channel_name_target:
                for slot_index, slot in enumerate(active_material.texture_paint_slots):
                    if slot.name == canvas['channel_image_name']:   
                        canvas['channel_index'] = slot_index 
                        OP_Layer_Paint_Activate_Canvas(self, context, index, active_material)
                        break  
                break

    def CleanUp(self, context):
        self.m_enter_painting_mode = False

        if self.m_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.m_handle, 'WINDOW')
            self.m_handle = None

        if len(self.m_channel_active) > 0:
            for canvas in self.m_channel_active:
                if canvas['channel_name'] == self.m_channel_name_target:
                    manager_id      = canvas['manager_id']                
                    tmtexture_id    = canvas['channel_tmtexture_id']
                    tm_logic.TM_Logic_TMTexture_Virtual_Image_Update(context, manager_id, tmtexture_id)
                    tm_logic.TM_Logic_TMTexture_Switch_To_Virtual(context, manager_id, tmtexture_id)
                    break
            self.m_channel_active.clear()
            
        self.m_show_text = ""
        self.m_channel_name_target = ""
        
        context.scene.TM_User_Data.m_ui_tm_paint_mode_enable = False
        if self.m_active_object:
            self.m_active_object = None        

def OP_Layer_Paint_Activate_Canvas(self, context, index, active_material):
    user_data               = context.scene.TM_User_Data
    user_brush_data         = user_data.m_brush_data

    blender_image_paint     = context.tool_settings.image_paint

    blender_brush           = blender_image_paint.brush

    if bpy.app.version >= (5, 0, 0):
        blender_unified_brush   = blender_image_paint.unified_paint_settings
    elif bpy.app.version >= (4, 5, 0) and bpy.app.version < (5, 0, 0):
        blender_unified_brush   = context.tool_settings.unified_paint_settings

    blender_unified_brush.use_unified_color = True
    blender_unified_brush.use_unified_size  = True
    blender_unified_brush.use_unified_strength = True
    blender_unified_brush.use_unified_input_samples = True    

    canvas                      = self.m_channel_active[index]
    channel_index               = canvas['channel_index']          
    channel_color_neutral       = canvas['channel_color_neutral']
    channel_node_system_id      = canvas['channel_node_system_id']
    channel_node_texture_name   = canvas['channel_node_texture_name']
    channel_enable              = getattr(user_brush_data, f"m_channel_{canvas['channel_init']}_enable")    
    channel_color               = getattr(user_brush_data,f"m_brush_{canvas['channel_init']}_color")  
    channel_blend               = getattr(user_brush_data,f"m_brush_{canvas['channel_init']}_blend")  
    channel_canvas              = bpy.data.images.get(canvas['channel_image_name'])   

    if channel_enable: 
        channel_color_rgb       = (channel_color[0], channel_color[1], channel_color[2])
    else:
        channel_color_rgb       = (channel_color_neutral[0], channel_color_neutral[1], channel_color_neutral[2])

    if hasattr(active_material,"paint_active_slot"):
        setattr(active_material,"paint_active_slot", channel_index)

    if hasattr(blender_image_paint,"canvas"):
        setattr(blender_image_paint,"canvas", channel_canvas)
    
    if hasattr(blender_unified_brush,"color"):
        setattr(blender_unified_brush,"color", channel_color_rgb)

    if hasattr(blender_unified_brush,"secondary_color"):
        setattr(blender_unified_brush,"secondary_color", channel_color_rgb)        

    if hasattr(blender_brush,"blend"):
        setattr(blender_brush,"blend", channel_blend)

    tm_logic.TM_Logic_ShaderNode_Set_Internal_Node_Active(active_material, channel_node_system_id, channel_node_texture_name)
#endregion [Texture Painting]

#region [Export]
class TM_OT_Export_Template_Create_New(bpy.types.Operator):
    """TM_OT_Export_Template_Create_New"""
    bl_idname       = "texture_mixer.export_template_create_new"
    bl_label        = "Create New Export Template"
    bl_description  = "Create New Export Template"
    bl_options      = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):

        new_template = tm_logic.TM_Logic_Export_Template_Create_New(context)

        if new_template:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class TM_OT_Export_Template_Delete(bpy.types.Operator):
    """TM_OT_Export_Template_Delete"""
    bl_idname       = "texture_mixer.export_template_delete"
    bl_label        = "Delete Export Template"
    bl_description  = "Delete Export Template"
    bl_options      = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):

        remove_action = tm_logic.TM_Logic_Export_Template_Remove(context)

        if remove_action:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class TM_OT_Export_Bake(bpy.types.Operator):
    """TM_OT_Export_Bake"""
    bl_idname       = "texture_mixer.export_bake"
    bl_label        = "Bake Export Texture"
    bl_description  = "Bake Export Texture"
    bl_options      = {'REGISTER', 'INTERNAL', 'BLOCKING'}

    m_process_state : EnumProperty(name="Process State", items=[
        ('None', "", ""),
        ('Start', "", ""),
        ('BakeMap', "", ""),
        ('Exporting', "", ""),
        ('CleanUp', "", ""),
    ], default='None')

    m_map_to_bake = []
    m_baked_pixel_cache = {}

    m_ui_watermark_handle = None
    m_ui_progress_handle = None

    m_ui_progress_text = "Progress - Start Initializing"

    m_progress_total = 0
    m_progress_count = 0
    m_start_time = 0
    m_force_update_timer = None

    m_active_manager = None
    m_active_material = None
    m_active_output_node = None
    m_active_composer_node = None
    m_active_emission_node = None
    m_active_bake_target_tex_node = None
    m_main_shader_node = None
    m_export_resolution = None

    m_original_viewtransform = None
    m_original_look = None
    m_original_exposure = None

    def invoke(self, context, event):
        try:
            self.DrawUI(context)
            return self.Start(context, event)
        except Exception as e:
            # print(f"Invoke Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}   
        
    def modal(self, context, event):
        try:                 
            if event.type == 'TIMER':
                pass

            if context.area:
                context.area.tag_redraw()

            if self.m_process_state == 'BakeMap':
                return self.BakeTexture(context)

            elif self.m_process_state == 'Exporting':
                return self.AssemblyExportMap(context)

            elif self.m_process_state == 'CleanUp':
                self.CleanUp(context)
                return {'FINISHED'}

            return {'RUNNING_MODAL'} 
        except Exception as e:
            # print(f"Modal Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}  

    def cancel(self, context):
        try:
            self.CleanUp(context)        
        except Exception as e:
            # print(f"Cancel Exception: {e}")
            self.CleanUp(context)
            return {'CANCELLED'}  
    

    def DrawUI(self, context):        
        self.m_ui_watermark_handle = bpy.types.SpaceView3D.draw_handler_add(self.DrawUI_WaterMark, (context,), 'WINDOW', 'POST_PIXEL')
        self.m_ui_progress_handle = bpy.types.SpaceView3D.draw_handler_add(self.DrawUI_Progress, (context,), 'WINDOW', 'POST_PIXEL')
        
    def DrawUI_WaterMark(self, context):
        text                    = f"TM | Bake-Export"
        font_id                 = 0
        font_size               = 25
        font_color              = (1.0, 1.0, 1.0)
        font_alpha              = 1.0

        
        pos_x = (context.region.width / 2) - (context.region.width / 20)  
        pos_y = (context.region.height / 2) + (context.region.height / 20)

        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0.0, 0.0, 0.0, font_alpha) 
        blf.shadow_offset(font_id, 1, -1)

        blf.position(font_id, pos_x, pos_y, 0)
        blf.size(font_id, font_size)
        blf.color(font_id, font_color[0], font_color[1], font_color[2], font_alpha)
        blf.draw(font_id, text)

        blf.disable(font_id, blf.SHADOW)

    def DrawUI_Progress(self, context):
        try:
            text = self.m_ui_progress_text
        except ReferenceError:
            return

        font_id                 = 0
        font_size               = 15
        font_color              = (1.0, 1.0, 1.0)
        font_alpha              = 1.0

        pos_x = (context.region.width / 2) - (context.region.width / 20)
        pos_y = (context.region.height / 2) + ((context.region.height / 20) - (font_size * 2.0))

        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0.0, 0.0, 0.0, font_alpha) 
        blf.shadow_offset(font_id, 1, -1)

        blf.position(font_id, pos_x, pos_y, 0)
        blf.size(font_id, font_size)
        blf.color(font_id, font_color[0], font_color[1], font_color[2], font_alpha)
        blf.draw(font_id, text)

        blf.disable(font_id, blf.SHADOW)
    

    def Start(self, context, event):        
        #region [Init]
        self.m_active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not self.m_active_manager:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_active_material = tm_logic.TM_Logic_Material_Get_Active_Material(context)
        if not self.m_active_material:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_active_output_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(self.m_active_material, self.m_active_manager.m_shader_node_output_id)
        if not self.m_active_output_node:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_active_composer_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(self.m_active_material, self.m_active_manager.m_shader_node_system_composer_id)
        if not self.m_active_composer_node:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_main_shader_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(self.m_active_material, self.m_active_manager.m_shader_node_main_shader_id)
        if not self.m_main_shader_node:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_active_emission_node = tm_logic.TM_Logic_ShaderNode_Create_New_By_IdName(context, self.m_active_material, 'ShaderNodeEmission')
        if not self.m_active_emission_node:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_active_bake_target_tex_node = tm_logic.TM_Logic_ShaderNode_Create_New_By_IdName(context, self.m_active_material, 'ShaderNodeTexImage')
        if not self.m_active_bake_target_tex_node:
            self.CleanUp(context)  
            return {'CANCELLED'}
                        
        self.m_export_resolution   = tm_logic.TM_Logic_Utility_Get_Resolution_From_Preset(self.m_active_manager.m_output_resolution)
        #endregion [Init]

        export_path = self.m_active_manager.m_data.m_export_save_file_path
        if not export_path or not os.path.exists(export_path):
            self.CleanUp(context)
            return {'CANCELLED'}
        
        self.m_original_viewtransform   = context.scene.view_settings.view_transform
        self.m_original_look            = context.scene.view_settings.look
        self.m_original_exposure        = context.scene.view_settings.exposure

        context.scene.view_settings.view_transform = 'Standard'
        context.scene.view_settings.look = 'None'
        context.scene.view_settings.exposure = 0.0
        
        self.m_process_state = 'Start'
        self.m_start_time = time.time()
        self.m_force_update_timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        #region [Export Data]
        export_template_collection = self.m_active_manager.m_managed_tm_texture_export_collection
        if len (export_template_collection) == 0:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_baked_pixel_cache.clear()
        self.m_map_to_bake.clear()
        non_render_map = {'Black', 'White', 'None'}
        for template in export_template_collection:
            if not template.m_enable:
                continue
            def check_template(channel_name:str):
                map = getattr(template,f"m_slot_{channel_name}_map")
                if not map in non_render_map and not map in self.m_map_to_bake:
                    self.m_map_to_bake.append(map)
            check_template('r')
            check_template('g')
            check_template('b')
            check_template('a')

        if len(self.m_map_to_bake) == 0:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        self.m_progress_total += len(self.m_map_to_bake)
        #endregion [Export Data]           
        
        #region [Prepare-BakeMap]        
        viewport_set_mode = tm_logic.TM_Logic_Utility_Viewport_Set_Mode(context, 'OBJECT')
        if not viewport_set_mode:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        viewport_set_shading = tm_logic.TM_Logic_Utility_Viewport_Set_Shading(context, 'WIREFRAME', False)
        if not viewport_set_shading:
            self.CleanUp(context)  
            return {'CANCELLED'}
        
        context.scene.render.engine = 'CYCLES'        
        context.scene.cycles.use_denoising = False
        context.scene.cycles.use_adaptive_sampling = False
        tm_logic.TM_Logic_Render_Set_GPU_Rendering(context)
        #endregion [Prepare-BakeMap]   
        
        #region [TM_Texture]
        tm_texture_collection = self.m_active_manager.m_managed_tm_texture_collection
        for tm_texture in tm_texture_collection:
            tm_logic.TM_Logic_TMTexture_Switch_To_Preserved(context, self.m_active_manager.m_id, tm_texture.m_id)
        #endregion [TM_Texture]  
        
        self.m_process_state = 'BakeMap'

        return {'RUNNING_MODAL'}
        
    def CleanUp(self, context):
        self.m_progress_total = 0
        self.m_progress_count = 0
        self.m_start_time = 0

        if self.m_original_viewtransform:
            context.scene.view_settings.view_transform = self.m_original_viewtransform
            self.m_original_viewtransform = None

        if self.m_original_look:
            context.scene.view_settings.look           = self.m_original_look
            self.m_original_look = None

        if self.m_original_exposure:
            context.scene.view_settings.exposure       = self.m_original_exposure
            self.m_original_exposure = None

        if bpy.app.version >= (5, 0, 0):
            context.scene.render.engine = 'BLENDER_EEVEE'
        elif bpy.app.version >= (4, 5, 0) and bpy.app.version < (5, 0, 0):
            context.scene.render.engine = 'BLENDER_EEVEE_NEXT'            

        if self.m_force_update_timer:
            context.window_manager.event_timer_remove(self.m_force_update_timer)

        if self.m_ui_watermark_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.m_ui_watermark_handle, 'WINDOW')

        if self.m_ui_progress_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.m_ui_progress_handle, 'WINDOW')
        
        tm_logic.TM_Logic_Utility_Viewport_Set_Shading(context, 'MATERIAL', True)
        
        if self.m_baked_pixel_cache:
            self.m_baked_pixel_cache.clear()            
        
        tm_texture_collection = self.m_active_manager.m_managed_tm_texture_collection
        for tm_texture in tm_texture_collection:
            tm_logic.TM_Logic_TMTexture_Switch_To_Virtual(context, self.m_active_manager.m_id, tm_texture.m_id)

        if self.m_active_emission_node:
            tm_logic.TM_Logic_ShaderNode_Remove_Node_By_Id(self.m_active_material, self.m_active_emission_node.get(stamp_id))
            self.m_active_emission_node = None

        if self.m_active_bake_target_tex_node:
            tm_logic.TM_Logic_ShaderNode_Remove_Node_By_Id(self.m_active_material, self.m_active_bake_target_tex_node.get(stamp_id))
            self.m_active_bake_target_tex_node = None        

        tm_logic.TM_Logic_Layer_Refresh_ShaderNode(context, self.m_active_manager.m_id)

        self.m_active_manager = None
        self.m_active_material = None
        self.m_active_output_node = None
        self.m_active_composer_node = None
        self.m_export_resolution = None    
        self.m_main_shader_node = None

        self.m_process_state = 'None'            


    def BakeTexture(self, context):
        if not self.m_map_to_bake:
            self.m_ui_progress_text = f"Progress - Assembly & Export Map"
            self.m_process_state = 'Exporting'          
            return {'RUNNING_MODAL'}       

        map_name = self.m_map_to_bake.pop(0)
        self.m_progress_count += 1

        self.m_ui_progress_text = f"Progress ({self.m_progress_count}/{self.m_progress_total}) - Bake {map_name} texture (Please Wait)"
        
        export_set_metadata = tm_property.TM_DT_Export_Texture_Metadata 
        export_data = export_set_metadata.get(map_name)
        export_color_space = export_data.get('color_space')
        export_shader_output = export_data.get('shader_output')
        export_socket_output = export_data.get('socket_output')
        export_bake_type = export_data.get('bake_type')
        export_channel_rgb = export_data.get('channel_rgb')

        if not export_channel_rgb:
            return {'RUNNING_MODAL'}

        image_bake_target = tm_logic.TM_Logic_Image_Generate_New(context, self.m_export_resolution, (0.0,0.0,0.0,0.0), True, True, export_color_space)

        self.m_active_bake_target_tex_node.image = image_bake_target
        
        export_margin = self.m_active_manager.m_data.m_export_render_margin_size
        
        context.scene.cycles.samples = export_data.get('bake_cycles_samples', 64)     

        if export_shader_output == 'BSDF':

            if hasattr(context.scene.render.bake, "use_pass_direct"):
                context.scene.render.bake.use_pass_direct = export_data.get('use_pass_direct', False)
                
            if hasattr(context.scene.render.bake, "use_pass_indirect"):
                context.scene.render.bake.use_pass_indirect = export_data.get('use_pass_indirect', False)
            
            if hasattr(context.scene.render.bake, "use_pass_color"):
                context.scene.render.bake.use_pass_color = export_data.get('use_pass_color', False)
            
            if hasattr(context.scene.render.bake, "use_pass_ambient_occlusion"):
                context.scene.render.bake.use_pass_ambient_occlusion = export_data.get('use_pass_ambient_occlusion', False)
            
            if hasattr(context.scene.render.bake, "use_pass_shadow"):
                context.scene.render.bake.use_pass_shadow = export_data.get('use_pass_shadow', False)   

            tm_logic.TM_Logic_ShaderNode_Socket_Linker(self.m_active_material, self.m_main_shader_node, self.m_active_output_node, export_socket_output, 'Surface')
        elif export_shader_output == 'COMPOSER':
            tm_logic.TM_Logic_ShaderNode_Socket_Linker(self.m_active_material, self.m_active_emission_node, self.m_active_output_node, 'Emission', 'Surface')
            tm_logic.TM_Logic_ShaderNode_Socket_Linker(self.m_active_material, self.m_active_composer_node, self.m_active_emission_node, export_socket_output, 'Color')

        tm_logic.TM_Logic_ShaderNode_Set_Node_Active(self.m_active_material, self.m_active_bake_target_tex_node)
        
        bpy.ops.object.bake(type=export_bake_type, 
                            margin=export_margin, 
                            margin_type='EXTEND', 
                            use_clear=True)
        
        image_bake_target.update()

        width, height = self.m_export_resolution

        buffer = np.empty(width * height * 4, dtype=np.float32)

        image_bake_target.pixels.foreach_get(buffer)

        buffer = buffer.reshape((height, width, 4))

        channel_length = len(export_channel_rgb)

        if channel_length == 1:
            filtered_buffer = buffer[..., 0].copy()
        else:
            filtered_buffer = buffer[..., :3].copy()

        self.m_baked_pixel_cache[map_name] = filtered_buffer

        image_id = image_bake_target.get(stamp_id)

        self.m_active_bake_target_tex_node.image = None

        tm_logic.TM_Logic_Image_Remove_By_Id(image_id)

        return {'RUNNING_MODAL'}
    
    def AssemblyExportMap(self, context):
        """Assemble templates and save to disk"""
        width, height       = self.m_export_resolution
        template_collection = self.m_active_manager.m_managed_tm_texture_export_collection

        metadata            = tm_property.TM_DT_Export_Texture_Metadata
        file_type_data_set  = tm_property.TM_DT_Export_File_Type
        file_save_path      = self.m_active_manager.m_data.m_export_save_file_path
        output_buffer       = np.zeros((height, width, 4), dtype=np.float32)

        for template in template_collection:
            if not template.m_enable:
                continue

            output_buffer.fill(0.0)
            output_buffer[..., 3]   = 1.0

            file_type               = template.m_file_type
            file_type_data          = file_type_data_set.get(file_type)
            file_bit_depths         = file_type_data.get('bit_depths')
            file_extension          = file_type_data.get('extension')            
            file_support_alpha      = file_type_data.get('support_alpha')
            file_bit_depth          = file_bit_depths[1] if len(file_bit_depths)>1 else file_bit_depths[0]

            render_params = context.scene.render.image_settings
            render_params.file_format   = file_type
            render_params.color_mode    = 'RGBA' if file_support_alpha else 'RGB'
            render_params.color_depth   = file_bit_depth

            for i, slot in enumerate(['r', 'g', 'b', 'a']):
                map_source          = getattr(template, f"m_slot_{slot}_map")
                channel_source      = getattr(template, f"m_slot_{slot}_channel")
                invert              = getattr(template, f"m_slot_{slot}_invert")
                export_as_srgb      = getattr(template, f"m_slot_{slot}_as_srgb")
                color_space         = metadata.get(map_source).get('color_space')

                if slot == 'a':
                    if not file_support_alpha or map_source == 'None':
                        continue

                if map_source == 'None':
                    output_buffer[..., i] = 0.0
                elif map_source == 'White':
                    output_buffer[..., i] = 1.0
                elif map_source == 'Black':
                    output_buffer[..., i] = 0.0
                elif map_source in self.m_baked_pixel_cache:
                    cached_data = self.m_baked_pixel_cache[map_source]
                    is_vector3 = (cached_data.ndim == 3)

                    if channel_source == 'None':
                        work_data = 0.0
                    elif channel_source == 'BW':
                        work_data = cached_data[..., 0].copy() if is_vector3 else cached_data.copy()                        
                    elif channel_source == 'R':
                        work_data = cached_data[..., 0].copy() 
                    elif channel_source == 'G':
                        work_data = cached_data[..., 1].copy() 
                    elif channel_source == 'B':
                        work_data = cached_data[..., 2].copy()                    

                    if invert:
                        work_data = 1.0 - work_data

                    if export_as_srgb and  color_space == 'Non-Color':
                        np.maximum(work_data, 0.0, out=work_data)
                        np.power(work_data, 2.2, out=work_data)
                    elif not export_as_srgb and color_space != 'Non-Color':
                        np.maximum(work_data, 0.0, out=work_data)
                        np.power(work_data, 1.0/2.2, out=work_data)

                    output_buffer[..., i] = work_data

            export_name = f"{template.m_name}{file_extension}"
            full_path   = os.path.join(file_save_path, export_name)

            temp_img    = bpy.data.images.new(name="TM_Temp_Export", width=width, height=height, alpha=file_support_alpha, float_buffer=False if file_bit_depth == 8 else True)
            
            temp_img.pixels.foreach_set(output_buffer.ravel())
            temp_img.update()
            temp_img.file_format = template.m_file_type
            temp_img.save_render(filepath=full_path)
            
            bpy.data.images.remove(temp_img)

        del output_buffer

        total_time = time.time() - self.m_start_time
        print(f"\n--- TM EXPORT REPORT ---")
        print(f"Status: SUCCESS")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Resolution: {width}x{height}")
        print(f"------------------------\n")

        self.m_ui_progress_text = f"Progress - Finished in {total_time:.2f}s"
        self.m_process_state = 'CleanUp'
        return {'RUNNING_MODAL'}

class TM_OT_Export_Build_Active_Channels_Template(bpy.types.Operator):
    """TM_OT_Export_BuildActive_Channels_Template"""
    bl_idname       = "texture_mixer.export_build_active_channels_template"
    bl_label        = "Build Active Channels Template"
    bl_description  = "Build Active Channels Template"
    bl_options      = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):

        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return {'CANCELLED'}
        
        channel_metadata = tm_property.TM_DT_Channels_Metadata

        for channel in channel_metadata.values():
            init = channel.get('default_init')
            name = channel.get('default_name')
            rgba = channel.get('default_channel_rgba')
            is_enable = getattr(active_manager, f"m_channel_{init}_enable", False)

            if not is_enable:
                continue

            new_template = tm_logic.TM_Logic_Export_Template_Create_New(context)
            if not new_template:
                return {'CANCELLED'}
            
            new_template.m_name = f"Default_{name}_Map"

            if name == 'Normal':
                name = 'Processed Normal'

            if len(rgba) == 4:
                new_template.m_slot_r_map = name
                new_template.m_slot_r_channel = 'R'
                new_template.m_slot_g_map = name
                new_template.m_slot_g_channel = 'G'
                new_template.m_slot_b_map = name
                new_template.m_slot_b_channel = 'B'
                new_template.m_slot_a_map = 'Alpha'
                new_template.m_slot_a_channel = 'BW'
                new_template.m_file_type = 'PNG'
            elif len(rgba) == 3:
                new_template.m_slot_r_map = name
                new_template.m_slot_r_channel = 'R'
                new_template.m_slot_g_map = name
                new_template.m_slot_g_channel = 'G'
                new_template.m_slot_b_map = name
                new_template.m_slot_b_channel = 'B'
                new_template.m_slot_a_map = 'None'
                new_template.m_slot_a_channel = 'None'
                new_template.m_file_type = 'JPEG'
            elif len(rgba) == 1:
                new_template.m_slot_r_map = name
                new_template.m_slot_r_channel = 'BW'
                new_template.m_slot_g_map = name
                new_template.m_slot_g_channel = 'BW'
                new_template.m_slot_b_map = name
                new_template.m_slot_b_channel = 'BW'
                new_template.m_slot_a_map = 'None'
                new_template.m_slot_a_channel = 'None'
                new_template.m_file_type = 'JPEG'

        return {'FINISHED'}
#endregion [Export]
#-------------------------------------------------
#endregion [Operator]

#region [Sleeping-Beast]   
# Unfinished 
#region [PlaceHolder]
tm_undo         = None
undo_manager    = None  
#endregion [PlaceHolder]
class TM_OT_Layer_Paint_Experimental(bpy.types.Operator):
    """TM_OT_Layer_Paint_ExperimentalMode"""
    bl_idname       = "texture_mixer.layer_paint_xperimental_mode"
    bl_label        = "Experimental Layer Paint Mode"
    bl_description  = "Experimental Layer Paint Mode"
    bl_options      = {'REGISTER', 'INTERNAL'}

    # debug_id = "TM_OT_Layer_Paint_ExperimentalMode"
    
    m_enter_painting_mode = False 

    m_canvas_data = []  
    m_channel_active = [] 

    m_handle = None 
    m_falloff_lut = None
    m_position_map_buffer = None
    m_last_raycast_hit_position = None
    m_evaluated_mesh = None

    #region [Blender Default Functions]        
    def invoke(self, context, event):
        return self.Start(context, event)

    def modal(self, context, event):        
        if context.area:
            context.area.tag_redraw()

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.alt:
            return {'PASS_THROUGH'}  
        
        if event.type == 'LEFTMOUSE':
            return self.OnPointerEnter(context, event)
        
        if event.type == 'MOUSEMOVE':
            return self.OnPointerMove(context, event)
        
        enable_paint_mode = context.scene.TM_User_Data.m_ui_tm_paint_mode_enable
        if not enable_paint_mode or context.mode != 'PAINT_TEXTURE' or event.type in {'ESC', 'RIGHTMOUSE'}:
            return self.OnPointerExit(context) 
        
        return {'RUNNING_MODAL'}
    #endregion [Blender Default Functions]
    
    #region ['Runtime']    
    def Start(self, context, event):
        """[private void Start()]"""
        enable_paint_mode = context.scene.TM_User_Data.m_ui_tm_paint_mode_enable

        if enable_paint_mode and context.area.type == 'VIEW_3D' and context.mode == 'PAINT_TEXTURE':
            
            self.BuildCanvasData(context)            

            self.OnGUI(context)
            
            context.window_manager.modal_handler_add(self)           
            
            return {'RUNNING_MODAL'}        
        
        return {'CANCELLED'}
    
    def OnPointerEnter(self, context, event):
        if event.value == 'PRESS':
            self.m_enter_painting_mode = True
            self.PaintOnCanvas(context, event, True)
            return {'RUNNING_MODAL'}

        elif event.value == 'RELEASE' and self.m_enter_painting_mode:
            self.m_enter_painting_mode = False
            self.UpdateCanvas(context)
            return {'RUNNING_MODAL'}
            
        return {'RUNNING_MODAL'}    

    def OnPointerMove(self, context, event):
        if self.m_enter_painting_mode:
            self.PaintOnCanvas(context, event, False)
        return {'RUNNING_MODAL'}

    def OnPointerExit(self, context):
        """Handle exit process clean up"""

        self.m_enter_painting_mode = False

        if self.m_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.m_handle, 'WINDOW')
            self.m_handle = None

        if len(self.m_canvas_data) > 0:
            for canvas in self.m_canvas_data:
                canvas["canvas_image"].update()
            self.m_canvas_data.clear()

        if self.m_falloff_lut is not None:
            self.m_falloff_lut = None

        if self.m_position_map_buffer is not None:
            self.m_position_map_buffer = None

        if self.m_last_raycast_hit_position is not None:
            self.m_last_raycast_hit_position = None
        
        if self.m_evaluated_mesh is not None:
            self.m_evaluated_mesh = None

        if len(self.m_channel_active) > 0:
            for canvas in self.m_channel_active:
                manager_id = canvas['manager_id']                
                tmtexture_id = canvas['channel_tmtexture_id']
                tm_logic.TM_Logic_TMTexture_Virtual_Image_Update(context, manager_id, tmtexture_id)
                tm_logic.TM_Logic_TMTexture_Switch_To_Virtual(context, manager_id, tmtexture_id)
            self.m_channel_active.clear()

        return {'FINISHED'}

    def OnGUI(self, context):        
        self.m_handle = bpy.types.SpaceView3D.draw_handler_add(
            self.OnGUI_ShowUI, (context,), 'WINDOW', 'POST_PIXEL'
        )

    def OnGUI_ShowUI(self, context):
        text                    = "TM | Layer Paint Mode"
        font_id                 = 0
        font_size               = 20
        font_color              = (1.0, 1.0, 1.0)
        font_alpha              = 0.1 if self.m_enter_painting_mode else 0.9

        text_width, text_height = blf.dimensions(font_id, text)
        pos_x = (context.region.width / 2) - (text_width / 2)
        pos_y = context.region.height - (context.region.height / 10)

        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0.0, 0.0, 0.0, font_alpha) 
        blf.shadow_offset(font_id, 1, -1)

        blf.position(font_id, pos_x, pos_y, 0)
        blf.size(font_id, font_size)
        blf.color(font_id, font_color[0], font_color[1], font_color[2], font_alpha)
        blf.draw(font_id, text)

        blf.disable(font_id, blf.SHADOW)
    #endregion ['Runtime']

    def BuildCanvasData(self, context):
        self.m_channel_active   = tm_logic.TM_Logic_Layer_Paint_Mode_Get_Active_Channel_Data(context)
        
        if len(self.m_channel_active) == 0:
            # Debug.LogWarning("No active layer", self.debug_id)
            return  {'CANCELLED'}    

        self.m_falloff_lut      = tm_logic.TM_Logic_Brush_Get_Falloff_LUT(context)
        self.m_canvas_data.clear()

        all_snapshots                   = undo_manager.m_snapshots
        user_data                       = context.scene.TM_User_Data
        user_brush_data                 = user_data.m_brush_data
        active_manager                  = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        active_object                   = tm_logic.TM_Logic_Object_Get_Active_One(context)
        
        #region [Evaluated Mesh]
        evaluated_depsgraph             = context.evaluated_depsgraph_get()
        active_object_evaluated         = active_object.evaluated_get(evaluated_depsgraph)
        self.m_evaluated_mesh           = active_object_evaluated.to_mesh()
        #endregion [Evaluated Mesh]

        #region [Position Map]
        pos_map_id                      = active_manager.m_data.m_baked_position_map_id
        pos_map_image                   = tm_logic.TM_Logic_Image_Get_By_Id(pos_map_id)
        pos_map_buffer                  = tm_logic.TM_Logic_Utility_Image_To_NumpyArray(pos_map_image)
        pos_map_buffer                  = pos_map_buffer.reshape((pos_map_image.size[1], pos_map_image.size[0], 4))
        pos_map_buffer                  = np.flipud(pos_map_buffer)
        self.m_position_map_buffer      = pos_map_buffer
        #endregion [Position Map]

        if len(all_snapshots) == 0:
                start_snapshot = tm_undo.TM_Undo_Snapshot()

        for canvas in self.m_channel_active:
            channel_name                    = canvas['channel_name']
            channel_init                    = canvas['channel_init']
            channel_image_name              = canvas['channel_image_name']
            channel_color_neutral           = canvas['channel_color_neutral'] 
            default_color_space             = canvas['default_color_space'] 
            channel_image_id                = canvas['channel_image_id']
            channel_proxy_id                = canvas['channel_proxy_id']
                    
            #region [Canvas Buffer]
            canvas_image                    = bpy.data.images.get(channel_image_name)
            image_width, image_height       = canvas_image.size
            canvas_buffer                   = np.empty(image_width * image_height * 4, dtype=np.float32)
            canvas_image.pixels.foreach_get(canvas_buffer)
            canvas_buffer                   = canvas_buffer.reshape((image_height, image_width, 4))
            canvas_buffer                   = np.flipud(canvas_buffer)
            #endregion [Canvas Buffer]

            #region [Load Channel Brush Image]
            channel_brush_image             = None  
            paint_image = getattr(user_brush_data, f"m_brush_{channel_init}_image")                
            if paint_image:
                w, h                        = paint_image.size
                sample_buffer               = np.empty(w * h * 4, dtype=np.float32)
                paint_image.pixels.foreach_get(sample_buffer)
                result                      = sample_buffer.reshape((h, w, 4))
                if default_color_space     == 'sRGB':
                    channel_brush_image     = result
                else:
                    channel_brush_image     = tm_logic.TM_Logic_Utility_sRGB_To_Linear(result)    
            #endregion [Load Channel Brush Image]        

            self.m_canvas_data.append({
                "canvas_image"              : canvas_image,
                "canvas_buffer"             : canvas_buffer,
                "channel_init"              : channel_init,
                "channel_color_neutral"     : channel_color_neutral,
                "channel_brush_image"       : channel_brush_image,
                "channel_image_id"          : channel_image_id,
                "channel_proxy_id"          : channel_proxy_id,
            })

            if len(all_snapshots) == 0:                
                instance                    = tm_undo.TM_Undo_Instance()
                instance.m_target_image_id  = channel_image_id
                instance.m_proxy_image_id   = channel_proxy_id
                instance.m_save_state       = canvas_buffer.copy()
                
                start_snapshot.m_undo_instances.append(instance)

        if len(all_snapshots) == 0:       
            undo_manager.FreshStartSnapshot(start_snapshot)                

    def PaintOnCanvas(self, context, event, is_start):
        active_object           = tm_logic.TM_Logic_Object_Get_Active_One(context)
        blender_brush_data      = bpy.context.tool_settings.image_paint.brush
        blender_brush_uni_data  = bpy.context.tool_settings.image_paint.unified_paint_settings   

        user_data               = context.scene.TM_User_Data
        user_brush_data         = user_data.m_brush_data
        user_brush_mode         = user_brush_data.m_brush_mode       

        #region [Blender Brush Data Integration]
        brush_radius            = (blender_brush_uni_data.size * 0.5) / 1000.0
        brush_strength          = blender_brush_data.strength
        brush_pressure          = event.pressure if hasattr(event, 'pressure') else 1.0
        #endregion [Blender Brush Data Integration]

        #region [RaycastHit]
        space_data_coord        = (event.mouse_region_x, event.mouse_region_y)
        space_data_region       = context.region
        space_data_rv3d         = context.space_data.region_3d

        view_vector             = view3d_utils.region_2d_to_vector_3d(space_data_region, space_data_rv3d, space_data_coord)
        ray_origin              = view3d_utils.region_2d_to_origin_3d(space_data_region, space_data_rv3d, space_data_coord)

        active_object_inverted  = active_object.matrix_world.inverted()
        target_origin           = active_object_inverted @ ray_origin
        target_direction        = active_object_inverted @ (ray_origin + view_vector) - target_origin

        RaycastHit              = active_object.ray_cast(target_origin, target_direction)
        if not RaycastHit:
            return {'RUNNING_MODAL'}
        
        hit                     = RaycastHit[0]
        position                = RaycastHit[1]
        normal                  = RaycastHit[2]
        face_index              = RaycastHit[3]

        if not hit:
            return {'RUNNING_MODAL'}
        #endregion [RaycastHit]

        #region [UV Regional Slice]
        if face_index >= len(self.m_evaluated_mesh.polygons):
            return {'RUNNING_MODAL'}
        
        target_uv_vec = tm_logic.TM_Logic_Brush_Get_TargetUV(self.m_evaluated_mesh, position, face_index)

        img_w, img_h = self.m_canvas_data[0]["canvas_image"].size
        px_x = int(target_uv_vec.x * (img_w - 1))
        px_y = int((1.0 - target_uv_vec.y) * (img_h - 1))

        padding_px = int(brush_radius * 0.9 * max(img_w, img_h))

        x_min = max(0, px_x - padding_px)
        y_min = max(0, px_y - padding_px)
        x_max = min(img_w, px_x + padding_px)
        y_max = min(img_h, px_y + padding_px)

        if x_max <= x_min or y_max <= y_min:
            return {'RUNNING_MODAL'}
        #endregion [UV Regional Slice]

        #region [Brush Spacing]   
        current_hit_pos         = np.array(position, dtype=np.float32)
        dots_to_paint           = []

        if is_start:
            dots_to_paint.append(current_hit_pos)
            self.m_last_raycast_hit_position = current_hit_pos
        else:
            dist_since_last = np.linalg.norm(current_hit_pos - self.m_last_raycast_hit_position)

            spacing = brush_radius * 0.25

            if dist_since_last > spacing:
                # steps = int(dist_since_last / spacing)
                steps = min(int(dist_since_last / spacing), 50)
                for i in range(1, steps + 1):
                    delta = i/steps
                    lerp_position = self.m_last_raycast_hit_position * (1.0 - delta) + current_hit_pos * delta
                    dots_to_paint.append(lerp_position)
            else:
                return {'RUNNING_MODAL'}                    
        
        self.m_last_raycast_hit_position = current_hit_pos
        #endregion [Brush Spacing]

        #region [Brush Region]
        position_map_slice = self.m_position_map_buffer[y_min:y_max, x_min:x_max, :3]
        # position_map = self.m_position_map_buffer[:, :, :3]
        brush_radius_sq = brush_radius**2

        points_np = np.array(dots_to_paint, dtype=np.float32)
        diff = position_map_slice[:, :, np.newaxis, :] - points_np
        dist_sq = np.min(np.sum(diff**2, axis=3), axis=2)
        
        mask = dist_sq < brush_radius_sq
        #endregion [Brush Region]

        if np.any(mask):            
            dist = np.sqrt(dist_sq[mask])
            dist_normalized = np.clip(dist / brush_radius, 0, 1)

            lut_indices = (dist_normalized * 255).astype(np.int32)
            falloff_values = self.m_falloff_lut[lut_indices]

            effective_alpha = (falloff_values * brush_strength * brush_pressure).astype(np.float32)        
            alpha_input = effective_alpha[:, np.newaxis]
            
            for canvas in self.m_canvas_data:
                channel_init            = canvas["channel_init"]
                channel_enable          = getattr(user_brush_data, f"m_channel_{channel_init}_enable")
                channel_color_neutral   = canvas["channel_color_neutral"]
                channel_brush_image     = canvas["channel_brush_image"]
                canvas_buffer           = canvas["canvas_buffer"]
                canvas_buffer_slice     = canvas_buffer[y_min:y_max, x_min:x_max]

                if channel_enable:                               
                    if channel_brush_image is not None:
                        channel_color_rgb    = np.array(channel_color_neutral[:3])
                    else:
                        paint_color = getattr(user_brush_data, f"m_brush_{channel_init}_color")
                        channel_color_rgb    = np.array(paint_color[:3])
                else:
                    channel_color_rgb        = np.array(channel_color_neutral[:3])

                channel_color_rgb = channel_color_rgb.astype(np.float32)
                target_pixels = canvas_buffer_slice[mask]

                if user_brush_mode == 'TM_BRUSH_PAINT':
                    target_pixels[:, :3] = (channel_color_rgb * alpha_input) + (target_pixels[:, :3] * (1.0 - alpha_input))
                    
                    new_alpha = target_pixels[:, 3] + effective_alpha * (1.0 - target_pixels[:, 3])
                    target_pixels[:, 3] = np.clip(new_alpha, 0, 1)
                
                elif user_brush_mode == 'TM_BRUSH_ERASE':
                    target_pixels[:, 3] = np.clip(target_pixels[:, 3] - effective_alpha, 0, 1)

                canvas_buffer_slice[mask] = target_pixels

        for canvas in self.m_canvas_data:
            canvas_buffer = canvas["canvas_buffer"]
            canvas_image  = canvas["canvas_image"]
            out_buffer = np.flipud(canvas_buffer)
            canvas_image.pixels.foreach_set(out_buffer.ravel())
        return {'RUNNING_MODAL'}
    
    def UpdateCanvas(self, context):
        undo_snapshot = tm_undo.TM_Undo_Snapshot()

        for canvas in self.m_canvas_data:
            canvas_image                = canvas["canvas_image"]
            canvas_image.update()

            instance                    = tm_undo.TM_Undo_Instance()
            instance.m_target_image_id  = canvas["channel_image_id"]
            instance.m_proxy_image_id   = canvas["channel_proxy_id"]
            instance.m_save_state       = canvas["canvas_image"].copy()
            
            undo_snapshot.m_undo_instances.append(instance)

        undo_manager.PushSnapshot(undo_snapshot)
#endregion [Sleeping-Beast]
      
#region [Included Classes & Property To Register]
#-------------------------------------------------
included_classes = (   
    #--------------------------------------------- 
    TM_OT_Test_Dummy,
    #---------------------------------------------
    TM_OT_LayerManager_Create_New,
    TM_OT_LayerManager_Activate,
    TM_OT_LayerManager_Remove,
    TM_OT_LayerManager_Change_Main_Shader,
    TM_OT_LayerManager_Apply_Working_Resolution,
    TM_OT_LayerManager_Apply_Preview_Resolution,
    #---------------------------------------------
    TM_OT_Layer_Create_New_Paint,
    TM_OT_Layer_Create_New_Fill,
    TM_OT_Layer_Create_New_Group,
    TM_OT_Layer_Remove,
    TM_OT_Layer_Move,
    TM_OT_Layer_Join_Group,
    TM_OT_Layer_Exit_Group,
    TM_OT_Layer_Load_Texture,
    TM_OT_Layer_Remove_Texture,
    #---------------------------------------------
    TM_OT_Mask_Create_New_Paint_Black,
    TM_OT_Mask_Create_New_Paint_White,
    TM_OT_Mask_Create_New_Preserved,
    TM_OT_Mask_Move,
    TM_OT_Mask_Texture_Loader,
    TM_OT_Mask_Texture_Remover,
    TM_OT_Mask_Remove,
    #---------------------------------------------
    TM_OT_Enable_Texture_Painting_Mode,
    TM_OT_Layer_Paint_Blender_Multi_Channel,
    TM_OT_Layer_Paint_Blender_Single_Channel,
    #---------------------------------------------
    TM_OT_Export_Template_Create_New,
    TM_OT_Export_Template_Delete,
    #---------------------------------------------
    TM_OT_Export_Bake,
    TM_OT_Export_Build_Active_Channels_Template
    #---------------------------------------------
)
#-------------------------------------------------
def need_to_register():
    for cls in included_classes:
        bpy.utils.register_class(cls)
#-------------------------------------------------
def need_to_unregister():
    for cls in reversed(included_classes):
        bpy.utils.unregister_class(cls)
#-------------------------------------------------
#endregion [Included Classes & Property To Register]