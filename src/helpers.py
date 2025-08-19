
import os
import dbus

class SleepInhibitor:
    def __init__(self, reason):
        self.what = "sleep"
        self.who = "pyPL"
        self.why = reason
        self.mode = "block"
        self.file_descriptor = None
        self.file_descriptor_file = None

    def __enter__(self):
        try:
            with open("/proc/1/comm", "r") as f:
                if "systemd" not in f.read().strip():
                    raise Exception("systemd not available")

            bus = dbus.SystemBus()
            proxy = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
            iface = dbus.Interface(proxy, 'org.freedesktop.login1.Manager')

            self.file_descriptor = iface.Inhibit(
                self.what,
                self.who,
                self.why,
                self.mode,
                byte_arrays=True
            )
            self.file_descriptor_file = os.fdopen(self.file_descriptor.take(), 'rb')
            return self
        
        except Exception:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_descriptor_file:
            self.file_descriptor_file.close()
