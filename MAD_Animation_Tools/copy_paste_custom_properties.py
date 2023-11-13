import bpy
from mathutils import Vector

version = (1, 1)

PREF_TEXT = "Copy / paste custom properties"
PREF_DESCRIPTION = "Activate feature: 'Copy / paste custom properties', pose bone context menu"

class CopyBoneCustomPropsOperator(bpy.types.Operator):
    """Copy the values of this bone's Custom Properties, to be pasted on another bone's same custom properties"""
    bl_idname = "mad_anim_tools.cpcp_copy"
    bl_label = "(MAD) Copy Bone's custom property values"
    
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        context.window_manager['cpcp_clipboard'] = ""
        copy_string = "" 
        for tuple in context.active_pose_bone.items():
            if len(tuple) > 2:
                continue
            if isinstance(tuple[1], str):
                continue
            if tuple[0] == '_RNA_UI': continue
            if "<bpy id property array" in str(tuple[1]):
                copy_string += f"{tuple[0]}: Vector(("
                rangint = int(str(tuple[1])[-3])
                for i in range(rangint):
                    copy_string += f"{tuple[1][i]}, "
                    if i == rangint - 1:
                        copy_string = copy_string[:-2]
                copy_string += "))__cpcp__"
            else:
                copy_string += f"{tuple[0]}: {str(tuple[1])}__cpcp__"
            
        context.window_manager['cpcp_clipboard'] = copy_string
        print("copy_string", copy_string)
        return {'FINISHED'}

class PasteBoneCustomPropsOperator(bpy.types.Operator):
    """Paste the memorized values on this bone's correspondent Custom Properties"""
    bl_idname = "mad_anim_tools.cpcp_paste"
    bl_label = "(MAD) Paste Bone's custom property values"
    
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' and context.active_pose_bone

    def execute(self, context):
        copy_string = context.window_manager['cpcp_clipboard']
        for stuff in copy_string.split("__cpcp__"):
            keyvalue = stuff.split(": ")
            print("keyvalue", keyvalue)
            if keyvalue[0] not in context.active_pose_bone.keys():
                continue
            #if keyvalue[0] == '_RNA_UI': continue
            actual_value = eval(keyvalue[1])
            
            if actual_value is not None:
                context.active_pose_bone[keyvalue[0]] = actual_value
            else:
                self.report(type={'WARNING'}, message=f"can't convert the stored value '{keyvalue[1]}' into a Int, Float or Vector type.")
                context.window_manager['cpcp_clipboard'] = context.window_manager['cpcp_clipboard'].replace(keyvalue[0], "").replace(keyvalue[1], "")
        return {'FINISHED'}
    
def cpcp_menu_func(self, context):
    self.layout.separator()
    copy = self.layout.operator("mad_anim_tools.cpcp_copy", icon='COPYDOWN')
    paste = self.layout.operator("mad_anim_tools.cpcp_paste", icon='PASTEDOWN')

def copy_paste_custom_props_register():
    bpy.types.WindowManager.cpcp_clipboard = bpy.props.StringProperty(default="",
                                              #  name=' CPCP clipboard', 
                                              #  desctiption="prop: Value, ...",
                                                #update=register_subfolder_panels
                                                )
    bpy.utils.register_class(CopyBoneCustomPropsOperator)
    bpy.utils.register_class(PasteBoneCustomPropsOperator)
    bpy.types.VIEW3D_MT_pose_context_menu.append(cpcp_menu_func)

def copy_paste_custom_props__unregister():
    bpy.utils.unregister_class(CopyBoneCustomPropsOperator)
    bpy.utils.unregister_class(PasteBoneCustomPropsOperator)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(cpcp_menu_func)
    del bpy.types.WindowManager.cpcp_clipboard

if __name__ == "__main__":
    copy_paste_custom_props_register()
   