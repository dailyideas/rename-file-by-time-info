import subprocess


def execute(command: list, encoding: str = "utf-8") -> str | None:
    """Retrieving the output of subprocess.call()

    References:
    - Store output of subprocess.Popen call in a string [duplicate]. https://stackoverflow.com/q/2502833
    """
    try:
        result_bytes = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        return None
    else:
        return result_bytes.decode(encoding).rstrip("\r\n")
