import pygame
import main

def test_player_double_jump_mechanics():
    # Arrange: Przygotuj gracza, wy³¹cz dŸwiêki skoku
    pygame.mixer.init()
    main.jump_sfx = None 
    
    player = main.Player((0, 0), "Ninja Frog")
    
    # Symulujemy l¹dowanie gracza na platformie
    player.on_ground = True
    player.can_double_jump = False
    
    # Act 1: Pierwszy skok z ziemi
    player.handle_jump()
    
    # Assert 1: Gracz dosta³ ujemn¹ prêdkoœæ Y (skok w górê), oderwa³ siê od ziemi i dosta³ pozwolenie na drugi skok
    assert player.velocity.y == player.jump_speed
    assert player.on_ground == False
    assert player.can_double_jump == True
    
    # Act 2: Gracz jest w powietrzu i wciska przycisk skoku po raz drugi
    player.handle_jump()
    
    # Assert 2: Aktywuje siê podwójny skok, uruchamia siê animacja "flip" (salto)
    assert player.velocity.y == player.jump_speed
    assert player.can_double_jump == False
    assert player.is_doing_flip == True
    
    # Act 3: Próba trzeciego skoku (nie powinna siê udaæ)
    player.velocity.y = 0  # Zatrzymujemy go w powietrzu dla testu
    player.handle_jump()
    
    # Assert 3: Nic siê nie zmieni³o, gracz musi wyl¹dowaæ
    assert player.velocity.y == 0