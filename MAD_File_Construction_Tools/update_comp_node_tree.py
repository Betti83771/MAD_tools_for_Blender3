import bpy
from .ExtraSettingComp import *

def rename_all_paths_with_filename_2():
    """filewise"""
    to_replace_with_SCE = "SCE" + bpy.path.basename(bpy.data.filepath).split("SCE")[-1][:3]
    to_replace_with_CUT = "CUT" + bpy.path.basename(bpy.data.filepath).split("CUT")[-1][:3]
    if to_replace_with_SCE == "nopatt" or to_replace_with_CUT == "nopatt":
        return
    for scene in bpy.data.scenes:
        if scene.library != None: continue # se la scena è linkata, non fare niente
        for node in scene.node_tree.nodes: # per ogni nodo nel compositor node tree della scena:
            existing_base_path = getattr(node, "base_path", None) # prendi il base path del nodo
            if not existing_base_path: continue # se non c'è il base path, non fare più niente
            to_be_replaced_SCE_list = ["SCE" + tbr[:3] for tbr in node.base_path.split("SCE") if tbr[2].isdigit()]
            to_be_replaced_CUT_list = ["CUT" + tbr[:3] for tbr in node.base_path.split("CUT") if tbr[2].isdigit()]
            for to_be_replaced_SCE in to_be_replaced_SCE_list:
                node.base_path = node.base_path.replace(to_be_replaced_SCE, to_replace_with_SCE) 
            for to_be_replaced_CUT in to_be_replaced_CUT_list:
                node.base_path = node.base_path.replace(to_be_replaced_CUT, to_replace_with_CUT) 
            
        ren_to_be_replaced_SCE = "SCE" + scene.render.filepath.split("SCE")[-1][:3]
        ren_to_be_replaced_CUT = "CUT" + scene.render.filepath.split("CUT")[-1][:3]
        scene.render.filepath = scene.render.filepath.replace(ren_to_be_replaced_SCE, to_replace_with_SCE)
        scene.render.filepath = scene.render.filepath.replace(ren_to_be_replaced_CUT, to_replace_with_CUT)


def  overwrite_tree(self, scene_to_be_overwritten:bpy.types.Scene, scene_to_copy_from:bpy.types.Scene):
    for node in reversed(scene_to_be_overwritten.node_tree.nodes):
        scene_to_be_overwritten.node_tree.nodes.remove(node)
    links_dict_list = []
    print(scene_to_copy_from, scene_to_be_overwritten)
    for node_to_copy in scene_to_copy_from.node_tree.nodes:
        empty_dict = {}
        new_node = scene_to_be_overwritten.node_tree.nodes.new(node_to_copy.bl_idname)
        if node_to_copy.parent:
            if node_to_copy.parent.name in scene_to_be_overwritten.node_tree.nodes.keys():
                new_node.parent = scene_to_be_overwritten.node_tree.nodes[node_to_copy.parent.name]
        if new_node.bl_idname == 'CompositorNodeOutputFile':
            new_node.format.file_format = node_to_copy.format.file_format
            new_node.format.color_mode = node_to_copy.format.color_mode
            new_node.format.color_depth = node_to_copy.format.color_depth
            new_node.format.compression = node_to_copy.format.compression
            new_node.format.quality = node_to_copy.format.quality
            new_node.file_slots.clear()
            for file_slot in node_to_copy.file_slots:
                new_slot = new_node.file_slots.new(file_slot.path)
        if new_node.bl_idname == 'NodeFrame':
            new_node.text = node_to_copy.text
            new_node.label_size = node_to_copy.label_size
            new_node.use_custom_color = node_to_copy.use_custom_color
            new_node.color = node_to_copy.color
        if new_node.bl_idname == 'CompositorNodeGroup':
            new_node.name =  node_to_copy.name
            new_node.node_tree = node_to_copy.node_tree
            new_node.location = node_to_copy.location
        else:
            settings_dict = writeExtraSettings(empty_dict, node_to_copy, node_to_copy.type, "", "betti")
            new_node.name =  node_to_copy.name
            new_node.location = node_to_copy.location
            new_node.label = node_to_copy.label
            new_node.hide = settings_dict["hide"]
            new_node.height =  settings_dict["height"]
            new_node.width =  settings_dict["width"]
            
            if not settings_dict["extra_settings"][0][0] == -1: 
                readExtraSettings(settings_dict["extra_settings"], new_node)
        for i, input in enumerate(node_to_copy.inputs):
            if input.is_linked: continue
            new_node.inputs[i].default_value = input.default_value
        
        

        if(len(node_to_copy.inputs) < 1): continue
        for index, input in enumerate(node_to_copy.inputs):
            if not input.is_linked: continue
            temp_socket = str(input.links[0].from_socket.path_from_id()).split('outputs[')[-1]
            temp_socket = temp_socket.split(']')[0]
            links_dict_list.append({
                'output_node': input.links[0].from_node.name, 
                'output_socket': int(temp_socket),
                'input_node': node_to_copy.name,
                'input_socket': index,
            })
    for link in links_dict_list:
        try:  
            from_socket = scene_to_be_overwritten.node_tree.nodes[link['output_node']].outputs[link['output_socket']]
            to_socket = scene_to_be_overwritten.node_tree.nodes[link['input_node']].inputs[link['input_socket']]
            new_link = scene_to_be_overwritten.node_tree.links.new(to_socket, from_socket)
        except (IndexError, KeyError) as error: 
            self.report({'ERROR'}, f"Error during link: {error}")
            continue


    
def update_comp_node_tree_func(self, file_zero_path):
    linked_scenes = []
    local_scenes = []
    initial_linked_scenes = []
    node_groups = []
    try:
        with bpy.data.libraries.load(file_zero_path, link=True) as (data_from, data_to):
            data_to.scenes = [scene for scene in data_from.scenes if scene in bpy.data.scenes.keys()]
            data_to.node_groups = [node_group for node_group in data_from.node_groups ]
            for scene in data_to.scenes: initial_linked_scenes.append(scene)
            for node_group in data_to.node_groups: node_groups.append(node_group)
    except OSError:
        return "file_not_found"

    for scene in bpy.data.scenes:
        if scene.library != None: 
            linked_scenes.append(scene)
        else:
            local_scenes.append(scene)

    for local_scene in local_scenes:
        for linked_scene in reversed(linked_scenes):
            if local_scene.name == linked_scene.name: 
                local_scene.use_nodes = True
                overwrite_tree(self,local_scene, linked_scene)
                for node_group in bpy.data.node_groups:
                    if node_group.type != 'COMPOSITING' and node_group.name in node_groups:
                        bpy.data.node_groups.remove(node_group, do_unlink=True)
                bpy.data.scenes.remove(linked_scene, do_unlink=True)
                linked_scenes.remove(linked_scene)
                break
    rename_all_paths_with_filename_2()
    return str(initial_linked_scenes)
            
class MadUpdateComp(bpy.types.Operator):
    """Update compositor node tree from specified file zero"""
    bl_idname = "mad_file_construction.update_compositor_nodes"
    bl_label = "Update compositor node tree"
    bl_options = {'REGISTER', 'UNDO'}

    file_zero: bpy.props.StringProperty(
        name="file_zero"
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        updated_scenes = update_comp_node_tree_func(self, context.window_manager.twob_file_zero)
        if updated_scenes == "file_not_found": 
            self.report({'ERROR'}, f"File not found: {context.window_manager.twob_file_zero}")
            return {'FINISHED'}
        self.report({'INFO'}, f"Following scenes node trees updated: {updated_scenes}")
        return {'FINISHED'}

class MadRenamePaths(bpy.types.Operator):
    """Rinomina tutti i percorsi del file che contengono il nome del file base, con il nome del file corrente"""
    bl_idname = "mad_file_construction.rename_paths_filename"
    bl_label = "Rename Paths with file name"
    bl_options = {'REGISTER', 'UNDO'}

   # file_zero_name: bpy.props.StringProperty(
    #    name="file_zero"
    #)

    #@classmethod
    #def poll(cls, context):
     #   return cls.file_zero_name != ""

    def execute(self, context):
        rename_all_paths_with_filename_2()
        return{'FINISHED'}

class MadCompositingPanel(bpy.types.Panel):
    """Panel for useful operations regarding file construction"""
    bl_label = "Compositing"
    bl_idname = "MFC_PT_comppanel"
    bl_space_type = 'VIEW_3D'
    bl_category = "2B"
    bl_region_type = 'UI'
    def draw(self, context):
        layout = self.layout
        layout.row().prop(context.window_manager, "mad_file_construction_file_zero")
        layout.row().operator( "mad_file_construction.update_compositor_nodes")
        layout.row().label(text="Update the Scenes and Layers names first, otherwise this may fail.", icon='INFO')
        layout.row().separator
        layout.row().operator( "mad_file_construction.rename_paths_filename")
        layout.row().separator

classes = [
    #  classes here
    MadUpdateComp,
    MadRenamePaths,
    MadCompositingPanel
]

def update_comp_node_tree_register():
    bpy.types.WindowManager.mad_file_construction_file_zero = bpy.props.StringProperty(subtype='FILE_PATH',
                        name="File zero",
                        default=f"//..{os.sep}3D_ANM_SCE000{os.sep}3D_ANM_SCE000_CUT000.blend")
    for cls in classes:
        bpy.utils.register_class(cls)

def update_comp_node_tree_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.WindowManager.mad_file_construction_file_zero