
import os
import signal
import dbus

class SleepInhibitor:
    def __init__(self, reason):
        self.what = "idle"
        self.who = "pyPL"
        self.why = reason
        self.mode = "block"
        self.fd = None  # file descriptor
        self.fd_file = None  # file descriptor file
        self.sig_handlers = {}  # original signal handlers

    def __enter__(self):
        try:
            # check that systemd is available
            with open("/proc/1/comm", "r") as f:
                if "systemd" not in f.read().strip():
                    raise Exception("systemd not available")

            # set up dbus connection
            bus = dbus.SystemBus()
            proxy = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
            iface = dbus.Interface(proxy, 'org.freedesktop.login1.Manager')

            # inhibit
            self.fd = iface.Inhibit(
                self.what,
                self.who,
                self.why,
                self.mode,
                byte_arrays=True
            )
            self.fd_file = os.fdopen(self.fd.take(), 'rb')

            # save and override signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGTSTP, signal.SIGHUP):
                self.sig_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, self._cleanup)

        except Exception as e:
            print("Failed to inhibit sleep:", e)
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
    
    def _cleanup(self, signum=None, frame=None):
        # close descriptor file
        if self.fd_file:
            self.fd_file.close()
            self.fd_file = None

        # restore original signal handlers
        for sig, handler in self.sig_handlers.items():
            signal.signal(sig, handler)

        # re-raise signal with default handler
        if signum:
            os.kill(os.getpid(), signum)


class PerformanceHolder:
    def __init__(self, reason):
        self.what = "performance"
        self.who = "pyPL"
        self.why = reason
        self.ppd = None  # power profiles daemon dbus interface
        self.cookie = None  # cookie associated with the profile hold
        self.sig_handlers = {}  # original signal handlers

    def __enter__(self):
        try:
            # check that systemd is available
            with open("/proc/1/comm", "r") as f:
                if "systemd" not in f.read().strip():
                    raise Exception("systemd not available")

            # set up dbus connection
            self.ppd = dbus.Interface(dbus.SystemBus().get_object('net.hadess.PowerProfiles', '/net/hadess/PowerProfiles'), 'net.hadess.PowerProfiles')

            # hold profile
            self.cookie = self.ppd.HoldProfile(
                self.what,
                self.why,
                self.who
            )

            # save and override signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGTSTP, signal.SIGHUP):
                self.sig_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, self._cleanup)

        except Exception as e:
            print("Failed to hold performance profile:", e)
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
    
    def _cleanup(self, signum=None, frame=None):
        # release profile
        if self.cookie:
            self.ppd.ReleaseProfile(self.cookie)

        # restore original signal handlers
        for sig, handler in self.sig_handlers.items():
            signal.signal(sig, handler)

        # re-raise signal with default handler
        if signum:
            os.kill(os.getpid(), signum)
