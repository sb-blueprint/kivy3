
import os
import math
from kivy.app import App
from kivy.clock import Clock

from kivy3 import Scene, Renderer, PerspectiveCamera, Geometry, Vector3, Material, Mesh, Face3
from kivy3.core.line2 import Line2
from kivy3.extras.geometries import BoxGeometry
from kivy3.extras.grid import GridGeometry
from kivy3.loaders import OBJLoader
from kivy.uix.floatlayout import FloatLayout
from kivy3.objects.lines import Lines


class MainApp(App):

    def build(self):
        self.renderer = Renderer()
        scene = Scene()
        camera = PerspectiveCamera(45, 1, 0.1, 2500)
        self.renderer.set_clear_color((.2, .2, .2, 1.))

        self.camera = camera
        root = ObjectTrackball(camera, 10)

        # add a cube to the environment as an example
        # NOTE: the grid will be rendered without transparency if it
        # is added before the box.
        # This may be because the shader is not called until a 'triangles' mesh is
        # rendered? Hence the Fragment Shader has not yet been called?
        geometry = BoxGeometry(1, 1, 1)
        material = Material(color=(1., 1., 1.), diffuse=(1., 1., 1.),
                            specular=(.35, .35, .35))
        obj = Mesh(geometry, material)
        scene.add(obj)

        # create a grid on the xz plane
        geometry = GridGeometry(size=(30, 30), spacing=1)
        material = Material(color=(1., 1., 1.), diffuse=(1., 1., 1.),
                            specular=(.35, .35, .35), transparency=.1)
        lines = Lines(geometry, material)
        lines.rotation.x = 90
        scene.add(lines)

        self.renderer.render(scene, camera)
        self.renderer.main_light.intensity = 500

        root.add_widget(self.renderer)
        self.renderer.bind(size=self._adjust_aspect)
        return root

    def _adjust_aspect(self, inst, val):
        rsize = self.renderer.size
        aspect = rsize[0] / float(rsize[1])
        self.renderer.camera.aspect = aspect


class ObjectTrackball(FloatLayout):

    def __init__(self, camera, radius, *args, **kw):
        super(ObjectTrackball, self).__init__(*args, **kw)
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

    def on_touch_up(self, touch):
        touch.ungrab(self)
        self._touches.remove(touch)

    def on_touch_move(self, touch):
        if touch in self._touches and touch.grab_current == self:
            if len(self._touches) == 1:
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


if __name__ == '__main__':
    MainApp().run()
