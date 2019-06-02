// The initial screen where the user can log into an account.
class SceneLogin extends Phaser.Scene {
    constructor() {
        super({ key: 'login' });

        this.default_font = {
            fontFamily: 'Calibri',
            fontSize: 13,
            color: '#FFFFFF'
        };
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

        this.username_label = this.add.text(120, 193, 'Username:', this.default_font);
        this.password_label = this.add.text(120, 213, 'Password:', this.default_font);

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
                color: '#BBBBBB'
            }
        ).setShadow(0, 0, "#000000", 5, false, true);

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
    }
}
