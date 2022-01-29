from logging import exception
from math import ceil
from map.graph import Graphe
import pytmx
import random
import pygame

class RenderMap:
    def __init__(self, screen_width, screen_height, directory):
        """cf la documentation de pytmx"""
        self.directory=directory
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.graphe=Graphe(directory)
        # permit the visualisation of the map in the file "final_output.txt"
        self.graphe.write_matrix_txt()
        # seperate the map in 4 regions, will output it in "final_output2.txt" to permit a visualisation
        # self.graphe.seperate_by_region()
        self.graphe.write_matrix_txt(file=2)

        # informations about 1 map, concaining valides informations for every maps such as the width / tiewidht...
        self.tm = pytmx.util_pygame.load_pygame(f'{directory}\\assets\\tiled_maps\\1\\1.tmx', pixelalpha=True)

        # list containing the id of all tiles of the map
        self.liste_tile=[]
        # the +2 are because we add empty maps around the current map so the player dont see 'nothing' when he is in a border of the map
        for _ in range(self.graphe.height*2 +2):
            for _ in range(self.tm.height):
                self.liste_tile.append([])
        for line in self.liste_tile:
            for _ in range(self.graphe.width*2 +2):
                for _ in range(self.tm.width):
                    line.append(None)
                    
        # keys : map id in the form y_x when y and x are the coordinates of the map in self.liste_tile
        # value : dictionnary : keys : id of the tile value : image of the tile
        self.picture_dictionnary={}         
        self.zoom=2

        # matrix map is used to load all the map objects
        self.matrix_map=[[None for _ in range(len(self.graphe.matrix_of_node[0])*2+2)] for _ in range(len(self.graphe.matrix_of_node)*2+2)]
        
        # we dont start at 0 since the map as empty maps around it
        i=self.tm.height;z=self.tm.width
        for line in self.graphe.matrix_of_node:
            self.load_map("", i, 0, empty=True)
            self.load_map("", i+self.tm.height, 0, empty=True)
            for node in line:
                if node != None:
                    # E and S correspond to if the map has a neightboor on the right or on the bot
                    id, E, S=self.graphe.get_type_node(node)
                    if E:  self.load_map(7, i, z+self.tm.width)
                    else: self.load_map("", i, z+self.tm.width, empty=True)
                    if S:self.load_map(10, i+self.tm.height, z)
                    else: self.load_map("", i+self.tm.height, z, empty=True)
                    self.load_map(id, i, z)
                else:
                    self.load_map("", i, z, empty=True)
                    self.load_map("", i+self.tm.height, z, empty=True)
                    self.load_map("", i, z+self.tm.width, empty=True)
                # just remove it and see what happened if you dont understand why we load this map
                self.load_map("", i+self.tm.height, z+self.tm.width, empty=True)
                z+=self.tm.width*2
            i+=self.tm.height*2
            z=self.tm.width

        # loading of empty maps around the map
        z=0
        for node in self.graphe.matrix_of_node[0]:
            self.load_map("", 0, z, empty=True)
            self.load_map("", 0, z+self.tm.width, empty=True)
            z+=self.tm.width*2
                    
        self.current_map_objects={"walls":[], "grounds":[], "ceillings":[], "plateformes":[], "spawn_player":()}    
        self.current_map=[]
        self.current_map_is_wave=False
        self.coord_current_map=(0,0)
        for _ in range(self.tm.height):
            self.current_map.append([])
            for _ in range(self.tm.width):
                self.current_map[-1].append(None)
        
        self.get_first_map()["info"]["beated"]=True
        
        self.type_objects_map=[[None for _ in range(len(self.graphe.matrix_of_node[0])*2+2)] for _ in range(len(self.graphe.matrix_of_node)*2+2)]
        differents_types_random=["wave","wave","wave", "fontain", "devil", "old_men", "secret", "trap"]
        # at least one of those
        pile_types=['trader', 'boss',"wave", "fontain", "devil", "old_men", "secret", "trap"]
        c=self.get_first_map(index=True)
        self.type_objects_map[c[0]][c[1]]="spawn"
        liste=[]
        for i, line in enumerate(self.matrix_map):
            for y,map in enumerate(line):
                if map != None and list((i,y))!=list(self.get_first_map(index=True)):
                    liste.append((i,y))
        random.shuffle(liste)
        while len(liste)>0:
            if len(pile_types)>0:
                type_=pile_types.pop()
            else:
                type_=random.choice(differents_types_random)
            temp=liste.pop()
            self.type_objects_map[temp[0]][temp[1]]=type_
            
        string=""
        for line in self.type_objects_map:
            for obj in line:
                if obj != None:
                    string+=obj+"-"*(7-len(obj))+" "
                else:
                    string+="-"*7+" "
            string+="\n"
        with open(f"{self.directory}\\map\\output\\objects_maps.txt", "w") as f:
            f.write(string)
    
    def get_height(self):
        """return the height of the map in coordonates"""
        # we remove the 2 empty map that are on the top and on the bot of the map
        return len(self.liste_tile)*self.zoom*self.tm.tileheight - self.tm.tileheight*self.tm.height*2

    def get_width(self):
        """return the width of the map in coordonates"""
        # we remove the 2 empty map that are on the left and on the right of the map
        return len(self.liste_tile)*self.zoom*self.tm.tilewidth - self.tm.tilewidth*self.tm.width*2
                    
    def get_first_map(self, index=False):
        """return the if of the map of spawn in  self.matrix_map"""
        for i, line in enumerate(self.matrix_map):
            for y, map in enumerate(line):
                if map != None:
                    if not index:
                        return map
                    else:
                        return (i,y)

                    
    def load_objects_map(self,tm,  i, z, type_, choice):
        """load every objects in self.matrix_map, the differents objects re listed below in the dictionnary"""
        self.matrix_map[i//self.tm.height][z//self.tm.width]={"wall":[], "ground":[], "ceilling":[], "platform":[],"bot":{"platform_right":[], "platform_left":[], "platform_go_right":[], "platform_go_left":[]}, "spawn_player":(), "object_map":(), "object_map":(), "spawn_crab":[], "info":{"beated":True, "type":str(type_), "id": str(choice)}}
        dico=self.matrix_map[i//self.tm.height][z//self.tm.width]
        self._load_objects_map(dico, i, z, tm)
        
    def _load_objects_map(self, dico, i, z, tm):
        for obj in tm.objects:
            x=obj.x*self.zoom + z*self.tm.tilewidth*self.zoom
            y=obj.y*self.zoom + i*self.tm.tileheight*self.zoom
            if obj.type == "collision" and obj.name in ("wall", "ground", "ceilling", "platform"):
                dico[obj.name].append([pygame.Rect(x  , y , obj.width * self.zoom, obj.height * self.zoom )])             
            elif obj.type == "spawn":
                if obj.name in ["spawn_player", "object_map", "object_map"]:
                    dico[obj.name]=(x,y)
                elif obj.name in ["spawn_crab"]:
                    dico[obj.name].append((x,y))
            elif obj.type=='bot' and obj.name in ("platform_right", "platform_left", "platform_go_right", "platform_go_left"):
                dico['bot'][obj.name].append([pygame.Rect(x , y , obj.width * self.zoom , obj.height * self.zoom )])
               
    def load_map(self, id, i, z, empty=False):
        """call load_objects_map if the map is not empty and load all tiles for the map widht the coordinates i and z"""
        if not empty:
            # load a random map of the right id
            with open(f"{self.directory}\\assets\\tiled_maps\\{id}\\number_of_maps.txt") as f:
                choice=random.randint(1, int(f.readlines()[0]))
            tm = pytmx.util_pygame.load_pygame(f'{self.directory}\\assets\\tiled_maps\\{str(id)}\\{str(choice)}.tmx')
            self.load_objects_map(tm, i, z, id, choice)
        else:
            tm = pytmx.util_pygame.load_pygame(f'{self.directory}\\assets\\tiled_maps\\empty.tmx')
        ti = tm.get_tile_image_by_gid
        for a, layer in enumerate(tm.visible_layers):
            if a == 0:
                if isinstance(layer, pytmx.TiledTileLayer):
                    c=i//self.tm.height;d=z//self.tm.width
                    self.picture_dictionnary[f"{c}_{d}"]={}
                    for y, x, gid, in layer:
                        if ti(gid):
                            if self.picture_dictionnary.get(str(gid)) == None:
                                self.picture_dictionnary[f"{c}_{d}"][str(gid)] = pygame.transform.scale(ti(gid), (round(ti(gid).get_width()*self.zoom), round(ti(gid).get_height()*self.zoom)))
                            self.liste_tile[i+x][z+y]=str(gid)
    
    def is_current_map_beated(self, cam_x, cam_y):
        y_min, y_max, x_min, x_max, a, b, c, d = self.get_coord_tile_matrix(cam_x, cam_y)
        if self.matrix_map[d][c]!=None:
            return self.matrix_map[d][c]["info"]["beated"]
        return True
    
    def get_coord_tile_matrix(self, cam_x, cam_y):
        y_min = ceil((cam_y-self.screen_height/2)/(self.tm.tileheight*self.zoom))-2
        y_max = ceil((cam_y+self.screen_height/2)/(self.tm.tileheight*self.zoom))+1
        x_min = ceil((cam_x-self.screen_width/2)/(self.tm.tilewidth*self.zoom))-2
        x_max = ceil((cam_x+self.screen_width/2)/(self.tm.tilewidth*self.zoom))+1
        a=((x_max+x_min)/2)/(self.tm.width)
        b=((y_max+y_min)/2)/(self.tm.height) 
        c=((x_max+x_min)//2)//(self.tm.width)
        d=((y_max+y_min)//2)//(self.tm.height) 
        if c==0: c+=1
        if d==0: c+=1
        return y_min, y_max, x_min, x_max, a, b, c ,d
        
    def render(self, surface, cam_x, cam_y):
        """called all tick => blit only the visible tiles (compare to the position of the camera) to 'surface'"""

        # computation of the minimal and maximals coordinates that the tiles need to have to be visible
        y_min, y_max, x_min, x_max, a, b, c, d = self.get_coord_tile_matrix(cam_x, cam_y)

        # try:
        if not self.current_map_is_wave:
            #bliting those tiles in the surface in parameter
            y = y_min
            x = x_min
            for ligne in self.liste_tile[y_min:y_max]:
                for gid in ligne[x_min:x_max]:
                    if gid != None:
                        c_=y//self.tm.height;d_=x//self.tm.width
                        surface.blit(self.picture_dictionnary[f"{c_}_{d_}"][gid], (self.screen_width/2 + x*self.tm.tilewidth*self.zoom - cam_x, self.screen_height/2 + y*self.tm.tileheight*self.zoom - cam_y))
                    x+=1
                x=x_min
                y += 1

        else:
            y = 0
            x = 0
            for ligne in self.current_map:
                for tile in ligne:
                    if tile != None:
                        surface.blit(tile, (self.screen_width/2 + self.coord_current_map[0]*self.tm.width*self.tm.tilewidth*self.zoom +x*self.tm.tilewidth*self.zoom +  - cam_x, self.screen_height/2 + self.coord_current_map[1]*self.tm.height*self.tm.tileheight*self.zoom + y*self.tm.tileheight*self.zoom - cam_y))
                    x+=1
                x=0
                y += 1