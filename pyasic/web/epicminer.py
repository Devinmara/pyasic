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
import json
from typing import Union, Any, Literal

import httpx

from pyasic.settings import PyasicSettings
from pyasic.web import BaseWebAPI


class EPICWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.pwd = PyasicSettings().global_epicminer_password

    async def send_privileged_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Any,
    ):
        return await self.send_command(
            command=command,
            ignore_errors=ignore_errors,
            allow_warning=allow_warning,
            **parameters,
            password=self.pwd,
        )

    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Any,
    ) -> dict:
        url = f"http://{self.ip}:4028/{command}"
        try:
            async with httpx.AsyncClient() as client:
                if parameters:
                    data = await client.post(
                        url, data=json.dumps(parameters), timeout=15  # noqa
                    )
                else:
                    data = await client.get(url)
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        async with httpx.AsyncClient() as client:
            # shouldn't need to auth, if needed add
            # await self.auth(client)
            tasks = [
                asyncio.create_task(self._handle_multicommand(client, command))
                for command in commands
            ]
            all_data = await asyncio.gather(*tasks)

        data = {}
        for item in all_data:
            data.update(item)

        data["multicommand"] = True
        return data

    async def _handle_multicommand(self, client: httpx.AsyncClient, command: str):
        try:
            url = f"http://{self.ip}:4028/{command}"
            ret = await client.get(url)
        except httpx.HTTPError:
            pass
        else:
            if ret.status_code == 200:
                try:
                    json_data = ret.json()
                    return {command: json_data}
                except json.decoder.JSONDecodeError:
                    pass
        return {command: {}}

    async def auth(self, client: httpx.AsyncClient) -> None:
        # assume auth is session based
        # assume client is already in use
        url = f"http://{self.ip}:4028/authenticate"
        await client.post(url, json={"password": self.pwd, "param": None})

    async def clear_hashrate(self):
        return await self.send_privileged_command("clearhashrate")

    async def coin(self, conf: dict):
        return await self.send_privileged_command("coin", param=conf)

    async def fanspeed(self, speed: int):
        return await self.send_privileged_command("fanspeed", param=speed)

    async def id(self, unique: bool):
        return await self.send_privileged_command("id", param=unique)

    async def id_variant(self, variant: Literal["IpAddress", "MacAddress", "CpuId"]):
        return await self.send_privileged_command("id/variant", param=variant)

    async def identify(self, led_on: bool):
        return await self.send_privileged_command("identify", param=led_on)

    async def miner(self, autostart: bool):
        if autostart:
            return await self.send_privileged_command("miner", param="Autostart")
        # Not sure if this is right, might be Autostop
        return await self.send_privileged_command("miner", param="stop")

    async def set_network(
        self,
        protocol: Literal["dhcp", "static"],
        ip: str,
        dns: str,
        dns2: str,
        gateway: str,
        mac_address: str,
        subnet_mask: str,
    ) -> dict:
        if protocol == "dhcp":
            return await self.send_privileged_command("network", param={"dhcp": None})
        conf = {
            "address": ip,
            "dns": dns,
            "dns2": dns2,
            "gateway": gateway,
            "mac_address": mac_address,
            "netmask": subnet_mask,
        }

        return await self.send_command("network", param=conf)

    async def password(self, new_pwd: str):
        await self.send_privileged_command("password", param=new_pwd)

    async def set_perpetual_tune(self, perpetual: bool):
        return await self.send_privileged_command("perpetualtune", param=perpetual)

    # TODO: add algo literals, such as Literal["VoltageOptimizer"]
    async def perpetual_tune_algo(self, algo: str, target: int):
        return await self.send_privileged_command("perpetualtune/algo", param={"algo": algo, "target": target})

    # TODO: add algo literals, such as Literal["VoltageOptimizer"]
    async def perpetual_tune_reset(self, algo: str):
        return await self.send_privileged_command("perpetualtune/reset", param=algo)

    async def reboot(self, delay: int = 0):
        return await self.send_privileged_command("reboot", param=delay)

    async def shutdown_temp(self, temp: int):
        return await self.send_privileged_command("shutdowntemp", param=temp)

    async def soft_reboot(self):
        return await self.send_privileged_command("softreboot", param=None)

    async def system_update(self):
        raise NotImplementedError

    async def tune(self, clock: int, voltage: int):
        return await self.send_privileged_command("tune", param={"clks": clock, "voltage":voltage})

    async def tune_clock_all(self, clock: int):
        return await self.send_privileged_command("tune/clock/all", param=clock)

    async def tune_clock_chip(self, conf: dict):
        # using this is awful, too complicated, just let the user send a dict
        return await self.send_privileged_command("tune/clock/chip", param=conf)

    async def tune_clock_voltage(self, voltage: int):
        return await self.send_privileged_command("tune/clock/all", param=voltage)


    async def capabilities(self):
        return await self.send_command("capabilities")

    async def clocks(self):
        return await self.send_command("clocks")

    async def hashrate(self):
        return await self.send_command("hashrate")

    async def hashrate_history_continuous(self):
        return await self.send_command("hashrate/history/continuous")

    async def hashrate_history_discrete(self):
        return await self.send_command("hashrate/history/discrete")

    async def history(self):
        return await self.send_command("history")

    async def log(self):
        return await self.send_command("log")

    async def network(self):
        return await self.send_command("network")

    async def perpetual_tune(self):
        return await self.send_command("perpetualtune")

    async def summary(self):
        return await self.send_command("summary")

    async def temps(self):
        return await self.send_command("temps")

    async def voltages(self):
        return await self.send_command("voltages")