import xmlrpc.client

import tspart._files


class NeosPingError(ConnectionError):
    pass


class NeosSubmitError(ConnectionError):
    pass


class NeosSolveError(RuntimeError):
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
    result += tspart._files.make_tsplib(points).replace("\r\n", "\n")
    result += "]]></tsp>\n"

    result += "<ALGTYPE><![CDATA[con]]></ALGTYPE>\n"
    result += "<RDTYPE><![CDATA[fixed]]></RDTYPE>\n"
    result += "<PLTYPE><![CDATA[no]]></PLTYPE>\n"

    result += "<comment><![CDATA[]]></comment>\n"

    result += "</document>"

    return result


def submit_solve(client, email, points):
    xml_request = make_solver_job(email, points)

    job_number, password = client.SubmitJob(xml_request)

    if job_number == 0:
        raise NeosSubmitError(password)

    return job_number, password


def cancel_solve(client, job_number, password):
    client.killJob(job_number, password)


def get_solve(client, job_number, password):
    if client.getJobStatus(job_number, password) != "Done":
        return None

    completion_code = client.getCompletionCode(job_number, password)
    if completion_code != "Normal":
        raise NeosSolveError(f"Neos job completed with failed code: {completion_code}")

    neos_results = client.getFinalResults(job_number, password)

    results_arr = [_.strip() for _ in neos_results.data.decode().split("\n") if _.strip() != ""]

    process_arr = []
    for line in results_arr[::-1]:
        if not all([_.isnumeric() for _ in line.split(" ")]):
            break

        process_arr.append(line)
    process_arr = process_arr[::-1][1:]

    solve = []
    for line in process_arr:
        nums = [int(_) for _ in line.split(" ")]

        solve += nums

    return solve
