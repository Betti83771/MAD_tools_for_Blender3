# ====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ======================= END GPL LICENSE BLOCK ========================


bl_info = {
    "name": "MAD Rigging Tools ",
    "author": "Betti",
    "version": (2, 0, 2),
    "blender": (3, 0, 0),
    "location": "Nodes > MAD Rigging Tools",
    "description": """In this addon: Material node autorig, image sequence &co. node autorig, grease pencil shading autorig""",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}


import bpy
import os
import importlib 
from sys import modules


def import_and_reload_all_modules(modules_names:list):
    """Detects the modules with a .py extension and without a special name that are part of the addon;
    imports and reloads them, so when adding a new module I don't have to remember to add it to __init__.py
    to be imported and reloaded, in order to be updated correctly by Blender upon making changes to it."""
    
    addon_path = os.path.split(__file__)[0]
    for root, dirs, files in os.walk(addon_path, topdown=False):
        if ".git" in root: continue
        if ".vscode" in root: continue
        if "__" in root: continue
        root2 = root.replace(addon_path, ".").replace(os.sep, ".")
        for file in files:
            if file.startswith("."): continue
            if not file.endswith(".py"): continue
            if "__" in file: continue
            file2 = file.replace(".py", "")
            modules_names.append((root2 + "." + file2)[1:])

    for module_name in modules_names:
        importlib.import_module(__name__ + module_name)
        actual_module = modules[__name__ + module_name]
        importlib.reload(actual_module)



from . import addon_updater_ops 
from . import addon_updater_ops_global 
from .ui import *
from .preferences_ui import Prefs
from .material_node_rig.node_ui import *
from .deps.operators_refresh_drivers import refr_drvs_register, refr_drvs_unregister
from .gp_shading.grease_pencil_rigging import gpr_register, gpr_unregister
from .image_sequence_node_autorig import isoa_register, isoa_unregister



def register():
    import_and_reload_all_modules([])
    addon_updater_ops.addon_update_register(bl_info)
    addon_updater_ops_global.addon_update_register(bl_info)
    bpy.utils.register_class(Prefs)
    try:
        bpy.ops.object.refresh_drivers.poll()
    except AttributeError:
        refr_drvs_register()
    node_ui_register()
    gpr_register()
    isoa_register()  
    ui_register()
    
    


def unregister():
    ui_unregister()
    isoa_unregister()
    gpr_unregister()
    node_ui_unregister()
    try:
        refr_drvs_unregister()
    except AttributeError:
        pass
        
    bpy.utils.unregister_class(Prefs)
    addon_updater_ops_global.addon_update_unregister()
    addon_updater_ops.addon_update_unregister()
