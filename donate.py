import os


class Donate:
    def __init__(self) -> None:
        self.DONTATION_DATA_FILE = "Donate/donation_data.json"
        pass

    def getDonationData(self):
        with open(self.DONTATION_DATA_FILE, "r") as donation_data:
            print(donation_data)
