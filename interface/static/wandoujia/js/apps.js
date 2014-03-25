(function(window) {
    var utils = {};

    utils.log = function(data) {
        data = data || {};

        var url = 'wdj://window/log.json';
        var datas = [];
        var d;
        for (d in data) {
            if (data.hasOwnProperty(d)) {
                datas.push(d + '=' + window.encodeURIComponent(data[d]));
            }
        }
        url += '?' + datas.join('&');

        var req = window.OneRingRequest;
        if (req) {
            req('get', url, '', function(resp) {
                resp = JSON.parse(resp);
                console.log(resp);
                if (resp.state_code != 200) {
                    console.error("log failed");
                }
            });
        }
    };

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

(function() {})(window);

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

function _log(event) {
    function get_version() {
        var originalVersion = navigator.userAgent.split(' ')[navigator.userAgent.split(' ').length - 1];
        var version;
        var arr = originalVersion.split('.');
        _.each(arr, function(v, index) {
            if (index === 0) {
                version = v + '.';
            } else {
                version += v;
            }
        });

        return parseFloat(version);
    }

    function get_brand() {
        var build = Narya.Device.get("build");
        return build ? (build.get("brand") || "unknown") : "unknown";
    }

    function get_model() {
        var build = Narya.Device.get("build");
        return build ? (build.get("model") || "unknown") : "unknown";
    }

    var log = {
        event: event,
        user: username,
        subj: subject_id,
        brand: get_brand(),
        client: get_version(),
        model: get_model()
    };
    console.log(log);
    utils.log(log);
}

function _ready(callback) {
    require(["Narya", "IO/IO"], function(__, IO) {
        $(function() {
            callback(Narya, IO);
        });
    });
}

_ready(function(Narya, IO) {


    var tasks = {};
    tasks.ERR = "error";

    tasks.all = function(cb) {
        IO.requestAsync({
            url: "wdj://jobs/show.json",
            success: function(resp) {
                if (resp.state_code !== 200) {
                    return cb(tasks.ERR);
                }

                return cb(null, resp.body.status);
            }
        });
    };

    tasks.clear = function() {
        tasks.all(function(err, tasks) {
            if (err) {
                return;
            }

            var jobs = _.map(tasks, function(task) {
                return task.id;
            }).join(",");
            IO.requestAsync({
                url: 'wdj://jobs/clear.json',
                data: {
                    job: jobs,
                    clear: 0
                },
                success: function(resp) {}
            });
        });
    };

    tasks.cancel = function(apps, cb) {
        var names = _.map(apps, function(app) {
            return app.name;
        });

        tasks.all(function(err, tasks) {
            if (err) {
                return cb(err);
            }

            console.log(tasks);
            var tasks = _.filter(tasks, function(item) {
                return names.indexOf(item.title) !== -1;
            });

            if (!tasks.length) {
                return cb(null);
            }

            var jobs = _.map(tasks, function(task) {
                return task.id;
            }).join(",");
            IO.requestAsync({
                url: 'wdj://jobs/clear.json',
                data: {
                    job: jobs,
                    clear: 0
                },
                success: function(resp) {
                    if (resp.state_code !== 200) {
                        console.log("fail to cancel tasks");
                    }
                    cb(resp.state_code !== 200 ? tasks.ERR : null);
                }
            });
        });
    };

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
        this.$cancelBtn = this.$el.find("#cancel-btn");
        this.$cancelBtn.click(function() {
            var handler = self.cancelHandler;
            handler && handler.call(null);
        });
        this.onCancel = function(handler) {
            this.cancelHandler = handler;
        };

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
        };

        this.showSuccessMsg = function(count) {
            this.resetProgress();
            this.$progressSection.hide();
            this.$result.html("安装成功").addClass("success");
            this.$resultSection.show();
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
        CANCELLING: "cancelling",
        CANCELLED: "cancelled",
        FAILED: "failed",
        SUCCESS: "success"
    };

    installer.status = installer.INIT;
    installer.onProcess = function(func) {
        var self = this;
        return function(result) {
            if (self.status !== self.PROCESSING) {
                return console.log("install is not processing, ignore it!");
            }

            func && func(result);
        };
    };

    window.onbeforeunload = function() {
        if (installer.status === installer.PROCESSING ||
            installer.status === installer.CANCELLING) {
            return "确认要离开该专题吗？";
        }
    };

    window.onunload = function() {
        if (installer.status === installer.PROCESSING ||
            installer.status === installer.CANCELLING) {
            tasks.clear();
        }
    };

    $(".user-area a").click(function(e) {
        if (installer.status === installer.PROCESSING ||
            installer.status === installer.CANCELLING) {
            e.preventDefault();
        }
    });

    statusBar.onCancel(installer.onProcess(function() {
        installer.status = installer.CANCELLING;
        statusBar.$cancelBtn.attr("disabled", "disabled");
        tasks.cancel(apps.getProcessingApps(), function(err) {
            installer.status = installer.CANCELLED;
            statusBar.$cancelBtn.removeAttr("disabled");

            if (err) {
                console.error("fail to cancel all tasks", err);
            }

            installer.status = installer.FAILED;
            console.log("Installation has been cancelled.");
            console.log("only", apps.countFinished(), "installed");

            statusBar.hide();
            $install.removeAttr("disabled");
        });
    }));

    var $install = $("#install");
    $install.click(function() {
        if (installer.status === self.PROCESSING ||
            installer.status === self.CANCELLING) {
            return console.log("installer is processing or cancelling tasks now, ignore it!");
        }

        var linkEls = $appList.find(".app a.install-link").toArray();
        _.each(linkEls, function(el) {
            el.click();
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
            console.log(finishedApps, "apps installed");
            return;
        }

        $install.removeAttr("disabled");
        if (apps.isAllInstalled()) {
            installer.status = installer.SUCCESS;
            _log("tianyin.install.success");
            console.log("all installed!");
            statusBar.showSuccessMsg();
        } else {
            installer.status = installer.FAILED;
            console.log("only", apps.countFinished(), "installed");
            statusBar.showFailMsg(apps.count() - apps.countFinished());
        }
    }

    IO.onmessage({
        "data.channel": "apps.install.success"
    }, installer.onProcess(function(result) {
        apps.success(result.package_name);
        onTaskStatusChanged();
    }));

    IO.onmessage({
        "data.channel": "apps.install.failed"
    }, installer.onProcess(function(result) {
        apps.fail(result.package_name);
        onTaskStatusChanged();
    }));

    function __jobs(jobs) {
        var TYPES = [
            'install', 'download', 'local_install',
            'push', 'parsing_video_url', 'merge_video',
            'unzip', 'restore_app_data', 'push_phone'
        ];
        var STATES = [
            'added', 'waiting', 'pause', 'processing',
            'success', 'fail', ' stopped'
        ];
        _.each(jobs, function(job) {
            job.type = TYPES[job.type - 1];
            job.state = STATES[job.state - 1];
        });
    }

    _.each(["add", "start", "changed", "status_changed", "stop"], function(event) {
        var channel = "jobs." + event;
        IO.onmessage({
            "data.channel": channel
        }, function(result) {
            __jobs(result.status);
            console.log(channel);
            console.log(result);
        });
    });

    IO.onmessage({
        "data.channel": "jobs.stop"
    }, function(result) {
        tasks.all(function(err, tasks) {
            if (err) {
                return console.error("fail to get tasks");
            }

            __jobs(tasks);
            _.each(tasks, function(task) {
                var processingApps = apps.getProcessingApps();
                for (var i = 0; i < processingApps.length; i++) {
                    var app = processingApps[i];
                    if (app.name === task.title) {
                        task.app = app;
                    }
                }
            });

            var failedTasks = _.filter(tasks, function(task) {
                return task.app &&
                    task.type === "install" &&
                    task.state === "success" &&
                    task.message === "DEVICE_NOT_FOUND";
            });

            _.each(failedTasks, function(task) {
                task.app.status = apps.FAILED;
            });
            onTaskStatusChanged();
        });
    });
});
