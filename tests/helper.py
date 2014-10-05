from subprocess import Popen, PIPE

def runShellCommand(command):
    """ Runs an arbitrary shell command.

    Returns a tuple containing (STDOUT-output, STDERR-output, return code).
    """
    pipe = Popen( command, stdout=PIPE, stderr=PIPE )
    out, err = pipe.communicate()
    return out, err, pipe.returncode
