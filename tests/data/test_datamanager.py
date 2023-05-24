from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pytest
import torch
import yaml

from nerfstudio.cameras.cameras import Cameras
from nerfstudio.configs.base_config import InstantiateConfig
from nerfstudio.data.datamanagers.base_datamanager import (
    DataparserOutputs,
    VanillaDataManager,
    VanillaDataManagerConfig,
)
from nerfstudio.data.datasets.base_dataset import InputDataset
from nerfstudio.data.datasets.depth_dataset import DepthDataset


class DummyDataParser:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, __name: str) -> Any:
        if __name.startswith("_"):
            return object.__getattribute__(self, __name)
        return None

    def get_dataparser_outputs(self, *args, **kwargs):
        return DataparserOutputs(
            [],
            Cameras(
                torch.ones((0, 3, 4)),
                torch.ones((0, 1)),
                torch.ones((0, 1)),
                torch.ones((0, 1)),
                torch.ones((0, 1)),
                10,
                10,
            ),
            metadata={"depth_filenames": [], "depth_unit_scale_factor": 1.0},
        )


@pytest.fixture
def config():
    config = VanillaDataManagerConfig()
    setattr(config, "dataparser", InstantiateConfig(_target=DummyDataParser))
    setattr(config.dataparser, "data", None)
    return config


def test_data_manager_type_inference(config):
    # Mock for a faster test

    assert VanillaDataManager(config).dataset_type is InputDataset
    assert VanillaDataManager[DepthDataset](config).dataset_type is DepthDataset

    class tmp(VanillaDataManager):
        pass

    assert tmp(config).dataset_type is InputDataset

    class tmp2(VanillaDataManager[DepthDataset]):
        pass

    assert tmp2(config).dataset_type is DepthDataset


def test_data_manager_type_can_be_serialized(config):
    # Mock for a faster test

    assert VanillaDataManager(config).dataset_type is InputDataset
    obj = yaml.load(yaml.dump(VanillaDataManager(config)), Loader=yaml.UnsafeLoader)
    assert obj.dataset_type is InputDataset
    assert isinstance(obj, VanillaDataManager)

    assert VanillaDataManager[DepthDataset](config).dataset_type is DepthDataset
    obj = yaml.load(yaml.dump(VanillaDataManager[DepthDataset](config)), Loader=yaml.UnsafeLoader)
    assert obj.dataset_type is DepthDataset
    assert isinstance(obj, VanillaDataManager)

    class tmp(VanillaDataManager):
        pass

    try:
        globals()["tmp"] = tmp
        assert tmp(config).dataset_type is InputDataset
        obj = yaml.load(yaml.dump(tmp(config)), Loader=yaml.UnsafeLoader)
        assert obj.dataset_type is InputDataset
        assert isinstance(obj, tmp)
    finally:
        globals().pop("tmp")

    class tmp2(VanillaDataManager[DepthDataset]):
        pass

    try:
        globals()["tmp2"] = tmp2

        assert tmp2(config).dataset_type is DepthDataset
        obj = yaml.load(yaml.dump(tmp2(config)), Loader=yaml.UnsafeLoader)
        assert obj.dataset_type is DepthDataset
        assert isinstance(obj, tmp2)
    finally:
        globals().pop("tmp2")


def _dummy_function():
    return True


@dataclass
class Test:
    func: Callable = _dummy_function


def test_serialize_dataclass_with_callable():
    assert Test().func()
    print(yaml.dump(Test()))
    obj = yaml.load(yaml.dump(Test()), Loader=yaml.Loader)
    assert obj.func()


def test_deserialize_config1():
    with open(Path(__file__).parent / "configs" / "test_config1.yml", "r") as f:
        config_str = f.read()
    obj = yaml.load(config_str, Loader=yaml.Loader)
    obj.pipeline.datamanager.collate_fn([1, 2, 3])


def test_deserialize_config2():
    with open(Path(__file__).parent / "configs" / "test_config2.yml", "r") as f:
        config_str = f.read()
    obj = yaml.load(config_str, Loader=yaml.Loader)
    obj.pipeline.datamanager.collate_fn([1, 2, 3])
