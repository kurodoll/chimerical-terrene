// The scene for rending and handling the game world itself.
class SceneGame extends Phaser.Scene {
    constructor() {
        super({ key: 'game' });
    }

    preload() {
        this.load.image('tileset cave', '/graphics/tilesets/cave');
        this.load.json('tileset cave data', '/data/tilesets/cave');

        this.load.image('player', '/graphics/sprites/player');
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
        for (let i = 0; i < this.level.entities.length; i++) {
            if ('sprite' in this.level.entities[i].components) {
                const ent = this.level.entities[i];

                const pos_x = ent.components.position.data.x * this.level.tile_width;
                const pos_y = ent.components.position.data.y * this.level.tile_height;

                if (ent.image) {
                    ent.image.x = pos_x;
                    ent.image.y = pos_y;

                    if (ent.image.old_x && ent.image.old_y) {
                        this.add.tween({
                            targets: [ ent.image ],
                            ease: 'Sine.easeInOut',
                            duration: 100,
                            delay: 0,
                            x: {
                                getStart: () => ent.image.old_x,
                                getEnd: () => pos_x
                            },
                            y: {
                                getStart: () => ent.image.old_y,
                                getEnd: () => pos_y
                            },
                            onComplete: () => {
                                ent.image.old_x = pos_x;
                                ent.image.old_y = pos_y;
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

                    // If this sprite is the player character of this client, have the camera follow it.
                    if (ent.components.user_controlled && ent.components.user_controlled.data.owner == client_sid) {
                        this.controlling_entity = ent;
                        this.cameras.main.startFollow(ent.image, true, 0.09, 0.09);
                    }
                }
            }
        }
    }

    entityUpdate(entity) {
        let exists = false;

        for (let i = 0; i < this.level.entities.length; i++) {
            if (entity.id == this.level.entities[i].id) {
                exists = true;

                if (this.level.entities[i].image) {
                    const old_x = this.level.entities[i].image.x;
                    const old_y = this.level.entities[i].image.y;

                    const image = this.level.entities[i].image; 
                    this.level.entities[i] = entity;
                    this.level.entities[i].image = image;

                    this.level.entities[i].image.old_x = old_x;
                    this.level.entities[i].image.old_y = old_y;
                }
                else {
                    this.level.entities[i] = entity;
                }

                break;
            }
        }

        if (!exists) {
            this.level.entities.push(entity);
        }

        this.renderSprites();
    }
}
