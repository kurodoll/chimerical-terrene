class SceneCharacterSelect extends Phaser.Scene {
    constructor() {
        super({ key: 'character_select' });

        // Common text styles.
        this.default_font = {
            fontFamily: 'Calibri',
            fontSize: 13,
            color: '#FFFFFF'
        };

        // The element that will be changed if the user types.
        this.active_element = '';

        // Create a list of characters that are valid for text input.
        this.valid_keys = [ 32 ]; // 32 = Space

        for (let i = 48; i <= 57; i++) { // Numbers 0-9 & their symbols
            this.valid_keys.push(i);
        }

        for (let i = 65; i <= 90; i++) { // Characters a-z & A-Z
            this.valid_keys.push(i);
        }
    }

    create() {
        this.add.text(20, 20, 'a) New character', this.default_font);

        // Listen for key presses.
        this.input.keyboard.on('keydown', (key) => {
            if (this.active_element == '') {
                if (key.key == 'a') {
                    this.newCharacterScreen();
                }
            }
            else if (this.active_element == 'name') {
                // Check whether the pressed key is valid.
                if (this.valid_keys.indexOf(key.keyCode) > -1) {
                    // Max character name length is 20 characters.
                    if (this.name.text.length < 20) {
                        this.name.text += key.key;
                    }
                }

                // If the user pressed enter, submit the new character.
                else if (key.keyCode == 13) {
                    socket.emit('character selected', {
                        name: this.name.text
                    });
                }
            }
        });
    }

    newCharacterScreen() {
        this.active_element = 'name';

        this.name_label = this.add.text(200, 20, 'Character name:', this.default_font).setInteractive();
        this.name = this.add.text(300, 20, '', this.default_font);

        this.name_label.on('pointerover', () => {
            if (this.active_element != 'name') {
                this.name_label.setStyle({ color: '#0088FF' });
            }
        });
        this.name_label.on('pointerdown', () => {
            this.name_label.setStyle({ color: '#FFFFFF' });
            this.active_element = 'name';
        });
        this.name_label.on('pointerout', () => {
            if (this.active_element != 'name') {
                this.name_label.setStyle({ color: '#888888' });
            }
        });
    }

    // Used for forwarding special keypresses from elsewhere.
    keypress(e) {
        if (e.keyCode == 8) {
            // Backspace the active element.
            if (this.active_element == 'name') {
                this.name.text = this.name.text.slice(0, -1);
            }
        }
    }
}
