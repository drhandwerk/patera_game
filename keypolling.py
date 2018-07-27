from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from pyglet.window import key
from pyglet.window.key import KeyStateHandler

class MyLayer(Layer):
    is_event_handler = True

    def __init__(self):
        super(MyLayer, self).__init__()
        self.keys = KeyStateHandler()
        director.window.push_handlers(self.keys)
        self.schedule(self.act_on_input)

    def on_key_press(self, symbol, modifiers):
        print('Key press!')
        if self.keys[key.SPACE]:
            print('Space!')

    def act_on_input(self, dt):
        if self.keys[key.SPACE]:
            print('Space!')
        elif self.keys[key.UP]:
            print('Up!')
        elif self.keys[key.DOWN]:
            print('Down!')
        elif self.keys[key.LEFT]:
            print('Left!')
        elif self.keys[key.RIGHT]:
            print('Right!')

def main():
    director.init(resizable=False, width=1024, height=786)
    title_scene = Scene(MyLayer())
    director.run(title_scene)

if __name__ == '__main__':
    main()