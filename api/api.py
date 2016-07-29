
from time import time
from configobj import ConfigObj
from google.protobuf import descriptor

import requests

import api.gplay_pb2 as gplay

class GooglePlayAPI():
    # commented lines were not necessary to get it working
    # but are left because they might become necessary in the future

    BASE_URL = "https://android.clients.google.com/"
    FDFE_URL = BASE_URL + "fdfe/"
    CHECKIN_URL = BASE_URL + "checkin"
    LOGIN_URL = BASE_URL + "auth"
    SEARCH_URL = FDFE_URL + "search"
    UPLOADDEVICE_URL = FDFE_URL + "uploadDeviceConfig"

    def __init__(self, config_file = "default.ini", proxy=""):
        self.config = ConfigObj(config_file)
        self.email = self.config["GPlay"]["Email"]
        self.password = self.config["GPlay"]["Password"]
        if self.config["GPlay"]["AndroidId"]:
            self._androidId = self.config["GPlay"]["AndroidId"]
        else:
            self._androidId = None
        self.sdkVersion = int(self.config["GPlay"]["SdkVersion"])
        self.higherOpenGLVersion = (
            int((self.config["GPlay"]["OpenGLVersion"]).split(".")[0]))
        self.lowerOpenGLVersion = (
            int((self.config["GPlay"]["OpenGLVersion"]).split(".")[1]))
        self.country = self.config["GPlay"]["Country"]
        self.lang = self.config["GPlay"]["Language"]
        self.sess = requests.Session()
        if proxy:
            http_proxy = "http://" + proxy
            https_proxy = "https://" + proxy
            proxies = { "http": http_proxy, "https": https_proxy }
            self.sess.proxies = proxies
            self.sess.verify = False

    def search(self, query):
        data = dict()
        data["c"] = 3
        data["q"] = query
        data["o"] = "0"
        data["n"] = "10"
        resp = self._executeGET(self.SEARCH_URL, data)
        return resp

    def checkin(self):
        """Posts a Android Checkin"""
        headers = dict()
        headers["Host"] = "android.clients.google.com"
        headers["Content-Type"] = "application/x-protobuffer"
        resp = self.sess.post(self.CHECKIN_URL,
                data = self._generate_checkin_request().SerializeToString(),
                headers=headers)
        #if resp.status_code == 200:
        #    and_resp = gplay.AndroidCheckinResponse().FromString(resp.content)
        #else:
        #    print("ERROR during first checkin: Response body:\n {}"
        #            .format(resp.content.decode("utf-8")))
        #    exit(1)
        #ac2dm_auth = self._login_ac2dm()
        #android_id = and_resp.androidId
        #secToken = and_resp.securityToken
        #second_checkin = self._generate_checkin_request()
        #second_checkin.id = android_id
        #second_checkin.securityToken = secToken
        #second_checkin.accountCookie.append("[{}]".format(self.email))
        #second_checkin.accountCookie.append("{}".format(ac2dm_auth))
        #resp = self.sess.post(self.CHECKIN_URL,
        #        data = second_checkin.SerializeToString(),
        #        headers=headers)
        if resp.status_code == 200:
            and_resp = gplay.AndroidCheckinResponse().FromString(resp.content)
            and_id = hex(and_resp.androidId)[2:]
            print("Got Android ID: {}".format(and_id))
            return and_id
        else:
            print("ERROR during second checkin: Response body:\n {}"
                    .format(resp.content.decode("utf-8")))
            exit(1)

    def _login_ac2dm(self):
        """Logs user into AC2DM"""
        data = dict()
        data["Email"] = self.email
        data["Passwd"] = self.password
        data["service"] = "ac2dm"
        #data["accountType"] =  "HOSTED_OR_GOOGLE"
        #data["has_permission"] = 1
        #data["source"] = "android"
        #data["androidId"] = self.androidId()
        data["app"] = "com.android.vending"
        data["device_country"] = self.country
        data["lang"] = self.lang
        data["sdk_version"] = self.sdkVersion
        resp = self.sess.post(self.LOGIN_URL, data=data)
        authToken = ""
        for line in resp.content.splitlines():
            line = line.decode("utf-8")
            if "Auth=" in line:
                authToken = line.split("=")[1].strip()
        if authToken:
            print("Got AC2DM auth token: {}".format(authToken))
            self.authToken = authToken
        else:
            print("ERROR during AC2DM Login: Response body:\n{}"
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
            self._androidId = self.checkin()
            self.config["GPlay"]["AndroidId"] = self._androidId
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
        resp = self.sess.post(self.LOGIN_URL, data=data)
        authToken = ""
        for line in resp.content.splitlines():
            line = line.decode("utf-8")
            if "Auth=" in line:
                authToken = line.split("=")[1].strip()
        if authToken:
            print("Got AndroidMarket auth token: {}".format(authToken))
            self.authToken = authToken
        else:
            print("ERROR during AndroidMarket Login: Response body:\n{}"
                    .format(resp.content.decode("utf-8")))
            exit(1)

    def _executeGET(self, url, params):
        content_type = (
            "application/x-ww-form-urlencoded; charset=UTF-8")
        resp = self.sess.get(url, headers=self._get_headers(content_type), 
            params=params)
        if resp.status_code == 200:
            return gplay.ResponseWrapper().FromString(resp.content)
        else:
            print("ERROR: URL: {}\nResponse body:\n{}".format(
                resp.url, gplay.ResponseWrapper().FromString(resp.content)))

    def _executePOST(self, url, data):
        content_type = "application/x-protobuf"
        resp = self.sess.post(url, headers=self._get_headers(content_type),
                data=data)
        if resp.status_code == 200:
            return gplay.ResponseWrapper().FromString(resp.content)
        else:
            print("ERROR: URL: {}\nResponse body:\n{}".format(
                resp.url, gplay.ResponseWrapper().FromString(resp.content)))


    def _get_headers(self, content_type):
        headers = dict()
        if not hasattr(self, "authToken"):
            self.login()
        headers["Authorization"] = "GoogleLogin auth={}".format(self.authToken)
        headers["X-DFE-Device-Id"] = self.androidId()
        #headers["X-DFE-Client-Id"] = "am-android-google"
        #headers["Host"] = "android.clients.google.com"
        headers["X-DFE-Filter-Level"] = "3"
        #headers["X-DFE-SmallesScreenWidthDp"] = "400"
        headers["Content-Type"] = content_type
        #headers["X-DFE-Enabled-Experiments"] = (
        #    "cl:billing.select_add_instrument_by_default")
        #headers["X-DFE-Unsupported-Experiments"] = (
        #    "nocache:billing.use_charging_poller,market_emails,"
        #    "buyer_currency,prod_baseline,checkin.set_asset_paid_app_field,"
        #    "shekel_test,content_ratings,buyer_currency_in_app,"
        #    "nocache:encrypted_apk,recent_changes")
        headers["User-Agent"] = "Android-Finsky"
        #headers["User-Agent"] = ("Android-Finsky/6.5.08.D-all "
        #    "(versionCode=80650800,sdk=23,device=noblelte,hardware=noblelte,"
        #    "product=noblelte,build=MMB29K:user)")
        headers["Accept-Language"] = ("{}-{}"
            .format(self.lang, self.country.upper()))
        #headers["Accept-Language"] = "en-EN"
        #headers["Accept-Language"] = "US"
        return headers


    def _generate_checkin_request(self):
        """Generates a AndroidCheckinRequest for a Oneplus One"""
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
        req.deviceConfiguration.MergeFrom(self._generate_device_configuration())
        #req.locale="en_US"
        #req.timeZone = "Europe/Berlin"
        req.version = 3
        #req.fragment = 0
        req.checkin.build.sdkVersion = self.sdkVersion
        return req

    def _generate_device_configuration(self):
        """Generates a device configuration for a Oneplus One"""
        cfg = gplay.DeviceConfigurationProto()
        cfg.touchScreen = 3
        cfg.keyboard = 1
        cfg.navigation = 1
        cfg.screenLayout = 2
        cfg.hasHardKeyboard = False
        cfg.screenDensity = 400
        cfg.hasFiveWayNavigation = False
        cfg.glEsVersion = int(
                format(self.higherOpenGLVersion, "04x")
                + format(self.lowerOpenGLVersion,"04x"), 16)
        cfg.nativePlatform.extend(["armeabi-v7l", "armeabi"])
        cfg.systemSharedLibrary.extend([
            "android.test.runner", "com.android.future.usb.accessory",
            "com.android.location.provider", "com.android.nfc_extras",
            "com.google.android.maps", "com.google.android.media.effects",
            "com.google.widevine.software.drm", "javax.obex"])
        cfg.systemAvailableFeature.extend([
            "android.hardware.bluetooth", "android.hardware.camera",
            "android.hardware.camera.autofocus",
            "android.hardware.camera.flash", "android.hardware.camera.front",
            "android.hardware.faketouch", "android.hardware.location",
            "android.hardware.location.gps",
            "android.hardware.location.network", "android.hardware.microphone",
            "android.hardware.nfc", "android.hardware.screen.landscape",
            "android.hardware.screen.portrait",
            "android.hardware.sensor.accelerometer",
            "android.hardware.sensor.barometer",
            "android.hardware.sensor.compass",
            "android.hardware.sensor.gyroscope",
            "android.hardware.sensor.light",
            "android.hardware.sensor.proximity", "android.hardware.telephony",
            "android.hardware.telephony.gsm", "android.hardware.touchscreen",
            "android.hardware.touchscreen.multitouch",
            "android.hardware.touchscreen.multitouch.distinct",
            "android.hardware.touchscreen.multitouch.jazzhand",
            "android.hardware.usb.accessory", "android.hardware.usb.host",
            "android.hardware.wifi", "android.hardware.wifi.direct",
            "android.software.live_wallpaper", "android.software.sip",
            "android.software.sip.voip", "com.cyanogenmod.android",
            "com.cyanogenmod.nfc.enhanced",
            "com.google.android.feature.GOOGLE_BUILD", "com.nxp.mifare",
            "com.tmobile.software.themes"])
        #cfg.screenWidth = 1080
        #cfg.screenHeight = 1920
        return cfg
