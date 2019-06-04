class SceneGUI extends Phaser.Scene {
    constructor() {
        super({ key: 'gui' });

        // The element that will be changed if the user types.
        this.active_element = '';

        // Create a list of characters that are valid for text input.
        this.valid_keys = [ 32, 59 ]; // 32 = Space, 59 = ;

        for (let i = 48; i <= 57; i++) { // Numbers 0-9 & their symbols
            this.valid_keys.push(i);
        }

        for (let i = 65; i <= 90; i++) { // Characters a-z & A-Z
            this.valid_keys.push(i);
        }

        this.monitor_data = {};
    }

    create() {
        const cw = this.sys.game.canvas.width;
        const ch = this.sys.game.canvas.height;

        // Combat details display.
        this.strength = this.add.text(
            20, ch - 20, '', {
                fontFamily: 'Verdana',
                fontSize: 10,
                color: '#FFAA66'
            }
        );
        this.health_label = this.add.text(
            100, ch - 20, 'Hit Points', {
                fontFamily: 'Verdana',
                fontSize: 10,
                color: '#FF4444'
            }
        );
        this.health = this.add.text(
            100, ch - 50, '', {
                fontFamily: 'Verdana',
                fontSize: 25,
                color: '#FF8888'
            }
        );

        this.current_combat_mode = this.add.text(
            cw / 2, 50, '', {
                fontFamily: 'Verdana',
                fontSize: 50,
                color: '#000000'
            }
        ).setOrigin(0.5).setShadow(0, 0, "#FFFFFF", 2, false, true);
        this.current_combat_details = this.add.text(
            cw / 2 - 100, 80, '', {
                fontFamily: 'Verdana',
                fontSize: 10,
                color: '#FFFFFF'
            }
        );

        // Console window.
        this.console_bg = this.add.graphics();
        this.console_bg.fillStyle(0xFFFFFF);
        this.console_bg.fillRect(10, 10, 400, 20);
        this.console_bg.visible = false;

        this.console_command = this.add.text(
            14, 14, '', {
                fontFamily: 'Consolas',
                fontSize: 11,
                color: '#000000'
            }
        );

        // Monitor output.
        this.monitor_output = this.add.text(
            10, 30, '', {
                fontFamily: 'Calibri',
                fontSize: 10,
                color: '#FFFFFF'
            }
        );

        // Listen for key presses.
        this.input.keyboard.on('keydown', (key) => {
            if (key.key == '`') {
                // Show a console window.
                if (this.console_bg.visible) {
                    this.console_bg.visible = false;
                    this.active_element = '';
                }
                else {
                    this.console_bg.visible = true;
                    this.active_element = 'console';
                }
            }
            else {
                if (this.active_element == 'console') {
                    // Check whether the pressed key is valid.
                    if (this.valid_keys.indexOf(key.keyCode) > -1 || key.key == '_') {
                        this.console_command.text += key.key;
                    }

                    // On enter, submit the command to the server.
                    else if (key.keyCode == 13) {
                        socket.emit('console command', this.console_command.text);

                        this.console_bg.visible = false;
                        this.active_element = '';
                        this.console_command.text = '';
                    }
                }
            }
        });
    }

    setPlayerStats(details) {
        this.health.text = details.data.health + '/' + details.data.health_max;
        this.strength.text = 'Str ' + details.data.strength;
    }

    setCombatDetails(details, level) {
        if (details.in_combat) {
            this.current_combat_mode.text = ' COMBAT ';

            let details_text = '';

            for (let i = 0; i < details.with.length; i++) {
                const eid = details.with[i];

                for (let i = 0; i < level.entities.length; i++) {
                    if (level.entities[i] && eid == level.entities[i].id) {
                        const e = level.entities[i];
                        details_text += '> ' + e.components.name.data.name + '\n';
                    }
                }
            }

            this.current_combat_details.text = details_text;
        }
        else {
            this.current_combat_mode.text = '';
            this.current_combat_details.text = '';
        }
    }

    showDamage(details) {
        const cw = this.sys.game.canvas.width;
        const ch = this.sys.game.canvas.height;

        if (details.type == 'given') {
            const damage_given = this.add.text(
                cw / 2, ch / 2, details.amount, {
                    fontFamily: 'Verdana',
                    fontSize: 20,
                    color: '#FFCC88'
                }
            ).setOrigin(0.5);

            this.add.tween({
                targets: [ damage_given ],
                ease: 'Sine.easeInOut',
                duration: 1000,
                delay: 0,
                x: {
                    getStart: () => cw / 2,
                    getEnd: () => cw / 2
                },
                y: {
                    getStart: () => ch / 2,
                    getEnd: () => ch / 2 - 100
                },
                onComplete: () => {
                    damage_given.destroy();
                }
            });
        }
        else if (details.type == 'taken') {
            const damage_taken = this.add.text(
                cw / 2, ch / 2, details.amount, {
                    fontFamily: 'Verdana',
                    fontSize: 20,
                    color: '#FF0000'
                }
            ).setOrigin(0.5);

            this.add.tween({
                targets: [ damage_taken ],
                ease: 'Sine.easeInOut',
                duration: 1000,
                delay: 0,
                x: {
                    getStart: () => cw / 2,
                    getEnd: () => cw / 2
                },
                y: {
                    getStart: () => ch / 2,
                    getEnd: () => ch / 2 + 100
                },
                onComplete: () => {
                    damage_taken.destroy();
                }
            });
        }
    }

    monitorUpdate(data) {
        // If we're sent level data, we want to hide all the tile data.
        if (data.data.tiles) {
            delete data.data.tiles;
        }

        this.monitor_data[data.monitor] = data.data;

        // Make the output look good and display it on-screen.
        this.monitor_output.text = JSON.stringify(this.monitor_data, null, 4)
            .replace(/{/g, '')
            .replace(/}/g, '')
            .replace(/"/g, '')
            .replace(/,/g, '');
    }

    // Used for forwarding special keypresses from elsewhere.
    keypress(e) {
        if (e.keyCode == 8) {
            // Backspace the active element.
            if (this.active_element == 'console') {
                this.console_command.text = this.console_command.text.slice(0, -1);
            }
        }
    }
}

