import pygame
import time
import os
directory = os.path.dirname(os.path.realpath(__file__))
pygame.init()
window = pygame.display.set_mode((448*3, 252*3))
screen = pygame.Surface((448*3, 252*3))

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

class annimated_sprite_sheet(object):
    def __init__(self,direct_return = False):
        self.frame = 0
        self.incrementor = 1
        self.spritesheets:dict[list[sprite_sheet]] = {}
        self.surface:sprite_sheet = ...
        self.__loaded = None
        self.direct_return = direct_return

    def add_annimation(self,name,spritesheet:sprite_sheet,_frame:int):
        _increment = 1/_frame
        self.spritesheets[name or f"animation-{time.time()}"] = [spritesheet,_increment]

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

_bg = sprite_sheet(f"{directory}\\background_sheet.png",(448,252))
_bg.config(window.get_size())
test = annimated_sprite_sheet(direct_return=True)
test.add_annimation("test",_bg,6)
test.load("test")

def get_background():
    cloud_f_sheet = pygame.image.load(f"{directory}\\cloud_front_sheet.png").convert_alpha()
    cloud_f_sheet = pygame.transform.scale(cloud_f_sheet,(cloud_f_sheet.get_width()*3,cloud_f_sheet.get_height()*3))
    
    cloud_b_sheet = pygame.image.load(f"{directory}\\cloud_back_sheet.png").convert_alpha()
    cloud_b_sheet = pygame.transform.scale(cloud_b_sheet,(cloud_b_sheet.get_width()*3,cloud_b_sheet.get_height()*3))
    print(cloud_b_sheet.get_size(),window.get_size())
    
    background = pygame.Surface(window.get_size(),pygame.SRCALPHA)
    size = (448,252)
    
    while True:
        #background.blit(_bg[pygame.time.get_ticks()//100],(0,0))
        background.blit(test.surface,(0,0))
        background.blit(cloud_b_sheet,(-((pygame.time.get_ticks()/100)%(448*3)),0))
        background.blit(cloud_f_sheet,(-((pygame.time.get_ticks()/50)%(448*3)),0))

        yield background

class Terrain(pygame.Surface):
    def __init__(self,pos,size,**kargs):
        super().__init__(size,pygame.SRCALPHA,**kargs)
        self.blit(pygame.transform.scale(pygame.image.load("mapalternate.png"),size),(0,0))
        self.pos = pos
        self.mask = pygame.mask.from_surface(self)
        self.rect = self.get_rect(topleft = pos)
    
    def add_damage(self,pos,radius=15):
        offset = [pos[i]-self.pos[i] for i in range(len(self.pos))]
        pygame.draw.circle(self, (0,0,0,0), offset, radius)
        self.mask = pygame.mask.from_surface(self)
        
water = pygame.transform.scale(pygame.image.load("final_idle.png"),(1000,800))
ter = Terrain((window.get_width()*0.05,window.get_height()*0.1),(window.get_width()*0.9,window.get_height()*0.9))
run = True

water_y = window.get_height()
water_y_target = window.get_height()*0.85
water_annim = ["final_idle.png","final_2.png","final_idle2.png","final_1.png"]

clock = pygame.time.Clock()

_bg = get_background()

while run:
    window.blit(next(_bg),(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            position = event.pos
            ter.add_damage(position,radius=60)
            water_y_target -= 25
    mouse_pos = pygame.mouse.get_pos()
    t1 = time.time()
    if ter.rect.collidepoint(mouse_pos):
        t1 = time.time()
        mask_x = mouse_pos[0] - ter.rect.left
        mask_y = mouse_pos[1] - ter.rect.top
        if ter.mask.get_at((mask_x, mask_y)):
            window.fill((0,0,0))
    window.blit(ter.convert_alpha(),ter.pos)
    if water_y>water_y_target:
        water_y -= 0.1
    water = pygame.transform.scale(pygame.image.load(water_annim[int(time.time()%4)%(4 if water_y>water_y_target else 2)*(1 if water_y>water_y_target else 2)]),window.get_size())
    window.blit(water.convert_alpha(),(0,int(water_y)))

    clock.tick()
    #print(clock.get_fps())
    pygame.display.update()

pygame.quit()
exit()
