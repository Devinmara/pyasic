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
import asyncio
import logging
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import toml

from pyasic.API.bosminer import BOSMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.web.bosminer import BOSMinerWebAPI
from pyasic.web.epicminer import EPICWebAPI

EPICMINER_DATA_LOC = {
    "mac": {
        "cmd": "get_mac",
        "kwargs": {"web_network": {"web": "network"}},
    },
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {
        "cmd": "get_api_ver",
        "kwargs": {},
    },
    "fw_ver": {
        "cmd": "get_fw_ver",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "hostname": {
        "cmd": "get_hostname",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "hashrate": {
        "cmd": "get_hashrate",
        "kwargs": {"web_hashrate": {"web": "hashrate"}},
    },
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {},
    },
    "hashboards": {
        "cmd": "get_hashboards",
        "kwargs": {},
    },
    "wattage": {
        "cmd": "get_wattage",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "wattage_limit": {
        "cmd": "get_wattage_limit",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "fans": {
        "cmd": "get_fans",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {"web_summary": {"web": "summary"}}},
    "temperature_avg": {
        "cmd": "get_env_temp",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "errors": {
        "cmd": "get_errors",
        "kwargs": {},
    },
    "fault_light": {
        "cmd": "get_fault_light",
        "kwargs": {},
    },
    "pools": {
        "cmd": "get_pools",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "is_mining": {
        "cmd": "is_mining",
        "kwargs": {},
    },
    "uptime": {
        "cmd": "get_uptime",
        "kwargs": {},
    },
}


class EPICMiner(BaseMiner):
    def __init__(self, ip: str, api_ver="0.0.0") -> None:
        super().__init__(ip)
        # interfaces
        self.web = EPICWebAPI(ip)
        # self.web = BOSMinerWebAPI(ip)

        # static data
        self.api_type = "EPICMiner"
        # data gathering locations
        self.data_locations = EPICMINER_DATA_LOC
        # autotuning/shutdown support
        # self.supports_autotuning = True
        # self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def fault_light_on(self) -> bool:
        """Turn the fault light of the miner on and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light on.
        """
        pass

    async def fault_light_off(self) -> bool:
        """Turn the fault light of the miner off and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light off.
        """
        pass

    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        """Get the uptime of the miner in seconds.

        Returns:
            The uptime of the miner in seconds.
        """
        data = await self.web.send_command("summary")
        if data is not None:
            return data["Session"]["Uptime"]

    async def get_config(self) -> MinerConfig:
        # Not a data gathering function, since this is used for configuration and not MinerData
        """Get the mining configuration of the miner and return it as a [`MinerConfig`][pyasic.config.MinerConfig].

        Returns:
            A [`MinerConfig`][pyasic.config.MinerConfig] containing the pool information and mining configuration.
        """
        pass

    async def reboot(self) -> bool:
        """Reboot the miner and return success as a boolean.

        Returns:
            A boolean value of the success of rebooting the miner.
        """
        pass

    async def restart_backend(self) -> bool:
        """Restart the mining process of the miner (bosminer, bmminer, cgminer, etc) and return success as a boolean.

        Returns:
            A boolean value of the success of restarting the mining process.
        """
        pass

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Set the mining configuration of the miner.

        Parameters:
            config: A [`MinerConfig`][pyasic.config.MinerConfig] containing the mining config you want to switch the miner to.
            user_suffix: A suffix to append to the username when sending to the miner.
        """
        return None

    async def stop_mining(self) -> bool:
        """Stop the mining process of the miner.

        Returns:
            A boolean value of the success of stopping the mining process.
        """
        pass

    async def resume_mining(self) -> bool:
        """Resume the mining process of the miner.

        Returns:
            A boolean value of the success of resuming the mining process.
        """
        pass

    async def set_power_limit(self, wattage: int) -> bool:
        """Set the power limit to be used by the miner.

        Parameters:
            wattage: The power limit to set on the miner.

        Returns:
            A boolean value of the success of setting the power limit.
        """
        pass

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self, web_network: dict) -> Optional[str]:
        """Get the MAC address of the miner and return it as a string.

        Returns:
            A string representing the MAC address of the miner.
        """
        if web_network is None:
            try:
                web_network = await self.web.network()
            except APIError:
                pass

        if web_network is not None:
            try:
                return web_network["dhcp"]["mac_address"]
            except LookupError:
                pass
        return self.fw_ver

    async def get_model(self) -> Optional[str]:
        """Get the model of the miner and return it as a string.

        Returns:
            A string representing the model of the miner.
        """
        if self.model is not None:
            return self.model + " (ePIC)"
        return "? (ePIC)"

    async def get_api_ver(self, *args, **kwargs) -> Optional[str]:
        """Get the API version of the miner and is as a string.

        Returns:
            API version as a string.
        """
        pass

    async def get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        """Get the firmware version of the miner and is as a string.

        Returns:
            Firmware version as a string.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                self.fw_ver = web_summary["Software"]
            except LookupError:
                pass
        return self.fw_ver

    async def get_version(self, *args, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """Get the API version and firmware version of the miner and return them as strings.

        Returns:
            A tuple of (API version, firmware version) as strings.
        """
        pass

    async def get_hostname(self, web_summary: dict = None) -> Optional[str]:
        """Get the hostname of the miner and return it as a string.

        Returns:
            A string representing the hostname of the miner.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                self.hostname = web_summary["Hostname"]
            except LookupError:
                pass
        return self.hostname

    async def get_nominal_hashrate(self) -> Optional[float]:
        """Get the hashrate of the miner and return it as a float in TH/s.

        Returns:
            Hashrate of the miner in TH/s as a float.
        """
        return None

    async def get_hashrate(self, web_hashrate: dict) -> Optional[float]:
        """Get the hashrate of the miner and return it as a float in TH/s.

        Returns:
            Hashrate of the miner in TH/s as a float.
        """
        if web_hashrate is None:
            try:
                web_hashrate = await self.web.hashrate()
            except APIError:
                pass

        if web_hashrate is not None:
            try:
                total_hash = 0
                for d in web_hashrate:
                    total_hash += d["Total"][0] / 1000000
                return total_hash
            except LookupError:
                pass
        return self.hostname

    async def get_hashboards(self, web_summary: dict = None) -> List[HashBoard]:
        """Get hashboard data from the miner in the form of [`HashBoard`][pyasic.data.HashBoard].

        Returns:
            A [`HashBoard`][pyasic.data.HashBoard] instance containing hashboard data from the miner.
        """
        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                hb_list = web_summary["HBs"]
                # might have to check by index?
                for idx in range(len(hb_list)):
                    hashboards[idx].hashrate = round(hb_list[idx]["Hashrate"][0] / 1000000, 2)
                    hashboards[idx].temp = round(hb_list[idx]["Temperature"], 2)
                    hashboards[idx].chip_temp = round(hb_list[idx]["Temperature"], 2)
                    hashboards[idx].missing = False
            except LookupError:
                pass
        return hashboards

    async def get_env_temp(self, web_summary: dict = None) -> Optional[float]:
        """Get environment temp from the miner as a float.

        Returns:
            Environment temp of the miner as a float.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                temp_avg = 0
                count = 0
                for i, d in enumerate(web_summary["HBs"]):
                    temp_avg += d["Temperature"]
                    count += i
                return temp_avg / count
            except LookupError:
                pass

    async def get_wattage(self, web_summary: dict = None) -> Optional[int]:
        """Get wattage from the miner as an int.

        Returns:
            Wattage of the miner as an int.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                return web_summary["Power Supply Stats"]["Input Power"]
            except LookupError:
                pass

    async def get_wattage_limit(self, web_summary: dict = None) -> Optional[int]:
        """Get wattage limit from the miner as an int.

        Returns:
            Wattage limit of the miner as an int.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                return web_summary["Power Supply Stats"]["Target Voltage"]
            except LookupError:
                pass

    async def get_fans(self, web_summary: dict = None) -> List[Fan]:
        """Get fan data from the miner in the form [fan_1, fan_2, fan_3, fan_4].

        Returns:
            A list of fan data.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        fans = []
        if web_summary is not None:
            try:
                for i, d in enumerate(web_summary["Fans Rpm"]):
                    fan_value = web_summary["Fans Rpm"][f"{d}"]
                    fans.append(Fan(speed=fan_value))
            except LookupError:
                pass
        return fans

    async def get_fan_psu(self, *args, **kwargs) -> Optional[int]:
        """Get PSU fan speed from the miner.

        Returns:
            PSU fan speed.
        """
        pass

    async def get_pools(self, web_summary: dict = None) -> List[dict]:
        """Get pool information from the miner.

        Returns:
            Pool groups and quotas in a list of dicts.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            groups = []
            try:
                pools = {}
                pools_config = web_summary["StratumConfigs"]
                for i, pool in enumerate(pools_config):
                    pools[f"pool_{i+1}_url"] = (
                        pool["pool"]
                        .replace("stratum+tcp://", "")
                        .replace("stratum2+tcp://", "")
                    )
                    pools[f"pool_{i+1}_user"] = pool["login"]
                groups.append(pools)
            except Exception as ex:
                logging.debug(f"Error getting pools for Epic: {ex}")
        return groups

    async def get_errors(self, *args, **kwargs) -> List[MinerErrorData]:
        """Get a list of the errors the miner is experiencing.

        Returns:
            A list of error classes representing different errors.
        """
        pass

    async def get_fault_light(self, *args, **kwargs) -> bool:
        """Check the status of the fault light and return on or off as a boolean.

        Returns:
            A boolean value where `True` represents on and `False` represents off.
        """
        pass

    async def is_mining(self, web_summary: dict = None) -> Optional[bool]:
        """Check whether the miner is mining.

        Returns:
            A boolean value representing if the miner is mining.
        """
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                return web_summary["Status"]["Operating State"] == "Mining"
            except LookupError:
                pass
