// The initial screen where the user can log into an account.
class SceneLogin extends Phaser.Scene {
    constructor() {
        super({ key: 'login' });
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
    }
}
