#coding: utf-8
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
_application_icon_pattern = re.compile("application-icon-\d+?:'(res/drawable-((l|m|tv|h|xh|xx)dpi)/icon.png)'")
_permission_pattern = re.compile("permission: (.+)")
PER_DICT = {
    "android.permission-group.ACCOUNTS" : "访问你的账号",
    "android.permission-group.COST_MONEY" : "需要你付费的服务",
    "android.permission-group.DEVELOPMENT_TOOLS" : "开发工具",
    "android.permission-group.LOCATION" : "你的位置",
    "android.permission-group.HARDWARE_CONTROLS" : "硬件控制",
    "android.permission-group.MESSAGES" : "读写你的短信和邮件",
    "android.permission-group.NETWORK" : "访问网络",
    "android.permission-group.PERSONAL_INFO" : "你的个人信息",
    "android.permission-group.PHONE_CALLS" : "手机通话",
    "android.permission-group.STORAGE" : "读写 SD 卡",
    "android.permission-group.SYSTEM_TOOLS" : "系统工具",
    "android.permission.ACCESS_CHECKIN_PROPERTIES" : "访问检入属性",
    "android.permission.ACCESS_COARSE_LOCATION" : "读取基于网络的粗略位置",
    "android.permission.ACCESS_FINE_LOCATION" : "读取精准的 GPS 位置",
    "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS" : "访问额外的位置信息提供程序命令",
    "android.permission.ACCESS_MOCK_LOCATION" : "使用模拟地点进行测试",
    "android.permission.ACCESS_NETWORK_STATE" : "查看网络状态",
    "android.permission.ACCESS_SURFACE_FLINGER" : "访问 SurfaceFlinger",
    "android.permission.ACCESS_WIFI_STATE" : "查看 Wi-Fi 状态",
    "android.permission.BATTERY_STATS" : "修改电池统计信息",
    "android.permission.BLUETOOTH" : "创建蓝牙连接",
    "android.permission.BLUETOOTH_ADMIN" : "蓝牙管理",
    "android.permission.BRICK" : "变砖",
    "android.permission.BROADCAST_PACKAGE_REMOVED" : "发送包删除的广播",
    "android.permission.BROADCAST_STICKY" : "发送置顶广播",
    "android.permission.CALL_PHONE" : "拨打电话",
    "android.permission.CALL_PRIVILEGED" : "拨打任何电话",
    "android.permission.CAMERA" : "拍照",
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE" : "启用或停用应用程序组件",
    "android.permission.CHANGE_CONFIGURATION" : "更改用户界面设置",
    "android.permission.CHANGE_NETWORK_STATE" : "更改网络连接性",
    "android.permission.CHANGE_WIFI_STATE" : "更改 Wi-Fi 状态",
    "android.permission.CLEAR_APP_CACHE" : "删除所有应用程序缓存数据",
    "android.permission.CLEAR_APP_USER_DATA" : "删除应用程序的数据",
    "android.permission.CONTROL_LOCATION_UPDATES" : "控制位置更新通知",
    "android.permission.DELETE_CACHE_FILES" : "删除其他应用程序的缓存",
    "android.permission.DELETE_PACKAGES" : "删除应用程序",
    "android.permission.DEVICE_POWER" : "开机或关机",
    "android.permission.DIAGNOSTIC" : "读取/写入诊断所拥有的资源",
    "android.permission.DISABLE_KEYGUARD" : "停用键盘锁",
    "android.permission.DUMP" : "检索系统内部状态",
    "android.permission.EXPAND_STATUS_BAR" : "展开/收拢状态栏",
    "android.permission.FACTORY_TEST" : "在出厂测试模式下运行",
    "android.permission.FLASHLIGHT" : "控制闪光灯",
    "android.permission.FORCE_BACK" : "强制应用程序关闭",
    "android.permission.GET_ACCOUNTS" : "发现已知账号",
    "android.permission.GET_PACKAGE_SIZE" : "计算应用程序存储空间",
    "android.permission.GET_TASKS" : "检索当前运行的应用程序",
    "android.permission.HARDWARE_TEST" : "测试硬件",
    "android.permission.INJECT_EVENTS" : "按键和控制按钮",
    "android.permission.INSTALL_PACKAGES" : "直接安装应用程序",
    "android.permission.public_SYSTEM_WINDOW" : "显示未授权的窗口",
    "android.permission.INTERNET" : "网络通信",
    "android.permission.MANAGE_APP_TOKENS" : "管理应用程序令牌",
    "android.permission.MASTER_CLEAR" : "将系统恢复为出厂设置",
    "android.permission.MODIFY_AUDIO_SETTINGS" : "更改你的音频设置",
    "android.permission.MODIFY_PHONE_STATE" : "修改手机状态",
    "android.permission.READ_PHONE_STATE" : "读取手机状态和身份",
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS" : "装载和卸载文件系统",
    "android.permission.PERSISTENT_ACTIVITY" : "让应用程序始终运行",
    "android.permission.PROCESS_OUTGOING_CALLS" : "拦截外拨电话",
    "android.permission.READ_CALENDAR" : "访问日历",
    "android.permission.READ_CONTACTS" : "访问联系人数据",
    "android.permission.READ_FRAME_BUFFER" : "读取帧缓冲区",
    "android.permission.READ_INPUT_STATE" : "记录你键入的内容和执行的操作",
    "android.permission.READ_LOGS" : "读取系统日志文件",
    "android.permission.READ_OWNER_DATA" : "读取所有者数据",
    "android.permission.READ_SMS" : "读取短信或彩信",
    "android.permission.READ_SYNC_SETTINGS" : "读取同步设置",
    "android.permission.READ_SYNC_STATS" : "读取同步统计信息",
    "android.permission.REBOOT" : "强行重新启动手机",
    "android.permission.RECEIVE_BOOT_COMPLETED" : "开机时自动启动",
    "android.permission.RECEIVE_MMS" : "接收彩信",
    "android.permission.RECEIVE_SMS" : "接收短信",
    "android.permission.RECEIVE_WAP_PUSH" : "接收 WAP",
    "android.permission.RECORD_AUDIO" : "录音",
    "android.permission.REORDER_TASKS" : "对正在运行的应用程序重新排序",
    "android.permission.RESTART_PACKAGES" : "重新启动应用程序",
    "android.permission.SEND_SMS" : "发送短信",
    "android.permission.SET_ACTIVITY_WATCHER" : "监控所有应用程序的启动",
    "android.permission.SET_ALWAYS_FINISH" : "关闭所有后台应用程序",
    "android.permission.SET_ANIMATION_SCALE" : "修改全局动画速度",
    "android.permission.SET_DEBUG_APP" : "启用应用程序调试",
    "android.permission.SET_ORIENTATION" : "更改屏幕显示方向",
    "android.permission.SET_PREFERRED_APPLICATIONS" : "设置首选应用程序",
    "android.permission.SET_PROCESS_FOREGROUND" : "允许应用程序强行运行到前端",
    "android.permission.SET_PROCESS_LIMIT" : "限制运行的进程个数",
    "android.permission.SET_TIME_ZONE" : "设置时区",
    "android.permission.SET_WALLPAPER" : "设置壁纸",
    "android.permission.SET_WALLPAPER_HINTS" : "设置有关壁纸大小的提示",
    "android.permission.SIGNAL_PERSISTENT_PROCESSES" : "向应用程序发送 Linux 信号",
    "android.permission.STATUS_BAR" : "停用或修改状态栏",
    "android.permission.SUBSCRIBED_FEEDS_READ" : "读取订阅的供稿",
    "android.permission.SYSTEM_ALERT_WINDOW" : "显示系统级警报",
    "android.permission.VIBRATE" : "控制振动器",
    "android.permission.WAKE_LOCK" : "防止手机休眠",
    "android.permission.WRITE_APN_SETTINGS" : "写入「接入点名称」设置",
    "android.permission.WRITE_CALENDAR" : "添加或修改日历活动以及向邀请对象发送电子邮件",
    "android.permission.WRITE_CONTACTS" : "编辑或写入联系人",
    "android.permission.WRITE_GSERVICES" : "修改 Google 服务地图",
    "android.permission.WRITE_OWNER_DATA" : "写入所有者数据",
    "android.permission.WRITE_SETTINGS" : "修改全局系统设置",
    "android.permission.WRITE_SMS" : "编辑短信或彩信",
    "android.permission.WRITE_SYNC_SETTINGS" : "写入同步设置"
}

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
        self.xhdpiIcon = None
        self.xxdpiIcon = None
        self.permissions = []

    def getAppName(self):
        return _first(self.appName, self.applicationLabel)

    def getIcon(self):
        return _first(self.hdpiIcon, self.icon, self.mdpiIcon, self.tvdpiIcon, 
                        self.xhdpiIcon, self.xxdpiIcon)

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

def _parsePermissions(apk_info, text):
    result = _permission_pattern.search(text)
    if result:
        if PER_DICT.has_key(result.group(1)):
            permission = PER_DICT[result.group(1)]
            apk_info.permissions.append(permission)


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
    if level == 'xhdpi': 
        apk_info.xhdpiIcon = result.group(1)
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
    pipe = Popen(["android/aapt", "dump", "permissions", path], stdout=PIPE, stderr=PIPE)
    out, err = pipe.communicate()
    if pipe.returncode != 0:
        raise InspectFailedException(err)

    for line in out.splitlines():
        _parsePermissions(apk_info, line)

    apk_info.packageSize = os.path.getsize(path)
    return apk_info

def read_icon(path, cb):
    apk_info = inspect(path)
    with zipfile.ZipFile(path, 'r') as zip:
        name = apk_info.getIcon()
        with zip.open(name) as f:
            cb(name, f) 
        

if __name__ == '__main__':
    import sys
    info = inspect(sys.argv[1])
    print info.permissions 

    
    
