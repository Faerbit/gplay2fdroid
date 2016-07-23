
from time import time
from configobj import ConfigObj
from google.protobuf import descriptor

import requests

import api.gplay_pb2 as gplay

class GooglePlayAPI():

    BASE_URL = "https://android.clients.google.com/"
    CHECKIN_URL = BASE_URL + "checkin"
    LOGIN_URL = BASE_URL + "auth"

    def __init__(self, config_file = "default.ini"):
        self.config = ConfigObj(config_file)
        self.email = self.config["GPlay"]["Email"]
        self.password = self.config["GPlay"]["Password"]
        if self.config["GPlay"]["AndroidId"]:
            self._androidId = int(self.config["GPlay"]["AndroidId"])
        else:
            self._androidId = None
        self.sdkVersion = int(self.config["GPlay"]["SdkVersion"])
        self.higherOpenGLVersion = (
            int((self.config["GPlay"]["OpenGLVersion"]).split(".")[0]))
        self.lowerOpenGLVersion = (
            int((self.config["GPlay"]["OpenGLVersion"]).split(".")[1]))
        self.country = self.config["GPlay"]["Country"]
        self.lang = self.config["GPlay"]["Language"]


    def checkin(self):
        """Posts a Android Checkin"""
        headers = dict()
        headers["Host"] = "android.clients.google.com"
        headers["Content-Type"] = "application/x-protobuffer"
        resp = requests.post(self.CHECKIN_URL,
                data = self._generate_checkin_request().SerializeToString(),
                headers=headers)
        if resp.status_code == 200:
            and_resp = gplay.AndroidCheckinResponse().FromString(resp.content)
            print("Got Android ID: {}".format(and_resp.androidId))
            return and_resp
        else:
            print("ERROR during Checkin: Response body:\n {}"
                    .format(resp.content.decode("utf-8")))
            return None

    def androidId(self):
        """
        Returns the android id from config if available. Otherwise posts a
        checkin and saves the aquired android id.
        """
        if self._androidId:
            return self._androidId
        else:
            self._androidId = int(self.checkin().androidId)
            self.config["GPlay"]["AndroidId"] = str(self._androidId)
            self.config.write()
            return self._androidId


    def login(self):
        data = dict()
        data["Email"] = self.email
        data["Passwd"] = self.password
        data["service"] = "androidmarket"
        #data["accountType"] =  "HOSTED_OR_GOOGLE"
        #data["has_permission"] = 1
        #data["source"] = "android"
        data["androidId"] = self.androidId()
        data["app"] = "com.android.vending"
        data["device_country"] = self.country
        data["lang"] = self.lang
        data["sdk_version"] = self.sdkVersion
        resp = requests.post(self.LOGIN_URL, data=data)
        authToken = ""
        for line in resp.content.splitlines():
            line = line.decode("utf-8")
            if "Auth=" in line:
                authToken = line.split("=")[1]
        if authToken:
            return authToken
        else:
            print("ERROR during Login: Response body:\n{}"
                    .format(resp.content.decode("utf-8")))
            return None

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
        req.deviceConfiguration.glEsVersion = int(
                format(self.higherOpenGLVersion, "04x")
                + format(self.lowerOpenGLVersion,"04x"), 16)
        req.checkin.build.sdkVersion = self.sdkVersion
        return req
