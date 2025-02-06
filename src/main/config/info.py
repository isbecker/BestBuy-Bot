from typing import List, Optional
from omegaconf import OmegaConf, MISSING
from dataclasses import dataclass
import os


@dataclass
class LinkConfig:
    url: str = MISSING  # Required field
    weight: int = MISSING  # Required field


@dataclass
class InfoConfig:
    email: str = MISSING  # Required field
    password: str = MISSING  # Required field
    cvv: str = MISSING  # Required field
    links: List[LinkConfig] = MISSING  # Required field
    chromium_version: Optional[int] = None  # Optional field
    log_level: str = "INFO"  # Optional field, default to INFO


_conf = OmegaConf.load("config.yaml")

links = [OmegaConf.structured(LinkConfig(**link)) for link in _conf.links]

info_config = OmegaConf.structured(
    InfoConfig(
        email=_conf.email,
        password=_conf.password,
        cvv=_conf.cvv,
        links=links,
        chromium_version=_conf.chromium.version if "chromium" in _conf else None,
        log_level=_conf.log_level if "log_level" in _conf else "INFO",
    )
)
