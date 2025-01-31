from typing import NamedTuple

from omegaconf import OmegaConf


class InfoConfig(NamedTuple):
    email: str
    password: str
    cvv: str
    rtx_links: list[str]


_conf = OmegaConf.load("config.yaml")

info_config = InfoConfig(
    email=_conf.email, password=_conf.password, cvv=_conf.cvv, rtx_links=_conf.rtx_links
)
