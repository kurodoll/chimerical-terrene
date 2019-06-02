const socket = io.connect();

$(() => {
    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                              Phaser Init
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    const phaser_config = {
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        scene: [ SceneLogin, SceneCharacterSelect, SceneGame, SceneGUI ],
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

    socket.on('character initialized', () => {
        game.scene.switch('character_select', 'game');
        game.scene.start('gui');

        socket.emit('get present level');
    });

    socket.on('present level', (level) => {
        console.log(level);
    });

    socket.on('monitor update', (update) => {
        console.log(new Date($.now()) + '\nMonitor Update (' + update.monitor + '):', update.data);
    });


    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                             jQuery Stuff
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    // If the user presses backspace, don't go back in the browser history.
    // Instead, forward the keypress to the current scene.
    $(document).on('keydown', (e) => {
        if (e.keyCode == 8 || e.keyCode == 9) {
            e.preventDefault();

            if (game.scene.isActive('login')) {
                game.scene.getScene('login').keypress(e);
            }
            else if (game.scene.isActive('character_select')) {
                game.scene.getScene('character_select').keypress(e);
            }
            else if (game.scene.isActive('gui')) {
                game.scene.getScene('gui').keypress(e);
            }
        }
    });
});
