import os
import shutil
import sys
import time
from enum import Enum
from typing import Sequence, Tuple

import numpy as np
from PIL import Image

from tspart._image import split_cmyk as _split_cmyk
from tspart._image import split_rgb as _split_rgb
from tspart._image import rgb_to_grayscale as _rgb_to_grayscale
from tspart._image import base64_to_image as _base64_to_image
from tspart._image import image_to_base64 as _image_to_base64
from tspart._draw import draw_cmyk_routes as _draw_cmyk_routes
from tspart._draw import draw_rgb_routes as _draw_rgb_routes
from tspart._draw import draw_route as _draw_route
from tspart._helpers import array_to_image as _array_to_image
from tspart._helpers import image_to_array as _image_to_array
from tspart._helpers import image_array_size as _image_array_size
from tspart._helpers import filter_white_points_multi as _filter_white_points_multi
from tspart._helpers import factors_from_image_multi as _factors_from_image_multi
from tspart._helpers import ndarray_to_array_2d as _ndarray_to_array_2d
from tspart._helpers import array_to_ndarray_2d as _array_to_ndarray_2d
from tspart._files import save_json as _save_json
from tspart._files import load_json as _load_json
from tspart import voronoi as _voronoi
from tspart import neos as _neos
from tspart import tsp as _tsp


class ColorMode(Enum):
    CMYK = "CMYK"
    RGB = "RGB"
    GRAYSCALE = "L"


class InadequateResultsWarning(RuntimeWarning):
    pass


class InadequateResultsError(RuntimeError):
    pass


class TspStudio:
    def __init__(
            self,
            mode: ColorMode,
            image: Image.Image | str,
            num_points: int = 5000,
            line_width: float = 2,
            white_threshold: int = 254,
            invert: bool = False,
            background: Tuple[int, int, int] | str = (255, 255, 255),
            foreground: Tuple[int, int, int] | str = (0, 0, 0),
            points: Sequence[Sequence[float | Sequence[float]] | None] | None = None,
            is_routed: bool = False,
            jobs: Sequence[Sequence[int | str] | None | bool] | None = None
    ):
        self.neos = None
        self.factors = None
        self.num_channels = None

        self.mode = mode
        self.invert = invert
        self.image = image
        self.num_points = num_points
        self.line_width = line_width
        self.white_threshold = white_threshold

        self.background = background
        self.foreground = foreground
        self.points = points
        self.is_routed = is_routed
        if jobs is None:
            self.jobs = [None] * self.num_channels
        else:
            self.jobs = jobs

    @property
    def mode(self) -> ColorMode:
        return self._mode

    @mode.setter
    def mode(self, value: ColorMode | str):
        if isinstance(value, ColorMode):
            self._mode = value
        else:
            self._mode = ColorMode(value)

        match self._mode:
            case ColorMode.CMYK:
                self.num_channels = 4
            case ColorMode.RGB:
                self.num_channels = 3
            case ColorMode.GRAYSCALE:
                self.num_channels = 1

    @property
    def image(self) -> Image:
        return _array_to_image(self._image)

    @image.setter
    def image(self, value: Image.Image | str):
        if isinstance(value, str):
            self.image_string = value
            self._image = _image_to_array(_base64_to_image(self.image_string))
        else:
            self._image = _image_to_array(value)
            self.image_string = _image_to_base64(_array_to_image(self._image))

        self.size = _image_array_size(self._image)

        match self.mode:
            case ColorMode.CMYK:
                self.channels = _split_cmyk(self._image, invert=self._real_invert)
            case ColorMode.RGB:
                self.channels = _split_rgb(self._image, invert=self._real_invert)
            case ColorMode.GRAYSCALE:
                self.channels = [_rgb_to_grayscale(self._image, invert=self._real_invert)]

    @property
    def num_points(self) -> int:
        return self._num_points

    @num_points.setter
    def num_points(self, value: int):
        self._num_points = max(1, value)

        self.points = None

    @property
    def line_width(self) -> float:
        return self._line_width

    @line_width.setter
    def line_width(self, value: float | int):
        self._line_width = max(0, value)

    @property
    def white_threshold(self) -> int:
        return self._white_threshold

    @white_threshold.setter
    def white_threshold(self, value: int):
        self._white_threshold = min(255, max(0, value))

    @property
    def invert(self):
        return self._invert

    @invert.setter
    def invert(self, value: bool):
        self._invert = value

        match self.mode:
            case ColorMode.CMYK:
                self._real_invert = self._invert
            case ColorMode.RGB:
                self._real_invert = not self._invert
            case ColorMode.GRAYSCALE:
                self._real_invert = self._invert

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value

    @property
    def foreground(self):
        return self._foreground

    @foreground.setter
    def foreground(self, value):
        self._foreground = value

    @property
    def points(self) -> Sequence[Sequence[float | Sequence[float]]]:
        return self._points

    @points.setter
    def points(self, value: Sequence[Sequence[float | Sequence[float]]] | None):
        self._points = value
        if self._points is None:
            self.factors = None
        else:
            self._compute_factors()

        self.is_routed = False

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
    def jobs(self, value: Sequence[Sequence[int | str] | None | bool]):
        self._jobs = value

    @property
    def data(self):
        return {
            "mode": self.mode,
            "num_points": self.num_points,
            "line_width": self.line_width,
            "white_threshold": self.white_threshold,
            "invert": self.invert,
            "background": self.background,
            "foreground": self.foreground,
            "is_routed": self.is_routed,
            "jobs": self.jobs,
            "points": self.points,
            "image": self.image_string
        }

    def save(self, filename):
        save(
            filename=filename,
            studio=self
        )

    def stipple(self, iterations=50, logging=True):
        self.points = _voronoi.stipple_image_multi(
            grayscale_arrays=self.channels,
            points=self.num_points,
            iterations=iterations,
            logging=logging
        )

        if self.white_threshold < 255:
            self.points = _filter_white_points_multi(
                grayscale_arrays=self.channels,
                points_list=self.points,
                threshold=self.white_threshold
            )

        for idx, p in enumerate(self.points):
            length = len(p)
            if length == 0:
                raise InadequateResultsError(f"Channel {idx}: "
                                             f"Stippling produced no points, try raising the white threshold")
            if length < 100:
                raise InadequateResultsWarning(f"Channel {idx}: "
                                               f"Stippling produced very few ({length}) points, solves may fail")

    def _compute_factors(self):
        if self.points is None:
            raise ValueError("Points not initialized")
        self.factors = _factors_from_image_multi(
            grayscale_arrays=self.channels,
            points_list=self.points
        )

    def _setup_online_solves(self):
        if self.neos is None:
            self.neos = _neos.get_client()

    def _submit_online_solve(self, points, email):
        self._setup_online_solves()

        job_number, password = _neos.submit_solve(
            client=self.neos,
            email=email,
            points=points
        )

        return job_number, password

    def _get_online_solve(self, points, job_number, password):
        self._setup_online_solves()

        return _neos.get_solve(
            client=self.neos,
            job_number=job_number,
            password=password,
            points=points
        )

    def online_solves(self, email, delay_minutes=0.25, max_tries=3, logging=True, save_filename=None):
        if self.points is None:
            raise ValueError("Points not initialized")

        self._setup_online_solves()

        # TODO: Implement max tries, if any channel hits the limit, give up on it, set job to False, and throw a warning

        # None = Not scheduled yet (default)
        # Tuple = Currently scheduled, last seen as processing
        # False = Tried and failed
        # True = Tried and succeeded, that channel is sorted

        tries = [0] * self.num_channels
        jobs_not_completed = [_ is not True for _ in self._jobs]
        while any(jobs_not_completed):
            if logging:
                print(f"Submitting {sum(jobs_not_completed)} solves...", file=sys.stderr)

            # Make requests for any failed or unattempted jobs
            for idx, job in enumerate(self._jobs):
                if job is None or job is False:
                    if logging:
                        print(f"Submitting solve #{idx}.", file=sys.stderr)
                    if tries[idx] == max_tries:
                        if logging:
                            print(f"Reached max tries for solve #{idx}, canceling other solves", file=sys.stderr)
                        self.cancel_online_solves()
                        return False
                    try:
                        self._jobs[idx] = self._submit_online_solve(
                            points=self.points[idx],
                            email=email
                        )
                    except:
                        self._jobs[idx] = False
                        if logging:
                            print(f"Failed to submit solve #{idx} failed, will retry later.", file=sys.stderr)

            if save_filename is not None:
                self.save(save_filename)
                if logging:
                    print(f"Saved to {save_filename}", file=sys.stderr)

            # Try to get each job in a loop until they all fail or finish
            jobs_not_ended = [not isinstance(_, bool) for _ in self._jobs]
            while any(jobs_not_ended):
                if logging:
                    print(f"Trying to get {sum(jobs_not_ended)} solves...", file=sys.stderr)
                for idx, job in enumerate(self._jobs):
                    if not isinstance(job, bool) and job is not None:
                        job_number, password = job
                        try:
                            result = self._get_online_solve(
                                points=self.points[idx],
                                job_number=job_number,
                                password=password
                            )
                            if result is not None:
                                self._points[idx] = result
                                self._jobs[idx] = True
                                if logging:
                                    print(f"Got solve #{idx}!", file=sys.stderr)
                            else:
                                if logging:
                                    print(f"Still waiting for solve #{idx}...", file=sys.stderr)
                        except _neos.NeosSolveError as e:
                            self._jobs[idx] = False
                            tries[idx] += 1
                            if logging:
                                print(f"Solve #{idx} failed, will retry later.", file=sys.stderr)

                jobs_not_ended = [not isinstance(_, bool) for _ in self._jobs]

                if logging:
                    print(f"Still waiting for {sum(jobs_not_ended)} solves...", file=sys.stderr)

                if save_filename is not None:
                    self.save(save_filename)
                    if logging:
                        print(f"Saved to {save_filename}", file=sys.stderr)

                time.sleep(delay_minutes * 60)

            jobs_not_completed = [_ is not True for _ in self._jobs]

        if logging:
            print(f"All solves done!", file=sys.stderr)

        return True

    def cancel_online_solves(self):
        self._setup_online_solves()

        _neos.cancel_solves(
            client=self.neos,
            job_list=self.jobs
            )

        self.jobs = [None] * self.num_channels

    '''
    def submit_online_solves(self, email):
        if self.points is None:
            raise ValueError("Points not initialized")

        self._setup_online_solves()
        self.cancel_online_solves()

        self.jobs = _neos.submit_solves(
            client=self.neos,
            email=email,
            points_list=self.points
        )
    '''

    '''
    def get_online_solves(self) -> bool:
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.jobs is None:
            raise ValueError("Jobs not initialized")

        self._setup_online_solves()

        results = _neos.get_solves(
            client=self.neos,
            job_list=self.jobs,
            points_list=self.points
        )

        if all([_ is not None for _ in results]):
            self.points = results
            self.is_routed = True
            self.jobs = [None] * self.num_channels
            return True

        return False
    '''

    '''
    def get_online_solves_blocking(self, delay_minutes=0.25, logging=True):
        if self.points is None:
            raise ValueError("Points not initialized")
        if self.jobs is None:
            raise ValueError("Jobs not initialized")

        self._setup_online_solves()

        results = _neos.get_solves_blocking(
            client=self.neos,
            job_list=self.jobs,
            points_list=self.points,
            delay_minutes=delay_minutes,
            logging=logging
        )

        self.points = results
        self.is_routed = True
        self.jobs = [None] * self.num_channels
    '''

    def offline_solves(self, time_limit_minutes=60, symmetric=True, logging=True, verbose=False):
        if self.points is None:
            raise ValueError("Points not initialized")

        self.cancel_online_solves()

        results = _tsp.heuristic_solves(
            points_list=self.points,
            time_limit_minutes=time_limit_minutes,
            symmetric=symmetric,
            logging=logging,
            verbose=verbose
        )

        if all([_ is not None for _ in results]):
            self.points = results
            self.jobs = [True] * len(results)
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
            case ColorMode.CMYK:
                return _draw_cmyk_routes(
                    cmyk_points=self.points,
                    cmyk_factors=self.factors,
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    subpixels=subpixels
                )
            case ColorMode.RGB:
                return _draw_rgb_routes(
                    rgb_points=self.points,
                    rgb_factors=self.factors,
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    subpixels=subpixels
                )
            case ColorMode.GRAYSCALE:
                return _draw_route(
                    points=self.points[0],
                    factors=self.factors[0],
                    size=self.size,
                    line_width=self.line_width,
                    scale=scale,
                    closed=closed,
                    background=self.background,
                    foreground=self.foreground,
                    subpixels=subpixels
                )


def load(filename) -> TspStudio:
    obj = _load_json(filename)

    obj["mode"] = ColorMode(obj["mode"])
    if obj["points"] is not None:
        obj["points"] = _array_to_ndarray_2d(obj["points"])
    obj["background"] = tuple(obj["background"])
    obj["foreground"] = tuple(obj["foreground"])

    return TspStudio(
        mode=obj["mode"],
        image=obj["image"],
        num_points=obj["num_points"],
        line_width=obj["line_width"],
        white_threshold=obj["white_threshold"],
        invert=obj["invert"],
        background=obj["background"],
        foreground=obj["foreground"],
        points=obj["points"],
        is_routed=obj["is_routed"],
        jobs=obj["jobs"]
    )


def save(filename, studio, round_places=2):
    obj = studio.data

    obj["mode"] = obj["mode"].value
    if obj["points"] is not None:
        obj["points"] = _ndarray_to_array_2d(
            array=obj["points"],
            round_places=round_places
        )

    _save_json(filename, obj, indent=None)
