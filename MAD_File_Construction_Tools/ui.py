import bpy


classes = [
    #  classes here

]

def ui_register():
    # ui property definitions here (window_manager props)
    
    for cls in classes:
        bpy.utils.register_class(cls)

def ui_unregister():
    
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # ui property deletions here 
   