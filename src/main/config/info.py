from typing import NamedTuple

from omegaconf import OmegaConf


class LinkConfig(NamedTuple):
    url: str
    weight: int


class InfoConfig(NamedTuple):
    email: str
    password: str
    cvv: str
    links: list[LinkConfig]  # Updated to use LinkConfig


_conf = OmegaConf.load("config.yaml")

links = [LinkConfig(url=link["url"], weight=link["weight"]) for link in _conf.links]

info_config = InfoConfig(
    email=_conf.email, password=_conf.password, cvv=_conf.cvv, links=links
)
