import os
import shutil
from enum import Enum
from typing import Sequence

import numpy as np
from PIL import Image

from tspart._image import split_cmyk as _split_cmyk
from tspart._image import split_rgb as _split_rgb
from tspart._image import rgb_to_grayscale as _rgb_to_grayscale
from tspart._draw import draw_cmyk_routes as _draw_cmyk_routes
from tspart._draw import draw_rgb_routes as _draw_rgb_routes
from tspart._draw import draw_route as _draw_route
from tspart._helpers import array_to_image as _array_to_image
from tspart._helpers import image_to_array as _image_to_array
from tspart._helpers import image_array_size as _image_array_size
from tspart._helpers import filter_white_points_multi as _filter_white_points_multi
from tspart._helpers import factors_from_image_multi as _factors_from_image_multi
from tspart import voronoi as _voronoi
from tspart import neos as _neos
from tspart import tsp as _tsp


class TspStudioMode(Enum):
    CMYK = "CMYK"
    RGB = "RGB"
    GRAYSCALE = "L"


class TspStudio:
    def __init__(
            self,
            mode: TspStudioMode,
            image: Image,
            num_points: int = 5000,
            line_width: float = 2,
            white_threshold: int = 1,
            points: Sequence[Sequence[float | Sequence[float]]] | None = None,
            is_routed: bool = False,
            jobs: Sequence[Sequence[int | str]] | None = None
    ):
        self.mode = mode
        self.image = image
        self.num_points = num_points
        self.line_width = line_width
        self.white_threshold = white_threshold
        self.points = points
        self.is_routed = is_routed
        self.jobs = jobs

        self.neos = None
        self.factors = None

    @property
    def mode(self) -> TspStudioMode:
        return self._mode

    @mode.setter
    def mode(self, value: TspStudioMode | str):
        if isinstance(value, TspStudioMode):
            self._mode = value
        else:
            self._mode = TspStudioMode(value)

    @property
    def image(self) -> Image:
        return _array_to_image(self._image)

    @image.setter
    def image(self, value: Image):
        self._image = _image_to_array(value)

        self.size = _image_array_size(self._image)

        match self.mode:
            case TspStudioMode.CMYK:
                self.channels = _split_cmyk(self._image, invert=False)
            case TspStudioMode.RGB:
                self.channels = _split_rgb(self._image, invert=True)
            case TspStudioMode.GRAYSCALE:
                self.channels = [_rgb_to_grayscale(self._image, invert=False)]

    @property
    def num_points(self) -> int:
        return self._num_points

    @num_points.setter
    def num_points(self, value: int):
        self._num_points = min(1, value)

        self.points = None
        self.is_routed = False
        self.factors = None

    @property
    def line_width(self) -> float:
        return self._line_width

    @line_width.setter
    def line_width(self, value: float | int):
        self._line_width = min(0, value)

    @property
    def white_threshold(self) -> int:
        return self._white_threshold

    @white_threshold.setter
    def white_threshold(self, value: int):
        self._white_threshold = min(1, value)

    @property
    def points(self) -> Sequence[Sequence[float | Sequence[float]]]:
        return self._points

    @points.setter
    def points(self, value: Sequence[Sequence[float | Sequence[float]]] | None):
        self._points = value
        self.is_routed = False
        self.factors = None

    @property
    def is_routed(self) -> bool:
        return self._is_routed

    @is_routed.setter
    def is_routed(self, value: bool):
        self._is_routed = value

    @property
    def jobs(self) -> Sequence[Sequence[int | str]]:
        return self._jobs

    @jobs.setter
    def jobs(self, value: Sequence[Sequence[int | str]] | None):
        self._jobs = value

    @property
    def data(self):
        return {
            "mode": self.mode,
            "image": self.image,
            "num_points": self.num_points,
            "line_width": self.line_width,
            "white_threshold": self.white_threshold,
            "points": self.points,
            "is_routed": self.is_routed,
            "jobs": self.jobs
        }

    def stipple(self, iterations=50, logging=True):
        self.points = _voronoi.stipple_image_multi(
            grayscale_arrays=self.channels,
            points=self.num_points,
            iterations=iterations,
            logging=logging
        )

    def remove_white_points(self, threshold=1, blur_sigma=1):
        if self.points is None:
            raise ValueError("Points not initialized")

        self.points = _filter_white_points_multi(
            grayscale_arrays=self.channels,
            points_list=self.points,
            threshold=threshold,
            blur_sigma=blur_sigma
        )

    def setup_online_solve(self):
        if self.neos is None:
            self.neos = _neos.get_client()

    def submit_online_solve(self, email):
        if self.points is None:
            raise ValueError("Points not initialized")

        self.setup_online_solve()
        self.cancel_online_solve()

        self.jobs = _neos.submit_solves(
            client=self.neos,
            email=email,
            points_list=self.points
        )

    def cancel_online_solve(self):
        self.setup_online_solve()

        if self.jobs is not None:
            _neos.cancel_solves(
                client=self.neos,
                job_list=self.jobs
            )

        self.jobs = None

    def get_online_solve(self) -> bool:
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.jobs is None:
            raise ValueError("Jobs not initialized")

        results = _neos.get_solves(
            client=self.neos,
            job_list=self.jobs,
            points_list=self.points
        )

        if all([_ is not None for _ in results]):
            self.points = results
            self.factors = _factors_from_image_multi(
                grayscale_arrays=self.channels,
                points_list=self.points
            )
            self.is_routed = True
            return True

        return False

    def get_online_solve_blocking(self, delay_minutes=0.25, logging=True):
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.jobs is None:
            raise ValueError("Jobs not initialized")

        results = _neos.get_solves_blocking(
            client=self.neos,
            job_list=self.jobs,
            points_list=self.points,
            delay_minutes=delay_minutes,
            logging=logging
        )

        self.points = results
        self.factors = _factors_from_image_multi(
            grayscale_arrays=self.channels,
            points_list=self.points
        )
        self.is_routed = True

    def offline_solves(self, time_limit_minutes=60, symmetric=True, logging=True, verbose=False):
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.jobs is None:
            raise ValueError("Jobs not initialized")

        results = _tsp.heuristic_solves(
            points_list=self.points,
            time_limit_minutes=time_limit_minutes,
            symmetric=symmetric,
            logging=logging,
            verbose=verbose
        )

        if all([_ is not None for _ in results]):
            self.points = results
            self.factors = _factors_from_image_multi(
                grayscale_arrays=self.channels,
                points_list=self.points
            )
            self.is_routed = True
            return True

        return False

    def draw(self, scale=1, closed=True, subpixels=8):
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.factors is None:
            raise ValueError("Factors not initialized")
        if not self.is_routed:
            raise ValueError("Not routed yet")

        match self.mode:
            case TspStudioMode.CMYK:
                return _draw_cmyk_routes(
                    cmyk_points=self.points,
                    cmyk_factors=self.factors,
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    subpixels=subpixels
                )
            case TspStudioMode.RGB:
                return _draw_rgb_routes(
                    rgb_points=self.points,
                    rgb_factors=self.factors,
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    subpixels=subpixels
                )
            case TspStudioMode.GRAYSCALE:
                return _draw_route(
                    points=self.points[0],
                    factors=self.factors[0],
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    subpixels=subpixels
                )
