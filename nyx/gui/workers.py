# Copyright 2024, The Tor Project
# See LICENSE for licensing information

"""
QThread workers for async Tor controller queries.
All signals are processed in the main thread (Qt.QueuedConnection).
"""

import time
import threading
import logging
import logging.handlers
import queue

from PyQt6.QtCore import QThread, pyqtSignal

import stem
import stem.control
import stem.util.log

from nyx.country import get_country_name
from nyx.i18n import _

import nyx
import nyx.tracker

from nyx import tor_controller

# Buffer for NYX log messages (nyx/stem Python logging).
# Set up at import time so early messages are not lost.
_NYX_LOG_BUFFER = queue.Queue()
_NYX_LOGGER = logging.handlers.QueueHandler(_NYX_LOG_BUFFER)
_NYX_LOGGER.setLevel(logging.DEBUG)
stem.util.log.get_logger().addHandler(_NYX_LOGGER)


class HeaderWorker(QThread):
    """Updates the header status bar every 2 seconds."""

    status_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._halt = False

    def run(self):
        while not self._halt:
            try:
                data = self._collect()
                self.status_updated.emit(data)
            except Exception as exc:
                stem.util.log.debug(_('HeaderWorker error: %s') % exc)
            for _ in range(20):  # 2 Sekunden in 0.1s-Schritten
                if self._halt:
                    return
                time.sleep(0.1)

    def _collect(self):
        controller = tor_controller()
        data = {
            'connected': False,
            'version': '',
            'pid': None,
            'nickname': '',
            'fingerprint': '',
            'flags': [],
            'cpu': 0.0,
            'memory': 0,
            'memory_percent': 0.0,
            'uptime': 0,
            'or_port': '',
            'dir_port': '',
        }

        if not controller or not controller.is_alive():
            return data

        data['connected'] = True
        data['version'] = str(controller.get_version(''))
        data['pid'] = controller.get_pid(None)
        data['nickname'] = controller.get_conf('Nickname', 'Unnamed')
        data['fingerprint'] = controller.get_info('fingerprint', '')

        start_time = controller.get_start_time(None)
        if start_time:
            data['uptime'] = int(time.time() - start_time)

        try:
            listeners = controller.get_listeners(stem.control.Listener.OR, [])
            if listeners:
                data['or_port'] = str(listeners[0][1])
        except Exception:
            pass

        data['dir_port'] = controller.get_conf('DirPort', '')

        try:
            resources = nyx.tracker.get_resource_tracker().get_value()
            if resources:
                data['cpu'] = resources.cpu_sample * 100
                data['memory'] = resources.memory_bytes
                data['memory_percent'] = resources.memory_percent * 100
        except Exception:
            pass

        try:
            ct = nyx.tracker.get_consensus_tracker()
            entry = ct.my_router_status_entry()
            if entry:
                data['flags'] = [str(f) for f in entry.flags]
        except Exception:
            pass

        return data

    def stop(self):
        self._halt = True


class BandwidthWorker(QThread):
    """Delivers bandwidth data on each BW event (~1/second)."""

    bw_updated = pyqtSignal(int, int)  # bytes_read, bytes_written

    def __init__(self, parent=None):
        super().__init__(parent)
        self._halt = False
        self._lock = threading.Event()
        self._callback = None
        self._controller = None

    def run(self):
        controller = tor_controller()
        if not controller:
            return
        self._controller = controller

        def _on_bw(event):
            if not self._halt:
                self.bw_updated.emit(event.read, event.written)

        self._callback = _on_bw
        controller.add_event_listener(self._callback, stem.control.EventType.BW)

        try:
            while not self._halt:
                time.sleep(0.2)
        finally:
            try:
                controller.remove_event_listener(self._callback)
            except Exception:
                pass

    def stop(self):
        self._halt = True
        if self._callback and self._controller:
            try:
                self._controller.remove_event_listener(self._callback)
            except Exception:
                pass


class LogWorker(QThread):
    """Delivers Tor and nyx log entries in real time."""

    log_entry = pyqtSignal(object)  # nyx.log.LogEntry

    def __init__(self, events=None, parent=None):
        super().__init__(parent)
        self._halt = False
        self._callback = None
        self._events = events or ['NOTICE', 'WARN', 'ERR',
                                   'NYX_NOTICE', 'NYX_WARNING', 'NYX_ERROR']

    def run(self):
        import nyx.log
        import stem.response.events

        # flush past NYX_* messages from the buffer
        while not _NYX_LOG_BUFFER.empty():
            try:
                record = _NYX_LOG_BUFFER.get_nowait()
                self.log_entry.emit(nyx.log.LogEntry(
                    int(record.created),
                    'NYX_%s' % record.levelname,
                    record.msg,
                ))
            except Exception:
                pass

        # forward future NYX_* messages directly
        _original_emit = _NYX_LOGGER.emit

        def _nyx_emit(record):
            if not self._halt:
                self.log_entry.emit(nyx.log.LogEntry(
                    int(record.created),
                    'NYX_%s' % record.levelname,
                    record.msg,
                ))

        _NYX_LOGGER.emit = _nyx_emit

        # load historical Tor logs from the log file
        try:
            log_location = nyx.log.log_file_path(tor_controller())
            if log_location:
                for entry in reversed(list(nyx.log.read_tor_log(log_location))):
                    if not self._halt:
                        self.log_entry.emit(entry)
        except Exception as exc:
            stem.util.log.debug(_('LogWorker: Historical logs not readable: %s') % exc)

        # Live Tor-Events registrieren
        def _on_log(event):
            if self._halt:
                return
            msg = ' '.join(str(event).split(' ')[1:])
            if isinstance(event, stem.response.events.LogEvent):
                msg = event.message
            self.log_entry.emit(nyx.log.LogEntry(event.arrived_at, event.type, msg))

        self._callback = _on_log
        nyx.log.listen_for_events(self._callback, self._events)

        try:
            while not self._halt:
                time.sleep(0.2)
        finally:
            _NYX_LOGGER.emit = _original_emit
            self._remove_listener()

    def _remove_listener(self):
        if self._callback is None:
            return
        try:
            controller = tor_controller()
            if controller:
                controller.remove_event_listener(self._callback)
        except Exception:
            pass

    def stop(self):
        self._halt = True
        self._remove_listener()


class ConnectionWorker(QThread):
    """Updates the connection list every 5 seconds."""

    connections_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._halt = False

    def run(self):
        while not self._halt:
            try:
                data = self._collect()
                self.connections_updated.emit(data)
            except Exception as exc:
                stem.util.log.debug(_('ConnectionWorker error: %s') % exc)
            for _ in range(50):  # 5 Sekunden
                if self._halt:
                    return
                time.sleep(0.1)

    def _collect(self):
        result = []
        try:
            tracker = nyx.tracker.get_connection_tracker()
            if not tracker:
                return result

            connections = tracker.get_value()
            if not connections:
                return result

            controller = tor_controller()
            circuits = {}
            if controller:
                try:
                    for c in controller.get_circuits([]):
                        circuits[c.id] = c
                except Exception as exc:
                    stem.util.log.debug(_('ConnectionWorker: Circuits not retrievable: %s') % exc)

            ct = nyx.tracker.get_consensus_tracker()

            for conn in connections:
                entry = {
                    'type': 'OUTBOUND',
                    'local': '%s:%s' % (conn.local_address, conn.local_port),
                    'remote': '%s:%s' % (conn.remote_address, conn.remote_port),
                    'fingerprint': '',
                    'nickname': '',
                    'country': '',
                    'uptime': int(time.time() - conn.start_time) if conn.start_time else 0,
                }

                try:
                    fp = ct.get_relay_fingerprints(conn.remote_address).get(conn.remote_port)
                    if fp:
                        entry['fingerprint'] = fp[:8] + '...'
                        nick = ct.get_relay_nickname(fp)
                        if nick:
                            entry['nickname'] = nick
                except Exception:
                    pass

                try:
                    country = controller.get_info('ip-to-country/%s' % conn.remote_address, '')
                    code = country.upper()
                    entry['country_code'] = code
                    entry['country'] = get_country_name(code)
                except Exception:
                    pass

                result.append(entry)
        except Exception as exc:
            stem.util.log.debug(_('ConnectionWorker._collect error: %s') % exc)

        return result

    def stop(self):
        self._halt = True


class ConfigWorker(QThread):
    """Loads Tor configuration options once at startup."""

    config_loaded = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._halt = False

    def stop(self):
        self._halt = True

    def run(self):
        try:
            data = self._collect()
            self.config_loaded.emit(data)
        except Exception as exc:
            stem.util.log.debug(_('ConfigWorker error: %s') % exc)
            self.config_loaded.emit([])

    def _collect(self):
        result = []
        controller = tor_controller()
        if not controller:
            return result

        config_names = controller.get_info('config/names', '')
        if not config_names:
            return result

        for line in config_names.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            name, value_type = parts[0], parts[1]
            try:
                value = controller.get_conf(name, '')
                is_set = controller.is_set(name, False)
            except Exception:
                value = ''
                is_set = False

            result.append({
                'name': name,
                'type': value_type,
                'value': value if value else '<default>',
                'is_set': is_set,
                'summary': '',
            })

        return result
