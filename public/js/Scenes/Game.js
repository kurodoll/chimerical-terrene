// The scene for rending and handling the game world itself.
class SceneGame extends Phaser.Scene {
    constructor() {
        super({ key: 'game' });
    }

    preload() {
        this.load.image('tileset cave', '/graphics/tilesets/cave');
        this.load.json('tileset cave data', '/data/tilesets/cave');

        this.load.image('player', '/graphics/sprites/player');
        this.load.image('floating paper', '/graphics/sprites/floating_paper');
    }

    create() {
        // Set up inputs.
        const movement_keys = [ '1', '2', '3', '4', '6', '7', '8', '9' ];

        this.input.keyboard.on('keydown', (e) => {
            // Actions that require you be controlling an entity.
            if (this.controlling_entity) {
                // Movement.
                if (movement_keys.indexOf(e.key) > -1) {
                    socket.emit(
                        'action',
                        'move',
                        {
                            'entity': this.controlling_entity.id,
                            'dir': e.key
                        }
                    );
                }
            }
        });
    }

    setLevel(level) {
        this.level = level;

        // Create a map of tiles to be rendered.
        this.map = this.make.tilemap({
            tileWidth: level.tile_width,
            tileHeight: level.tile_height,
            width: level.width,
            height: level.height
        });

        // Use the specified tileset.
        this.tileset = this.map.addTilesetImage(
            'tileset ' + level.tileset,
            'tileset ' + level.tileset,
            level.tile_width,
            level.tile_height,
            0, 0
        );

        // Get the tileset data, which maps tile type to its index in the
        // tileset image.
        const tileset_json_name = 'tileset ' + level.tileset + ' data';
        this.tileset_data = this.cache.json.get(tileset_json_name);

        // This is necessary for rendering to work?
        this.layer = this.map.createBlankDynamicLayer('Layer 1', this.tileset);

        // Go through each tile in the level and render it.
        for (let x = 0; x < level.width; x++) {
            for (let y = 0; y < level.height; y++) {
                const tile_type = level.tiles[y * level.width + x].type;
                const tileset_index = this.tileset_data[tile_type];

                this.map.putTileAt(tileset_index, x, y);
            }
        }

        // Center the map and zoom to the specified zoom amount for this level.
        this.cameras.main.centerOn(
            (level.width * level.tile_width) / 2,
            (level.height * level.tile_height) / 2
        );

        this.cameras.main.setZoom(level.zoom);

        this.renderSprites();
    }

    renderSprites() {
        let player_ent;

        for (let i = 0; i < this.level.entities.length; i++) {
            if ('sprite' in this.level.entities[i].components) {
                const ent = this.level.entities[i];

                if (ent.components.user_controlled && ent.components.user_controlled.data.owner == client_sid) {
                    player_ent = ent;
                }

                const pos_x = ent.components.position.data.x * this.level.tile_width;
                const pos_y = ent.components.position.data.y * this.level.tile_height;

                if (ent.image) {
                    // Only update the sprite if it has moved.
                    if (pos_x != ent.image.x || pos_y != ent.image.y) {
                        ent.image.tween = this.add.tween({
                            targets: [ ent.image ],
                            ease: 'Sine.easeInOut',
                            duration: 100,
                            delay: 0,
                            x: {
                                getStart: () => ent.image.x,
                                getEnd: () => pos_x
                            },
                            y: {
                                getStart: () => ent.image.y,
                                getEnd: () => pos_y
                            }
                        });
                    }
                }
                else {
                    ent.image =
                        this.add.sprite(
                            pos_x,
                            pos_y,
                            ent.components.sprite.data.sprite
                        ).setOrigin(0, 0);
                }
            }
        }

        // Update LOS and camera for player.
        this.determineSight({
            x: player_ent.components.position.data.x,
            y: player_ent.components.position.data.y
        });

        this.controlling_entity = player_ent;
        this.cameras.main.startFollow(player_ent.image, true, 0.09, 0.09);
    }

    // Determines which tiles are visible and which are not.
    determineSight(from_pos) {
        for (let x = 0; x < this.level.width; x++) {
            for (let y = 0; y < this.level.height; y++) {
                const distance = Math.sqrt(
                    Math.pow(Math.abs(x - from_pos.x), 2) + Math.pow(Math.abs(y - from_pos.y), 2)
                );

                const brightness = 1 / (distance / 5);
                this.layer.getTileAt(x, y).setAlpha(brightness);

                // Reset the tint of the tile.
                this.layer.getTileAt(x, y).tint = 0xFFFFFF;

                // Get a list of tiles that exist between the two points.
                const tiles = this.getTilesOnLine(from_pos, { x: x, y: y });

                // Whether this tile has been declared hidden from view.
                let tile_hidden = false;

                // Check if any of the tiles between the two points block view.
                for (let i = 0; i < tiles.length; i++) {
                    const index = tiles[i].y * this.level.width + tiles[i].x;

                    // Ensure that the tile is within the level.
                    // Since the LOS algorithm rounds, it can get values
                    // outside of the bounds of the level.
                    if (!this.level.tiles[index]) {
                        continue;
                    }

                    // If this tile is blocked, either hide or tint it.
                    if (this.level.tiles[index].type == 'wall') {
                        // We just tint the tile blue if we've seen it before.
                        if (this.level.tiles[y * this.level.width + x].known) {
                            this.layer.getTileAt(x, y).tint = 0xFF8800;
                        }
                        else {
                            this.layer.getTileAt(x, y).tint = 0x000000;
                        }

                        tile_hidden = true;
                        break;
                    }
                }

                // If the tile wasn't hidden, mark it as known.
                if (!tile_hidden) {
                    this.level.tiles[y * this.level.width + x].known = true;
                }
            }
        }

        // Hide entities that are out of sight.
        for (let i = 0; i < this.level.entities.length; i++) {
            if (this.level.entities[i].image) {
                if (this.level.entities[i].components.position) {
                    const x = this.level.entities[i].components.position.data.x;
                    const y = this.level.entities[i].components.position.data.y;

                    if (this.layer.getTileAt(x, y).tint != 0xFFFFFF) {
                        this.level.entities[i].image.visible = false;
                    }
                    else {
                        const distance = Math.sqrt(
                            Math.pow(Math.abs(x - from_pos.x), 2) + Math.pow(Math.abs(y - from_pos.y), 2)
                        );

                        const brightness = 1 / (distance / 5);

                        this.level.entities[i].image.visible = true;
                        this.level.entities[i].image.setAlpha(brightness);
                    }
                }
            }
        }
    }

    // Returns a list of tiles that intersect a line from point A to B.
    // TODO: Fix so that sight is equal from point A to B and vice versa.
    getTilesOnLine(from, to) {
        let tiles = [];
        let x0, x1, y0, y1;

        // This is so that walls show up.
        if (from.x < to.x) { to.x -= 1; }
        if (from.x > to.x) { to.x += 1; }

        if (from.y < to.y) { to.y -= 1; }
        if (from.y > to.y) { to.y += 1; }

        // Make sure the "from" x is smaller than the "to" x.
        if (from.x > to.x) {
            x0 = to.x;
            y0 = to.y;
            x1 = from.x;
            y1 = from.y;
        }
        else {
            x0 = from.x;
            y0 = from.y;
            x1 = to.x;
            y1 = to.y;
        }

        const dx = Math.abs(x0 - x1); // Distance between x points
        const dy = Math.abs(y0 - y1); // Distance between y points
        const sy = y1 > y0 ? 1 : -1; // The slope of y

        // Determines how many points are checked for intersection.
        const delta = 0.1;

        let x = x0;
        let y = y0;

        if (dx > dy) {
            const cy = dy / dx;

            for (; x < x1; x += delta) {
                y += cy * sy * delta;
                tiles.push({ x: Math.round(x), y: Math.round(y) });
            }
        }
        else {
            const cx = dx / dy;

            while (true) {
                y += sy * delta;
                x += cx * delta;
                tiles.push({ x: Math.round(x), y: Math.round(y) });

                if ((sy == 1 && y >= y1) || (sy == -1 && y <= y1)) {
                    break;
                }
            }
        }

        return tiles;
    }

    entityUpdates(updates) {
        for (let i = 0; i < updates.length; i++) {
            const entity = updates[i];
            let exists = false;

            for (let i = 0; i < this.level.entities.length; i++) {
                if (this.level.entities[i] && entity.id == this.level.entities[i].id) {
                    exists = true;

                    // Check if the entity is being deleted.
                    if (entity.deleted) {
                        if (this.level.entities[i].image) {
                            this.level.entities[i].image.destroy();
                        }

                        this.level.entities.splice(i, 1);
                    }
                    else {
                        if (this.level.entities[i].image) {
                            const image = this.level.entities[i].image;
                            this.level.entities[i] = entity;
                            this.level.entities[i].image = image;
                        }
                        else {
                            this.level.entities[i] = entity;
                        }
                    }

                    break;
                }
            }

            if (!exists) {
                this.level.entities.push(entity);
            }
        }

        this.renderSprites();
    }
}
