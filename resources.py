import pyglet
#pyglet.lib.load_library('avbin')
#pyglet.have_avbin=True

pyglet.resource.path=['data']
pyglet.resource.reindex()

player = pyglet.resource.image('playerShip1_blue.png')
enemy = pyglet.resource.image('enemyRed1.png')
logo = pyglet.resource.image('logo.png')
background = pyglet.resource.image('black.png')

PLAYERSHIPS = {'type1': {
                    'blue': pyglet.resource.image('playerShip1_blue.png'),
                    'green': pyglet.resource.image('playerShip1_green.png'),
                    'red': pyglet.resource.image('playerShip1_red.png'),
                    'orange': pyglet.resource.image('playerShip1_orange.png')               
               },
               'type2': {
                    'blue': pyglet.resource.image('playerShip2_blue.png'),
                    'green': pyglet.resource.image('playerShip2_green.png'),
                    'red': pyglet.resource.image('playerShip2_red.png'),
                    'orange': pyglet.resource.image('playerShip2_orange.png')
               }
              }

ENEMYSHIPS = {'type1': {
                    'black': pyglet.resource.image('enemyBlack1.png'),
                    'blue': pyglet.resource.image('enemyBlue1.png'),
                    'green': pyglet.resource.image('enemyGreen1.png'),
                    'red': pyglet.resource.image('enemyRed1.png')
              },
              'type2': {
                    'black': pyglet.resource.image('enemyBlack2.png'),
                    'blue': pyglet.resource.image('enemyBlue2.png'),
                    'green': pyglet.resource.image('enemyGreen2.png'),
                    'red': pyglet.resource.image('enemyRed2.png')
              },
              'type3': {
                    'black': pyglet.resource.image('enemyBlack3.png'),
                    'blue': pyglet.resource.image('enemyBlue3.png'),
                    'green': pyglet.resource.image('enemyGreen3.png'),
                    'red': pyglet.resource.image('enemyRed3.png')
              }
             }

explosion_frames = (pyglet.resource.image('explosion1a.png'),
                    pyglet.resource.image('explosion1b.png'),
                    pyglet.resource.image('explosion1c.png'),
                    pyglet.resource.image('explosion1d.png'),
                    pyglet.resource.image('explosion1e.png'),
                    pyglet.resource.image('explosion1f.png'),
                    pyglet.resource.image('explosion1g.png'),
                    pyglet.resource.image('explosion1h.png'),
                    pyglet.resource.image('explosion1i.png'))
explosion_animation = pyglet.image.Animation.from_image_sequence(explosion_frames, 0.1, False)

EXPLOSIONS = {'player_destroyed': explosion_animation,
              'enemy_destroyed': explosion_animation}

WEAPONS = {'player1': { # blue weapons
                'basic': pyglet.resource.image('laser_p1_short.png'),
                'long': pyglet. resource.image('laser_p1_long.png')
                },
           'player2': { # green weapons
                'basic': pyglet.resource.image('laser_p2_short.png'),
                'long': pyglet.resource.image('laser_p2_long.png')
                },
           'enemy': { # red weapons
                'basic': pyglet.resource.image('laser_enemy_long.png')
                }
        }


POWERUPS = {'bolt': {
                'blue': pyglet.resource.image('powerupBlue_bolt.png')
                },
            'shield': {
                'blue': pyglet.resource.image('powerupBlue_shield.png')
                },
            'star': {
                'blue': pyglet.resource.image('powerupBlue_star.png')
                }
        }

HUD = {'playerlife': {
                'blue1': pyglet.resource.image('playerLife1_blue.png'),
                'green1': pyglet.resource.image('playerLife1_green.png'),
                'orange1': pyglet.resource.image('playerLife1_orange.png')
                }
      }

STARS = (pyglet.resource.image('star1.png'), pyglet.resource.image('star2.png'), \
    pyglet.resource.image('star3.png'))
''' Sounds don't work
SOUNDS = {'laser': {
                'basic': pyglet.resource.media('sfx_laser_basic.wav', streaming=False),
                'basic2': pyglet.resource.media('sfx_laser_basic2.wav', streaming=False)
                }
         }
'''

WALLS = {'horizontal': pyglet.resource.image('horizontal_wall.png')}
