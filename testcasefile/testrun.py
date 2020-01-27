import subprocess
import resource
from platform import system

def runCommand(*popenargs,input=None, capture_output=False, timeout=None, check=False,memorylimit=300,**kwargs):
    #mocking the standard implementation of subprocess.run
    #so we can set memory limit
    if input is not None:
        if kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError('stdout and stderr arguments may not be used '
                             'with capture_output.')
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    with subprocess.Popen(*popenargs, **kwargs) as process:
        if system()=='Linux':
            memorylimithard=memorylimit*1024**2+10024
            resource.prlimit(process.pid,resource.RLIMIT_STACK,(memorylimit*1024**2,memorylimithard))
            resource.prlimit(process.pid,resource.RLIMIT_DATA,(memorylimit*1024**2,memorylimithard))
        try:
            stdout, stderr = process.communicate(input, timeout=1)
            print(stdout,stderr)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            if subprocess._mswindows:
                # Windows accumulates the output in a single blocking
                # read() call run on child threads, with the timeout
                # being done in a join() on those threads.  communicate()
                # _after_ kill() is required to collect that and add it
                # to the exception.
                exc.stdout, exc.stderr = process.communicate()
            else:
                # POSIX _communicate already populated the output so
                # far into the TimeoutExpired exception.
                process.wait()
            raise
        except:  # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            raise
        retcode = process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(process.args, retcode, stdout, stderr)


print(runCommand(["go","run","test.go"] ,capture_output=True,timeout= 1,input='2\n7\n8\n9\n10',encoding="utf-8"))
