// The initial screen where the user can log into an account.
class SceneLogin extends Phaser.Scene {
    constructor() {
        super({ key: 'login' });

        // Common text styles.
        this.default_font = {
            fontFamily: 'Calibri',
            fontSize: 13,
            color: '#FFFFFF'
        };

        this.default_font_subdued = {
            fontFamily: 'Calibri',
            fontSize: 13,
            color: '#888888'
        };

        // The element that will be changed if the user types.
        this.active_element = 'username';

        // Create a list of characters that are valid for text input.
        this.valid_keys = [ 32 ]; // 32 = Space

        for (let i = 48; i <= 57; i++) { // Numbers 0-9 & their symbols
            this.valid_keys.push(i);
        }

        for (let i = 65; i <= 90; i++) { // Characters a-z & A-Z
            this.valid_keys.push(i);
        }
    }

    preload() {
        this.load.image('login bg', '/graphics/art/login_bg');

        // So that Google fonts can be loaded.
        this.load.script(
            'webfont',
            'https://ajax.googleapis.com/ajax/libs/webfont/1.6.26/webfont.js'
        );
    }

    create() {
        const cw = this.sys.game.canvas.width;

        // Render the background image.
        this.background = this.add.image(0, 0, 'login bg').setOrigin(0, 0);
        this.background.displayWidth = cw;
        this.background.scaleY = this.background.scaleX;

        // Fade the background in.
        this.add.tween({
            targets: [ this.background ],
            ease: 'Sine.easeInOut',
            duration: 3000,
            delay: 0,
            alpha: {
                getStart: () => 0,
                getEnd: () => 1
            }
        });

        // Load font needed for the game title.
        WebFont.load({
            google: {
                families: [ 'IM Fell English SC' ]
            },
            active: () => {
                // Render the game title.
                const game_title = this.add.text(
                    50, 50,
                    'Chimerical Terrene',
                    {
                        fontFamily: 'IM Fell English SC',
                        fontSize: 100,
                        color: '#FFFFFF'
                    }
                ).setShadow(0, 0, "#000000", 5, false, true);

                // Fade the game title in.
                this.add.tween({
                    targets: [ game_title ],
                    ease: 'Sine.easeInOut',
                    duration: 5000,
                    delay: 0,
                    alpha: {
                        getStart: () => 0,
                        getEnd: () => 1
                    }
                });
            }
        });

        // Render the login prompt.
        this.login_background = this.add.graphics();
        this.login_background.fillStyle(0x000000, 0.5);
        this.login_background.fillRoundedRect(100, 180, 300, 60, 10);

        this.username_label = this.add.text(120, 193, 'Username:', this.default_font).setInteractive();
        this.password_label = this.add.text(120, 213, 'Password:', this.default_font_subdued).setInteractive();

        this.username = this.add.text(190, 193, '', this.default_font);
        this.password = this.add.text(190, 213, '', this.default_font);

        // Handle login labels hover/click.
        this.username_label.on('pointerover', () => {
            if (this.active_element != 'username') {
                this.username_label.setStyle({ color: '#0088FF' });
            }
        });
        this.username_label.on('pointerdown', () => {
            this.password_label.setStyle({ color: '#888888' });
            this.username_label.setStyle({ color: '#FFFFFF' });

            this.active_element = 'username';
        });
        this.username_label.on('pointerout', () => {
            if (this.active_element != 'username') {
                this.username_label.setStyle({ color: '#888888' });
            }
        });

        this.password_label.on('pointerover', () => {
            if (this.active_element != 'password') {
                this.password_label.setStyle({ color: '#0088FF' });
            }
        });
        this.password_label.on('pointerdown', () => {
            this.username_label.setStyle({ color: '#888888' });
            this.password_label.setStyle({ color: '#FFFFFF' });

            this.active_element = 'password';
        });
        this.password_label.on('pointerout', () => {
            if (this.active_element != 'password') {
                this.password_label.setStyle({ color: '#888888' });
            }
        });

        // Render the login button.
        this.login_button = this.add.graphics();
        this.login_button.fillStyle(0x000000, 0.5);
        this.login_button.fillRoundedRect(410, 180, 200, 60, 10);

        this.login_label = this.add.text(
            450, 190,
            'LOGIN',
            {
                fontFamily: 'Times New Roman',
                fontSize: 40,
                color: '#888888'
            }
        ).setShadow(0, 0, "#000000", 5, false, true).setInteractive();

        // Fade in the login prompt text elements.
        this.add.tween({
            targets: [ this.username_label, this.password_label, this.login_label ],
            ease: 'Sine.easeInOut',
            duration: 3000,
            delay: 0,
            alpha: {
                getStart: () => 0,
                getEnd: () => 1
            }
        });

        // Handle login button text hover/click.
        this.login_label.on('pointerover', () => {
            this.login_label.setStyle({ color: '#FFFFFF' });
        });
        this.login_label.on('pointerout', () => {
            this.login_label.setStyle({ color: '#888888' });
        });

        this.login_label.on('pointerdown', () => {
            socket.emit('login', {
                username: this.username.text,
                password: this.password.text
            });
        });

        // Listen for key presses.
        this.input.keyboard.on('keydown', (key) => {
            if (this.active_element == 'username') {
                // Check whether the pressed key is valid.
                if (this.valid_keys.indexOf(key.keyCode) > -1) {
                    // Max username length is 20 characters.
                    if (this.username.text.length < 20) {
                        this.username.text += key.key;
                    }
                }

                // If the user pressed enter, move them to the password field.
                else if (key.keyCode == 13) {
                    this.username_label.setStyle({ color: '#888888' });
                    this.password_label.setStyle({ color: '#FFFFFF' });

                    this.active_element = 'password';
                }
            }
            else if (this.active_element == 'password') {
                // Check whether the pressed key is valid.
                if (this.valid_keys.indexOf(key.keyCode) > -1) {
                    this.password.text += key.key;
                }

                // If the user pressed enter, log them in.
                else if (key.keyCode == 13) {
                    socket.emit('login', {
                        username: this.username.text,
                        password: this.password.text
                    });
                }
            }
        });
    }

    // Used for forwarding special keypresses from elsewhere.
    keypress(e) {
        if (e.keyCode == 8) {
            // Backspace the active element.
            if (this.active_element == 'username') {
                this.username.text = this.username.text.slice(0, -1);
            }
            else if (this.active_element == 'password') {
                this.password.text = this.password.text.slice(0, -1);
            }
        }

        // If the user pressed tab, move them to the next input field.
        else if (e.keyCode == 9) {
            if (this.active_element == 'username') {
                this.username_label.setStyle({ color: '#888888' });
                this.password_label.setStyle({ color: '#FFFFFF' });

                this.active_element = 'password';
            }
            else if (this.active_element == 'password') {
                this.username_label.setStyle({ color: '#FFFFFF' });
                this.password_label.setStyle({ color: '#888888' });

                this.active_element = 'username';
            }
        }
    }
}
