# avoid running mpi with serial (1 process) jobs
# by checking whether mpi is actually being used over multiple processes
# Probe number of processes with OMPI_COMM_WORLD_SIZE (openmpi) and MPI_LOCALNRANKS (mpich)

from os import getenv as os_getenv
from sys import modules as sys_modules
from importlib import import_module

_OPENMPI_MULTIPROC = os_getenv('OMPI_COMM_WORLD_SIZE') is not None
_MPICH_MULTIPROC = os_getenv('MPI_LOCALNRANKS') is not None
_MPI_USE_ALWAYS = os_getenv('H5PY_ALWAYS_USE_MPI') is not None

_MPI_ACTIVE = _OPENMPI_MULTIPROC or _MPICH_MULTIPROC or _MPI_USE_ALWAYS

if _MPI_ACTIVE:
    try:
        from . import _debian_h5py_mpi as _h5py
    except:
        from . import _debian_h5py_serial as _h5py
else:
    from . import _debian_h5py_serial as _h5py

__version__ = _h5py.__version__

# make generic h5py module behaviour the same as specific builds
# by importing public and weak internal symbols (single _underscore)
api = [ k for k in _h5py.__dict__.keys() if not k.startswith('__') and not k.endswith('__') ]
this_module=sys_modules[__name__]
for key in api:
    # "imports" symbols (makes them accessible)
    setattr(this_module,key,getattr(_h5py,key))
    # rename symbols as properties of toplevel h5py module
    sys_modules['h5py.{}'.format(key)] = getattr(_h5py,key)
del api
del this_module

# tests are not loaded with h5py, but can be imported separately with
# "import h5py.tests"
tests = import_module('{}.tests'.format(_h5py.__name__))
sys_modules['h5py.tests'] = tests
del tests

# likewise for h5py_warnings
h5pyw = import_module('{}.h5py_warnings'.format(_h5py.__name__))
sys_modules['h5py.h5py_warnings'] = h5pyw
del h5pyw

del os_getenv, sys_modules, import_module
