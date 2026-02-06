#----------------------------------------------------
#################| Custom Debugger |#################
#----------------------------------------------------
# Author    = Candra Agung Prasetyo                 |
# Email     = yuyevon777@gmail.com                  |
# File      = texture_mixer_debug.py                |
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
import os
import platform
import datetime
#-------------------------------------------------
DEFAULT_NAME = "TextureMixer"
DEFAULT_LOG = " INFO: "
DEFAULT_ERROR = " ERROR: "
DEFAULT_LOGWARNING = " WARNING: "
DEFAULT_SEPARATOR = ""
#-------------------------------------------------
#endregion [IMPORT]

#region [OS Windows Helper]
_CONSOLE_INITIALIZED = False

def _init_console():
    global _CONSOLE_INITIALIZED
    if _CONSOLE_INITIALIZED:
        return
    
    if platform.system() == 'Windows':
        os.system('') 
    
    _CONSOLE_INITIALIZED = True

_init_console()
#endregion [OS Windows Helper]

#region [Stop Spam]
#-------------------------------------------------
STOP_LOG_SPAM = [
    "TextureMixer_Icon_Loader",
    # "TM_Logic_ID_Get_New",
    "TM_Logic_Object_Get_Active_One",
    "TM_Logic_Material_Get_By_Id",
    "TM_Logic_LayerManager_Get_Active_Manager",
    "TM_logic_LayerManager_Get_By_Id",
    "TM_Logic_Layer_Get_Active_Layer",
    "TM_Logic_Layer_Get_By_Id",
    "TM_Logic_Layer_Get_Index_By_Id",
    "TM_Logic_Mask_Get_Active_Mask",
    "TM_Logic_ShaderNode_Get_By_Id",
    "TM_Logic_ShaderNode_Socket_Disconnector",
    "TM_Logic_ShaderNode_Socket_Linker",
    "TM_Logic_TMTexture_Get_By_Id",
    "TM_Logic_Utility_Get_Main_Shader_Name",
    # "TM_Logic_Utility_Get_Resolution_From_Preset",
]
#-------------------------------------------------
STOP_LOGWARNING_SPAM = [
    "TM_Logic_Object_Get_Active_One",
    "TM_Logic_LayerManager_Get_Active_Manager",
    "TM_Logic_Layer_Get_Active_Layer"
]
#-------------------------------------------------
STOP_LOGERROR_SPAM = []
#-------------------------------------------------
CUSTOM_TAGS = [
    ".start",
    ".cancelled",
    ".finished",
]
#-------------------------------------------------
#endregion [Stop Spam]

#region [Debug System]
class Debug:
    ENABLED = True
    #---------------------------------------------
    SHOW_INFO = False
    SHOW_WARNING = True
    SHOW_ERROR = True
    #---------------------------------------------
    SHOW_CUSTOM_TAGS = False
    SHOW_REGION = False
    SHOW_SEPARATOR = False
    #---------------------------------------------
    SHOW_TIMESTAMP = True
    SHOW_COLOR = True
    #---------------------------------------------

    #region [Color MSG]
    _RESET = "\033[0m"
    _INFO = "\033[32m"      
    _WARNING = "\033[33m"   
    _ERROR = "\033[31m"     
    _BOLD = "\033[1m"
    _DIM = "\033[2m"
    #endregion [Color MSG]     

    @staticmethod
    def _timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def Separator(region: str = None, char: str = "—", length: int = 50):
        if not Debug.ENABLED or not Debug.SHOW_SEPARATOR: 
            return
        
        if region in STOP_LOG_SPAM or region in STOP_LOGWARNING_SPAM or region in STOP_LOGERROR_SPAM:
            return
        
        line = char * length
        ts = f"{Debug._timestamp()} " if Debug.SHOW_TIMESTAMP else ""
        region_tag = f"[{region}]{DEFAULT_SEPARATOR}" if region and Debug.SHOW_REGION else DEFAULT_SEPARATOR
        prefix = f"|[{DEFAULT_NAME}]|{region_tag}"

        if Debug.SHOW_COLOR:
            print(f"{Debug._DIM}{ts}{prefix}{line}{Debug._RESET}")
        else:            
            print(f"{ts}{prefix}{line}")

    @staticmethod
    def LogSuper(msg: str):
        ts = f"{Debug._timestamp()} " if Debug.SHOW_TIMESTAMP else ""
        region_tag = " "

        if Debug.SHOW_COLOR:
            prefix = f"{Debug._INFO}|{Debug._BOLD}[{DEFAULT_NAME}]{Debug._RESET}{Debug._INFO}|{Debug._RESET}"
            print(f"{Debug._DIM}{ts}{Debug._RESET}{prefix}{Debug._INFO}{region_tag}{Debug._RESET}{msg}")
        else:
            prefix = f"|[{DEFAULT_NAME}]|"
            print(f"{ts}{prefix}{region_tag}{msg}")


    @staticmethod
    def Log(msg: str, region: str = None):
        if not Debug.ENABLED or not Debug.SHOW_INFO:
            return
        
        if region in STOP_LOG_SPAM:
            return
        
        if not Debug.SHOW_CUSTOM_TAGS:
            for tag in CUSTOM_TAGS:
                if tag in msg:
                    return

        if Debug.SHOW_COLOR:
            ts = f"{Debug._DIM}{Debug._timestamp()}{Debug._RESET} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"[{region}]{DEFAULT_LOG}" if region and Debug.SHOW_REGION else DEFAULT_LOG
            prefix = f"{Debug._INFO}|{Debug._RESET}{Debug._BOLD}[{DEFAULT_NAME}]{Debug._RESET}{Debug._INFO}|{Debug._RESET}{region_tag}"
            print(f"{ts}{prefix}{msg}")
        else:
            ts = f"{Debug._timestamp()} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"[{region}]{DEFAULT_LOG}" if region and Debug.SHOW_REGION else DEFAULT_LOG
            prefix = f"|[{DEFAULT_NAME}]|{region_tag}"
            print(f"{ts}{prefix}{msg}")

    @staticmethod
    def LogWarning(msg: str, region: str = None):
        if not Debug.ENABLED or not Debug.SHOW_WARNING:
            return
        
        if region in STOP_LOGWARNING_SPAM:
            return
        
        if not Debug.SHOW_CUSTOM_TAGS:
            for tag in CUSTOM_TAGS:
                if tag in msg:
                    return
        
        if Debug.SHOW_COLOR:
            ts = f"{Debug._DIM}{Debug._timestamp()}{Debug._RESET} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"{Debug._WARNING}[{region}]{DEFAULT_LOGWARNING}{Debug._RESET}" if region and Debug.SHOW_REGION else f"{Debug._WARNING}{DEFAULT_LOGWARNING}{Debug._RESET}"
            prefix = f"{Debug._WARNING}|{Debug._RESET}{Debug._WARNING}{Debug._BOLD}[{DEFAULT_NAME}]{Debug._RESET}{Debug._RESET}{Debug._WARNING}|{Debug._RESET}{region_tag}"
            print(f"{ts}{prefix}{Debug._WARNING}{msg}{Debug._RESET}")
        else:
            ts = f"{Debug._timestamp()} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"[{region}]{DEFAULT_LOGWARNING}" if region and Debug.SHOW_REGION else DEFAULT_LOGWARNING
            prefix = f"|[{DEFAULT_NAME}]|{region_tag}"
            print(f"{ts}{prefix}{msg}")

    @staticmethod
    def LogError(msg: str, region: str = None):
        if not Debug.ENABLED or not Debug.SHOW_ERROR:
            return
        
        if region in STOP_LOGERROR_SPAM:
            return
        
        if not Debug.SHOW_CUSTOM_TAGS:
            for tag in CUSTOM_TAGS:
                if tag in msg:
                    return
        
        if Debug.SHOW_COLOR:
            ts = f"{Debug._DIM}{Debug._timestamp()}{Debug._RESET} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"{Debug._ERROR}[{region}]{DEFAULT_ERROR}{Debug._RESET}" if region and Debug.SHOW_REGION else f"{Debug._ERROR}{DEFAULT_ERROR}{Debug._RESET}"
            prefix = f"{Debug._ERROR}|{Debug._RESET}{Debug._ERROR}{Debug._BOLD}[{DEFAULT_NAME}]{Debug._RESET}{Debug._RESET}{Debug._ERROR}|{Debug._RESET}{region_tag}"
            print(f"{ts}{prefix}{Debug._ERROR}{msg}{Debug._RESET}")
        else:
            ts = f"{Debug._timestamp()} " if Debug.SHOW_TIMESTAMP else ""
            region_tag = f"[{region}]{DEFAULT_ERROR}" if region and Debug.SHOW_REGION else DEFAULT_ERROR
            prefix = f"|[{DEFAULT_NAME}]|{region_tag}"
            print(f"{ts}{prefix}{msg}")
#endregion [Debug System]