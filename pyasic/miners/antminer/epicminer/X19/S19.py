# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

from pyasic.miners.backends import EPICMiner
from pyasic.miners.types import (
    S19,
    S19L,
    S19XP,
    S19a,
    S19aPro,
    S19j,
    S19jNoPIC,
    S19jPro,
    S19Pro,
    S19ProPlus,
)


class EPICS19(EPICMiner, S19):
    pass


class EPICS19Pro(EPICMiner, S19Pro):
    pass


class EPICS19ProPlus(EPICMiner, S19ProPlus):
    pass


class EPICS19XP(EPICMiner, S19XP):
    pass


class EPICS19a(EPICMiner, S19a):
    pass


class EPICS19aPro(EPICMiner, S19aPro):
    pass


class EPICS19j(EPICMiner, S19j):
    pass


class EPICS19jNoPIC(EPICMiner, S19jNoPIC):
    pass


class EPICS19jPro(EPICMiner, S19jPro):
    pass


class EPICS19L(EPICMiner, S19L):
    pass
