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

