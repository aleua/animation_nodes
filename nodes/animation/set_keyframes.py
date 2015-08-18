import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import propertyChanged

pathTypes = ("Custom", "Location", "Rotation", "Scale", "LocRotScale")
pathTypeItems = [(pathType, pathType, "") for pathType in pathTypes]

class an_KeyframePath(bpy.types.PropertyGroup):
    path = StringProperty(default = "", update = propertyChanged, description = "Path to the property")
    index = IntProperty(default = -1, update = propertyChanged, min = -1, soft_max = 2, description = "Used index if the path points to an array (-1 will set a keyframe on every index)")

class SetKeyframesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetKeyframesNode"
    bl_label = "Set Keyframes"

    inputNames = { "Enable" : "enable",
                   "Set Keyframe" : "setKeyframe",
                   "Remove Unwanted" : "removeUnwanted",
                   "Object" : "object" }
    outputNames = {}

    paths = CollectionProperty(type = an_KeyframePath)

    selectedPathType = EnumProperty(default = "Location", items = pathTypeItems, name = "Path Type")
    attributePath = StringProperty(default = "", name = "Attribute Path")

    def create(self):
        self.width = 200
        self.inputs.new("an_BooleanSocket", "Enable").value = False
        self.inputs.new("an_BooleanSocket", "Set Keyframe")
        self.inputs.new("an_BooleanSocket", "Remove Unwanted")
        self.inputs.new("an_ObjectSocket", "Object")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "selectedPathType", text = "")
        self.callFunctionFromUI(row, "addKeyframePath", icon = "PLUS")

        col = layout.column(align = True)
        for i, item in enumerate(self.paths):
            row = col.row(align = True)
            split = row.split(align = True, percentage = 0.7)
            split.prop(item, "path", text = "")
            split.prop(item, "index", text = "")
            self.callFunctionFromUI(row, "removeItemFromList", icon = "X", data = str(i))

    def execute(self, enable, setKeyframe, removeUnwanted, object):
        if not enable: return
        frame = bpy.context.scene.frame_current
        if setKeyframe:
            for item in self.paths:
                try:
                    obj, path = self.getResolvedNestedPath(object, item.path)
                    obj.keyframe_insert(data_path = path, frame = frame, index = item.index)
                except: pass
        elif removeUnwanted:
            for item in self.paths:
                try:
                    obj, path = self.getResolvedNestedPath(object, item.path)
                    obj.keyframe_delete(data_path = path, frame = frame, index = item.index)
                except: pass

    def getResolvedNestedPath(self, object, path):
        index = path.find(".")
        if index == -1: return object, path
        else:
            data = eval("object." + path[:index])
            return data, path[index+1:]

    def newPath(self, path, index = -1):
        item = self.paths.add()
        item.path = path
        item.index = index

    def addKeyframePath(self):
        type = self.selectedPathType
        if type == "Custom": self.newPath("")
        elif type == "Location": self.newPath("location")
        elif type == "Rotation": self.newPath("rotation_euler")
        elif type == "Scale": self.newPath("scale")
        elif type == "LocRotScale":
            self.newPath("location")
            self.newPath("rotation_euler")
            self.newPath("scale")

    def removeItemFromList(self, strIndex):
        self.paths.remove(int(strIndex))
