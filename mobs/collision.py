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
        
        if not platform_only:
            for ground in self.dico["ground"]:
                if mob.feet.collidelist(ground) > -1:
                    if not mob.is_jumping_edge and not mob.is_jumping:
                        mob.position[1] = ground[0].y - mob.image.get_height() + 1 + mob.increment_foot*2
                        # comme le joueur est sur le sol, il peut de nouveau dash / sauter
                        mob.a_sauter = False
                        mob.a_dash = False
                    return True
        if not ground_only:
            for plateforme in self.dico["platform"]:
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
        for ceilling in self.dico["ceilling"]:
            if mob.head.collidelist(ceilling) > -1:
                return True
        return False
        
    def stop_if_collide(self, direction,mob, head = False):
        """fait en sorte que le joueur avance plus lorsque qu'il vance dans un mur"""
        if head:rect = mob.head
        else:rect = mob.body
        for wall in self.dico["wall"]:
            if rect.collidelist(wall) > -1:
                # si le joueur va a droite en etant a gauche du mur
                # limage est plus grande que la partie visible du joueur, d'où mob.image.get_width()/2
                if direction == 'right' and wall[0].x > mob.position[0] + mob.complement_collide_wall_right: 
                    mob.move_back()   
                    return True
                # si le joueur va a gauche en etant a droite du mur
                if direction == 'left' and wall[0].x < mob.position[0] + mob.complement_collide_wall_left:  
                    mob.move_back()  
                    return True
        return False