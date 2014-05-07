function __log(s) {
    //return;
    $("#logs").append("<li>" + s + "</li>");
}

(function(window) {
    var utils = {};

    utils.bitsize = function(size) {
        var result = "";
        if (size < 1024 * 1024) {
            result = (size / 1024).toFixed(2) + " KB";
        } else {
            result = (size / 1024 / 1024).toFixed(2) + " MB";
        }
        return result;
    };

    window.utils = utils;
})(window);


(function(window) {
    var apps = {};

    var INITIALIZED = "initialized";
    var PENDING = "pending";
    var FAILED = "failed";
    var SUCCESS = "success";

    apps.load = function() {
        var list = this.list = [];
        $appList.find(".app").each(function() {
            var $this = $(this);
            var $link = $this.find("a.install-link");
            list.push({
                name: $this.data("name"),
                package: $link.data("package"),
                status: INITIALIZED
            });
        });
    };

    apps.all = function() {
        return this.list;
    };

    apps.count = function() {
        return this.list.length;
    };

    apps.find = function(package) {
        var list = this.list;
        for (var i = 0; i < list.length; i++) {
            if (package === list[i].package) {
                return list[i];
            }
        }

        return null;
    };

    apps.fail = function(package) {
        var app = this.find(package);
        if (app) {
            app.status = FAILED;
        }
    };

    apps.success = function(package) {
        var app = this.find(package);
        if (app) {
            app.status = SUCCESS;
        }
    }

    apps.countFinished = function() {
        return _.reduce(this.list, function(count, app) {
            return app.status === SUCCESS ? ++count : count;
        }, 0);
    };

    apps.isAllInstalled = function() {
        return this.countFinished() == this.list.length;
    };

    apps.isPending = function(cb) {
        var list = this.list;
        for (var i = 0; i < list.length; i++) {
            var item = list[i];
            if (item.status === PENDING) {
                return true;
            }
        }

        return false;
    };

    apps.getProcessingApps = function() {
        var tasks = _.filter(this.list, function(item) {
            return item.status === PENDING;
        });
        console.log("processing tasks:", tasks);
        return tasks;
    };

    apps.startAll = function() {
        _.each(this.list, function(app) {
            app.status = PENDING;
        });
    };

    window.apps = apps;
})(window);

var $appList = null;
var $tip = null;
var username = null;

function show_tip() {
    var bits = 0;
    $appList.find(".app").each(function() {
        var $this = $(this);
        bits += parseInt($this.data("size"), 10);
    });
    var count = $appList.find(".app").length;
    var $tip = $("#tip");
    $tip.html("共" + count + "款应用，共" + utils.bitsize(bits));
}

var model = "";
var brand = "";
var deviceid = "";
var imei = "";
var connected = false;

setTimeout(function() {
    if (model === "" || brand === "" || imei === "") {
        return $(".alert").html("手机连接异常，请重试").fadeIn();
    }
}, 10 * 1000);


$(function() {
    function ensureToInstall() {
        __log("----ensure connection, device info and installer's status");

        if (!connected) {
            __log("not connect");
            return;
        }

        if (model === "" || brand === "" || imei === "") {
            __log("device info not ready");
            return;
        }

        if (installer.status === installer.PROCESSING) {
            __log("installer is processing");
            return;
        }

        __log("---connected, devcie info read, installer idle, start install!!!");
        install();
    }

    $(nativeMessage).on("device.info", function(e, deviceInfo) {
        __log(_.pairs(deviceInfo));
        if (!deviceInfo.is_available) {
            return $(".alert").html("手机连接异常，请重试").fadeIn();
        }

        if (deviceInfo.is_connected !== connected) {
            connected = deviceInfo.is_connected;
            __log("connection changed!!!");
            // on connection changed
            ensureToInstall();
        }

        if (model !== "" && brand !== "" && imei !== "") {
            return;
        }

        model = deviceInfo.model;
        brand = deviceInfo.brand;
        deviceid = deviceInfo.device_id;
        imei = deviceInfo.imei;
        __log("device info ready!!!");
        ensureToInstall();
    });

    function StatusBar(el) {
        var self = this;

        this.el = el;
        this.$el = $(el);
        this.show = function() {
            this.$el.fadeIn();
        };

        this.hide = function() {
            this.$el.fadeOut();
        };

        this.$progressSection = this.$el.find(".progress-section");
        this.$progressBar = this.$el.find(".progressbar");
        this.$amount = this.$el.find(".amount");

        this.$resultSection = this.$el.find(".result-section");
        this.$result = this.$el.find(".result");
        this.$failedApps = this.$el.find(".failed-apps");
        this.$closeBtn = this.$el.find("#close-btn");
        this.$closeBtn.click(function() {
            self.hide();
        });

        this.showProgress = function(total) {
            self.reset();
            this.total = total;
        };

        this.updateProgress = function(count) {
            this.$amount.html(count);
            var percent = (count * 1.0) / this.total * 100;
            this.$progressBar.find(".progressbar-block").css("width", percent + "%");
        };

        this.resetProgress = function() {
            this.$amount.html("0");
            this.$progressBar.find(".progressbar-block").css("width", "0%");
        };

        this.showFailMsg = function(count) {
            this.resetProgress();
            this.$progressSection.hide();
            this.$result.html("安装失败").addClass("fail");
            this.$failedApps.html(count + "款应用安装失败");
            this.$resultSection.show();
            this.$closeBtn.show();
        };

        this.showSuccessMsg = function(count) {
            this.resetProgress();
            this.$progressSection.hide();
            this.$result.html("安装成功").addClass("success");
            this.$resultSection.show();
            this.$closeBtn.show();
        };

        this.resetResult = function() {
            this.$result.empty().removeClass("fail").removeClass("success");
            this.$failedApps.empty();
        };

        this.reset = function() {
            this.resetProgress();
            this.$progressSection.show();
            this.resetResult();
            this.$resultSection.hide();
            this.$closeBtn.hide();
        };
    }

    var statusBar = new StatusBar($("#statusbar")[0]);
    username = $(".user-area > .username").html();
    $appList = $(".app-list");
    apps.load();
    show_tip();

    var installer = {
        INIT: "init",
        PROCESSING: "processing",
        FAILED: "failed",
        SUCCESS: "success"
    };

    installer.status = installer.INIT;
    installer.counter = 0;
    installer.tasks = null;
    installer.onProcess = function(func) {
        var self = this;
        return function(result) {
            if (self.status !== self.PROCESSING) {
                return console.log("install is not processing, ignore it!");
            }

            func && func(result);
        };
    };

    function _log(event) {
        var log = {
            event: event,
            user: username,
            subj: subject_id,
            brand: brand,
            did: deviceid,
            imei: imei,
            model: model
        };
        console.log(log);
        sendLog($.toJSON(log));
    };

    window.onbeforeunload = function() {
        if (installer.status === installer.PROCESSING ||
            installer.status === installer.CANCELLING) {
            return "确认要离开该专题吗？";
        }
    };

    var $install = $("#install");
    $install.removeAttr("disabled", "disabled");
    $install.click(function() {
        if (installer.status === self.PROCESSING) {
            return console.log("installer is processing tasks now, ignore it!");
        }

        installer.tasks = {};
        var timestamp = new Date().getTime();
        var count = 0;
        var linkEls = $appList.find(".app a.install-link").toArray();
        _.each(linkEls, function(el) {
            var baseid = (timestamp + "_") + (count++);
            var $el = $(el);
            var task_info = {
                url: $el.attr('href'),
                task_type: 1,
                task_base_id: baseid,
                package_name: $el.data('package'),
                display_name: $el.data('name'),
                icon: $el.data('icon'),
                md5: $el.data('md5'),
                size: $el.data('size')
            };
            __log(_.pairs(task_info).join("<br/>"));
            installer.tasks[baseid] = task_info;
            sendMessageToNative('app.download', task_info);
        });

        installer.status = installer.PROCESSING;
        apps.startAll();
        statusBar.show();
        statusBar.showProgress(apps.count());
        $install.attr("disabled", "disabled");

        _log("tianyin.install");
    });

    function onTaskStatusChanged() {
        if (apps.isPending()) {
            var finishedApps = apps.countFinished();
            statusBar.updateProgress(finishedApps);
            return console.log(finishedApps, "apps installed");
        }

        $install.removeAttr("disabled");
        if (apps.isAllInstalled()) {
            installer.status = installer.SUCCESS;
            _log("tianyin.install.success");
            console.log("all installed!");
            statusBar.showSuccessMsg();
        } else {
            installer.status = installer.FAILED;
            __log("only " + apps.countFinished() + " installed");
            statusBar.showFailMsg(apps.count() - apps.countFinished());
        }
    }

    $(nativeMessage).on('app.progress', function(e, progress) {
        __log("progress!!! " + _.pairs(progress));
        var STATUS_FINISH = 5;
        var STATUS_ERROR = 6;
        var status = progress.progress_name;
        if (status !== STATUS_FINISH && status !== STATUS_ERROR) {
            return;
        }

        var task = installer.tasks[progress.task_base_id];
        if (task === undefined) {
            return __log("Invalid task, ignore it!");
        }

        if (status === STATUS_FINISH) {
            __log("app " + task.package_name + " install successfully");
            apps.success(task.package_name);
        } else {
            __log("app " + task.package_name + " fail to be installed");
            apps.fail(task.package_name);
        }
        onTaskStatusChanged();
    });

    function install() {
        $install.trigger("click");
    }
});

$(function() {
    sendMessageToNative('dom.ready', '');
    sendMessageToNative('device.info', '');
});
