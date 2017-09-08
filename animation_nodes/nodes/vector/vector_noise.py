import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... libs.FastNoiseSIMD import Noise3DNodeBase
from ... data_structures import DoubleList



class VectorNoiseNode(bpy.types.Node, AnimationNode, Noise3DNodeBase):
    bl_idname = "an_VectorNoiseNode"
    bl_label = "Vector Noise"

    def create(self):
        self.newInput("Vector List", "Vectors", "vectors")
        self.createSettingsInputs()
        self.newOutput("Float List", "Value", "value")

    def draw(self, layout):
        self.drawNoiseSettings(layout)

    def execute(self, vectors, *settings):
        noise = self.calculateNoise(vectors, settings)
        return DoubleList.fromValues(noise)
