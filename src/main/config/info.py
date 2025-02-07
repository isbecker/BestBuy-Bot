from typing import List, Optional
from omegaconf import OmegaConf, MISSING
from dataclasses import dataclass
import os


@dataclass
class LinkConfig:
    url: str = MISSING  # Required field
    weight: int = MISSING  # Required field


@dataclass
class ChromiumConfig:
    version: Optional[int] = None  # Optional field


@dataclass
class InfoConfig:
    email: str = MISSING  # Required field
    password: str = MISSING  # Required field
    cvv: str = MISSING  # Required field
    links: List[LinkConfig] = MISSING  # Required field
    chromium: ChromiumConfig = MISSING  # Nested ChromiumConfig object
    log_level: str = "INFO"  # Optional field, default to INFO


_conf = OmegaConf.load("config.yaml")

info_config = OmegaConf.merge(OmegaConf.structured(InfoConfig), _conf)
