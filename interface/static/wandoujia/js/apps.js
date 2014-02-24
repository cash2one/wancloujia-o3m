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
        return this.countFinshed() == this.list.length;
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

function _log(event) {
    function get_brand() {
        var build = Narya.Device.get("build");
        return build ? (build.get("brand") || "") : "";
    }

    function get_model() {
        var build = Narya.Device.get("build");
        return build ? (build.get("model") || "") : "";
    }

    var log = {
        event: event,
        user: username,
        subj: subject_id,
        brand: get_brand(),
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
    installer.onProcess = function(func) {
        var that = this;
        return function(result) {
            if(that.status !== that.PROCESSING) {
                return console.log("install is not processing, ignore it!");
            }
            
            func && func(result);
        };
    };

    var $install = $("#install");
    var appStatuses = null;
    $install.click(function() {
        _.each(apps, function(app) {
            app.status = "pending";
        });
        _log("tianyin.subject.install");
        var linkEls = $appList.find(".app a.install-link").toArray();
        _.each(linkEls, function(el) {
            el.click();
        });

        installer.status = installer.PROCESSING;
        apps.startAll();
    });

    function onTaskStatusChanged() {
        if (apps.isPending()) {
            // TODO notify finished apps
            console.log(apps.countFinished(), "apps installed");
            return;
        }

        status = apps.isAllInstalled() ? "success" : "failed";
        if (status === success) {
            _log("tianyin.subject.install.success");
            console.log("all installed!");
            // TODO  notify user 
        } else {
            console.log("not all installed");
            // TODO notify user
        }
    }

    IO.onmessage({
        "data.channel": "apps.installed"
    }, function(result) {
        console.log("apps installed", result);
    });

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
});

/*
    var tasks = {};
    tasks.ERR = "error";

    tasks.all = function(cb) {
        IO.requestAsync({
            url: "wdj://jobs/show.json",
            success: function(resp) {
                if (resp.state_code !== 200) {
                    return cb(tasks.ERR);
                }

                return cb(null, resp.body);
            }
        });
    };

    tasks.data = function(app, cb) {
        tasks.all(function(err, data) {
            if (err) {
                return cb(err);
            }

            var item = null;
            for (var i = 0; i < data.status.length; i++) {
                if (data.status[i].title === app.name) {
                    item = data.status[i];
                    break;
                }
            }

            return cb(null, item);
        });
    };

    tasks.cancel = function(app, cb) {
        tasks.data(app, function(err, data) {
            if (err) {
                return cb(err);
            }

            if (!data) {
                cb(null);
            }

            IO.requestAsync({
                url: "wdj://cancel.json",
                success: function(resp) {
                    cb(resp.state_code === 200 ? null, tasks.error);
                }
            }, {
                // TODO
                id: data.id
            });
        });
    };
    */
