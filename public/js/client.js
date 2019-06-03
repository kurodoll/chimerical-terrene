const socket = io.connect();
let client_sid;

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
    game.scene.start('game'); // Hack to preload data correctly
    game.scene.switch('game', 'login');


    // >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    //                                                       Server Interaction
    // <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    socket.on('logged in', (sid) => {
        game.scene.switch('login', 'character_select');
        client_sid = sid;
    });

    socket.on('character initialized', () => {
        game.scene.switch('character_select', 'game');
        game.scene.start('gui');

        socket.emit('get present level');
    });

    socket.on('present level', (level) => {
        game.scene.getScene('game').setLevel(level);
    });

    socket.on('entity update', (entity) => {
        game.scene.getScene('game').entityUpdate(entity);
    });

    socket.on('monitor update', (update) => {
        console.log(new Date($.now()) + '\nMonitor Update (' + update.monitor + '):', update.data);
        game.scene.getScene('gui').monitorUpdate(update);
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
