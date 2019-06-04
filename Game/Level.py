from log import log
from . import Tile

import random


class Level:
    def __init__(self, level_data):
        log(f'Level:{level_data["id"]}', f'Creating level.', 'debug')

        self.id = level_data['id']
        self.name = level_data['name']

        self.width = level_data['width']
        self.height = level_data['height']

        self.tile_width = level_data['tile_width']
        self.tile_height = level_data['tile_height']
        self.zoom = level_data['zoom']

        self.tileset = level_data['tileset']

        self.entities = []
        self.mobs = level_data['mobs']

        # If the level has a generator field, the level itself needs to be
        # procedurally generated.
        if 'generator' in level_data and 'tile_weights' in level_data:
            self.generateLevel(
                level_data['generator'],
                level_data['tile_weights']
            )

        log(f'Level:{self.id}', f'Loaded level.')

        self.valid_movements = [
            'ground', 'ground_rough',
            'grass'
        ]

    def generateLevel(self, generator, tile_weights):
        log(
            f'Level:{self.id}',
            f'Generating level of type [{generator}].',
            'debug'
        )

        if generator == 'cave':
            tiles_n = self.width * self.height
            tiles_fill_n = int(tiles_n / 3)  # Number of tiles to place

            # Start walk in the center of the level area.
            cur_x = int(self.width / 2)
            cur_y = int(self.height / 2)

            # Keep track of open/walkable tiles.
            open_tiles = []

            # Create an empty level.
            self.tiles = []
            for i in range(0, tiles_n):
                self.tiles.append(Tile.Tile('empty'))

            # Use a random walk algorithm to create a random floor plan.
            for i in range(0, tiles_fill_n):
                # Choose a tile type to place.
                tile_prob = random.randint(1, 100)

                for t in tile_weights:
                    if tile_prob <= tile_weights[t]:
                        tile_type = t
                        break

                tile_index = int(cur_y * self.width + cur_x)
                self.tiles[tile_index].setType(tile_type)

                open_tiles.append({
                    'x': cur_x,
                    'y': cur_y
                })

                # Move the "cursor" randomly until a new spot to place a tile
                # is found.
                while True:
                    if random.random() > 0.5:
                        if random.random() > 0.5:
                            cur_x += 1
                        else:
                            cur_x -= 1
                    else:
                        if random.random() > 0.5:
                            cur_y += 1
                        else:
                            cur_y -= 1

                    if cur_x < 1 or cur_x >= self.width - 1 or cur_y < 1 or cur_y >= self.height - 1:  # noqa
                        cur_x = int(self.width / 2)
                        cur_y = int(self.height / 2)

                    # If we're on an empty tile, break from the loop.
                    if self.tiles[cur_y * self.width + cur_x].type == 'empty':
                        break

            # Place walls around the ground area.
            for x in range(0, self.width):
                for y in range(0, self.height):
                    if self.tiles[y * self.width + x].type == 'empty':
                        adjacent = self.getAdjacentTiles(x, y)

                        for adj in adjacent:
                            if adj.type != 'empty' and adj.type != 'wall':
                                self.tiles[y * self.width + x].setType('wall')
                                break

            # Place a spawn point somewhere.
            spawn_tile_index = random.randint(0, len(open_tiles) - 1)
            spawn_tile = open_tiles[spawn_tile_index]

            self.elements = {
                'spawn_tile': spawn_tile
            }

            self.tiles[spawn_tile['y'] * self.width + spawn_tile['x']].addAttribute('spawn_tile')  # noqa

    def getRandomClearTile(self):
        clear_tiles = []

        for x in range(0, self.width):
            for y in range(0, self.height):
                t = self.tiles[y * self.width + x]

                if t.type in self.valid_movements:
                    clear_tiles.append({'x': x, 'y': y})

        index = random.randint(0, len(clear_tiles))
        return clear_tiles[index]

    def getAdjacentTiles(self, x, y):
        adjacent = []
        coords = [
            {'x': x - 1, 'y': y - 1},
            {'x': x, 'y': y - 1},
            {'x': x + 1, 'y': y - 1},

            {'x': x - 1, 'y': y},
            {'x': x + 1, 'y': y},

            {'x': x - 1, 'y': y + 1},
            {'x': x, 'y': y + 1},
            {'x': x + 1, 'y': y + 1},
        ]

        for c in coords:
            try:
                tile = self.tiles[c['y'] * self.width + c['x']]
                adjacent.append(tile)
            except IndexError:
                pass

        return adjacent

    def addEntity(self, entity):
        self.entities.append(entity)

    # Given a mob entity, give it a position component and spawn it.
    def spawnMob(self, entity, ComponentManager):
        spawn_at = self.getRandomClearTile()

        position_comp = ComponentManager.new(
            entity,
            'position',
            {
                'x': spawn_at['x'],
                'y': spawn_at['y'],
                'on_level': self.id
            }
        )

        entity.addComponent(position_comp)

    def delEntity(self, entity_id):
        for i in range(0, len(self.entities)):
            if self.entities[i].id == entity_id:
                del self.entities[i]
                return

    def getTilesAsJSON(self):
        tiles = []

        for t in self.tiles:
            tiles.append({
                'type': t.type,
                'attributes': t.attributes
            })

        return tiles

    def getEntitiesAsJSON(self):
        entities = []

        for e in self.entities:
            entities.append(e.toJSON())

        return entities

    def getAsJSON(self):
        return {
            'id': self.id,
            'name': self.name,

            'width': self.width,
            'height': self.height,

            'tile_width': self.tile_width,
            'tile_height': self.tile_height,
            'zoom': self.zoom,

            'tileset': self.tileset,

            'tiles': self.getTilesAsJSON(),
            'elements': self.elements,
            'entities': self.getEntitiesAsJSON()
        }
