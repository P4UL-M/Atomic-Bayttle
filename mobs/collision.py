import pygame
import time

class Collision:
    def __init__(self, zoom, map):
        self.zoom=zoom
        self.map=map
                    
    def joueur_sur_sol(self, mob, first=False):
        """renvoie True si les pieds du joueur est sur une plateforme ou sur le sol.
        De plus, place la coordonee en y du joueur juste au dessus de la plateforme / du sol"""
        passage_a_travers = time.time() - mob.t1_passage_a_travers_plateforme < mob.cooldown_passage_a_travers_plateforme
        #pygame.sprite.collide_mask(self.render.map, self.player)
        # for obj in self.dico["collision"]:
        #     if mob.feet.collidelist(obj) > -1:
        #         if not mob.is_jumping:
        #             # comme le joueur est sur le sol, il peut de nouveau dash / sauter
        #             mob.a_sauter = False
        #             mob.a_dash = False
        #         return True
        if pygame.sprite.collide_mask(self.map, mob.feet_mask):
            if not mob.is_jumping:
                mob.a_sauter = False
            if first:
                while pygame.sprite.collide_mask(self.map, mob.feet_mask):
                    mob.position[1]-=1
                    mob.update_coord_rect()
                mob.position[1]+=2
                
                mob.update_coord_rect()
            if mob.position[1]%2!=0:
                mob.position[1]+=2+mob.position[1]%2
            return True
        return False

    def joueur_se_cogne(self, mob):
        """renvoie True si la tete du joueur est en collision avec un plafond"""
        if pygame.sprite.collide_mask(self.map, mob.head_mask):
            return True
        return False
        
    def stop_if_collide(self, direction,mob):
        """fait en sorte que le joueur avance plus lorsque qu'il vance dans un mur"""
        if pygame.sprite.collide_mask(self.map, mob.body_mask):
            # si le joueur va a droite en etant a gauche du mur
            # limage est plus grande que la partie visible du joueur, d'où mob.image.get_width()/2
            if direction == 'right' and pygame.sprite.collide_mask(self.map, mob.body_right_mask):
                mob.move_back()   
                return True
            # si le joueur va a gauche en etant a droite du mur
            if direction == 'left' and pygame.sprite.collide_mask(self.map, mob.body_left_mask):
                mob.move_back()  
                return True
        return False