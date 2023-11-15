import bpy

def gp_apply_from_panel(obj_name, layer_name, type):
    layer = bpy.data.objects[obj_name].data.layers[layer_name]
    if type == "not_use_lights":
        layer.use_lights = False
    if type == "opacity":
        layer.opacity = 0.5

class GPApplyFromPanel(bpy.types.Operator):
    """Apply this information to the object"""
    bl_idname = "mad_anim_tools.gp_apply_from_panel"
    bl_label = "Apply"

    obj_name: bpy.props.StringProperty(name="obj_name")
    layer_name: bpy.props.StringProperty(name="layer_name")
    index: bpy.props.IntProperty(name="index")
    type: bpy.props.EnumProperty(name="type", items=[("not_use_lights","not_use_lights",""),("opacity","opacity","")])

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        gp_apply_from_panel(self.obj_name, self.layer_name, self.type)
        return {'FINISHED'}

class GPCSubpanelGP(bpy.types.Panel):
    bl_label = "Grease pencil checker"
    bl_idname = "OBJECT_PT_gpc_panel"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
   # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        for gp in bpy.data.grease_pencils: #each for cycle is a row
            gp_obj_name = next((obj.name for obj in bpy.data.objects if obj.data == gp), None)
            if not gp_obj_name:
                #orphan data?
                continue 
            name_gpobj = False
            for layer in gp.layers:
                name_layer = False
                if layer.use_lights:
                    if not name_gpobj:
                        row = self.layout.row()
                        row.label(text=gp_obj_name, icon='GREASEPENCIL')
                        name_gpobj = True
                    row = self.layout.row()
                    row.label(text="   " + layer.info)
                    name_layer = True
                    row = self.layout.row()
                    row.label(text="    Use lights is active")
                    apply = row.operator("mad_anim_tools.gp_apply_from_panel", text="Disable")
                    apply.obj_name = gp_obj_name
                    apply.layer_name = layer.info
                    apply.type = "not_use_lights"
                if layer.opacity == 1:
                    if not name_gpobj:
                        row = self.layout.row()
                        row.label(text=gp_obj_name, icon='GREASEPENCIL')
                        name_gpobj = True
                    if not name_layer:
                        row = self.layout.row()
                        row.label(text="   " + layer.info)
                    row = self.layout.row()
                    row.label(text="    Opacity is 1")
                    apply = row.operator("mad_anim_tools.gp_apply_from_panel", text="Set to 0.5")
                    apply.obj_name = gp_obj_name
                    apply.layer_name = layer.info
                    apply.type = "opacity"
                    
                
def grease_pencil_layer_ckecker_register():
    bpy.utils.register_class(GPApplyFromPanel)
    bpy.utils.register_class(GPCSubpanelGP)

def grease_pencil_layer_ckecker_unregister():
    bpy.utils.unregister_class(GPCSubpanelGP)
    bpy.utils.unregister_class(GPApplyFromPanel)


if __name__ == "__main__":
    grease_pencil_layer_ckecker_register()

