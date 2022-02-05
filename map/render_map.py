from math import ceil
import pygame

# à remplacer avec nouveau système de map sans pytmx

class RenderMap:
    def __init__(self, screen_width, screen_height, directory):
        """cf la documentation de pytmx"""
        self.directory=directory
        self.screen_width = screen_width
        self.screen_height = screen_height

        # informations about 1 map, concaining valides informations for every maps such as the width / tiewidht...
        self.tm = pytmx.util_pygame.load_pygame(f'{directory}\\assets\\tiled_maps\\1.tmx', pixelalpha=True)

        # list containing the id of all tiles of the map
        self.liste_tile=[]
        # the +2 are because we add empty maps around the current map so the player dont see 'nothing' when he is in a border of the map
        for _ in range(self.tm.height):
            self.liste_tile.append([])
        for line in self.liste_tile:
                for _ in range(self.tm.width):
                    line.append(None)
   
        self.zoom=2
        
        self.load_map()
        
        self.dico={"wall":[], "ground":[], "ceilling":[], "platform":[], "spawn_player":()}
        self._load_objects_map(self.dico, self.tm)
    
    def get_height(self):
        """return the height of the map in coordonates"""
        # we remove the 2 empty map that are on the top and on the bot of the map
        return len(self.liste_tile)*self.zoom*self.tm.tileheight

    def get_width(self):
        """return the width of the map in coordonates"""
        # we remove the 2 empty map that are on the left and on the right of the map
        return len(self.liste_tile)*self.zoom*self.tm.tilewidth
        
    def _load_objects_map(self, dico, tm):
        for obj in tm.objects:
            x=obj.x*self.zoom
            y=obj.y*self.zoom
            if obj.type == "collision" and obj.name in ("wall", "ground", "ceilling", "platform"):
                dico[obj.name].append([pygame.Rect(x  , y , obj.width * self.zoom, obj.height * self.zoom )])             
            elif obj.type == "spawn":
                if obj.name in ["spawn_player", "object_map", "object_map"]:
                    dico[obj.name]=(x,y)
                elif obj.name in ["spawn_crab"]:
                    dico[obj.name].append((x,y))
               
    def load_map(self):
        i,z=0,0
        tm = pytmx.util_pygame.load_pygame(f'{self.directory}\\assets\\tiled_maps\\1.tmx')
        ti = tm.get_tile_image_by_gid
        for a, layer in enumerate(tm.visible_layers):
            if a == 0:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for y, x, gid, in layer:
                        if ti(gid):
                            self.liste_tile[i+x][z+y]=pygame.transform.scale(ti(gid), (round(ti(gid).get_width()*self.zoom), round(ti(gid).get_height()*self.zoom)))
        
    def render(self, surface, cam_x, cam_y):
        """called all tick => blit only the visible tiles (compare to the position of the camera) to 'surface'"""

        # computation of the minimal and maximals coordinates that the tiles need to have to be visible
        y_min = ceil((cam_y-self.screen_height/2)/(self.tm.tileheight*self.zoom))-2
        y_max = ceil((cam_y+self.screen_height/2)/(self.tm.tileheight*self.zoom))+1
        x_min = ceil((cam_x-self.screen_width/2)/(self.tm.tilewidth*self.zoom))-2
        x_max = ceil((cam_x+self.screen_width/2)/(self.tm.tilewidth*self.zoom))+1
        if y_min<0: y_min=0
        elif y_min>self.tm.height: y_min=self.tm.height
        if x_min<0: x_min=0
        elif x_min>self.tm.width: x_min=self.tm.width
        #bliting those tiles in the surface in parameter
        y = y_min
        x = x_min
        for ligne in self.liste_tile[y_min:y_max]:
            for img in ligne[x_min:x_max]:
                if img != None:
                    surface.blit(img, (self.screen_width/2 + x*self.tm.tilewidth*self.zoom - cam_x, self.screen_height/2 + y*self.tm.tileheight*self.zoom - cam_y))
                x+=1
            x=x_min
            y += 1