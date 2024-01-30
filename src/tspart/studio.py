from datetime import datetime
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

    def submit_online_solves(self, email, logging=True):
        self._setup_online_solves()

        def message(text):
            if logging:
                print(text, file=sys.stderr)

        jobs_submitted = 0

        num_jobs_to_submit = sum([_ is None or _ is False for _ in self._jobs])
        if num_jobs_to_submit > 0:
            message(f"Submitting {num_jobs_to_submit} solves...")
            for idx, job in enumerate(self._jobs):
                if job is None or job is False:
                    try:
                        self._jobs[idx] = self._submit_online_solve(
                            points=self.points[idx],
                            email=email
                        )
                        jobs_submitted += 1
                        message(f"Submitted solve #{idx}.")
                    except _neos.NeosSubmitError as e:
                        self._jobs[idx] = False
                        message(f"Failed to submit solve #{idx}.\n{e}")
            message(f"{jobs_submitted} solves submitted.")
        else:
            message("Nothing to submit.")

        if all([_ is True for _ in self._jobs]):
            self.is_routed = True

        return jobs_submitted

    def get_online_solves(self, logging=True):
        if self.points is None:
            raise ValueError("Points not initialized")

        self._setup_online_solves()

        def message(text):
            if logging:
                print(text, file=sys.stderr)

        jobs_gotten = 0
        jobs_in_processing = [isinstance(_, Sequence) for _ in self._jobs]
        num_jobs_in_processing = sum(jobs_in_processing)
        if num_jobs_in_processing > 0:
            message(f"Trying to get {num_jobs_in_processing} solves...")
            for idx, job in enumerate(self._jobs):
                if jobs_in_processing[idx]:
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
                            jobs_gotten += 1
                            message(f"Got solve #{idx}!")
                        else:
                            message(f"Solve #{idx} is still processing.")
                    except (_neos.NeosSolveError, _neos.NeosNoDataError) as e:
                        self._jobs[idx] = False
                        message(f"Solve #{idx} failed.")
                        message(f"--------\n{e}\n^^^^^^^^")
        else:
            message("No solves currently in processing.")

        if all([_ is True for _ in self._jobs]):
            self.is_routed = True

        if jobs_gotten > 0:
            self._compute_factors()

        return jobs_gotten

    def cancel_online_solves(self):
        self._setup_online_solves()

        _neos.cancel_solves(
            client=self.neos,
            job_list=self.jobs
            )

        self.jobs = [_ if isinstance(_, bool) else None for _ in self._jobs]

    def online_solves(
            self,
            email,
            delay_minutes=0.25,
            requeue_minutes=10,
            logging=True,
            save_filename=None
    ):
        if self.points is None:
            raise ValueError("Points not initialized")

        self._setup_online_solves()

        # None = Not scheduled yet (default)
        # Tuple = Currently scheduled, last seen as processing
        # False = Tried and failed
        # True = Tried and succeeded, that channel is sorted

        def message(text):
            if logging:
                print(text, file=sys.stderr)

        def save_file():
            if save_filename is not None:
                self.save(save_filename)
                message(f"Saved to {save_filename}\n")
            else:
                message("\n")

        def delay():
            time.sleep(delay_minutes * 60)

        while any([_ is not True for _ in self._jobs]):
            # Make requests for any failed or unattempted jobs
            last_requeue_time = datetime.now()
            num_jobs_to_submit = sum([_ is None or _ is False for _ in self._jobs])
            if num_jobs_to_submit > 0:
                jobs_submitted = self.submit_online_solves(
                    email=email,
                    logging=logging
                )
                save_file()

                delay()

            # Try to get each job in a loop until they all fail or finish, or until we hit max retries
            jobs_not_ended = [not isinstance(_, bool) for _ in self._jobs]
            while any(jobs_not_ended):
                jobs_gotten = self.get_online_solves(
                    logging=logging
                )

                jobs_not_ended = [not isinstance(_, bool) for _ in self._jobs]
                num_jobs_not_ended = sum(jobs_not_ended)

                requeue_message = ""
                requeue = False
                if requeue_minutes is not None:
                    if (datetime.now() - last_requeue_time).total_seconds() >= requeue_minutes * 60:
                        requeue_message = "Requeue time expired"
                        requeue = True
                if num_jobs_not_ended == 0:
                    requeue_message = "All jobs failed"
                    requeue = True
                if jobs_gotten > 0:
                    requeue_message = "Got result(s)"
                    requeue = True
                if requeue:
                    message(f"{requeue_message}, attempting requeue of needed results (if any)...")
                    save_file()
                    break  # Once we get a result, immediately try requests again

                message(f"Still waiting for {num_jobs_not_ended} solves...")
                save_file()

                delay()

        message(f"All solves done!")

        self.is_routed = True
        save_file()
        return True

    def offline_solves(self, time_limit_minutes=60, symmetric=True, logging=True, verbose=False):
        # TODO: Logging, partial solution saving, checkpointing

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

    def draw(self, scale=1, minimum_line_width_factor=(1/255), closed=True, subpixels=8):
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
                    minimum_line_width_factor=minimum_line_width_factor,
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
                    minimum_line_width_factor=minimum_line_width_factor,
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
                    minimum_line_width_factor=minimum_line_width_factor,
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
