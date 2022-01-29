import pygame
import time

class Collision:
    def __init__(self, zoom, matrix):
        self.zoom=zoom
        self.matrix_map=matrix
        self.dico_map_wave={}
        self.current_map_is_wave=False
        
    def _get_coords_maps(self, c, d):
        liste=[]    
        if self.matrix_map[d][c]!=None: liste.append((d,c))
        if c < len(self.matrix_map[0])-1 and self.matrix_map[d][c+1]!=None: 
            if d < len(self.matrix_map)-1 and self.matrix_map[d+1][c+1]!=None:
                liste.append((d+1,c+1))
            if d > 0 and self.matrix_map[d-1][c+1]!=None:
                liste.append((d-1,c+1))
            liste.append((d,c+1))
        if c > 0 and self.matrix_map[d][c-1]!=None:
            if d < len(self.matrix_map)-1 and self.matrix_map[d+1][c-1]!=None:
                liste.append((d+1,c-1))
            if d > 0 and self.matrix_map[d-1][c-1]!=None:
                liste.append((d-1,c-1))
            liste.append((d,c-1))
        if d < len(self.matrix_map)-1 and self.matrix_map[d+1][c]!=None:
            liste.append((d+1,c))
        if d > 0 and self.matrix_map[d-1][c]!=None:
            liste.append((d-1,c))
        return liste

    def _get_dico(self, coord_map):
        liste=[]
        if not self.current_map_is_wave:
            for tu in self._get_coords_maps(coord_map[0], coord_map[1]):
                liste.append(self.matrix_map[tu[0]][tu[1]])
        else:
            liste.append(self.dico_map_wave)
        return liste

    def collide_platform_bot(self,mob, direction, add=""):
        for dico in self._get_dico(mob.coord_map):
            if direction=="right" and dico["bot"][f"platform_{add}right"] != []:
                for rect in dico["bot"][f"platform_{add}right"]:
                    if mob.body.collidelist(rect) > -1:    
                        return True
            elif direction=="left" and dico["bot"][f"platform_{add}left"] != []:
                for rect in dico["bot"][f"platform_{add}left"]:
                    if mob.body.collidelist(rect) > -1:    
                        return True
        return False 
                    
    def joueur_sur_sol(self, mob, platform_only=False):
        """renvoie True si les pieds du joueur est sur une plateforme ou sur le sol.
        De plus, place la coordonee en y du joueur juste au dessus de la plateforme / du sol"""
        passage_a_travers = time.time() - mob.t1_passage_a_travers_plateforme < mob.cooldown_passage_a_travers_plateforme
        
        for dico in self._get_dico(mob.coord_map):
            if not platform_only:
                for ground in dico["ground"]:
                    if mob.feet.collidelist(ground) > -1:
                        if not mob.is_jumping_edge and not mob.is_jumping:
                            mob.position[1] = ground[0].y - mob.image.get_height() + 1 + mob.increment_foot*2
                            # comme le joueur est sur le sol, il peut de nouveau dash / sauter
                            mob.a_sauter = False
                            mob.a_dash = False
                        return True
            for plateforme in dico["platform"]:
                # and not sprite.is_sliding
                if not passage_a_travers:
                    if mob.feet.collidelist(plateforme) > -1:
                        if (mob.position[1] + mob.image.get_height() - plateforme[0].y < 20) or "crab" in mob.id:
                            if not mob.is_jumping_edge and not mob.is_jumping:
                                mob.position[1] = plateforme[0].y - mob.image.get_height() + 1 + mob.increment_foot*2
                                # comme le joueur est sur une plateforme, il peut de nouveau dash / sauter
                                mob.a_sauter = False
                                mob.a_dash = False
                            return True
        return False

    def joueur_se_cogne(self, mob):
        """renvoie True si la tete du joueur est en collision avec un plafond"""
        for dico in self._get_dico(mob.coord_map):
            for ceilling in dico["ceilling"]:
                if mob.head.collidelist(ceilling) > -1:
                    return True
        return False
        
    def stop_if_collide(self, direction,mob, head = False):
        """fait en sorte que le joueur avance plus lorsque qu'il vance dans un mur"""
        if head:rect = mob.head
        else:rect = mob.body
        for dico in self._get_dico(mob.coord_map):
            for wall in dico["wall"]:
                if rect.collidelist(wall) > -1:
                    # si le joueur va a droite en etant a gauche du mur
                    # limage est plus grande que la partie visible du joueur, d'où mob.image.get_width()/2
                    if direction == 'right' and wall[0].x > mob.position[0] + mob.complement_collide_wall_right:
                        if not mob.is_dashing: 
                            mob.move_back()   
                        return True
                    # si le joueur va a gauche en etant a droite du mur
                    if direction == 'left' and wall[0].x < mob.position[0] + mob.complement_collide_wall_left:  
                        if not mob.is_dashing: 
                            mob.move_back()  
                        return True
        return False

    def stick_to_wall(self, mob, no_head):
        wall_=None
        for dico in self._get_dico(mob.coord_map):
            for wall in dico["wall"]:
                if mob.body_grab_wall.collidelist(wall) > -1:
                    if wall_==None or wall[0].y< wall_.y:
                        wall_=wall[0]
        
        if mob.direction == "right":
            if not no_head or time.time() - mob.timer_grab_idle < mob.cooldown_grab_idle:
                mob.position[0] = wall_.x - mob.image.get_width() + mob.body_grab_wall.w*0.45
            else:
                mob.position[0] = wall_.x - mob.image.get_width() + mob.body_grab_wall.w*0.87
                mob.position[1] = wall_.y - mob.body.h*0.45
        elif mob.direction == "left":
            if not no_head or time.time() - mob.timer_grab_idle < mob.cooldown_grab_idle:
                mob.position[0] = wall_.x + wall_.w - mob.body_grab_wall.w*0.45
            else:
                mob.position[0] = wall_.x + wall_.w - mob.body_grab_wall.w*0.87
                mob.position[1] = wall_.y - mob.body.h*0.45
    
    def check_grab(self, mob):
        """Grab SSI head collide"""
        no_head=True
        if ("Wall_slide" in mob.actions and mob.action!="Wall_slide") or ("edge_idle" in mob.actions and mob.action!="edge_idle") and mob.action!="edge_climb":
            for dico in self._get_dico(mob.coord_map):
                for wall in dico["wall"]:
                    if mob.head_grab_wall.collidelist(wall) > -1:
                        no_head=False
            
            for dico in self._get_dico(mob.coord_map):
                for wall in dico["wall"]:
                    if mob.body_grab_wall.collidelist(wall) > -1:
                        if not mob.is_jumping_edge:
                            mob.fin_chute()
                            mob.debut_grab_edge(no_head)
                        self.stick_to_wall(mob, no_head)
                          
    def check_pieds_collide_wall(self, mob):
        for dico in self._get_dico(mob.coord_map):
            for wall in dico["wall"]:
                if mob.feet.collidelist(wall) > -1:
                    return True
        return False
    
    def check_tombe_ou_grab(self, mob):
        """stop le grab edge si on est plus en collision avce un mur"""
        for dico in self._get_dico(mob.coord_map):
            for wall in dico["wall"]:
                if (mob.body_grab_wall.collidelist(wall) > -1 or mob.head.collidelist(wall) > -1) and (mob.action=="Wall_slide" or mob.action=="edge_idle" or mob.action=="edge_climb"):
                    return
        mob.fin_grab_edge()