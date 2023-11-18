import bpy

class MadGeneralToolsPanel(bpy.types.Panel):
    """To be split into drivers stuff and the rest"""
    bl_label = "Mad General tools"
    bl_idname = "MGU_PT_otheroperators"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD General Utilities"
    bl_region_type = 'UI'
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mad_utils.refresh_drivers")
        row = layout.row()
        row.operator("mad_utils.remobe_broken_drivers")
        row = layout.row()
        row.operator("mad_utils.bind_all")

class MadRelocatePathPanel(bpy.types.Panel):
    """Relocate paths"""
    bl_label = "Relocate library paths"
    bl_idname = "MGU_PT_relocpath"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD General Utilities"
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.row().prop(context.window_manager, "mad_relocate_paths_old_path")
        layout.row().prop(context.window_manager, "mad_relocate_paths_new_path")
        op =layout.row().operator( "mad_utils.relocate_paths")
        op.old_path = context.window_manager.mad_relocate_paths_old_path
        op.new_path = context.window_manager.mad_relocate_paths_new_path

class MadDriversInNodeEditorPanel(bpy.types.Panel):
    """Panel that appears in node editor so it can be useful with rigged nodes"""
    bl_label = "Driver operations"
    bl_idname = "MGU_PT_driversondeeditor"
    bl_space_type = 'NODE_EDITOR'
    bl_category = "MAD General Utilities"
    bl_region_type = 'UI'
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mad_utils.refresh_drivers")
        row = layout.row()
        row.operator("mad_utils.remobe_broken_drivers")

classes = [
    #  classes here
    MadGeneralToolsPanel,
    MadRelocatePathPanel

]

def ui_register():
    # ui property definitions here (window_manager props)
    bpy.types.WindowManager.mad_relocate_paths_old_path = bpy.props.StringProperty(
        name="Old Path",
        description="Path or path fragment to replace",
        subtype='FILE_PATH',
        default=f"//"
    )
    bpy.types.WindowManager.mad_relocate_paths_new_path = bpy.props.StringProperty(
        name="New Path",
        description="Path or path fragment to replace with",
        subtype='FILE_PATH',
        default=f"//"
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def ui_unregister():
    
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # ui property deletions here 
    del bpy.types.WindowManager.mad_relocate_paths_new_path
    del bpy.types.WindowManager.mad_relocate_paths_old_path 