const socket = io.connect();

$(() => {
    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                              Phaser Init
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    const phaser_config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        scene: [ SceneLogin, SceneCharacterSelect ],
        render: {
            'pixelArt': true // Don't blur when small images are enlarged.
        }
    };

    const game = new Phaser.Game(phaser_config);
    game.scene.start('login');


    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                       Server Interaction
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    socket.on('logged in', () => {
        game.scene.switch('login', 'character_select');
    });


    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                             jQuery Stuff
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    // If the user presses backspace, don't go back in the browser history.
    // Instead, forward the keypress to the current scene.
    $(document).on('keydown', (e) => {
        if (e.keyCode == 8) {
            e.preventDefault();

            if (game.scene.isActive('login')) {
                game.scene.getScene('login').keypress(e);
            }
        }
    });
});
