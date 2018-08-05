from .asyncnet import AsyncNetMode as asyncnet
from .mproc import MultiProcessMode as mproc
from .mthread import MultiThreadMode as mthread
from .traditional import TraditionalMode as traditional


# registering concurrent mode
factory = {
    asyncnet.NAME: asyncnet,
    mproc.NAME: mproc,
    mthread.NAME: mthread,
    traditional.NAME: traditional
}
