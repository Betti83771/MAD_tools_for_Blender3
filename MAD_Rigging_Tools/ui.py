import bpy

class OtherOperatorsPanel(bpy.types.Panel):
    """Subpanel of the main MAD Rigging tool, with additional operators"""
    bl_label = "Other Tools"
    bl_idname = "MST_PT_otheroperators"
    bl_space_type = 'NODE_EDITOR'
    bl_category = "MAD Rigging Tools"
    bl_region_type = 'UI'
    #bl_parent_id = "MST_PT_noderig"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mad_utils.refresh_drivers")
        row = layout.row()
        row.operator("maD_utils.remobe_broken_drivers")

classes = [
    #  classes here
    OtherOperatorsPanel

]

def ui_register():
    # ui property definitions here (window_manager props)
    
    for cls in classes:
        bpy.utils.register_class(cls)

def ui_unregister():
    # ui property deletions here 
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
