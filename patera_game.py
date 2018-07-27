import cocos, pyglet
import sys, os
import resources
import random

from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from cocos.scenes import *
from cocos.actions import *
from cocos.sprite import *
from cocos.menu import *
from cocos.text import *
from cocos.batch import *
import cocos.collision_model as cm

from pyglet.window import key
from pyglet.window.key import KeyStateHandler

''' Things to do:

    split into different files
    take out sprites being added to cm unless in update method
    fix HUD element positioning
    make fire button add player 2 if not joined
    add level ending/based on score?
    better hit boxes
    change where player 2 starts
    change collision_manager to grid
    add try catch blocks around sprite.kill() calls to stop child not found exception
    make sure powerups go away. i.e. remove their effects (maybe. or just have things last until death)
    add projectile batch for player 2 (for score reasons)
    prohibit adding of extra copies of players
    change powerups to spawn from killed enemies and move down off screen

    add vector for each enemy that determines their firing sequence.
    something like [1 2 4 1 2] will fire every 1,2,4,... seconds
    or send in randint in some range to wait until next fire. Look at 
    yield keyword and generators.
    '''


SCREEN_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = (1024, 768)
MIDDLE_OF_SCREEN = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
DIRECTIONS = [key.UP, key.DOWN, key.LEFT, key.RIGHT]
P1_START_X, P1_START_Y = (MIDDLE_OF_SCREEN[0], 100)
P2_START_X, P2_START_Y = (MIDDLE_OF_SCREEN[0], 100)

PURPLE = (136,32,201,200)
BLUE = (37,63,255,233)
GREEN = (65,220,11,104) 

UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'

PLAYER1 = 'player1'
PLAYER2 = 'player2'


'''----- Sprites -----'''
class Ship(Sprite):
    def __init__(self, image, x=0, y=0, speed=0, weapon=None, health=100, shield=0):
        super(Ship, self).__init__(image)
        self.position = (x, y)
        self.velocity = (0, 0)
        self.speed = 300
        self.weapon = weapon
        self.shield = shield
        self.cshape = cm.AARectShape(self.position, self.width//2, self.height//2)
        self.isAlive = True
        self.active_powerups = []

    def fire():
        pass

    def explode():
        pass

    def update(self, dt):
        if self.health <= 0:
            pass


class Player(Ship):
    ''' Extends Sprite class. Needs ship image and player number for laser color.'''
    def __init__(self, player_number):
        if player_number == 1:
            super(Player, self).__init__(resources.PLAYERSHIPS['type1']['blue'], P1_START_X, P1_START_Y, 400, DefaultPlayerWeapon(resources.WEAPONS['player1']['basic']))
        elif player_number == 2:
            super(Player, self).__init__(resources.PLAYERSHIPS['type1']['green'], P1_START_X, P1_START_Y, 400, DefaultPlayerWeapon(resources.WEAPONS['player2']['basic']))
        else:
            raise ValueError
        self.scale = .7
        self.maxspeed = 700

    def update(self, dt):
        if self.health <= 0:
            pass
        for powerup in self.active_powerups:
            powerup.update_bonus(dt)

    def explode(self):
        ''' kill sprite and animated death '''
        explosion = Explosion(resources.EXPLOSIONS['player_destroyed'], self.position)
        self.kill()
        #self.parent.add(explosion)
        self.parent.parent.explosion_batch.add(explosion)


class Enemy(Ship):
    def __init__(self, image, x, y, speed=300, weapon=None, health=50, shield=0):
        if weapon == None:
            super(Enemy, self).__init__(image, x, y, speed, DefaultEnemyWeapon(), health, shield)
        else:
            super(Enemy, self).__init__(image, x, y, speed, weapon, health, shield)
        self.scale = .7
    def explode(self):
        ''' kill sprite and animate death '''
        explosion = Explosion(resources.EXPLOSIONS['enemy_destroyed'], self.position)
        self.kill()
        self.parent.parent.explosion_batch.add(explosion)

class Explosion(Sprite):
    def __init__(self, animation, position):
        super(Explosion, self).__init__(animation)
        self.position = position
        self.cshape = cm.AARectShape(self.position, 0, 0)

    def on_animation_end(self):
        self.kill()

class Powerup(Sprite):
    ''' This should be a parent class for powerups. i.e. SpeedPowerup(Powerup)'''
    def __init__(self, image, x, y, timeleft=6):
        super(Powerup, self).__init__(image)
        self.position = (x, y)
        self.time_left = timeleft # amount of time player has to pick up
        self.cshape = cm.AARectShape(self.position, self.width//2, self.height//2)
        self.speed = 100
        self.shield = 50
        self.bonus_time_left = 5
        self.is_active = False
        self.player = None

    def update(self, dt):
        # animate and remove after time
        self.time_left -= 1*dt
        if int(self.time_left) == 2:
            self.do(Blink(10,2))
        if self.time_left <= 0:
            self.kill()

    def activate(self, player):
        pass

    def update_bonus(self, dt):
        pass

class SpeedPowerup(Powerup):
    def __init__(self, x, y):
        super(SpeedPowerup, self).__init__(resources.POWERUPS['bolt']['blue'], x, y, timeleft=10)
        self.original_speed = 0
        self.bonus_time_left = 3

    def activate(self, player, dt):
        self.player = player
        self.original_speed = self.player.speed
        self.player.speed += 100
        self.is_active = True
        

    def update_bonus(self, dt):
        if self.is_active:
            self.bonus_time_left -= dt
            print(self.bonus_time_left)
            if int(self.bonus_time_left) <= 0:
                print('power up ended')
                self.player.speed = self.original_speed
            

class ShieldPowerup(Powerup):
    def __init__(self, x, y):
        super(ShieldPowerup, self).__init__(resources.POWERUPS['shield']['blue'], x, y)

    def activate(self, player):
        player.shield = 100

class Projectile(Sprite):
    def __init__(self, image):
        super(Projectile, self).__init__(image)
        self.image = image
        self.speed = 0
        self.damage = 0
        self.cshape = cm.AARectShape(self.position, self.width//2, self.height//2)

    def fire(self):
        return Projectile(self.image)


class DefaultPlayerWeapon(Projectile):
    def __init__(self, image):
        super(DefaultPlayerWeapon, self).__init__(image)
        self.speed = 400
        self.velocity = (0, self.speed)
        self.damage = 10
        self.scale = .7

    def fire(self):
        #resources.SOUNDS['laser']['basic2'].play()
        return DefaultPlayerWeapon(self.image)

class DefaultEnemyWeapon(Projectile):
    def __init__(self):
        super(DefaultEnemyWeapon, self).__init__(resources.WEAPONS['enemy']['basic'])
        self.speed = 400
        self.velocity = (0, -self.speed)
        self.damage = 5
        self.scale = .7

    def fire(self):
        #resources.SOUNDS['laser']['basic'].play()
        return DefaultEnemyWeapon()

class MoveEnemy(Move):
    def __init__(self, enemy):
        random_x = random.randint(50, WINDOW_WIDTH)
        random_y = random.randint(MIDDLE_OF_SCREEN[1], WINDOW_HEIGHT-50)
        first_move = MoveTo((random_x, random_y), 1)
        main_move = MoveBy((100, 0), 1) + MoveBy((-100, 0), 1)
        last_move = MoveTo((MIDDLE_OF_SCREEN[0], -300), 1)
        enemy.do(first_move + loop(main_move,4) + last_move)
        

class Star(Sprite):
    def __init__(self, x, y, star_number=0, speed=50):
        super(Star, self).__init__(resources.STARS[star_number])
        self.star_number = star_number
        self.position = (x, y)
        self.speed = speed
        self.velocity = (0, -self.speed)
        self.scale = random.uniform(.45, .6) # vary size for depth


'''-----Layers-----'''
class MainMenu(Layer):
    def __init__(self):
        super(HelloWorld, self).__init__()
        label = cocos.text.Label('Main Menu',
                                  font_name='Verdana', 
                                  font_size=32,
                                  anchor_x='center', anchor_y='center')
        label.position = 320,240
        self.add(label)

class BackgroundDisplay(Layer):
    is_event_handler = False

    def __init__(self):
        super(BackgroundDisplay, self).__init__()
        self.star_speed = 50
        self.number_of_stars = 100
        self.star_batch = BatchNode()
        self.add(self.star_batch)

        # scheduled events
        self.schedule(self.update)

        # supply random starting positions for stars
        for star in range(self.number_of_stars):
            if random.random() < 0.8:
                star_number = 0
            else:
                star_number = 1
            star = Star(random.randint(0,WINDOW_WIDTH), random.randint(0,WINDOW_HEIGHT), star_number, self.star_speed)
            self.star_batch.add(star)
            star.do(Move())

        # background
        '''
        bg_image = Sprite(os.path.join('data',image))
        bg_image.position = MIDDLE_OF_SCREEN
        self.add(bg_image, z=0)
        '''
        # make batch of stars that just move down the screen with certain speed
        # can change speed for end of level animation 

    def update(self, dt):
        # move star to top if it's left bottom of screen
        for star in self.star_batch.get_children():
            if star.position[1] < 0:
                star.position = (random.randint(0,WINDOW_WIDTH), random.randint(WINDOW_HEIGHT+10, WINDOW_HEIGHT+40))



class HUD(Layer):
    ''' Handle display of lives, score, etc.'''
    P1_LIFE_POS = (50, WINDOW_HEIGHT-150)
    P2_LIFE_POS = (WINDOW_WIDTH-50, WINDOW_HEIGHT-150)
    P1_LIFE_SPRITE = resources.HUD['playerlife']['blue1']
    P2_LIFE_SPRITE = resources.HUD['playerlife']['green1']
    
    def __init__(self):
        super(HUD, self).__init__()
        self.player1_lives = self.last_p1_lives = 0
        self.player2_lives = self.last_p2_lives = 0
        self.player1_score = self.last_p1_score = 0
        self.player2_score = self.last_p2_score = 0
        
        self.p1_life_batch = BatchNode()
        self.p2_life_batch = BatchNode()
        self.add(self.p1_life_batch)
        self.add(self.p2_life_batch)

        # score labels
        ''' Player 1 '''
        self.p1_score_label = Label(text=str(self.player1_score),
                                font_name='Verdana',
                                font_size=28,
                                color=BLUE,
                                anchor_x='right', anchor_y='center')
        self.p1_score_label.position = (100, WINDOW_HEIGHT-100)
        self.add(self.p1_score_label)
        ''' Player 2 '''
        self.p2_score_label = Label(text=str(self.player2_score),
                                font_name='Verdana',
                                font_size=28,
                                color=GREEN,
                                anchor_x='right', anchor_y='center')
        self.p2_score_label.position = (WINDOW_WIDTH-100, WINDOW_HEIGHT-100)
        self.add(self.p2_score_label)


        # scheduled events
        self.schedule(self.update_score)
        self.schedule(self.update_lives)


    def update_score(self, dt):
        ''' Player 1 '''
        if self.last_p1_score != self.player1_score:
            self.p1_score_label.kill()
            self.p1_score_label = Label(text=str(self.player1_score),
                                font_name='Verdana',
                                font_size=28,
                                color=BLUE,
                                anchor_x='right', anchor_y='center')
            self.p1_score_label.position = (100, WINDOW_HEIGHT-100)
            self.add(self.p1_score_label)
            self.last_p1_score = self.player1_score
        ''' Player 2 '''
        if self.last_p2_score != self.player2_score:
            self.p2_score_label.kill()
            self.p2_score_label = Label(text=str(self.player2_score),
                                font_name='Verdana',
                                font_size=28,
                                color=GREEN,
                                anchor_x='right', anchor_y='center')
            self.p2_score_label.position = (WINDOW_WIDTH-100, WINDOW_HEIGHT-100)
            self.add(self.p2_score_label)
            self.last_p2_score = self.player2_score

    def update_lives(self, dt):
        ''' update and draw player lives '''
        if self.player1_lives != self.last_p1_lives:
            # remove old sprites. stack would be good for this
            for sprite in self.p1_life_batch.get_children():
                sprite.kill()
            for life in range(self.player1_lives):
                life_sprite = Sprite(HUD.P1_LIFE_SPRITE, (HUD.P1_LIFE_POS[0] + 50*life, HUD.P1_LIFE_POS[1]))
                self.p1_life_batch.add(life_sprite)
            self.last_p1_lives = self.player1_lives
        if self.player2_lives != self.last_p2_lives:
            # remove old sprites
            for sprite in self.p2_life_batch.get_children():
                sprite.kill()
            for life in range(self.player2_lives):
                life_sprite = Sprite(HUD.P2_LIFE_SPRITE, (HUD.P2_LIFE_POS[0] - 50*life, HUD.P2_LIFE_POS[1]))
                self.p2_life_batch.add(life_sprite)
            self.last_p2_lives = self.player2_lives

class ShipsDisplay(Layer):
    ''' Handle all of the ship, projectile, powerups, etc. The bulk of the game. '''
    is_event_handler = True

    def __init__(self):
        super(ShipsDisplay, self).__init__()
        # this cm is SLOW. Update to CollisinoManagerGrid()
        self.collision_manager = cm.CollisionManagerBruteForce()
        #self.collision_manager = cm.CollisionManagerGrid(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 1, 1)
        self.time_to_wait = 2

        # keep track of all BatchNodes
        self.batches = []
        
        # wall of destruction
        self.wod_batch = BatchNode()
        self.batches.append(self.wod_batch)
        self.add(self.wod_batch)
        top_wall = Sprite(resources.WALLS['horizontal'])
        top_wall.position = (WINDOW_WIDTH//2, WINDOW_HEIGHT+100)
        top_wall.cshape = cm.AARectShape(top_wall.position, top_wall.width//2, top_wall.height//2)
        bottom_wall = Sprite(resources.WALLS['horizontal'])
        bottom_wall.position = (WINDOW_WIDTH//2, -100)
        bottom_wall.cshape = cm.AARectShape(bottom_wall.position, bottom_wall.width//2, bottom_wall.height//2)
        self.wod_batch.add(top_wall)
        self.wod_batch.add(bottom_wall)
        self.collision_manager.add(top_wall)
        self.collision_manager.add(bottom_wall)

        # players
        self.player1 = None
        self.player2 = None
        self.players_are_alive = [True, False] # keep track of player status
        # need to keep player speed on press for powerups
        self.player1_sop = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        self.player2_sop = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        
        self.player_batch = BatchNode()
        self.batches.append(self.player_batch)
        self.add(self.player_batch, z=3)
        self.player_projectile_batch = BatchNode()
        self.add(self.player_projectile_batch, z=2)
        
        # enemies
        self.enemy_batch = BatchNode()
        self.batches.append(self.enemy_batch)
        self.add(self.enemy_batch, z=1)
        self.enemy_projectile_batch = BatchNode()
        self.add(self.enemy_projectile_batch, z=0)

        # explosions
        self.explosion_batch = BatchNode()
        self.batches.append(self.explosion_batch)
        self.add(self.explosion_batch, z=4) # on top of everything

        # powerups
        self.powerup_batch = BatchNode()
        self.batches.append(self.powerup_batch)
        self.add(self.powerup_batch, z=3)

        # scheduled events
        self.schedule(self.check_alive)
        self.schedule(self.remove_offscreen_sprites)
        self.schedule(self.update_ships)
        self.schedule(self.update_powerups)
        self.schedule_interval(self.spawn_random_enemy, 2)
        self.schedule_interval(self.fire_enemy_weapon, 2)
        self.schedule_interval(self.spawn_random_powerup, 30)
        #self.schedule_interval(self.count_sprites, 2)
        #self.schedule(self.act_on_input)


    def count_sprites(self, dt):
        '''for debugging'''
        num_sprites = 0
        for sprite in self.wod_batch.get_children():
            num_sprites += 1
        for sprite in self.player_batch.get_children():
            num_sprites += 1
        for sprite in self.enemy_batch.get_children():
            num_sprites += 1
        for sprite in self.enemy_projectile_batch.get_children():
            num_sprites += 1
        for sprite in self.player_projectile_batch.get_children():
            num_sprites += 1
        for sprite in self.explosion_batch.get_children():
            num_sprites += 1
        print('Number of ship layer sprites: ', num_sprites)
        print('Number of CM objs: ', len(self.collision_manager.known_objs()))
        

    def act_on_input(self, dt):
        pass

    def on_key_press(self, symbol, modifiers):

        if symbol == key.T: # test things
            self.add_player(PLAYER2)
            self.parent.HUD_layer.player2_lives = 3
            print('Player2 added')

        '''----- Player 1 controls -----'''
        if self.players_are_alive[0]: # only allow controls if player is alive
            if symbol == key.SPACE:
                # make a new projectile sprite based on player's weapon and move it 
                projectile = self.player1.weapon.fire()
                projectile.position = self.player1.position
                #self.add(projectile)
                self.player_projectile_batch.add(projectile) # for collisions
                self.collision_manager.add(projectile)
                projectile.do(Move())
            if symbol == key.UP:
                self.player1_sop['up'] = self.player1.speed
                self.player1.velocity = (self.player1.velocity[0], self.player1.velocity[1] + self.player1.speed)
            if symbol == key.DOWN:
                self.player1_sop['down'] = self.player1.speed
                self.player1.velocity = (self.player1.velocity[0], self.player1.velocity[1] - self.player1.speed)
            if symbol == key.LEFT:
                self.player1_sop['left'] = self.player1.speed
                self.player1.velocity = (self.player1.velocity[0] - self.player1.speed, self.player1.velocity[1])
            if symbol == key.RIGHT:
                self.player1_sop['right'] = self.player1.speed
                self.player1.velocity = (self.player1.velocity[0] + self.player1.speed, self.player1.velocity[1])

        '''----- Player 2 controls -----'''
        if self.players_are_alive[1]: # only allow controls if player is alive
            if symbol == key.LSHIFT:
                # make a new projectile sprite based on player's weapon and move it 
                projectile = self.player2.weapon.fire()
                projectile.position = self.player2.position
                #self.add(projectile)
                self.player_projectile_batch.add(projectile) # for collisions
                self.collision_manager.add(projectile)
                projectile.do(Move())
            if symbol == key.W:
                self.player2_sop['up'] = self.player2.speed
                self.player2.velocity = (self.player2.velocity[0], self.player2.velocity[1] + self.player2.speed)
            if symbol == key.S:
                self.player2_sop['down'] = self.player2.speed
                self.player2.velocity = (self.player2.velocity[0], self.player2.velocity[1] - self.player2.speed)
            if symbol == key.A:
                self.player2_sop['left'] = self.player2.speed
                self.player2.velocity = (self.player2.velocity[0] - self.player2.speed, self.player2.velocity[1])
            if symbol == key.D:
                self.player2_sop['right'] = self.player2.speed
                self.player2.velocity = (self.player2.velocity[0] + self.player2.speed, self.player2.velocity[1])


    def on_key_release(self, symbol, modifiers):
        '''----- Player 1 controls -----'''
        if symbol == key.SPACE:
            pass
        # Return ship velocity to pre-keypress levels
        if self.players_are_alive[0]:
            if symbol == key.UP:
                self.player1.velocity = (self.player1.velocity[0], self.player1.velocity[1] - self.player1_sop['up'])
            if symbol == key.DOWN:
                self.player1.velocity = (self.player1.velocity[0], self.player1.velocity[1] + self.player1_sop['down'])
            if symbol == key.LEFT:
                self.player1.velocity = (self.player1.velocity[0] + self.player1_sop['left'], self.player1.velocity[1])
            if symbol == key.RIGHT:
                self.player1.velocity = (self.player1.velocity[0] - self.player1_sop['right'], self.player1.velocity[1])

        '''----- Player 2 controls -----'''
        # Return ship velocity to pre-keypress levels
        if self.players_are_alive[1]:
            if symbol == key.W:
                self.player2.velocity = (self.player2.velocity[0], self.player2.velocity[1] - self.player2_sop['up'])
            if symbol == key.S:
                self.player2.velocity = (self.player2.velocity[0], self.player2.velocity[1] + self.player2_sop['down'])
            if symbol == key.A:
                self.player2.velocity = (self.player2.velocity[0] + self.player2_sop['left'], self.player2.velocity[1])
            if symbol == key.D:
                self.player2.velocity = (self.player2.velocity[0] - self.player2_sop['right'], self.player2.velocity[1])


    def display_message(self, message):
        message_text = Label(message,
                            font_name='Verdana',
                            font_size=32,
                            color=(136,32,201,200),
                            anchor_x='center', anchor_y='center')
        message_text.position = (512,384)
        self.add(message_text)

    def check_alive(self, dt):
        ''' switch to game over scene if players have no lives left'''
        # update players_are_alive based on HUD info
        if self.parent.HUD_layer.player1_lives <= 0:
            self.players_are_alive[0] = False
        if self.parent.HUD_layer.player2_lives <= 0:
            self.players_are_alive[1] = False
        if not any(self.players_are_alive):
            director.replace(FadeTransition(GameOverScene(), duration=5))
            self.players_are_alive[0] = True # so this runs only once

    def add_player(self, player):
        if player == PLAYER1:
            self.player1 = Player(1) 
            #self.add(self.player1)
            self.players_are_alive[0] = True
            self.player_batch.add(self.player1)
            self.collision_manager.add(self.player1)
            self.player1.do(BoundedMove(WINDOW_WIDTH, WINDOW_HEIGHT))
            
        if player == PLAYER2:
            self.player2 = Player(2)
            #self.add(self.player2)
            self.players_are_alive[1] = True
            self.player_batch.add(self.player2)
            self.collision_manager.add(self.player2)
            self.player2.do(BoundedMove(WINDOW_WIDTH, WINDOW_HEIGHT))

    def remove_offscreen_sprites(self, dt):
        ''' remove enemies and projectiles that go off screen by detecting collision with off-screen walls'''
        # remove enemies
        for enemy in self.enemy_batch.get_children():
            for wall in set(self.wod_batch.get_children()).intersection(self.collision_manager.objs_colliding(enemy)):
                enemy.kill()
                break # only needs to collide with one wall

        # remove enemy projectiles
        for projectile in self.enemy_projectile_batch.get_children():
            for wall in set(self.wod_batch.get_children()).intersection(self.collision_manager.objs_colliding(projectile)):
                projectile.kill()
                break # only needs to collide with one wall

        # remove player projectiles
        for projectile in self.player_projectile_batch.get_children():
            for wall in set(self.wod_batch.get_children()).intersection(self.collision_manager.objs_colliding(projectile)):
                projectile.kill()
                break # only needs to collide with one wall


    def update_ships(self, dt):
        ''' updates collision_manager, determines hits, removes sprites '''
        # clear cm
        self.collision_manager.clear()
        # update cshapes due to movement
        for player in self.player_batch.get_children():
            player.cshape.center = player.position
        for projectile in self.player_projectile_batch.get_children():
            projectile.cshape.center = projectile.position
        for enemy in self.enemy_batch.get_children():
            enemy.cshape.center = enemy.position
        for projectile in self.enemy_projectile_batch.get_children():
            projectile.cshape.center = projectile.position
        # add sprites to cm
        for batch in self.batches:
            for sprite in batch.get_children():
                self.collision_manager.add(sprite)


        # determine if player hit by enemy projectile
        for projectile in self.enemy_projectile_batch.get_children():
            for player in set(self.player_batch.get_children()).intersection(self.collision_manager.objs_colliding(projectile)):
                projectile.kill()
                if player == self.player1:
                    #self.players_are_alive[0] = False
                    self.parent.HUD_layer.player1_lives -= 1
                    player.explode()
                    if self.parent.HUD_layer.player1_lives > 0:
                        # need to ignore key_press action before death
                        self.player1_sop = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
                        self.add_player(PLAYER1)
                elif player == self.player2:
                    #self.players_are_alive[1] = False
                    self.parent.HUD_layer.player2_lives -= 1
                    player.explode()
                    if self.parent.HUD_layer.player2_lives > 0:
                        self.player2_sop = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
                        self.add_player(PLAYER2)

        # determine if enemy hit by player projectile
        for projectile in self.player_projectile_batch.get_children():
            for enemy in set(self.enemy_batch.get_children()).intersection(self.collision_manager.objs_colliding(projectile)):
                enemy.explode()
                self.parent.HUD_layer.player1_score += 100
                try:
                    projectile.kill() # do enemy damage stuff
                except Exception as inst: 
                    print(type(inst))
                    print(inst.args)
                    print(inst)
        
    ''' Enemy actions '''    
    def spawn_random_enemy(self, dt):
        # spawn group of enemies of random size determined by level
        number_to_spawn = random.randint(1,5)
        for i in range(number_to_spawn):
            # Spawn basic enemy at random location in top half of screen
            self.add_enemy(resources.ENEMYSHIPS['type1']['black'], random.randint(0,WINDOW_WIDTH), random.randint(WINDOW_HEIGHT+10, WINDOW_HEIGHT+30))

    def add_enemy(self, image, x, y):
        #move = MoveBy((100, 0), 2)
        enemy = Enemy(image, x, y)
        self.enemy_batch.add(enemy)
        self.collision_manager.add(enemy)
        #enemy.do(Repeat(move + Reverse(move)))
        MoveEnemy(enemy)

    def fire_enemy_weapon(self, dt):
        for enemy in self.enemy_batch.get_children():
            projectile = enemy.weapon.fire()
            projectile.position = enemy.position
            self.enemy_projectile_batch.add(projectile) # for collisions
            self.collision_manager.add(projectile)
            projectile.do(Move())
            
    ''' Powerup actions '''            
    def spawn_random_powerup(self, dt):
        self.add_powerup(resources.POWERUPS['star']['blue'], random.randint(0,WINDOW_WIDTH), random.randint(50, MIDDLE_OF_SCREEN[1]))

    def add_powerup(self, image, x, y):
        powerup = SpeedPowerup(x, y)
        self.powerup_batch.add(powerup)
        self.collision_manager.add(powerup)
        
    def update_powerups(self, dt):
        for powerup in self.powerup_batch.get_children():
            # update powerup timer
            powerup.update(dt)
            # see if player collected
            for player in set(self.player_batch.get_children()).intersection(self.collision_manager.objs_colliding(powerup)):
                powerup.activate(player, dt)
                powerup.kill()

        #remove this when done testing
        self.speed_text = self.player1.speed
    

class MessageDisplay(Layer):
    is_event_handler = True

    def __init__(self, message):
        super(MessageDisplay, self).__init__()
        self.message = message

        if self.message == 'title':
            logo = Sprite(resources.logo)
            logo.scale = .7
            logo.position = MIDDLE_OF_SCREEN
            self.add(logo, z=1)

            # notification
            start_text = Label('Press Any Key',
                                font_name='Verdana',
                                font_size=32,
                                color=(136,32,201,200),
                                anchor_x='center', anchor_y='center')
            start_text.position = (MIDDLE_OF_SCREEN[0], 100)
            self.add(start_text,z=2)

            # do stuff
            pulse = ScaleBy(scale=1.1, duration=.7)
            start_text.do(Repeat(pulse + Reverse(pulse)))

        elif self.message == 'gameover':
            game_over_text = Label('GAME OVER',
                            font_name='Verdana',
                            font_size=44,
                            color=(136,32,201,200),
                            anchor_x='center', anchor_y='center')
            game_over_text.position = MIDDLE_OF_SCREEN
            self.add(game_over_text)

            # Animate game over text
            pulse = ScaleBy(scale=1.1, duration=.7)
            game_over_text.do(Repeat(pulse + Reverse(pulse)))
        
        else:
            pass

    def on_key_release(self, symbol, modifiers):
        if self.message == 'title':
            director.replace(EnvelopeTransition(Level1(),duration=1))
        if self.message == 'gameover' and self.parent.can_continute:
            director.replace(EnvelopeTransition(Level1(),duration=1))

'''----- Scenes -----''' 
class GameOverScene(Scene):
    is_event_handler = True

    def __init__(self):
        super(GameOverScene, self).__init__()
        self.can_continute = False
        self.time_elapsed = 0

        self.schedule(self.enable_can_continue)

        # make message layer
        self.message_layer = MessageDisplay('gameover')
        self.add(self.message_layer)

    def enable_can_continue(self, dt):
        ''' Wait a bit to take keypresses.'''
        self.time_elapsed += dt
        if int(self.time_elapsed >=2):
            self.can_continute = True


class Level(Scene):
    is_event_handler = True

    def __init__(self):
        super(Level, self).__init__()

  
    def goto_next_level(self):
        pass # director change to level 2

class Level1(Level):
    is_event_handler = True

    def __init__(self):
        super(Level1, self).__init__()
        self.start_text = Label('Level 1',
                            font_name='Verdana',
                            font_size=32,
                            color=(136,32,201,200),
                            anchor_x='center', anchor_y='center')
        self.start_text.position = MIDDLE_OF_SCREEN
        self.add(self.start_text,z=4)
        self.start_text.do(ScaleBy(scale=1.3, duration=.5) + FadeOut(3))

        # make background layer
        self.background_layer = BackgroundDisplay()
        self.add(self.background_layer, z=0)

       
        # make HUD layer
        self.HUD_layer = HUD()
        self.add(self.HUD_layer, z=3)

        # make ship layer
        self.ship_layer = ShipsDisplay()
        self.add(self.ship_layer, z=2)
        self.ship_layer.add_player(PLAYER1)
        self.HUD_layer.player1_lives = 3

        
        


def main():
    director.init(resizable=False, width=1024, height=786)
    director.show_FPS = True
    title_scene = Scene(MessageDisplay('title'))
    director.run(title_scene)

if __name__ == '__main__':
    main()