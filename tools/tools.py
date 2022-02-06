import pygame

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
