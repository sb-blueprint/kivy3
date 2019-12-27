
import os
import math
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.stencil_instructions import StencilPush, StencilPop
from kivy.uix.button import Button

from kivy3 import Scene, Renderer, PerspectiveCamera, Geometry, Vector3, Material, Mesh, Face3
from kivy3.core.line2 import Line2
from kivy3.extras.geometries import BoxGeometry
from kivy3.extras.grid import GridGeometry
from kivy3.loaders import OBJLoader
from kivy.uix.floatlayout import FloatLayout
from kivy3.objects.lines import Lines

# Resource paths
_this_path = os.path.dirname(os.path.realpath(__file__))
shader_file = os.path.join(_this_path, "./blinnphong.glsl")

clear_color = (.2, .2, .2, 1.)


class MainApp(App):

    def build(self):
        self.renderer = Renderer(shader_file=shader_file)
        scene = Scene()
        camera = PerspectiveCamera(45, 1, 0.1, 2500)
        self.renderer.set_clear_color(clear_color)

        self.camera = camera

        root = ObjectTrackball(camera, 10, self.renderer)

        id_color = (0, 0, 0x7F)
        geometry = BoxGeometry(1, 1, 1)
        material = Material(color=(1., 1., 1.), diffuse=(1., 1., 1.),
                            specular=(.35, .35, .35), id_color=id_color,
                            shininess=1.)
        obj = Mesh(geometry, material)
        scene.add(obj)
        root.object_list.append({'id': id_color, 'obj': obj})

        id_color = (0, 0x7F, 0)
        geometry = BoxGeometry(1, 1, 1)
        material = Material(color=(0., 0., 1.), diffuse=(0., 0., 1.),
                            specular=(.35, .35, .35), id_color=id_color,
                            shininess=1.)
        obj = Mesh(geometry, material)
        obj.position.x = 2
        scene.add(obj)
        root.object_list.append({'id': id_color, 'obj': obj})

        # create a grid on the xz plane
        geometry = GridGeometry(size=(30, 30), spacing=1)
        material = Material(color=(1., 1., 1.), diffuse=(1., 1., 1.),
                            specular=(.35, .35, .35), transparency=.5)
        lines = Lines(geometry, material)
        lines.rotation.x = 90
        scene.add(lines)

        self.renderer.render(scene, camera)
        self.renderer.main_light.intensity = 1000
        self.renderer.main_light.pos = (10, 1, -10)

        root.add_widget(self.renderer)
        self.renderer.bind(size=self._adjust_aspect)

        return root

    def _adjust_aspect(self, inst, val):
        rsize = self.renderer.size
        aspect = rsize[0] / float(rsize[1])
        self.renderer.camera.aspect = aspect


class ObjectTrackball(FloatLayout):
    selected_object = None
    object_list = []

    def __init__(self, camera, radius, renderer, *args, **kw):
        super(ObjectTrackball, self).__init__(*args, **kw)
        self.renderer = renderer
        self.camera = camera
        self.radius = radius
        self.phi = 90
        self.theta = 0
        self._touches = []
        self.camera.pos.z = radius
        camera.look_at((0, 0, 0))

    def define_rotate_angle(self, touch):
        theta_angle = (touch.dx / self.width) * -360
        phi_angle = (touch.dy / self.height) * 360
        return phi_angle, theta_angle

    def on_touch_down(self, touch):
        touch.grab(self)
        self._touches.append(touch)

        self.renderer.fbo.shader.source = 'select_mode.glsl'
        self.renderer.set_clear_color((0., 0., 0., 0.))
        self.renderer.fbo.ask_update()
        self.renderer.fbo.draw()
        print(self.renderer.fbo.get_pixel_color(touch.x, touch.y))

        selection_id = self.renderer.fbo.get_pixel_color(touch.x, touch.y)
        print(self.get_selected_object(selection_id))

        self.renderer.fbo.shader.source = shader_file
        self.renderer.set_clear_color(clear_color)
        self.renderer.fbo.ask_update()
        self.renderer.fbo.draw()

    def on_touch_up(self, touch):
        touch.ungrab(self)
        self._touches.remove(touch)

    def on_touch_move(self, touch):
        if touch in self._touches and touch.grab_current == self:
            if self.selected_object:
                #TODO: Solve for moving the objects in a sensible axis based on camera angle
                self.selected_object.position.x += (touch.dx * 0.01)
                self.selected_object.position.y += (touch.dy * 0.01)
            elif len(self._touches) == 1:
                self.do_rotate(touch)
            elif len(self._touches) == 2:
                pass

    def do_rotate(self, touch):
        d_phi, d_theta = self.define_rotate_angle(touch)
        self.phi += d_phi
        self.theta += d_theta

        _phi = math.radians(self.phi)
        _theta = math.radians(self.theta)
        z = self.radius * math.cos(_theta) * math.sin(_phi)
        x = self.radius * math.sin(_theta) * math.sin(_phi)
        y = self.radius * math.cos(_phi)
        self.camera.pos = x, y, z
        self.camera.look_at((0, 0, 0))

    def get_selected_object(self, selected_id):
        for obj in self.object_list:
            if list(obj['id'][0:3]) == selected_id[0:3]:
                self.selected_object = obj['obj']
                return self.selected_object
        self.selected_object = None


if __name__ == '__main__':
    MainApp().run()