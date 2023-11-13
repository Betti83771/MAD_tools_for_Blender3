import bpy
from mathutils import Euler, Matrix, Vector, Quaternion


def apply_from_panel(obj, type):
    """type must be 'location', 'rotation', 'scale'"""
    curr_selected = bpy.context.view_layer.objects.selected
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    if type == 'location':
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    if type == 'rotation':
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if type == 'scale':
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for obj in curr_selected:
        obj.select_set(True)

def object_select(self, obj_name):
    obj = bpy.data.objects[obj_name]
    if obj_name not in bpy.context.view_layer.objects.keys():
        self.report({'WARNING'}, "{0} not in current view layer; can't be selected".format(obj_name))
        return
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_button_show(self, obj, type, nameshow=True):
            
            if type == 'scale':
                if obj.scale == Vector((1.0, 1.0, 1.0)):
                    return
                text = "Scale"
            if type == 'location':
                if obj.location == Vector((0.0, 0.0, 0.0)):
                    return
                text = "Location"
            if type == 'quat_rot':
                if obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)):
                    return
                type = 'rotation'
                text = "Quaternion rot"
            if type == 'eu_rot':
                if obj.rotation_euler.to_matrix() == Matrix(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-0.0, 0.0, 1.0))):
                    return
                type = 'rotation'
                text = "Euler rot"
            layout = self.layout
            row = layout.row()
            
            row.label(text=text)
            apply = row.operator("object.apply_from_panel")
            apply.obj_name = obj.name
            apply.type = type

def select_button_show(obj, row):
            select = row.operator("object.select_from_panel", icon='RESTRICT_SELECT_OFF')
            select.obj_name = obj.name


def nameshow(obj, row):
            if obj.data:
                if obj.data.name in bpy.data.armatures:
                    icon = 'ARMATURE_DATA'
                elif obj.data.name in bpy.data.grease_pencils:
                    icon = 'GREASEPENCIL'
                elif obj.data.name in bpy.data.curves:
                    icon = 'CURVE_DATA'
                else:
                    icon = 'OBJECT_DATA'
            else:
                icon = 'EMPTY_ARROWS'
            row.label(text=obj.name + ":", icon=icon)


class SelectFromPanel(bpy.types.Operator):
    """Select object"""
    bl_idname = "object.select_from_panel"
    bl_label = ""

    obj_name: bpy.props.StringProperty(name="obj_name")

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        object_select(self, self.obj_name)
        return {'FINISHED'}

class ApplyFromPanel(bpy.types.Operator):
    """Apply this transformation to the object"""
    bl_idname = "object.apply_from_panel"
    bl_label = "Apply"

    obj_name: bpy.props.StringProperty(name="obj_name")
    type: bpy.props.StringProperty(name="type")
    index: bpy.props.IntProperty(name="index")

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        apply_from_panel(bpy.data.objects[self.obj_name], self.type)
        return {'FINISHED'}

class TransformCheckerPanel(bpy.types.Panel):
    """Creates a Panel in the MAD Animation Tools panel in 3D View, with
    unapplied transforms and a handy operator do apply them 'on the fly' ;)"""
    bl_label = "Transform Checker"
    bl_idname = "OBJECT_PT_tracheck"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        layout = self.layout

        row= layout.row()
        row.label(text="Hide:")
        row= layout.row()
        if context.window_manager.mad_transform_checker_hide_loc:
            icon_loc='HIDE_ON'
        else:
            icon_loc='HIDE_OFF'
        row.prop(context.window_manager, "mad_transform_checker_hide_loc", icon=icon_loc)

        row= layout.row()
        if context.window_manager.mad_transform_checker_hide_rot:
            icon_rot='HIDE_ON'
        else:
            icon_rot='HIDE_OFF'
        row.prop(context.window_manager, "mad_transform_checker_hide_rot", icon=icon_rot)

        row= layout.row()
        if context.window_manager.mad_transform_checker_hide_scale:
            icon_scale='HIDE_ON'
        else:
            icon_scale='HIDE_OFF'
        row.prop(context.window_manager, "mad_transform_checker_hide_scale", icon=icon_scale)
        
        

class TCSubpanelNormalObjs(bpy.types.Panel):
    bl_label = "Objects"
    bl_idname = "OBJECT_PT_tc_subpanel_normalobjs"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_PT_tracheck'

    def draw(self, context):
        
        layout = self.layout
        for obj in bpy.context.scene.objects: #each for cycle is a row
            if not obj.data:
                continue
            if obj.data.name in bpy.data.cameras:
                continue
            if obj.data.name in bpy.data.curves:
                continue
            if obj.data.name in bpy.data.lights:
                continue
            if obj.data.name in bpy.data.lattices:
                continue
            if obj.data.name in bpy.data.grease_pencils:
                continue
            if obj.data.name  in bpy.data.armatures:
                continue
            if "WGT" in obj.name:
                continue
            if obj.scale == Vector((1.0, 1.0, 1.0)) and \
            obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)) and \
            obj.rotation_euler == Euler((0.0, 0.0, 0.0)) and \
            obj.location == Vector((0.0, 0.0, 0.0)) :
                continue
            
            row= layout.row()
            select_button_show(obj, row)
            nameshow(obj, row)
            if not context.window_manager.mad_transform_checker_hide_rot:
                if obj.rotation_mode == 'QUATERNION':
                    apply_button_show(self, obj, 'quat_rot')
                else:
                    apply_button_show(self, obj, 'eu_rot')
            if not context.window_manager.mad_transform_checker_hide_scale:
                apply_button_show(self, obj, 'scale')
            if not context.window_manager.mad_transform_checker_hide_loc:
                apply_button_show(self, obj, 'location')

class TCSubpanelArmatures(bpy.types.Panel):
    bl_label = "Armatures"
    bl_idname = "OBJECT_PT_tc_subpanel_armatures"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_PT_tracheck'

    def draw(self, context):
        for obj in bpy.context.scene.objects: #each for cycle is a row
            if not obj.data:
                continue
            if obj.data.name not in bpy.data.armatures:
                continue
            if obj.scale == Vector((1.0, 1.0, 1.0)) and \
            obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)) and \
            obj.rotation_euler == Euler((0.0, 0.0, 0.0)) and \
            obj.location == Vector((0.0, 0.0, 0.0)) :
                continue

            row= self.layout.row()
            select_button_show(obj, row)
            nameshow(obj, row)
            if not context.window_manager.mad_transform_checker_hide_rot:
                if obj.rotation_mode == 'QUATERNION':
                    apply_button_show(self, obj, 'quat_rot')
                else:
                    apply_button_show(self, obj, 'eu_rot')
            if not context.window_manager.mad_transform_checker_hide_scale:
                apply_button_show(self, obj, 'scale')
            if not context.window_manager.mad_transform_checker_hide_loc:
                apply_button_show(self, obj, 'location')

class TCSubpanelCurves(bpy.types.Panel):
    bl_label = "Curves"
    bl_idname = "OBJECT_PT_tc_subpanel_curves"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_PT_tracheck'

    def draw(self, context):
        for obj in bpy.context.scene.objects: #each for cycle is a row
            if not obj.data:
                continue
            if obj.data.name not in bpy.data.curves:
                continue
            if obj.scale == Vector((1.0, 1.0, 1.0)) and \
            obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)) and \
            obj.rotation_euler == Euler((0.0, 0.0, 0.0)) and \
            obj.location == Vector((0.0, 0.0, 0.0)) :
                continue

            row= self.layout.row()
            select_button_show(obj, row)
            nameshow(obj, row)
            if not context.window_manager.mad_transform_checker_hide_rot:
                if obj.rotation_mode == 'QUATERNION':
                    apply_button_show(self, obj, 'quat_rot')
                else:
                    apply_button_show(self, obj, 'eu_rot')
            if not context.window_manager.mad_transform_checker_hide_scale:
                apply_button_show(self, obj, 'scale')
            if not context.window_manager.mad_transform_checker_hide_loc:
                apply_button_show(self, obj, 'location')

class TCSubpanelEmpties(bpy.types.Panel):
    bl_label = "Empties"
    bl_idname = "OBJECT_PT_tc_subpanel_empties"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_PT_tracheck'

    def draw(self, context):
        for obj in bpy.context.scene.objects: #each for cycle is a row
            if obj.data:
                continue
            if obj.scale == Vector((1.0, 1.0, 1.0)) and \
            obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)) and \
            obj.rotation_euler == Euler((0.0, 0.0, 0.0)) and \
            obj.location == Vector((0.0, 0.0, 0.0)) :
                continue

            row= self.layout.row()
            select_button_show(obj, row)
            nameshow(obj, row)
            if not context.window_manager.mad_transform_checker_hide_rot:
                if obj.rotation_mode == 'QUATERNION':
                    apply_button_show(self, obj, 'quat_rot')
                else:
                    apply_button_show(self, obj, 'eu_rot')
            if not context.window_manager.mad_transform_checker_hide_scale:
                apply_button_show(self, obj, 'scale')
            if not context.window_manager.mad_transform_checker_hide_loc:
                apply_button_show(self, obj, 'location')

class TCSubpanelGP(bpy.types.Panel):
    bl_label = "Grease pencils"
    bl_idname = "OBJECT_PT_tc_subpanel_gp"
    bl_space_type = 'VIEW_3D'
    bl_category = "MAD Animation Tools"
    bl_region_type = 'UI'
    bl_parent_id = 'OBJECT_PT_tracheck'

    def draw(self, context):
        for obj in bpy.context.scene.objects: #each for cycle is a row
            if not obj.data:
                continue
            if  obj.data.name not in bpy.data.grease_pencils:
                continue
            if obj.scale == Vector((1.0, 1.0, 1.0)) and \
            obj.rotation_quaternion == Quaternion((1.0, 0.0, 0.0, 0.0)) and \
            obj.rotation_euler == Euler((0.0, 0.0, 0.0)) and \
            obj.location == Vector((0.0, 0.0, 0.0)) :
                continue

            row= self.layout.row()
            select_button_show(obj, row)
            nameshow(obj, row)
            if not context.window_manager.mad_transform_checker_hide_rot:
                if obj.rotation_mode == 'QUATERNION':
                    apply_button_show(self, obj, 'quat_rot')
                else:
                    apply_button_show(self, obj, 'eu_rot')
            if not context.window_manager.mad_transform_checker_hide_scale:
                apply_button_show(self, obj, 'scale')
            if not context.window_manager.mad_transform_checker_hide_loc:
                apply_button_show(self, obj, 'location')


def transform_checker_register():
    bpy.types.WindowManager.mad_transform_checker_hide_loc = bpy.props.BoolProperty(
        default=True,
        name='Location', 
        description="Hide Location Checks",
        #update=
        )
    bpy.types.WindowManager.mad_transform_checker_hide_rot = bpy.props.BoolProperty(
        default=False,
        name='Rotation', 
        description="Hide Rotation Checks",
        #update=
        )
    bpy.types.WindowManager.mad_transform_checker_hide_scale = bpy.props.BoolProperty(
        default=False,
        name='Scale', 
        description="Hide Scale Checks",
        #update=
        )
    bpy.utils.register_class(ApplyFromPanel)
    bpy.utils.register_class(SelectFromPanel)
    bpy.utils.register_class(TransformCheckerPanel)
    bpy.utils.register_class(TCSubpanelNormalObjs)
    bpy.utils.register_class(TCSubpanelArmatures)
    bpy.utils.register_class(TCSubpanelEmpties)
    bpy.utils.register_class(TCSubpanelGP)
    bpy.utils.register_class(TCSubpanelCurves)


def transform_checker_unregister():
    bpy.utils.unregister_class(TCSubpanelCurves)
    bpy.utils.unregister_class(TCSubpanelGP)
    bpy.utils.unregister_class(TCSubpanelEmpties)
    bpy.utils.unregister_class(TCSubpanelArmatures)
    bpy.utils.unregister_class(TCSubpanelNormalObjs)
    bpy.utils.unregister_class(ApplyFromPanel)
    bpy.utils.unregister_class(SelectFromPanel)
    bpy.utils.unregister_class(TransformCheckerPanel)
    del bpy.types.WindowManager.mad_transform_checker_hide_scale
    del bpy.types.WindowManager.mad_transform_checker_hide_rot
    del bpy.types.WindowManager.mad_transform_checker_hide_loc


if __name__ == "__main__":
    transform_checker_register()