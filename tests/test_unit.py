import pygame
import main

# Tworzymy fa³szywy obiekt udaj¹cy dane z mapy TMX, by nie musieæ wczytywaæ ca³ego poziomu
class FakeTmxObject:
    def __init__(self, x=0, y=0, width=32, height=32, properties=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.properties = properties if properties else {}
        self.name = "FakeObject"

def test_boss_hit_logic():
    # Arrange: Przygotuj Bossa i udawane dŸwiêki (¿eby gra nie wybuch³a bez g³oœników)
    pygame.mixer.init()
    main.boss_hit_sfx = None 
    main.boss_death_sfx = None
    
    fake_obj = FakeTmxObject(properties={'speed': 2.0})
    boss = main.Boss(fake_obj)
    
    # Assert 1: Boss na start powinien mieæ 2 ¿ycia i pe³n¹ prêdkoœæ
    assert boss.health == 2
    assert boss.speed == 2.0
    
    # Act: Zadajemy pierwsze obra¿enia
    boss.hit()
    
    # Assert 2: ¯ycie spada, Boss zwalnia o po³owê
    assert boss.health == 1
    assert boss.speed == 1.0
    
    # Act: Zadajemy œmiertelny cios
    boss.hit()
    
    # Assert 3: ¯ycie spada do 0, uruchamia siê proces œmierci
    assert boss.health == 0
    assert boss.is_dying == True

def test_fruit_collection():
    # Arrange: Przygotuj owoce
    main.collect_sfx = None
    fake_obj = FakeTmxObject(properties={'points': 5})
    fruit = main.Fruit(fake_obj)
    
    # Sprawdzenie stanu pocz¹tkowego
    assert fruit.is_collected == False
    
    # Act: Podnosimy owoc
    points_awarded = fruit.collect()
    
    # Assert: Owoc daje 5 punktów i oznacza siê jako zebrany
    assert points_awarded == 5
    assert fruit.is_collected == True
    
    # Act: Próbujemy zebraæ ten sam owoc jeszcze raz
    points_awarded_again = fruit.collect()
    
    # Assert: Owoc nie powinien oddaæ punktów po raz drugi
    assert points_awarded_again == 0