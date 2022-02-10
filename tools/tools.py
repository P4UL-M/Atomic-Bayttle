import pygame
import json
import pathlib

class Axis:
    value = 0
    increment = 0.1
    deadzone = (0,1)
    
    @staticmethod
    def bound(x:int,bounds:tuple):
        if bounds[0]> bounds[1]:
            bounds = bounds[::-1]
        return min(max(x,bounds[0]),bounds[1])

    @staticmethod
    def sign(x):
        if x>=0:
            return 1
        else:
            return -1

    @staticmethod
    def same_sign(x,y):
        if Axis.sign(x) == Axis.sign(y):
            return True
        else:
            return False

    def update(self,x_press:bool=False,y_press:bool=False):
        if not x_press and not y_press:
            self.value = self.bound(self.value - (self.increment)*self.sign(self.value)*1.25,(0,self.sign(self.value))) 
        elif x_press and y_press:
            return
        else:
            direction = 1 if x_press else -1
            if not self.same_sign(self.value,direction):
                self.value = 0
            self.value += self.increment * direction
        self.value = self.bound(self.value,(0,self.sign(self.value)))

    def __mul__(self, other):
        return self.get()*other

    def get(self):
        if self.value==0:
            return 0    
        return self.bound(self.value,(self.deadzone[0]*self.sign(self.value),self.deadzone[1]*self.sign(self.value)))

    def __call__(self):
        return self.get()

class sprite_sheet(pygame.Surface):

    def __init__(self,path,size:tuple[int]):
        _img = pygame.image.load(path)
        super().__init__(_img.get_size(),pygame.SRCALPHA)
        self.blit(_img,(0,0))

        self.tile_size = size
        self.render_size = size
        self.x_nb = (self.get_width()//self.tile_size[0])
        self.y_nb = (self.get_height()//self.tile_size[1])

    def __getitem__(self, key):
        x = (key%self.x_nb)*self.tile_size[0]
        y = ((key//self.x_nb)%self.y_nb)*self.tile_size[1]

        _surf = pygame.Surface(self.tile_size,pygame.SRCALPHA)

        _surf.blit(self,(0,0),pygame.Rect(x,y,*self.tile_size))

        _surf = pygame.transform.scale(_surf,self.render_size)

        return _surf

    def config(self,size):
        self.render_size = size

class annimation_Manager(object):
    def __init__(self,direct_return = False):
        self.frame = 0
        self.incrementor = 1
        self.spritesheets:dict[list[sprite_sheet]] = {}
        self.links:dict[list] = {}
        self.surface:pygame.Surface = ...
        self.__loaded:sprite_sheet = None
        self.direct_return = direct_return

    def add_annimation(self,name,spritesheet:sprite_sheet,_frame:int):
        _increment = 1/_frame
        self.spritesheets[name or f"animation-{pygame.time.get_ticks()}"] = [spritesheet,_increment]

    def load(self,name):
        if name in self.spritesheets.keys():
            self.__loaded = self.spritesheets[name][0]
            self.frame = 0
            self.incrementor = self.spritesheets[name][1]
        else:
            raise AttributeError

    def __getattribute__(self, __name: str):
        if __name == "surface":
            self.frame += self.incrementor
            return self.__loaded[int(self.frame)]
        else:
            return super().__getattribute__(__name)

class Vector2:
    """
    class Vecteur 2 dimension pour un stockage des position et range plus facile qu'avec un array tuple
    """
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    def __call__(self) -> tuple:
        """return a tuple of the vector"""
        return (self.x,self.y)

class Key:
    def __init__(self,key:int,alias:int=None):
        self.key = key
        self.alias = alias
        self.name = pygame.key.name(key)
        self.name_alias = pygame.key.name(alias) if alias else None

    def is_pressed(self):
        state = pygame.key.get_pressed()
        return state[self.key] or (state[self.alias] if self.alias else False)

class Keyboard:
    right = Key(pygame.K_d,pygame.K_RIGHT)
    left = Key(pygame.K_q,pygame.K_LEFT)
    up = Key(pygame.K_z,pygame.K_UP)
    down = Key(pygame.K_s,pygame.K_DOWN)
    jump = Key(pygame.K_SPACE)
    interract = Key(pygame.K_e)
    pause = Key(pygame.K_ESCAPE)
    end_turn = Key(pygame.K_RETURN)
    inventory = Key(pygame.K_i)

    @staticmethod
    def load(path):
        touche = json.load(open(path / "data" / "settings.json"))
        for key,val in touche["keys"].items():
            if type(val)!=list:
                open(path / "data" / "log.txt","a").write("Error while loading key from the settings")
                continue
            setattr(Keyboard,key,Key(val[0], val[1] if val[1]!=-1 else None))
   
    @staticmethod
    def save(path):
        touche = json.load(open(path / "data" / "settings.json"))
        touche["keys"] = dict()
        for key,val in Keyboard.__dict__.items():
            if type(val)==Key:
                touche["keys"][key] = [getattr(Keyboard,key).key,getattr(Keyboard,key).alias or -1]
        json.dump(touche,open(path / "data" / "settings.json","w"))