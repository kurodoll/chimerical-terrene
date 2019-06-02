class SceneCharacterSelect extends Phaser.Scene {
    constructor() {
        super({ key: 'character_select' });

        // Common text styles.
        this.default_font = {
            fontFamily: 'Calibri',
            fontSize: 13,
            color: '#FFFFFF'
        };
    }

    create() {
        this.add.text(20, 20, 'a) New character', this.default_font);
    }
}
