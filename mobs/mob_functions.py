import time

def pressed_left(liste_mob, collision):
    for mob in liste_mob:
        mob.save_location()
        bool = collision.joueur_sur_sol(mob)
        if bool:
            mob.move_left_right("left", pieds_sur_sol=True)
        # si le joueur ne dash pas et est en lair
        else:
            mob.move_left_right("left")
        collision.stop_if_collide("left", mob)

def pressed_right(liste_mob, collision):
    for mob in liste_mob:
        mob.save_location()
        bool = collision.joueur_sur_sol(mob)
        if bool:
            mob.move_left_right("right", pieds_sur_sol=True)
        # si le joueur ne dash pas et est en lair
        else:
            mob.move_left_right("right")
    
        collision.stop_if_collide("right", mob)
                
def pressed_up(liste_mob, down, left, right, pressed_up_bool, collision):
    for mob in liste_mob:
        if not down and not mob.action_image=="hurt" and (collision.joueur_sur_sol(mob) or time.time() - mob.timer_cooldown_able_to_jump < mob.cooldown_able_to_jump) \
            and not mob.a_sauter and time.time() - mob.timer_cooldown_next_jump > mob.cooldown_next_jump \
            and not mob.is_attacking:
            mob.debut_saut()

def pressed_attack(liste_mob):
    for mob in liste_mob:
        if "attack" in mob.actions:
            if (not mob.is_jumping or mob.can_attack_while_jump) and not mob.is_attacking and not mob.action_image=="hurt":
                if (not mob.is_falling and not mob.action == "jump") or not mob.has_air_attack:
                    if time.time()-mob.timer_attack < mob.cooldown_attack and not mob.a_attaquer2:
                        mob.attack2()
                    else:
                        mob.debut_attack()
                elif time.time() - mob.timer_attack_aerienne > mob.cooldown_attack_aerienne:
                    mob.debut_air_attack()
                
def pressed_down(liste_mob, collision):
    for mob in liste_mob:
        # le joueur passe a travers les plateformes pendant X secondes
        mob.t1_passage_a_travers_plateforme = time.time()
        
def handle_input_ralentissement(mob):
    # si le joueur avance pas, il deviens idle
    if mob.action != "fall" and mob.action != "up_to_fall":
        if mob.action == "run" and mob.ralentit_bool == False:
            mob.debut_ralentissement()
        # si mob.ralentissement na pas ete appele, mob.ralentissement aura aucun effet
        # => donc le ralentissement a lieu que quand le joueur arrete de courir
        mob.ralentissement()
        
def pressed_interact(liste_mob, group_object):
    for mob in liste_mob:
        if mob.id=='player1':
            for sprite in group_object:
                if sprite.rect.collidelist([mob.body]) > -1:
                    return sprite.id