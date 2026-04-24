import os
import pygame
from tiled_parser import TiledMapParser

pygame.init()
pygame.display.set_mode((1, 1))

base_dir = os.path.dirname(__file__)
map_path = os.path.join(base_dir, "maps", "LewelOne.tmx")

parser = TiledMapParser(map_path)

print("Map info:")
print(parser.get_map_info())