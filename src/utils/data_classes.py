from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0

@dataclass
class WindowInfo:
    name: str
    x: float
    y: float
    height: float
    width: float

@dataclass
class WindowConfig:
    x: int
    y: int
    width: int
    height: int
    pen_color: str
    pen_size: int

