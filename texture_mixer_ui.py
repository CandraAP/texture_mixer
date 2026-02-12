#----------------------------------------------------
# Texture Mixer (Blender Addon) #####################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_ui.py                   |
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
#-------------------------------------------------
from . import texture_mixer_icon as tm_icon
from . import texture_mixer_property as tm_property
from . import texture_mixer_logic as tm_logic
#-------------------------------------------------
# from dev_tools.texture_mixer_debug import Debug
#-------------------------------------------------
stamp_id    = tm_property.Addon_Data.m_addon_id_stamp
#endregion [IMPORT]

#region [Main Panel]
class TM_PT_UserInfo(bpy.types.Panel):
    """TM_PT_UserInfo"""
    bl_idname = f"TM_PT_UserInfo"
    bl_label = tm_property.Addon_Data.m_ui_panel_label_user_welcome
    bl_category = tm_property.Addon_Data.m_ui_panel_category
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return tm_logic.TM_Logic_Object_Get_Active_One(context)

    def draw(self, context):      
        user_data = context.scene.TM_User_Data
        active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        
        main_layout = self.layout
        
        if tm_property.Addon_Data.m_ui_enable_support:            
            box_support = main_layout.box()
            row = box_support.row(align=True)
            row.scale_y = 1.0
            row.alignment = 'LEFT'
            row.prop(user_data, "m_ui_show_support",text="Support This Project", icon='FUND'if user_data.m_ui_show_support else 'HEART', emboss=False)

            if user_data.m_ui_show_support:                
                col = box_support.column(align=True)
                col.scale_y = 1.0
                # col.operator("wm.url_open", text="SuperHive", icon='HEART').url = "..."
                # col.separator(factor=0.5)
                col.operator("wm.url_open", text="Become a Patron (Patreon)",   icon='HEART').url = "https://www.patreon.com/c/candraap"  
                col.separator(factor=0.5)              
                col.operator("wm.url_open", text="Buy me a coffee (Ko-Fi)",     icon='HEART').url = "https://ko-fi.com/candraap"

        box_logo = main_layout.box()
        row_logo = box_logo.row(align=True)
        row_logo.scale_y = 0.65
        row_logo.template_icon(icon_value=tm_icon.TM_Icon_Get_Icon("TM_LOGO_BIG"), scale=12.0) 

        box_version = main_layout.box()
        row_version = box_version.row(align=True) 
        row_version.scale_y = 1.0
        row_version.alignment = 'CENTER'
        row_version.label(text=f"Version: {tm_property.Addon_Data.m_addon_version}{tm_property.Addon_Data.m_addon_status}")

        if active_manager:
            UI_UserInfo_Target_Is_A_Member(context, main_layout, active_object)
        else:            
            if context.scene.TM_User_Data.m_ui_tm_paint_mode_enable:
                return
            UI_UserInfo_Target_Is_Not_Member(main_layout)

def UI_UserInfo_Target_Is_A_Member(context, main_layout, obj):
    """UI_UserInfo_Target_Is_A_Member"""
    box_info = main_layout.box()
    
    row_info_selected_object_name = box_info.row(align=True) 
    row_info_selected_object_name.scale_y = 1.0
    row_info_selected_object_name.label(text="Active Object ", icon='INFO')   
    row_info_selected_object_name.label(text=f": {obj.name}") 

    active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context) 
    if active_manager: 
        row_info_active_manager_name = box_info.row(align=True) 
        row_info_active_manager_name.scale_y = 1.0
        row_info_active_manager_name.label(text="Active Manager ", icon='INFO') 
        row_info_active_manager_name.label(text=f": {active_manager.m_name}")    

        bsdf_shader_name = tm_logic.TM_Logic_Utility_Get_Main_Shader_Name(active_manager.m_main_shader_type)
        row_info_active_manager_shader = box_info.row(align=True) 
        row_info_active_manager_shader.scale_y = 1.0
        row_info_active_manager_shader.label(text="Active Shader ", icon='INFO')
        if bsdf_shader_name:
            row_info_active_manager_shader.label(text=f": {bsdf_shader_name}")
        else:                    
            row_info_active_manager_shader.label(text=": Unknown Shader")

def UI_UserInfo_Target_Is_Not_Member(main_layout):
    """UI_UserInfo_Target_Is_Not_Member"""
    box_button = main_layout.box()
    row_button = box_button.row(align=True) 
    row_button.scale_y = 1.5
    row_button.operator("texture_mixer.layermanager_create_new", text="Add Layer Manager", icon='COLLECTION_NEW')
#endregion [Main Panel]

#region [UserSettings]
class TM_UL_Layer_Manager_List(bpy.types.UIList):
    """TM_UL_Layer_Manager_List"""
    bl_idname = f"TM_UL_Layer_Manager_List"  

    def filter_items(self, context, data, property):
        managers = getattr(data, property)
        flt_flags = []

        active_obj = tm_logic.TM_Logic_Object_Get_Active_One(context)
        if not active_obj or not active_obj.data or not getattr(active_obj.data, "materials", None):
            return [0] * len(managers), []

        current_material_id = {mat.get(stamp_id) for mat in active_obj.data.materials if mat is not None}
        
        for item in managers:
            if item.m_managed_material_id in current_material_id:
                flt_flags.append(self.bitflag_filter_item)  
            else:
                flt_flags.append(0)  

        return flt_flags, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0):
        tm_node_manager = item
        main_split = layout.split(factor=0.65)
        
        row_name = main_split.row(align=True)
        row_name.prop(tm_node_manager, "m_name", text="",icon='OUTLINER_COLLECTION', emboss=False)

        row_button = main_split.row(align=True)
        if tm_node_manager.m_enable:
            op = row_button.operator("texture_mixer.layermanager_activate", text="Active", emboss=False)
        else:
            op = row_button.operator("texture_mixer.layermanager_activate", text="Disabled", emboss=False)        
        op.m_manager_id = tm_node_manager.m_id

class TM_PT_UserSettings(bpy.types.Panel):
    """TM_PT_UserSettings"""
    bl_idname = f"TM_PT_UserSettings"
    bl_label = tm_property.Addon_Data.m_ui_panel_label_user_settings
    bl_category = tm_property.Addon_Data.m_ui_panel_category
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        user_data = context.scene.TM_User_Data
        active_paint_mode = user_data.m_ui_tm_paint_mode_enable
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        return bool(active_manager and not active_paint_mode)
        
    def draw(self, context):
        user_data = context.scene.TM_User_Data 
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)

        if user_data.m_ui_tm_paint_mode_enable:
            return
        
        main_layout = self.layout

        UI_UserSettings_Main_Menu(context, main_layout, user_data, active_manager)
        
def UI_UserSettings_Main_Menu(context, main_layout, user_data, active_manager):
    """UI_UserSettings_Main_Menu"""
    collection_manager = user_data.m_managed_tm_node_manager_collection

    if len(collection_manager) > 0:
        box = main_layout.box()

        row = box.row(align=True)
        row.prop(user_data, "m_ui_usersettings_tabs", expand=True)

        tab = user_data.m_ui_usersettings_tabs

        if tab == 'MANAGER':
            UI_UserSettings_Layer_Manager(main_layout, user_data)
        else:            
            if active_manager:
                if tab == 'CHANNEL':
                    UI_UserSettings_Channel_Shader_BSDF(main_layout, active_manager)
                    UI_UserSettings_Channel(main_layout, active_manager)
                elif tab == 'OPTIONS':
                    UI_UserSettings_Option_Input_Resolution(main_layout, active_manager)
            else:
                row_notification = box.row(align=True)
                row_notification.label(text="No active layer manager Found.", icon='ERROR')

def UI_UserSettings_Layer_Manager(main_layout, user_data):
    """UI_UserSettings_Layer_Manager"""
    box_button = main_layout.box()
    row_button = box_button.row(align=True)
    row_button.label(text="Add Layer Manager")
    row_button.operator("texture_mixer.layermanager_create_new", text="", icon='COLLECTION_NEW')
    row_button.separator()
    row_button.operator("texture_mixer.layermanager_remove", text="", icon='TRASH') 

    row_panel = main_layout.row(align=True)
    row_panel.scale_y = 1.4
    row_panel.template_list(
        f"TM_UL_Layer_Manager_List" , "", 
        user_data, "m_managed_tm_node_manager_collection",               
        user_data, "m_managed_tm_node_manager_pointer",
        rows=3, maxrows=3
    )    

def UI_UserSettings_Channel_Shader_BSDF(main_layout, active_manager):
    """UI_UserSettings_Channel_Shader_BSDF"""
    box = main_layout.box()

    row_header = box.row(align=True)
    row_header.label(text="Shader BSDF")

    row_value = box.row(align=True)
    row_value.prop(active_manager, "m_main_shader_type_cache", text="")

    if active_manager.m_main_shader_type != active_manager.m_main_shader_type_cache:
        row_value.operator("texture_mixer.layermanager_change_main_shader", text="Apply")

def UI_UserSettings_Channel(main_layout, active_manager):
    """UI_UserSettings_Channel"""
    box = main_layout.box()

    row_header = box.row(align=True)
    row_header.label(text="Channel Support")

    shader_type = active_manager.m_main_shader_type
    channel_set = tm_property.TM_DT_Channels_Based_On_Shader[shader_type]

    def draw_channel(channel_name: str, channel_prop: str):
        if channel_name not in channel_set:
            return
        current_value = getattr(active_manager, channel_prop)            
        row_channel = box.row(align=True)       
        if channel_name == 'Base Color':
            row_channel.alignment = 'CENTER'
            row_channel.label(text=f"{channel_name} Active", icon='DECORATE_LOCKED')
            row_channel.label(text=f"", icon='BLANK1')
            return     
        if current_value:
            row_channel.prop(active_manager, channel_prop, text=f"{channel_name} Active", toggle=True, emboss=True)
        else:
            row_channel.prop(active_manager, channel_prop, text=f"{channel_name} Disabled", toggle=True, emboss=True)

    supprted_channels = tm_property.TM_DT_Channels_Metadata.values()
    for channel in supprted_channels:
        channel_name = channel.get('default_name')        
        channel_prop = f"m_channel_{channel.get('default_init')}_enable"
        draw_channel(channel_name, channel_prop)

def UI_UserSettings_Option_Input_Resolution(main_layout, active_manager):
    """UI_UserSettings_Option_Resolution"""    
    box_working_resolution = main_layout.box()
    row_working_resolution = box_working_resolution.row(align=True)
    row_working_resolution.label(text="Working Resolution")
    row_working_resolution_value = box_working_resolution.row(align=True)
    row_working_resolution_value.prop(active_manager, "m_preserved_resolution_cache", text="")
    if active_manager.m_preserved_resolution != active_manager.m_preserved_resolution_cache:
        row_working_resolution_value.operator("texture_mixer.layermanager_apply_working_resolution", text="Apply")

    box_preview_resolution = main_layout.box()
    row_preview_resolution = box_preview_resolution.row(align=True)
    row_preview_resolution.label(text="Preview Resolution")
    row_preview_resolution_value = box_preview_resolution.row(align=True)
    row_preview_resolution_value.prop(active_manager, "m_virtual_resolution_cache", text="")
    if active_manager.m_virtual_resolution != active_manager.m_virtual_resolution_cache:
        row_preview_resolution_value.operator("texture_mixer.layermanager_apply_preview_resolution", text="Apply")
#endregion [UserSettings]

#region [LayerWorkSpace]
class TM_UL_Layer_List(bpy.types.UIList):
    """TM_UL_Layer_List"""
    bl_idname = f"TM_UL_Layer_List"

    def draw_filter(self, context, layout):
        pass

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        tm_node = item        

        main_split = layout.split(factor=0.65)

        row_name = main_split.row(align=True)
        if tm_node.m_group_id:
            row_name.label(text="", icon='BLANK1')
        if tm_node.m_type == 'LAYER_PAINTABLE':
            icon_type = 'TPAINT_HLT'
        elif tm_node.m_type == 'LAYER_PRESERVED':
            icon_type = 'TEXTURE_DATA'
        elif tm_node.m_type == 'GROUP':
            icon_type = 'OUTLINER_OB_GROUP_INSTANCE'         
        row_name.prop(tm_node, "m_name", text="", icon=icon_type, emboss=False)
        if tm_node.m_mask_enable:
            row_name.label(text="", icon='MOD_MASK')

        row_utility = main_split.row(align=True)        
        row_utility.prop(tm_node, "m_opacity", text="", slider=True, emboss=True)
        icon_enable = 'HIDE_OFF' if tm_node.m_enable else 'HIDE_ON'
        row_utility.prop(tm_node, "m_enable", text="", icon=icon_enable, emboss=False)

class TM_UL_Mask_List(bpy.types.UIList):
    """TM_UL_Mask_List"""
    bl_idname = f"TM_UL_Mask_List"
    
    def draw_filter(self, context, layout):
        pass

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        tm_mask = item

        main_split = layout.split(factor=0.65)

        row_name = main_split.row(align=True)
        if tm_mask.m_type == 'MASK_PAINTABLE':
            icon_type = 'TPAINT_HLT'
        elif tm_mask.m_type == 'MASK_PRESERVED':
            icon_type = 'TEXTURE_DATA'
        # another type
        row_name.prop(tm_mask, "m_name", text="", icon=icon_type, emboss=False)

        row_utility = main_split.row(align=True)        
        row_utility.prop(tm_mask, "m_opacity", text="", slider=True, emboss=True)
        icon_enable = 'HIDE_OFF' if tm_mask.m_enable else 'HIDE_ON'
        row_utility.prop(tm_mask, "m_enable", text="", icon=icon_enable, emboss=False)

class TM_PT_LayerWorkSpace(bpy.types.Panel):
    """TM_PT_LayerWorkSpace"""
    bl_idname = f"TM_PT_LayerWorkspaceNew"
    bl_label = tm_property.Addon_Data.m_ui_panel_label_layer_settings
    bl_category = tm_property.Addon_Data.m_ui_panel_category
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        user_data = context.scene.TM_User_Data
        active_paint_mode = user_data.m_ui_tm_paint_mode_enable
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        return bool(active_manager and not active_paint_mode)

    def draw(self, context):
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context) 
        user_data = context.scene.TM_User_Data 
        
        if user_data.m_ui_tm_paint_mode_enable:
            return
        
        main_layout = self.layout     

        UI_LayerWorkspace_Main_Menu(context, main_layout, user_data, active_manager)

def UI_LayerWorkspace_Main_Menu(context, main_layout, user_data, active_manager):
    """UI_LayerWorkspace_Main_Menu"""
    row_main = main_layout.row(align=True)
    box_main = row_main.box()

    row_tabs = box_main.row(align=True)
    row_tabs.prop(user_data, "m_ui_layer_option_tabs", expand=True)

    tab = user_data.m_ui_layer_option_tabs   
    
    if tab == 'LAYER':
        UI_LayerWorkspace_Layer(context, main_layout, user_data, active_manager)
        UI_LayerWorkspace_Layer_Channel_Property(context, main_layout, user_data, active_manager)
    elif tab == 'MASK':
        UI_LayerWorkspace_Mask(context, main_layout, user_data, active_manager)
    elif tab == 'OPTIONS':
        UI_LayerWorkspace_Layer_Default_Settings(main_layout, active_manager) 

    active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
    if not active_object:
        return
    
    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return  
    
    box_paint = main_layout.box()
    row_paint = box_paint.row(align=True)
    row_paint.label(text="Action:")
    
    if tab == 'LAYER':
        if active_layer.m_type != 'LAYER_PAINTABLE':

            row_notification = box_paint.row(align=True)
            row_notification.label(text="No paint options for this layer type.", icon='ERROR')
            return
        else:                                
            if active_object.mode != 'TEXTURE_PAINT':
                row_enable_paint = box_paint.row(align=True)
                row_enable_paint.scale_y = 1.5
                row_enable_paint.operator("texture_mixer.enable_texture_painting_mode", text=" Enable Texture Painting Mode", emboss=True, icon='BRUSHES_ALL')
            else:
                row_notification = box_paint.row(align=True)
                row_notification.label(text="Texture Painting [Layer] Enabled.", icon='INFO')

    elif tab == 'MASK':
        if not active_layer.m_mask_enable:
            row_notification = box_paint.row(align=True)
            row_notification.label(text="Please enable 'Mask Support'.", icon='ERROR')
            return
        
        active_mask = tm_logic.TM_Logic_Mask_Get_Active_Mask(context, active_manager.m_id, active_layer.m_id)
        if not active_mask:
            row_notification = box_paint.row(align=True)
            row_notification.label(text="Please create a mask.", icon='ERROR')
            return
                                
        if active_mask.m_type != 'MASK_PAINTABLE':
            row_notification = box_paint.row(align=True)
            row_notification.label(text="No paint options for this mask type.", icon='ERROR')
            return
        else:            
            if active_object.mode != 'TEXTURE_PAINT':
                row_enable_paint = box_paint.row(align=True)
                row_enable_paint.scale_y = 1.5
                row_enable_paint.operator("texture_mixer.enable_texture_painting_mode", text=" Enable Texture Painting Mode", emboss=True, icon='BRUSHES_ALL')            
            else:
                row_notification = box_paint.row(align=True)
                row_notification.label(text="Texture Painting [Mask] Enabled.", icon='INFO')

    elif tab == 'OPTIONS':
            row_notif = box_paint.row(align=True)
            row_notif.label(text="Select tab 'Layer' or 'Mask' to paint.", icon='ERROR')
    
def UI_LayerWorkspace_Layer(context, main_layout, user_data, active_manager):
    """UI_LayerWorkspace_Layer"""
    if active_manager:
        box_layer_button = main_layout.box()
        row_layer_button = box_layer_button.row(align=True)
        row_layer_button.label(text="Add layer")
        row_layer_button.separator()
        row_layer_button.operator("texture_mixer.layer_create_new_paint", text="", icon='TPAINT_HLT')
        row_layer_button.operator("texture_mixer.layer_create_new_fill", text="", icon='TEXTURE_DATA')
        row_layer_button.operator("texture_mixer.layer_create_new_group", text="", icon='OUTLINER_OB_GROUP_INSTANCE')
        row_layer_button.separator()
        row_layer_button.operator("texture_mixer.layer_remove", text="", icon='TRASH')

        row_layer_panel = main_layout.row(align=True)
        row_layer_panel.scale_y = 1.4
        row_layer_panel.template_list(
            f"TM_UL_Layer_List", "", 
            active_manager, "m_managed_tm_node_collection",
            active_manager, "m_managed_tm_node_pointer",
            columns=2,
            rows=4,
            type='DEFAULT',
            sort_reverse=False,    
            sort_lock=False
        )

        # box_navigation_button = main_layout.box()
        row_navigation_button = main_layout.row(align=True)
        row_navigation_button_split = row_navigation_button.split(factor=0.5, align=True)
        row_navigation_button_split.operator("texture_mixer.layer_move", text="", icon='TRIA_UP').direction = 'UP'
        row_navigation_button_split.operator("texture_mixer.layer_move", text="", icon='TRIA_DOWN').direction = 'DOWN'

        box_join_group= main_layout.box()
        row_show_join_group_opt = box_join_group.row(align=True)
        managed_layer = active_manager.m_managed_tm_node_collection

        if len(managed_layer) > 0:            
            icon_show_join_group_opt = 'TRIA_DOWN' if user_data.m_ui_show_layer_to_group_options else 'TRIA_RIGHT'
            row_show_join_group_opt.alignment = 'LEFT'
            row_show_join_group_opt.prop(user_data, "m_ui_show_layer_to_group_options", text="Group Options", icon=icon_show_join_group_opt, emboss=False)

            if not user_data.m_ui_show_layer_to_group_options:
                return

            pointer_active = active_manager.m_managed_tm_node_pointer                        
            layer_selected = managed_layer[pointer_active]
            
            if layer_selected.m_group_id:
                UI_LayerWorkspace_Layer_Exit_Group(context, box_join_group, active_manager)
            else:
                UI_LayerWorkspace_Layer_Join_Group(context, box_join_group, active_manager)   
        else:
            row_show_join_group_opt.label(text="", icon='TRIA_RIGHT') 
            row_show_join_group_opt.label(text="Group Options") 
    else:
        row_notification = box_join_group.row(align=True)
        row_notification.label(text="No active layer manager found.", icon='ERROR')

def UI_LayerWorkspace_Layer_Channel_Property(context, main_layout, user_data, active_manager):
    """UI_LayerWorkspace_Layer_Channel_Property"""    
    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if not active_layer:
        return
    
    host_material = tm_logic.TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return

    system_layer = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_layer.m_shader_node_system_layer_id)
    if not system_layer:
        return

    icon_show_layer_properties = 'TRIA_DOWN' if user_data.m_ui_show_layer_properties else 'TRIA_RIGHT'
    
    box_layer = main_layout.box()
    row_layer_content = box_layer.row(align=True)
    row_layer_content.alignment = 'LEFT'  
    row_layer_content.prop(user_data, "m_ui_show_layer_properties", text=f"'{active_layer.m_name}' Properties", icon=icon_show_layer_properties, emboss=False)
    
    if not user_data.m_ui_show_layer_properties:
        return

    row_tabs = box_layer.row(align=True)
    row_tabs.prop(user_data, "m_ui_channel_option_tabs", expand=True)

    tab = user_data.m_ui_channel_option_tabs 

    if tab == 'CHANNEL':
        if active_layer.m_type == 'LAYER_PAINTABLE' or active_layer.m_type == 'LAYER_PRESERVED':             
            socket_layer_enable     = system_layer.inputs.get("Layer Enable")  
            socket_layer_opacity    = system_layer.inputs.get("Layer Opacity")  
        else:
            socket_layer_enable     = system_layer.inputs.get("Enable Managed Folder")  
            socket_layer_opacity    = system_layer.inputs.get("Opacity Managed Folder")  

        ui_enable = True if socket_layer_enable.default_value and socket_layer_opacity.default_value > 0 else False

        shader_type = active_manager.m_main_shader_type
        channel_set = tm_property.TM_DT_Channels_Based_On_Shader[shader_type]

        box_alpha         = main_layout.box()
        row_alpha_split    = box_alpha.split(factor=0.45)

        row_alpha_split_l =  row_alpha_split.row(align=True)
        row_alpha_split_l.enabled = ui_enable
        row_alpha_split_l.label(text="Alpha")       

        row_alpha_split_r =  row_alpha_split.row(align=True)
        row_alpha_split_r.label(text="", icon='DECORATE') 
        row_alpha_split_r.enabled = ui_enable
        row_alpha_split_r.prop(active_layer, "m_blending_mode", text="")

        def draw_channel(
            channel_name: str, 
            is_channel_enable: str, 
            channel_prop_data: str,
            show_channel_ui: str):
            if channel_name not in channel_set:
                return
                
            current_value = getattr(active_manager, is_channel_enable)
            if not current_value:
                return

            channel_data = getattr(active_layer.m_channel, channel_prop_data)
            if not channel_data:
                return

            tm_texture_id       = channel_data.m_tm_texture_id
            tm_texture          = None
            if tm_texture_id:
                tm_texture = tm_logic.TM_Logic_TMTexture_Get_By_Id(context, active_manager.m_id, tm_texture_id)            

            if active_layer.m_type == 'LAYER_PAINTABLE' or active_layer.m_type == 'LAYER_PRESERVED': 
                socket_channel_enable   = system_layer.inputs.get(f"{channel_name} Enable")
                socket_channel_opacity  = system_layer.inputs.get(f"{channel_name} Opacity")
                socket_channel_value    = system_layer.inputs.get(f"{channel_name} Value")
                socket_channel_isolate  = system_layer.inputs.get(f"{channel_name} Isolate Blend")
            else:
                socket_channel_enable   = system_layer.inputs.get(f"Enable Managed {channel_name}")
                socket_channel_opacity  = system_layer.inputs.get(f"Opacity Managed {channel_name}")            

            # Main Box Container
            box_channel         = main_layout.box()
            box_channel.enabled = ui_enable

            # Header
            show_ui = getattr(user_data, show_channel_ui, False)

            row_header          = box_channel.row(align=True)
            row_header_split    = row_header.split(factor=0.45)

            icon_colapse = 'TRIA_DOWN' if show_ui else 'TRIA_RIGHT'

            row_header_left     = row_header_split.row(align=True)
            row_header_left.alignment = 'LEFT'
            row_header_left.prop(user_data, f"{show_channel_ui}", text=f"", emboss=False, icon=icon_colapse)
            row_header_left.label(text=channel_name)   
            
            socket_icon_enable      = 'HIDE_OFF' if socket_channel_enable.default_value else 'HIDE_ON'                
            row_header_right        = row_header_split.row(align=True)
            row_header_right.label(text="", icon='DECORATE')
            row_header_right.prop(socket_channel_opacity, "default_value", text="", slider=True, emboss=True)
            row_header_right.prop(socket_channel_enable, "default_value", text="", icon=socket_icon_enable, emboss=True)

            if show_ui and socket_channel_enable.default_value and socket_channel_opacity.default_value > 0:

                # blend mode
                if active_layer.m_type == 'LAYER_PRESERVED' or active_layer.m_type == 'GROUP':
                    row_blend_mode          = box_channel.row(align=True)
                    row_blend_mode_split    = row_blend_mode.split(factor=0.45)

                    row_blend_mode_left     = row_blend_mode_split.row(align=True)
                    row_blend_mode_left.label(text="", icon='BLANK1')
                    row_blend_mode_left.label(text="Blending")
                    
                    row_blend_mode_right    = row_blend_mode_split.row(align=True)
                    row_blend_mode_right.prop(channel_data, "m_blending_mode", text="") 
                    if active_layer.m_type == 'LAYER_PRESERVED': 
                        row_blend_mode_right.prop(socket_channel_isolate, "default_value", text="Isolate", toggle=True, emboss=True)
                    
                elif active_layer.m_type == 'LAYER_PAINTABLE':
                    if tm_texture_id:
                        row_blend_mode          = box_channel.row(align=True)
                        row_blend_mode_split    = row_blend_mode.split(factor=0.45)

                        row_blend_mode_left     = row_blend_mode_split.row(align=True)
                        row_blend_mode_left.label(text="", icon='BLANK1')
                        row_blend_mode_left.label(text="Blending Mode")
                        
                        row_blend_mode_right    = row_blend_mode_split.row(align=True)
                        row_blend_mode_right.prop(channel_data, "m_blending_mode", text="")
                        row_blend_mode_right.prop(socket_channel_isolate, "default_value", text="Isolate", toggle=True, emboss=True)  
                        
                # value content
                if active_layer.m_type == 'LAYER_PRESERVED':
                    if not tm_texture:
                        row_value               = box_channel.row(align=True)
                        row_value_mode_split    = row_value.split(factor=0.45)

                        row_value_mode_left     = row_value_mode_split.row(align=True)
                        row_value_mode_left.label(text="", icon='BLANK1')
                        row_value_mode_left.label(text="Color")

                        row_value_mode_right    = row_value_mode_split.row(align=True)
                        row_value_mode_right.prop(socket_channel_value, "default_value", text="")
                    else:
                        file_name = os.path.basename(tm_texture.m_user_texture_path)
                        row_value               = box_channel.row(align=True)
                        row_value_mode_split    = row_value.split(factor=0.45)

                        row_value_mode_left     = row_value_mode_split.row(align=True)
                        row_value_mode_left.label(text="", icon='BLANK1')
                        row_value_mode_left.label(text="File")
                        
                        row_value_mode_right    = row_value_mode_split.row(align=True)
                        row_value_mode_right.label(text=f": {file_name}")

                # Open file texture
                if active_layer.m_type == 'LAYER_PRESERVED':
                    if not tm_texture:  
                        row_open_file   =  box_channel.row(align=True)
                        row_open_file.label(text="", icon='BLANK1')
                        open_file = row_open_file.operator("texture_mixer.layer_load_texture", text=f"Open Texture File", icon='FILEBROWSER', emboss=True)
                        open_file.m_channel_name = channel_name
                    else:
                        row_open_file   =  box_channel.row(align=True)
                        row_open_file.label(text="", icon='BLANK1')
                        open_file = row_open_file.operator("texture_mixer.layer_load_texture", text=f"Replace Texture File", icon='FILE_REFRESH', emboss=True)  
                        open_file.m_channel_name = channel_name                  
                        remove_file = row_open_file.operator("texture_mixer.layer_remove_texture", text="", icon='TRASH', emboss=True)  
                        remove_file.m_channel_name = channel_name     

                if active_layer.m_type == 'LAYER_PAINTABLE':
                    row_data_exist   =  box_channel.row(align=True)
                    row_data_exist.label(text="", icon='BLANK1')
                    if tm_texture_id:
                        row_data_exist.label(text="Paint Canvas Available")
                    else:
                        row_data_exist.label(text="No Paint Canvas Data")
                
        supprted_channels = tm_property.TM_DT_Channels_Metadata.values()
        for channel in supprted_channels:
            channel_name = channel.get('default_name')
            is_channel_enable = f"m_channel_{channel.get('default_init')}_enable"
            channel_prop_data = f"m_channel_{channel.get('default_init')}"
            show_channel_ui = f"m_ui_show_{channel.get('default_init')}"
            draw_channel(channel_name, is_channel_enable, channel_prop_data, show_channel_ui)
        
    elif tab == 'OPTIONS':
        if active_layer.m_type == 'LAYER_PRESERVED':
            system_texture_mapping = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_layer.m_shader_node_system_texture_mapping_id)
            if not system_texture_mapping:
                return
            socket_offset_x     = system_texture_mapping.inputs.get("Input Offset X")
            socket_offset_y     = system_texture_mapping.inputs.get("Input Offset Y")
            socket_offset_z     = system_texture_mapping.inputs.get("Input Offset Z")
            socket_tiling_x     = system_texture_mapping.inputs.get("Input Tiling X")
            socket_tiling_y     = system_texture_mapping.inputs.get("Input Tiling Y")
            socket_tiling_z     = system_texture_mapping.inputs.get("Input Tiling Z")
            socket_rotation_x   = system_texture_mapping.inputs.get("Input Rotation X")
            socket_rotation_y   = system_texture_mapping.inputs.get("Input Rotation Y")
            socket_rotation_z   = system_texture_mapping.inputs.get("Input Rotation Z")
            
            box_offset          = main_layout.box()
            row_offset_x        = box_offset.row(align=True)     
            row_offset_x.label(text="Offset X")           
            row_offset_x.prop(socket_offset_x, "default_value", text="", slider=True, emboss=True)
            row_offset_y        = box_offset.row(align=True)  
            row_offset_y.label(text="Offset Y")     
            row_offset_y.prop(socket_offset_y, "default_value", text="", slider=True, emboss=True)
            row_offset_z        = box_offset.row(align=True)  
            row_offset_z.label(text="Offset Z")     
            row_offset_z.prop(socket_offset_z, "default_value", text="", slider=True, emboss=True)

            box_tiling          = main_layout.box()
            row_tiling_x        = box_tiling.row(align=True)
            row_tiling_x.label(text="Tiling X")   
            row_tiling_x.prop(socket_tiling_x, "default_value", text="", slider=True, emboss=True)
            row_tiling_y        = box_tiling.row(align=True)
            row_tiling_y.label(text="Tiling Y")   
            row_tiling_y.prop(socket_tiling_y, "default_value", text="", slider=True, emboss=True)
            row_tiling_z        = box_tiling.row(align=True)
            row_tiling_z.label(text="Tiling Z")   
            row_tiling_z.prop(socket_tiling_z, "default_value", text="", slider=True, emboss=True)
            
            box_rotation        = main_layout.box()
            row_rotation_x      = box_rotation.row(align=True)
            row_rotation_x.label(text="Rotation X")   
            row_rotation_x.prop(socket_rotation_x, "default_value", text="", slider=True, emboss=True)
            row_rotation_y      = box_rotation.row(align=True)
            row_rotation_y.label(text="Rotation Y")   
            row_rotation_y.prop(socket_rotation_y, "default_value", text="", slider=True, emboss=True)
            row_rotation_z      = box_rotation.row(align=True)
            row_rotation_z.label(text="Rotation Z")   
            row_rotation_z.prop(socket_rotation_z, "default_value", text="", slider=True, emboss=True)
        else:
            row_notification = box_layer.row(align=True)
            row_notification.label(text="No options.", icon='ERROR')

def UI_LayerWorkspace_Layer_Join_Group(context, main_layout, active_manager):
    """UI_LayerWorkspace_Layer_Join_Group"""
    managed_layer = active_manager.m_managed_tm_node_collection
    pointer_active = active_manager.m_managed_tm_node_pointer
    pointer_upper = pointer_active - 1
    pointer_below = pointer_active + 1
    layer_selected = managed_layer[pointer_active]

    if layer_selected.m_type == 'GROUP':
        row_label = main_layout.row(align=True)
        row_label.enabled = False
        row_label.label(text="No options.", icon='ERROR')
        return

    # Join Group UP Button
    enable_up_button = False
    text_up_button = "Join Group"
    row_up_button = main_layout.row(align=True)
    if pointer_upper >= 0 : 
        layer_upper = managed_layer[pointer_upper]
        if not layer_upper:
            return
        if  layer_upper.m_type == 'GROUP':
            enable_up_button = True
            text_up_button = f"Join '{layer_upper.m_name}'"
        elif layer_upper.m_group_id:
            enable_up_button = True
            layer_group_upper = tm_logic.TM_Logic_Layer_Get_By_Id(context, active_manager.m_id, layer_upper.m_group_id)
            if layer_group_upper:
                text_up_button = f"Join '{layer_group_upper.m_name}'" 
    row_up_button.enabled = enable_up_button
    row_up_button.operator("texture_mixer.layer_join_group", text=text_up_button, icon='TRIA_UP').direction = 'UP' 
    
    # Join Group DOWN Button  
    enable_down_button = False
    text_down_button = "Join Group"
    row_down_button = main_layout.row(align=True) 
    if pointer_below <= len(managed_layer)-1:
        layer_below = managed_layer[pointer_below]
        if not layer_below:
            return
        if layer_below.m_type == 'GROUP':
            enable_down_button = True
            text_down_button = f"Join '{layer_below.m_name}'"  
    row_down_button.enabled = enable_down_button
    row_down_button.operator("texture_mixer.layer_join_group", text=text_down_button, icon='TRIA_DOWN').direction = 'DOWN'

def UI_LayerWorkspace_Layer_Exit_Group(context, main_layout, active_manager):
    """UI_LayerWorkspace_Layer_Exit_Group"""    
    managed_layer = active_manager.m_managed_tm_node_collection
    pointer_active = active_manager.m_managed_tm_node_pointer
    layer_selected = managed_layer[pointer_active]
    
    if layer_selected.m_type == 'GROUP':
        row_label = main_layout.row(align=True)
        row_label.enabled = False
        row_label.label(text="No options.", icon='ERROR')
        return

    layer_group_header = tm_logic.TM_Logic_Layer_Get_By_Id(context, active_manager.m_id, layer_selected.m_group_id)

    row_up_button = main_layout.row(align=True)
    row_up_button.operator("texture_mixer.layer_exit_group", text=f"Exit '{layer_group_header.m_name}'", icon='TRIA_UP').direction = 'UP' 

    row_down_button = main_layout.row(align=True)
    row_down_button.operator("texture_mixer.layer_exit_group", text=f"Exit '{layer_group_header.m_name}'", icon='TRIA_DOWN').direction = 'DOWN' 

def UI_LayerWorkspace_Mask(context, main_layout, user_data, active_manager):
    """UI_LayerWorkspace_Mask"""

    active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
    if active_layer is not None:      

        box_mask_enabler = main_layout.box()
        row_mask_enabler = box_mask_enabler.row(align=True)
        if active_layer.m_mask_enable:            
            row_mask_enabler.prop(active_layer,"m_mask_enable", text=f"'{active_layer.m_name}' Mask Enabled", toggle=True, emboss=True)
        else:
            row_mask_enabler.prop(active_layer,"m_mask_enable", text=f"'{active_layer.m_name}' Mask Disabled", toggle=True, emboss=True)

    
        box_mask_button = main_layout.box()
        row_mask_button = box_mask_button.row(align=True)
        row_mask_button.enabled = active_layer.m_mask_enable
        row_mask_button.label(text="Add Mask")
        row_mask_button.separator()
        row_mask_button.operator("texture_mixer.mask_create_new_paint_black", text="", icon_value=tm_icon.TM_Icon_Get_Icon("TM_MASK_FILL_BLACK"))
        row_mask_button.operator("texture_mixer.mask_create_new_paint_white", text="", icon_value=tm_icon.TM_Icon_Get_Icon("TM_MASK_FILL_WHITE"))
        row_mask_button.operator("texture_mixer.mask_create_new_preserved", text="", icon='TEXTURE_DATA') 
        row_mask_button.separator()
        row_mask_button.operator("texture_mixer.mask_remove", text="", icon='TRASH')

        row_mask_panel = main_layout.row(align=True)
        row_mask_panel.enabled = active_layer.m_mask_enable
        row_mask_panel.scale_y = 1.4
        row_mask_panel.template_list(
            f"TM_UL_Mask_List", "", 
            active_layer, "m_managed_tm_mask_collection",
            active_layer, "m_managed_tm_mask_pointer",
            columns=2,
            rows=3,
            type='DEFAULT',
            sort_reverse=False,    
            sort_lock=False
        )

        row_navigation_button = main_layout.row(align=True)
        row_navigation_button.enabled = active_layer.m_mask_enable
        row_navigation_button_split = row_navigation_button.split(factor=0.5, align=True)
        row_navigation_button_split.operator("texture_mixer.mask_move", text="", icon='TRIA_UP').direction = 'UP'
        row_navigation_button_split.operator("texture_mixer.mask_move", text="", icon='TRIA_DOWN').direction = 'DOWN'

        UI_LayerWorkspace_Layer_Mask_Property(context, main_layout, active_manager, active_layer, active_layer.m_mask_enable)            
    else:
        box_notification = main_layout.box()
        row_notification = box_notification.row(align=True)
        row_notification.label(text="No active layer found.", icon='ERROR')

def UI_LayerWorkspace_Layer_Mask_Property(context, main_layout, active_manager, active_layer, is_enable = True):
    """UI_LayerWorkspace_Layer_Mask_Property"""   
    mask_layer = active_layer.m_managed_tm_mask_collection
    if not mask_layer:
        return   

    active_pointer = active_layer.m_managed_tm_mask_pointer
    if active_pointer < 0 or active_pointer > len(mask_layer)-1:
        return

    active_mask = mask_layer[active_pointer]
    if not active_mask:
        return
    
    host_material = tm_logic.TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return
    
    system_mask = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_mask.m_shader_node_system_mask_id)
    if not system_mask:
        return
    
    socket_invert_mask  = system_mask.inputs.get("Mask Invert")

    box_setting = main_layout.box()
    box_setting.enabled = is_enable

    row_invert_mask     = box_setting.row(align=True)   
    row_invert_mask.prop(socket_invert_mask, "default_value", text="Invert Mask", toggle=True, emboss=True)

    row_blend_mode          = box_setting.row(align=True)
    row_blend_mode_split    = row_blend_mode.split(factor=0.45)

    row_blend_mode_left     = row_blend_mode_split.row(align=True)
    row_blend_mode_left.label(text="Blending")
    
    row_blend_mode_right    = row_blend_mode_split.row(align=True)
    row_blend_mode_right.prop(active_mask, "m_blending_mode", text="") 

    if active_mask.m_type == 'MASK_PRESERVED':
        tm_texture = None
        if active_mask.m_tm_texture_id:
            tm_texture = tm_logic.TM_Logic_TMTexture_Get_By_Id(context, active_manager.m_id, active_mask.m_tm_texture_id)
        
        if not tm_texture:             
            row_open_file   =  box_setting.row(align=True)
            row_open_file.operator("texture_mixer.mask_texture_loader", text=f"Open Texture File", icon='FILEBROWSER', emboss=True)

        else:            
            system_texture_mapping = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, tm_texture.m_shader_node_system_texture_id)
            if not system_texture_mapping:
                return
            socket_offset_x     = system_texture_mapping.inputs.get("Offset X")
            socket_offset_y     = system_texture_mapping.inputs.get("Offset Y")
            socket_offset_z     = system_texture_mapping.inputs.get("Offset Z")
            socket_tiling_x     = system_texture_mapping.inputs.get("Tiling X")
            socket_tiling_y     = system_texture_mapping.inputs.get("Tiling Y")
            socket_tiling_z     = system_texture_mapping.inputs.get("Tiling Z")
            socket_rotation_x   = system_texture_mapping.inputs.get("Rotation X")
            socket_rotation_y   = system_texture_mapping.inputs.get("Rotation Y")
            socket_rotation_z   = system_texture_mapping.inputs.get("Rotation Z")
            
            file_name = os.path.basename(tm_texture.m_user_texture_path)
            row_value               = box_setting.row(align=True)
            row_value_mode_split    = row_value.split(factor=0.45)

            row_value_mode_left     = row_value_mode_split.row(align=True)
            row_value_mode_left.label(text="File")
            
            row_value_mode_right    = row_value_mode_split.row(align=True)
            row_value_mode_right.label(text=f": {file_name}")
    
            row_open_file   =  box_setting.row(align=True)
            row_open_file.operator("texture_mixer.mask_texture_loader", text=f"Replace Texture File", icon='FILE_REFRESH', emboss=True)                    
            row_open_file.operator("texture_mixer.mask_texture_remover", text="", icon='TRASH', emboss=True)
            
            box_offset          = main_layout.box()
            row_offset_x        = box_offset.row(align=True)  
            row_offset_x.enabled = is_enable         
            row_offset_x.label(text="Offset X")           
            row_offset_x.prop(socket_offset_x, "default_value", text="", slider=True, emboss=True)
            row_offset_y        = box_offset.row(align=True)  
            row_offset_y.enabled = is_enable         
            row_offset_y.label(text="Offset Y")     
            row_offset_y.prop(socket_offset_y, "default_value", text="", slider=True, emboss=True)
            row_offset_z        = box_offset.row(align=True)  
            row_offset_z.enabled = is_enable         
            row_offset_z.label(text="Offset Z")     
            row_offset_z.prop(socket_offset_z, "default_value", text="", slider=True, emboss=True)

            box_tiling          = main_layout.box()
            row_tiling_x        = box_tiling.row(align=True)
            row_tiling_x.enabled = is_enable         
            row_tiling_x.label(text="Tiling X")   
            row_tiling_x.prop(socket_tiling_x, "default_value", text="", slider=True, emboss=True)
            row_tiling_y        = box_tiling.row(align=True)
            row_tiling_y.enabled = is_enable         
            row_tiling_y.label(text="Tiling Y")   
            row_tiling_y.prop(socket_tiling_y, "default_value", text="", slider=True, emboss=True)
            row_tiling_z        = box_tiling.row(align=True)
            row_tiling_z.enabled = is_enable         
            row_tiling_z.label(text="Tiling Z")   
            row_tiling_z.prop(socket_tiling_z, "default_value", text="", slider=True, emboss=True)
            
            box_rotation        = main_layout.box()
            row_rotation_x      = box_rotation.row(align=True)
            row_rotation_x.enabled = is_enable         
            row_rotation_x.label(text="Rotation X")   
            row_rotation_x.prop(socket_rotation_x, "default_value", text="", slider=True, emboss=True)
            row_rotation_y      = box_rotation.row(align=True)
            row_rotation_y.enabled = is_enable         
            row_rotation_y.label(text="Rotation Y")   
            row_rotation_y.prop(socket_rotation_y, "default_value", text="", slider=True, emboss=True)
            row_rotation_z      = box_rotation.row(align=True)
            row_rotation_z.enabled = is_enable         
            row_rotation_z.label(text="Rotation Z")   
            row_rotation_z.prop(socket_rotation_z, "default_value", text="", slider=True, emboss=True)

def UI_LayerWorkspace_Layer_Default_Settings(main_layout, active_manager):
    """UI_LayerWorkspace_Layer_Default_Settings"""

    if not active_manager:
        return

    host_material = tm_logic.TM_Logic_Material_Get_By_Id(active_manager.m_managed_material_id)
    if not host_material:
        return

    system_composer_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_manager.m_shader_node_system_composer_id)
    system_default_node = tm_logic.TM_Logic_ShaderNode_Get_By_Id(host_material, active_manager.m_shader_node_system_default_id)
    if not system_composer_node or not system_default_node:
        return
    
    socket_default_base_color = system_default_node.inputs.get("Default Base Color")
    socket_default_alpha = system_default_node.inputs.get("Default Base Color Alpha")
    socket_default_metallic = system_default_node.inputs.get("Default Metallic")
    socket_default_roughness = system_default_node.inputs.get("Default Roughness")
    
    socket_option_bump_invert = system_composer_node.inputs.get("Option Bump Invert")
    socket_option_bump_strength = system_composer_node.inputs.get("Option Bump Strength")
    socket_option_bump_distance = system_composer_node.inputs.get("Option Bump Distance")
    socket_option_bump_filterwidth = system_composer_node.inputs.get("Option Bump Filter Width")
    socket_option_normal_strength = system_composer_node.inputs.get("Option Normal Strength")
    socket_option_emission_strength = system_composer_node.inputs.get("Option Emission Strength")

    socket_option_use_smoothness_mode = system_composer_node.inputs.get("Option Use Smoothness Mode")    
    
    #region [Use Option]
    row_option_use = main_layout.row(align=True)
    box_option_use = row_option_use.box()

    row_option_header = box_option_use.row(align=True)
    row_option_header.label(text="Options")

    row_option_use_smoothness_mode = box_option_use.row(align=True)
    row_option_use_smoothness_mode.label(text="Roughness as Gloss/Smooth-ness")
    row_option_use_smoothness_mode.label(text="", icon='BLANK1')
    row_option_use_smoothness_mode.prop(socket_option_use_smoothness_mode, "default_value", text="", emboss=True)
    #endregion [Use Option]

    #region [Default]
    row_defaults = main_layout.row(align=True)
    box_defaults = row_defaults.box()

    row_default_header = box_defaults.row(align=True)
    row_default_header.label(text="Default")

    row_default_base_color = box_defaults.row(align=True)
    row_default_base_color.label(text="Default Base Color")
    row_default_base_color.prop(socket_default_base_color, "default_value", text="")

    row_default_alpha = box_defaults.row(align=True)
    row_default_alpha.label(text="Default Alpha")
    row_default_alpha.prop(socket_default_alpha, "default_value", text="", slider=True, emboss=True)

    row_default_roughness = box_defaults.row(align=True)
    row_default_roughness.label(text="Default Roughness")
    row_default_roughness.prop(socket_default_roughness, "default_value", text="") 

    row_default_metallic = box_defaults.row(align=True)
    row_default_metallic.label(text="Default Metallic")
    row_default_metallic.prop(socket_default_metallic, "default_value", text="")   
    #endregion [Default]

    #region [Bump]
    row_option_bump = main_layout.row(align=True)
    box_option_bump = row_option_bump.box()

    row_option_bump_header = box_option_bump.row(align=True)
    row_option_bump_header.label(text="Bump")
    
    row_option_bump_invert = box_option_bump.row(align=True)
    row_option_bump_invert.label(text="Bump Invert")
    row_option_bump_invert.label(text="", icon='BLANK1')
    row_option_bump_invert.prop(socket_option_bump_invert, "default_value", text="", emboss=True)
    
    row_option_bump_strength = box_option_bump.row(align=True)
    row_option_bump_strength.label(text="Bump Strength")
    row_option_bump_strength.prop(socket_option_bump_strength, "default_value", text="", slider=True, emboss=True)
    
    row_option_bump_distance = box_option_bump.row(align=True)
    row_option_bump_distance.label(text="Bump Distance")
    row_option_bump_distance.prop(socket_option_bump_distance, "default_value", text="", slider=True, emboss=True)
    
    row_option_bump_filterwidth = box_option_bump.row(align=True)
    row_option_bump_filterwidth.label(text="Bump Filter Width")
    row_option_bump_filterwidth.prop(socket_option_bump_filterwidth, "default_value", text="", slider=True, emboss=True)
    #endregion [Bump]
    
    #region [Normal]
    row_option_normal = main_layout.row(align=True)
    box_option_normal = row_option_normal.box()

    row_option_normal_header = box_option_normal.row(align=True)
    row_option_normal_header.label(text="Normal")

    row_option_normal_strength = box_option_normal.row(align=True)
    row_option_normal_strength.label(text="Normal Strength")
    row_option_normal_strength.prop(socket_option_normal_strength, "default_value", text="", slider=True, emboss=True)
    #endregion [Normal]
    
    #region [Emission]
    row_option_emission = main_layout.row(align=True)
    box_option_emission = row_option_emission.box()

    row_option_emission_header = box_option_emission.row(align=True)
    row_option_emission_header.label(text="Emission")

    row_option_emission_strength = box_option_emission.row(align=True)
    row_option_emission_strength.label(text="Emission Strength")
    row_option_emission_strength.prop(socket_option_emission_strength, "default_value", text="", slider=True, emboss=True)
    #endregion [Emission]
#endregion [LayerWorkSpace]

#region [LayerBrush]
class TM_PT_LayerBrush(bpy.types.Panel):
    """TM_PT_LayerBrush"""
    bl_idname = f"TM_PT_LayerBrush"
    bl_label = tm_property.Addon_Data.m_ui_panel_label_brush_settings
    bl_category = tm_property.Addon_Data.m_ui_panel_category
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
        if not active_object:
            return False
        
        if active_object.mode != 'TEXTURE_PAINT':
            return False
        
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return False
        
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)        
        if not active_layer:
            return False
          
        return True
    
    def draw(self, context):
        active_object = tm_logic.TM_Logic_Object_Get_Active_One(context)
        if not active_object:
            return
        
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context)
        if not active_manager:
            return
        
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
        if not active_layer:
            return  
        
        user_data = context.scene.TM_User_Data 
        main_layout = self.layout

        if active_object.mode == 'TEXTURE_PAINT':  
            active_mask = tm_logic.TM_Logic_Mask_Get_Active_Mask(context, active_manager.m_id, active_layer.m_id)
            box_paint = main_layout.box()         
        
            if user_data.m_ui_layer_option_tabs == 'LAYER':
                if active_layer.m_type == 'LAYER_PAINTABLE':
                    row_paint = box_paint.row(align=True) 
                    row_paint.label(text="Texture Painting [Layer]")
                    UI_LayerBrush_Paint(context, main_layout, user_data, active_manager, f"Layer: {active_layer.m_name}")

            elif user_data.m_ui_layer_option_tabs == 'MASK':                                
                if not active_mask:
                    row_paint = box_paint.row(align=True) 
                    row_paint.label(text="Waiting for mask...")
                    return
                
                if active_mask.m_type == 'MASK_PAINTABLE':
                    row_paint = box_paint.row(align=True) 
                    row_paint.label(text="Texture Painting [Mask]")
                    UI_LayerBrush_Paint(context, main_layout, user_data, active_manager, f"Mask: {active_mask.m_name}") 

            if active_layer.m_type == 'LAYER_PAINTABLE' or active_mask and active_mask.m_type == 'MASK_PAINTABLE':
                row_tabs = box_paint.row(align=True)
                row_tabs.prop(user_data, "m_ui_brush_option_tabs", expand=True)
            else:
                row_notification = box_paint.row(align=True)
                row_notification.label(text="No options.", icon='ERROR')
        else:
            row_notification = main_layout.row(align=True)
            row_notification.label(text="No options.", icon='ERROR')
    
def UI_LayerBrush_Paint(context, main_layout, user_data, active_manager, show_text:str=""):
    """UI_LayerBrush_Paint"""
    user_brush_data = user_data.m_brush_data

    if user_data.m_ui_brush_option_tabs == 'PAINT_MODE':         
        # box_alpha_map = main_layout.box()
        # row_alpha_map = box_alpha_map.row(align=True)
        # row_alpha_map.label(text="Alpha Map")
        # row_alpha_map.label(text="", icon='BLANK1')
        # row_alpha_map.template_ID(user_brush_data, 'm_brush_alpha_image', text="", open="image.open")

        def draw_channel(channel_name: str, channel_init: str):

            channel_prop = f"m_channel_{channel_init}_enable"
            channel_brush_color = f"m_brush_{channel_init}_color" 
            channel_brush_image = f"m_brush_{channel_init}_image"
            channel_brush_blend = f"m_brush_{channel_init}_blend" 
            
            channel_available = getattr(active_manager, channel_prop, None)
            if channel_init != 'mask': 
                if not channel_available:
                    return          

            channel_brush_enable = getattr(user_brush_data, channel_prop, None)
            icon_channel_brush_enable = 'HIDE_OFF' if channel_brush_enable else 'HIDE_ON' 
            
            box_channel = main_layout.box()
            row_channel = box_channel.row(align=True)
            row_channel.label(text=channel_name)
            row_channel.label(text="", icon='DECORATE')
            if user_data.m_ui_layer_option_tabs != 'MASK':
                row_channel.prop(user_brush_data, channel_prop, text="", icon=icon_channel_brush_enable, emboss=True)                
        
            if channel_brush_enable:                                
                if not user_data.m_ui_tm_paint_mode_enable:

                    row_default_color = box_channel.row(align=True)
                    row_default_color.scale_y = 0.7
                    row_default_color.label(text="", icon='BLANK1') 
                    row_default_color.prop(user_brush_data, channel_brush_color, text="", slider=True, emboss=True)
                    row_default_color.prop(user_brush_data, channel_brush_blend, text="")
                    
                    # row_default_image = box_channel.row(align=True)
                    # row_default_image.label(text="", icon='BLANK1') 
                    # row_default_image.template_ID(user_brush_data, channel_brush_image, text="", open="image.open")
                    
                    row_single_channel_paint = box_channel.row(align=True)

                    if user_data.m_ui_layer_option_tabs != 'MASK':
                        row_single_channel_paint.label(text="", icon='BLANK1') 
                        op = row_single_channel_paint.operator("texture_mixer.layer_paint_blender_single_channel", text="Blender Paint Mode", emboss=True, icon='BRUSHES_ALL')
                        op.m_show_text = show_text
                        op.m_channel_name_target = channel_name
                        row_single_channel_paint.label(text="", icon='BLANK1')
                    elif user_data.m_ui_layer_option_tabs == 'MASK':
                        row_single_channel_paint.scale_y = 1.5
                        op = row_single_channel_paint.operator("texture_mixer.layer_paint_blender_single_channel", text="Blender Paint Mode", emboss=True, icon='BRUSHES_ALL')
                        op.m_show_text = show_text
                        op.m_channel_name_target = channel_name

        if user_data.m_ui_layer_option_tabs == 'LAYER': 
            shader_type = active_manager.m_main_shader_type   
            channel_set = tm_property.TM_DT_Channels_Based_On_Shader[shader_type]  
            supprted_channels = tm_property.TM_DT_Channels_Metadata.values()

            for channel in supprted_channels:
                channel_name = channel.get('default_name')
                channel_init = channel.get('default_init')
                if channel_name not in channel_set:
                    continue
                draw_channel(channel_name, channel_init)
            if not user_data.m_ui_tm_paint_mode_enable:
                box_notification = main_layout.box()
                row_notification = box_notification.row(align=True)
                row_notification.label(text="WIP Experimental", icon='ERROR')
                row_enable_paint = box_notification.row(align=True)
                row_enable_paint.scale_y = 1.5
                row_enable_paint.operator("texture_mixer.layer_paint_blender_multi_channel", text="Texture Mixer Paint Mode", emboss=True, icon='BRUSHES_ALL').m_show_text = show_text 

            else:
                box_notif = main_layout.box()
                row_notif = box_notif.row(align=True)
                row_notif.label(text="Press 'ESC' or 'RIGHTCLICK' to exit paint mode.", icon='DECORATE')

        elif user_data.m_ui_layer_option_tabs == 'MASK':
            channel_name = 'Mask'
            channel_init = 'mask'
            draw_channel(channel_name, channel_init)

            if user_data.m_ui_tm_paint_mode_enable:
                box_notif = main_layout.box()
                row_notif = box_notif.row(align=True)
                row_notif.label(text="Press 'ESC' to exit paint mode.", icon='DECORATE')
            
    elif user_data.m_ui_brush_option_tabs == 'OPTIONS':
        box_options = main_layout.box()

        row_options_header = box_options.row(align=True)
        row_options_header.label(text="Options")
        
        row_option_enable_smoothing = box_options.row(align=True)
        row_option_enable_smoothing.label(text="Enable Smoothing")
        row_option_enable_smoothing.label(text="", icon='BLANK1')
        row_option_enable_smoothing.prop(user_brush_data,"m_brush_option_enable_smoothing", text="", emboss=True)

        row_option_skip_channel = box_options.row(align=True)
        row_option_skip_channel.label(text="Skip Channel")
        row_option_skip_channel.label(text="", icon='BLANK1')
        row_option_skip_channel.prop(user_brush_data,"m_brush_option_skip_channel", text="", emboss=True)
#endregion [LayerBrush]

#region [Export]
class TM_UL_TextureExport_List(bpy.types.UIList):
    """TM_UL_Layer_List"""
    bl_idname = f"TM_UL_TextureExport_List"

    def draw_filter(self, context, layout):
        pass

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        tm_texture_export = item        

        row_name = layout.row(align=True)     
        row_name.prop(tm_texture_export, "m_name", text="", icon='FILE_IMAGE', emboss=False)

        row_utility = layout.row(align=True)        
        row_utility.prop(tm_texture_export, "m_enable", text="", emboss=True)

class TM_PT_TextureExport(bpy.types.Panel):
    """TM_PT_TextureExport"""
    bl_idname = f"TM_PT_TextureExport"
    bl_label = tm_property.Addon_Data.m_ui_panel_label_export_settings
    bl_category = tm_property.Addon_Data.m_ui_panel_category
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        user_data = context.scene.TM_User_Data
        active_paint_mode = user_data.m_ui_tm_paint_mode_enable
        active_layer = tm_logic.TM_Logic_Layer_Get_Active_Layer(context)
        return bool(active_layer and not active_paint_mode)

    def draw(self, context):
        active_manager = tm_logic.TM_Logic_LayerManager_Get_Active_Manager(context) 
        user_data = context.scene.TM_User_Data 
        
        if user_data.m_ui_tm_paint_mode_enable:
            return
        
        main_layout = self.layout  

        box_layer_button = main_layout.box()
        row_layer_button = box_layer_button.row(align=True)
        row_layer_button.label(text="Add Texture Export")
        row_layer_button.separator()
        row_layer_button.operator("texture_mixer.export_template_create_new", text="", icon='ADD')
        row_layer_button.separator()
        row_layer_button.operator("texture_mixer.export_template_delete", text="", icon='TRASH')

        row_layer_panel = main_layout.row(align=True)
        row_layer_panel.scale_y = 1.4
        row_layer_panel.template_list(
            f"TM_UL_TextureExport_List", "", 
            active_manager, "m_managed_tm_texture_export_collection",
            active_manager, "m_managed_tm_texture_export_pointer",
            columns=2,
            rows=3,
            type='DEFAULT',
            sort_reverse=False,    
            sort_lock=False
        )
        row_default_export_button = box_layer_button.row(align=True)
        row_default_export_button.operator("texture_mixer.export_build_active_channels_template", text="Add Default Active Channels", icon='ADD')

        active_export = tm_logic.TM_Logic_Export_Get_Active_Template(context)
        if not active_export:
            return
        
        box_export_rgba_settings = main_layout.box()
        icon_export_rgba_settings = 'TRIA_DOWN' if user_data.m_ui_show_export_rgba_settings else 'TRIA_RIGHT'

        row_export_rgba_settings = box_export_rgba_settings.row(align=True)
        row_export_rgba_settings.alignment = 'LEFT'
        row_export_rgba_settings.prop(user_data,"m_ui_show_export_rgba_settings",text="RGBA Settings", icon=icon_export_rgba_settings, emboss=False)
        
        if user_data.m_ui_show_export_rgba_settings:
            row_file_type = box_export_rgba_settings.row(align=True)
            row_file_type.label(text="File Type")
            row_file_type.label(text="", icon='BLANK1')
            row_file_type.prop(active_export, "m_file_type", text="")

            file_type_set = tm_property.TM_DT_Export_File_Type
            file_type_data = file_type_set.get(active_export.m_file_type)
            alpha_support = file_type_data.get('support_alpha')

            def ChannelDraw(channel:str):
                row_slot_split = box_export_rgba_settings.split(factor=0.075)

                if channel == 'a' and not alpha_support:
                    row_slot_split.enabled = False

                row_slot_l = row_slot_split.row(align=True)
                row_slot_l.label(text="", icon='BLANK1')
                row_slot_l.label(text=f"{channel.upper()}")

                row_slot_r = row_slot_split.row(align=True)
                row_slot_r_split = row_slot_r.split(factor=0.5)

                row_slot_r_split_l = row_slot_r_split.row(align=True)
                row_slot_r_split_l.prop(active_export,f"m_slot_{channel}_map", text="")
                
                row_slot_r_split_r = row_slot_r_split.row(align=True)
                row_slot_r_split_r.prop(active_export,f"m_slot_{channel}_channel", text="")

                invert_icon = 'CHECKBOX_HLT' if getattr(active_export,f"m_slot_{channel}_invert", False) else 'CHECKBOX_DEHLT'
                row_slot_r_split_r.prop(active_export,f"m_slot_{channel}_invert", text="", toggle=True, emboss=True, icon = invert_icon)

                as_srgb_icon = 'CHECKBOX_HLT' if getattr(active_export,f"m_slot_{channel}_as_srgb", False) else 'CHECKBOX_DEHLT'
                row_slot_r_split_r.prop(active_export,f"m_slot_{channel}_as_srgb", text="", toggle=True, emboss=True, icon = as_srgb_icon)

            ChannelDraw("r")
            ChannelDraw("g")
            ChannelDraw("b")
            ChannelDraw("a")


        box_export_path_settings = main_layout.box()
        icon_export_path_settings = 'TRIA_DOWN' if user_data.m_ui_show_export_path_settings else 'TRIA_RIGHT'

        row_export_path_settings = box_export_path_settings.row(align=True)
        row_export_path_settings.alignment = 'LEFT'
        row_export_path_settings.prop(user_data,"m_ui_show_export_path_settings",text="Export Settings", icon=icon_export_path_settings, emboss=False)
        
        if user_data.m_ui_show_export_path_settings:
            row_resolution = box_export_path_settings.row(align=True)
            row_resolution.label(text="", icon='DECORATE')            
            row_resolution.label(text="Export Resolution")            
            row_resolution.prop(active_manager, "m_output_resolution", text="")

            row_margin = box_export_path_settings.row(align=True)
            row_margin.label(text="", icon='DECORATE')            
            row_margin.label(text="Export Margin")
            row_margin.prop(active_manager.m_data, "m_export_render_margin_size", text="")

            path_resolution = box_export_path_settings.row(align=True)
            path_resolution.label(text="", icon='DECORATE')            
            path_resolution.label(text="Export Path")
            path_resolution.prop(active_manager.m_data,"m_export_save_file_path", text="")

            row_button_export = box_export_path_settings.row(align=True)
            row_button_export.scale_y = 2.0
            row_button_export.operator("texture_mixer.export_bake", text="BAKE-EXPORT", emboss=True)
#endregion [Export]

#region [Included Classes & Property To Register]
#-------------------------------------------------
included_classes = (   
    #--------------------------------------------- 
    TM_UL_Layer_List,
    TM_UL_Mask_List,
    TM_UL_Layer_Manager_List,
    TM_UL_TextureExport_List,
    #---------------------------------------------
    TM_PT_UserInfo,
    TM_PT_UserSettings,
    TM_PT_LayerWorkSpace,
    TM_PT_LayerBrush,
    TM_PT_TextureExport,
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