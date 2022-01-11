from miners.bosminer import BOSMiner


class BOSMinerS9(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "S9"
        self.api_type = "BOSMiner"

    def __repr__(self) -> str:
        return f"BOSminerS9: {str(self.ip)}"