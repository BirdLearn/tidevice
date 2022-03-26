import pathlib

from genericpath import isdir
from ._sync import Sync
import logging
from ._proto import LOG
from ._safe_socket import PlistSocket


logger = logging.getLogger(LOG.main)

# Ref: https://github.com/libimobiledevice/libimobiledevice/blob/master/tools/idevicecrashreport.c

class CrashManager(object):
    def __init__(self, move_conn: PlistSocket, copy_conn: PlistSocket, output_dir: str):
        self._afc = None
        self._move_conn = move_conn
        self._copy_conn = copy_conn
        self._output_dir = output_dir
        
        self._flush()
        self._afc = Sync(self._copy_conn)
    
    def _flush(self):
        ack = b'ping\x00'
        assert ack == self._move_conn.recvall(len(ack))

    def preview(self):
        logger.info("List of crash logs:")
        r = self._afc.listdir("/")
        if str(r) != "['']":
            self._afc.treeview("/")
        else:
            logger.info("No crash logs found")

    def copy(self):
        self._afc.pull("/", self._output_dir)
        logger.info("Crash file copied to '{}' from device".format(self._output_dir))

    def move(self):
        self._afc.pull("/", self._output_dir)
        self._afc.rmtree("/")
        logger.info("Crash file moved to '{}' from device".format(self._output_dir))

    def remove(self):
        self._afc.rmtree("/")
        logger.info("Crash file purged from device")