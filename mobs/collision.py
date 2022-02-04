import pygame
import time

class Collision:
    def __init__(self, zoom, dico):
        self.zoom=zoom
        self.dico=dico
                    
    def joueur_sur_sol(self, mob, platform_only=False, ground_only=False):
        """renvoie True si les pieds du joueur est sur une plateforme ou sur le sol.
        De plus, place la coordonee en y du joueur juste au dessus de la plateforme / du sol"""
        passage_a_travers = time.time() - mob.t1_passage_a_travers_plateforme < mob.cooldown_passage_a_travers_plateforme
        
        for obj in self.dico["collision"]:
            if mob.feet.collidelist(obj) > -1:
                if not mob.is_jumping:
                    # comme le joueur est sur le sol, il peut de nouveau dash / sauter
                    mob.a_sauter = False
                    mob.a_dash = False
                return True
        return False

    def joueur_se_cogne(self, mob):
        """renvoie True si la tete du joueur est en collision avec un plafond"""
        for obj in self.dico["collision"]:
            if mob.head.collidelist(obj) > -1:
                return True
        return False
        
    def stop_if_collide(self, direction,mob):
        """fait en sorte que le joueur avance plus lorsque qu'il vance dans un mur"""
        for obj in self.dico["collision"]:
            if mob.body.collidelist(obj) > -1:
                # si le joueur va a droite en etant a gauche du mur
                # limage est plus grande que la partie visible du joueur, d'où mob.image.get_width()/2
                if direction == 'right' and mob.body_right.collidelist(obj) > -1:
                    mob.move_back()   
                    return True
                # si le joueur va a gauche en etant a droite du mur
                if direction == 'left' and mob.body_left.collidelist(obj) > -1:
                    mob.move_back()  
                    return True
        return False