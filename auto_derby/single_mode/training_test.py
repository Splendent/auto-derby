from pathlib import Path

import PIL.Image

from .training import Training

_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_update_by_training_scene():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 26
    assert training.stamina == 0
    assert training.power == 14
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3


def test_update_by_training_scene_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_2.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 6
    assert training.stamina == 0
    assert training.power == 0
    assert training.guts == 0
    assert training.wisdom == 24
    assert training.skill == 8


def test_update_by_training_scene_3():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_3.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 6
    assert training.stamina == 0
    assert training.power == 6
    assert training.guts == 17
    assert training.wisdom == 0
    assert training.skill == 2


def test_update_by_training_scene_4():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_4.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 7
    assert training.stamina == 0
    assert training.power == 6
    assert training.guts == 16
    assert training.wisdom == 0
    assert training.skill == 2


def test_update_by_training_scene_issue9():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_issue9.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 12
    assert training.stamina == 0
    assert training.power == 7
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 2


def test_update_by_training_scene_issue24():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_issue24.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 0
    assert training.stamina == 9
    assert training.power == 0
    assert training.guts == 4
    assert training.wisdom == 0
    assert training.skill == 2


def test_update_by_training_scene_issue51():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "training_scene_issue51.png")
        .convert("RGB")
        .resize((540, 960))
    )

    training = Training.from_training_scene(img)
    assert training.speed == 21
    assert training.stamina == 0
    assert training.power == 10
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 3


def test_update_by_training_scene_issue55():
    img = PIL.Image.open(_TEST_DATA_PATH / "training_scene_issue55.png").convert("RGB")

    training = Training.from_training_scene(img)
    assert training.speed == 30
    assert training.stamina == 0
    assert training.power == 17
    assert training.guts == 0
    assert training.wisdom == 0
    assert training.skill == 4
