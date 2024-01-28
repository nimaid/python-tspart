import sys
import time
import xmlrpc.client

from tspart._files import make_tsplib as _make_tsplib
from tspart._helpers import map_points_to_tour as _map_points_to_tour


class NeosPingError(ConnectionError):
    pass


class NeosSubmitError(ConnectionError):
    pass


class NeosSolveError(RuntimeError):
    pass


class NeosNoDataError(RuntimeError):
    pass


def get_client(url="https://neos-server.org:3333"):
    client = xmlrpc.client.ServerProxy(url)

    if client.ping() != "NeosServer is alive\n":
        raise NeosPingError("Could not verify that Neos is online")

    return client


def make_solver_job(email, points):
    result = "<document>\n"

    result += "<category>co</category>\n"
    result += "<solver>concorde</solver>\n"
    result += "<inputMethod>TSP</inputMethod>\n"
    result += f"<email><![CDATA[{email}]]></email>\n"

    result += "<tsp><![CDATA[\n"
    result += _make_tsplib(points).replace("\r\n", "\n")
    result += "]]></tsp>\n"

    result += "<ALGTYPE><![CDATA[con]]></ALGTYPE>\n"
    result += "<RDTYPE><![CDATA[fixed]]></RDTYPE>\n"
    result += "<PLTYPE><![CDATA[no]]></PLTYPE>\n"

    result += "<comment><![CDATA[]]></comment>\n"

    result += "</document>"

    return result


def submit_solve(client, email, points):
    xml_request = make_solver_job(email, points)

    job_number, password = client.submitJob(xml_request)

    if job_number == 0:
        raise NeosSubmitError(password)

    return job_number, password


def submit_solves(client, email, points_list):
    result = []
    for points in points_list:
        r = submit_solve(
            client=client,
            email=email,
            points=points
        )

        result.append(r)

    return result


def cancel_solve(client, job_number, password):
    client.killJob(job_number, password)


def cancel_solves(client, job_list):
    for job in job_list:
        if job is None or isinstance(job, bool):
            continue

        job_number, password = job
        cancel_solve(
            client=client,
            job_number=job_number,
            password=password
        )


def get_solve(client, job_number, password, points=None):
    if client.getJobStatus(job_number, password) != "Done":
        return None

    completion_code = client.getCompletionCode(job_number, password)
    neos_results = client.getFinalResults(job_number, password)
    neos_results = neos_results.data.decode()
    if completion_code != "Normal":
        raise NeosSolveError(f"Neos job completed with failed code: {completion_code}\n\n"
                             f"Full response:\n"
                             f"{neos_results}")

    results_arr = [_.strip() for _ in neos_results.split("\n") if _.strip() != ""]

    # Get the tour indexes from the raw response
    raw_tour = []
    for line in results_arr[::-1]:
        if not all([_.isnumeric() for _ in line.split(" ")]):
            break

        raw_tour.append(line)

    if len(raw_tour) == 0:
        raise NeosNoDataError(f"Neos job did not return any data, got response:\n\n{neos_results}")

    raw_tour = raw_tour[::-1][1:]

    if len(raw_tour[0].split(" ")) == 3:
        short_mode = True
    else:
        short_mode = False

    tour = []
    for line in raw_tour:
        line = line.split(" ")
        if short_mode:
            tour.append(int(line[0]))
        else:
            nums = [int(_) for _ in line]
            tour += nums

    if points is None:
        return tour

    return _map_points_to_tour(points, tour)


def get_solves(client, job_list, points_list=None):
    result = []
    for idx, (job_number, password) in enumerate(job_list):
        points = None
        if points_list is not None:
            points = points_list[idx]

        r = get_solve(
            client=client,
            job_number=job_number,
            password=password,
            points=points
        )

        result.append(r)

    return result
