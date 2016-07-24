
from time import time, sleep
from configobj import ConfigObj
from google.protobuf import descriptor

import requests

import api.gplay_pb2 as gplay

class GooglePlayAPI():

    BASE_URL = "https://android.clients.google.com/"
    CHECKIN_URL = BASE_URL + "checkin"
    LOGIN_URL = BASE_URL + "auth"
    SEARCH_URL = BASE_URL + "fdfe/search"

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

    def search(self, query):
        data = dict()
        data["c"] = 3
        data["q"] = query
        data["o"] = "0"
        data["n"] = "10"
        resp = self._executeGET(self.SEARCH_URL, data)
        print(resp)

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
            exit(1)

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
        """Logs user in"""
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
                authToken = line.split("=")[1].strip()
        #print(resp.content.decode("utf-8"))
        if authToken:
            print("Got auth token: {}".format(authToken))
            self.authToken = authToken
        else:
            print("ERROR during Login: Response body:\n{}"
                    .format(resp.content.decode("utf-8")))
            exit(1)

    def _executeGET(self, url, params):
        resp = requests.get(url, headers=self._get_headers(), 
            params=params)
        if resp.status_code == 200:
            return gplay.ResponseWrapper().FromString(resp.content)
        else:
            print("ERROR: URL: {}\nResponse body:\n{}".format(
                resp.url, gplay.ResponseWrapper().FromString(resp.content)))
            #print(gplay.ResponseWrapper().FromString(resp.content))


    def _get_headers(self):
        headers = dict()
        if not hasattr(self, "authToken"):
            self.login()
        headers["Authorization"] = "GoogleLogin auth={}".format(self.authToken)
        headers["X-DFE-Device-Id"] = str(self.androidId)
        #headers["X-DFE-Client-Id"] = "am-android-google"
        #headers["Host"] = "android.clients.google.com"
        #headers["X-DFE-Filter-Level"] = "3"
        #headers["X-DFE-SmallesScreenWidthDp"] = "320"
        #headers["Content-Type"] = (
        #        "application/x-ww-form-urlencoded; charset=UTF-8")
        #headers["X-DFE-Enabled-Experiments"] = (
        #    "cl:billing.select_add_instrument_by_default")
        #headers["X-DFE-Unsupported-Experiments"] = (
        #    "nocache:bulling.use_charging_poller,market_emails,"
        #    "buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,"
        #    "shekel_test,content_ratings,buyer_currency_in_app,"
        #    "nocache:encrypted_apk,recent_changes")
        #headers["User-Agent"] = "Android-Finksy"
        #headers["User-Agent"] = "Android-Finsky/6.5.08.D-all (versionCode=80650800,sdk=23,device=noblelte,hardware=noblelte,product=noblelte,build=MMB29K:user)"
        #headers["Accept-Language"] = ("{}-{}"
        #    .format(self.lang, self.country.upper()))
        #headers["Accept-Language"] = "en-EN"
        return headers


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
