
from time import time
from google.protobuf import descriptor

import api.gplay_pb2 as gplay

class GooglePlayAPI():

    def checkin(self):
        pass

    def _generate_checkin_request(self):
        """Generate a AndroidCheckinRequest for a Oneplus One"""
        req = gplay.AndroidCheckinRequest()
        req.id = 0
        req.checkin.build.id = (
            "bacon-userdebug 6.0.1 MMB29X 6c84ef4d4c test-keys")
        req.checkin.build.product = "MSM8974"
        req.checkin.build.client = "android-google"
        req.checkin.build.timestamp = int(time())
        req.checkin.build.carrier = "Telekom"
        req.checkin.build.model = "A0001"
        req.checkin.build.bootloader = "unknown"
        req.checkin.build.manufacturer = "oneplus"
        req.checkin.build.otaInstalled = False
        req.checkin.lastCheckinMsec = 0
        req.checkin.roaming = ("mobile-notroaming")
        req.checkin.simOperator = "26201"
        req.checkin.cellOperator = "26201"
        req.checkin.userNumber = 0
        req.deviceConfiguration.touchScreen = 3
        req.deviceConfiguration.keyboard = 1
        req.deviceConfiguration.navigation = 1
        req.deviceConfiguration.screenLayout = 2
        req.deviceConfiguration.hasHardKeyboard = False
        req.deviceConfiguration.screenDensity = 400
        req.deviceConfiguration.nativePlatform
            .extend(["armeabi-v7l", "armeabi"])
        req.deviceConfiguration.screenWidth = 1080
        req.deviceConfiguration.screenHeight = 1920
        req.locale="en_US"
        req.timeZone = "Europe/Berlin"
        req.version = 3
        req.fragment = 0
        # important TODO: make configurable
        req.checkin.build.sdkVersion = 23
        return req
