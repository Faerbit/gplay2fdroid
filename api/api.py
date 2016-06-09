
from time import time
from google.protobuf import descriptor

import requests

import api.gplay_pb2 as gplay

class GooglePlayAPI():

    BASE_URL = "https://android.clients.google.com/"
    CHECKIN_URL = BASE_URL + "checkin"

    def checkin(self):
        """Posts a Android Checkin"""
        headers = dict()
        headers["Host"] = "android.clients.google.com"
        headers["Content-Type"] = "application/x-protobuffer"
        resp = requests.post(self.CHECKIN_URL,
                data = self._generate_checkin_request().SerializeToString(),
                headers=headers)
        if resp.status_code != 200:
            print("ERROR: Response body:\n {}"
                    .format(resp.content.decode("utf-8")))
            return None
        else:
            and_resp = gplay.AndroidCheckinResponse().FromString(resp.content)
            print(and_resp)
            return and_resp


    def _generate_checkin_request(self):
        """Generates a AndroidCheckinRequest for a Oneplus One"""
        # the commented lines are not necessary to get a valid android id
        # but I'm leaving them here should they become necessary
        req = gplay.AndroidCheckinRequest()
        req.id = 0
        #req.checkin.build.id = (
        #    "bacon-userdebug 6.0.1 MMB29X 6c84ef4d4c test-keys")
        #req.checkin.build.product = "MSM8974"
        #req.checkin.build.client = "android-google"
        #req.checkin.build.timestamp = int(time())
        #req.checkin.build.carrier = "Telekom"
        #req.checkin.build.model = "A0001"
        #req.checkin.build.bootloader = "unknown"
        #req.checkin.build.manufacturer = "oneplus"
        #req.checkin.build.otaInstalled = False
        #req.checkin.lastCheckinMsec = 0
        #req.checkin.roaming = "mobile-notroaming"
        #req.checkin.simOperator = "26201"
        #req.checkin.cellOperator = "26201"
        #req.checkin.userNumber = 0
        req.deviceConfiguration.touchScreen = 3
        req.deviceConfiguration.keyboard = 1
        req.deviceConfiguration.navigation = 1
        req.deviceConfiguration.screenLayout = 2
        req.deviceConfiguration.hasHardKeyboard = False
        req.deviceConfiguration.screenDensity = 400
        #(req.deviceConfiguration.nativePlatform
        #    .extend(["armeabi-v7l", "armeabi"]))
        #req.deviceConfiguration.screenWidth = 1080
        #req.deviceConfiguration.screenHeight = 1920
        #req.locale="en_US"
        #req.timeZone = "Europe/Berlin"
        req.version = 3
        #req.fragment = 0
        req.deviceConfiguration.hasFiveWayNavigation = False
        # important TODO: make configurable
        higher_gl_number = 3
        lower_gl_number = 0
        req.deviceConfiguration.glEsVersion = int(
                format(higher_gl_number, "04x") + format(0,"04x"), 16)
        req.checkin.build.sdkVersion = 23
        return req
