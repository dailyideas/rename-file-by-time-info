import subprocess


def execute(command: list, encoding: str = "utf-8"):
    """Retrieving the output of subprocess.call()

    References:
    - Store output of subprocess.Popen call in a string [duplicate]. https://stackoverflow.com/q/2502833
    """
    result_bytes = subprocess.check_output(command)
    result_str = result_bytes.decode(encoding)
    return result_str.rstrip("\r\n")
