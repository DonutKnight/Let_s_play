import pytmx


class TiledMapParser:
    def __init__(self, map_path):
        self.map_path = map_path
        self.tmx_data = pytmx.load_pygame(map_path)

    def get_map_info(self):
        return {
            "width": self.tmx_data.width,
            "height": self.tmx_data.height,
            "tile_width": self.tmx_data.tilewidth,
            "tile_height": self.tmx_data.tileheight,
            "layers": [layer.name for layer in self.tmx_data.layers],
        }