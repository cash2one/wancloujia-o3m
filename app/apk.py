import logging
import re
import zipfile
import os.path
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

_version_pattern = re.compile("(name|versionCode|versionName)='(.+?)'")
_sdk_version_pattern = re.compile("sdkVersion:'(\d+)'")
_target_sdk_version_pattern = re.compile("targetSdkVersion:'(\d+)'")
_application_info_pattern = re.compile("(label|icon)='(.+?)'")
_application_label_pattern = re.compile("application-label:'(.+)'")
_application_icon_pattern = re.compile("application-icon-\d+?:'(.+?drowable-((l|m|tv|h|x|xx)dpi).+?)'")

def _first(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None


class ApkInfo():
    def __init__(self):
        self.appName = None
        self.packageName = None
        self.packageSize = None
        self.applicationLabel = None
        self.versionName = None
        self.versionCode = None
        self.sdkVersion = None
        self.targetSdkVersion = None
        self.icon = None
        self.ldpiIcon = None
        self.mdpiIcon = None
        self.tvdpiIcon = None
        self.hdpiIcon = None
        self.xdpiIcon = None
        self.xxdpiIcon = None

    def getAppName(self):
        return _first(self.appName, self.applicationLabel)

    def getIcon(self):
        return _first(self.hdpiIcon, self.icon, self.mdpiIcon, self.tvdpiIcon, 
                        self.xdpiIcon, self.xxdpiIcon)

    def getPackageName(self):
        return self.packageName

    def getPackageSize(self):
        return self.packageSize

    def getMinSdkVersion(self):
        return self.sdkVersion

    def getTargetSdkVersion(self):
        return self.targetSdkVersion


def _parsePkgInfo(apk_info, text):
    matches = _version_pattern.findall(text)
    if len(matches) == 0:
        return
        
    for match in matches:
        key = match[0]
        value = match[1]
        if key == 'versionCode':
            apk_info.versionCode = int(value)
        if key == 'versionName':
            apk_info.versionName = value
        if key == 'name':
            apk_info.packageName = value


def _parseSdkVersion(apk_info, text):
    result = _sdk_version_pattern.search(text)
    apk_info.sdkVersion = int(result.group(1)) if result else None


def _parseTargetSdkVersion(apk_info, text):
    result = _target_sdk_version_pattern.search(text)    
    apk_info.targetSdkVersion = int(result.group(1)) if result else None


def _parseAppInfo(apk_info, text):
    matches = _application_info_pattern.findall(text)
    if len(matches) == 0:
        return

    for match in matches:
        key = match[0]
        value = match[1]
        if key == 'label':
            apk_info.appName = value
        if key == 'icon':
            apk_info.icon = value


def _parseApplicationLabel(apk_info, text):
    result = _application_label_pattern.search(text)
    apk_info.applicationLabel = result.group(1) if result else None


def _parseApplicationIcons(apk_info, text):
    result = _application_icon_pattern.search(text)
    if result is None:
        return

    level = result.group(2)
    if level == 'ldpi':
        apk_info.ldpiIcon = result.group(1)
    if level == 'mdpi':
        apk_info.mdpiIcon = result.group(1)
    if level == 'tvdpi':
        apk_info.tvdpiIcon = result.group(1)
    if level == 'hdpi':
        apk_info.hdpiIcon = result.group(1)
    if level == 'xdpi': 
        apk_info.xdpiIcon = result.group(1)
    if level == 'xxdpi': 
        apk_info.xxdpiIcon = result.group(1)


def _parse(content):
    apk_info = ApkInfo()
    for line in content.splitlines():
        if re.match('package:', line):            
            _parsePkgInfo(apk_info, line)
        if re.match('sdkVersion:', line):
            _parseSdkVersion(apk_info, line)
        if re.match('targetSdkVersion:', line):
            _parseTargetSdkVersion(apk_info, line)
        if re.match('application-label:', line):
            _parseApplicationLabel(apk_info, line)
        if re.match('application:', line):
            _parseAppInfo(apk_info, line)
        if re.match('application-icon-\d+?:', line):
            _parseApplicationIcons(apk_info, line)
    return apk_info


class  InspectFailedException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

def apiLevelToAndroidVersion(version):
    VERSIONS = [
        None, None, None, #1, 2, 3
        "1.6", None, None, #4, 5, 6
        "2.1", #7
        "2.2", #8
        "2.3", #9
        "2.3", None, #10, 11
        "3.1", #12
        "3.2", None, #13, 14
        "4.0", #15
        "4.1", #16
        "4.2", #17,
        "4.3", #18
    ]
    return VERSIONS[version-1] if version <= len(VERSIONS) else None

def inspect(path):
    pipe = Popen(["android/aapt", "dump", "badging", path], stdout=PIPE, stderr=PIPE)
    out, err = pipe.communicate()
    if pipe.returncode != 0:
        raise InspectFailedException(err)

    apk_info = _parse(out)
    apk_info.packageSize = os.path.getsize(path)
    return apk_info

def read_icon(path, cb):
    apk_info = inspect(path)
    with zipfile.ZipFile(path, 'r') as zip:
        name = apk_info.getIcon()
        with zip.open(name) as f:
            cb(name, f) 
        
