(function() {

    var selections = new Array();

    function parseSelections(value) {
        var selections = new Array();
        var arr = value.split(",");
        if (arr.length < 2) {
            return selections;
        }

        for (var i = 0; i < arr.length; i += 2) {
            selections.push({
                model: arr[i],
                subject: parseInt(arr[i + 1], 10)
            });
        }
        return selections;
    }

    function getSelection(model) {
        return _.find(selections, function(selection) {
            return selection.model === model;
        });
    }

    function serialize(selections) {
        var result = null;
        var arr = new Array();
        for (var i = 0; i < selections.length; i++) {
            var selection = selections[i];
            arr.push(selection.model);
            arr.push(selection.subject);
        }
        result = arr.join(",");
        __log("serialize selections: " + result + " length: " + result.length);

        if (result.length > 3000) {
            return serialize(selections.slice(0, selections.length-1));
        } else {
            return result;
        }
    }

    function getSelections() {
        var value = $.cookie("selections") || "";
        __log("selections in cookie: " + value);
        selections = parseSelections(value);
        __log(typeof(selections));
        __log("selections parsed: " + _.map(selections, _.pairs).join(","));
    }

    function updateSelection(model, subject) {
        var selection = null;
        for (var i = 0; i < selections.length; i++) {
            var _selection = selections[i];
            if (_selection.model === model) {
                _selection.subject = subject;
                selection = _selection;
            }
        }

        if (selection === null) {
            selections.unshift({
                model: model,
                subject: subject
            });
        }

        $.cookie("selections", serialize(selections), {expires: 30});
    }


    function __log(s) {
        $("#logs").append("<li>" + s + "</li>");
    }

    function getSubjects(model, size, callback) {
        $.get("/interface/getSubjects", {
            model: model,
            size: size,
            timestamp: new Date().getTime()
        }, "json").done(function(data) {
            if (data.ret_code != 0) {
                return callback("error");
            }

            callback(null, data);
        }).fail(function() {
            callback("error");
        });
    };

    var $empty;
    var $loading;
    var $subjects_wrap;
    var $subjects;

    var subject_template;

    var model = "";
    var deviceid = "";
    var size = "";
    var status = "init";


    function openSubject(id) {
        //setTimeout(function() {
        window.location = "/interface/subjects/" + id;
        //}, 2000);
    }

    function resetEmpty() {
        $empty.html("暂无应用专题");
    }

    function ready() {
        getSelections();

        $empty = $("#empty");
        $loading = $("#loading");
        $subjects_wrap = $("#subjects_wrap");
        $subjects = $subjects_wrap.find(".special-content");
        subject_template = _.template($("#subject_template").html());

        $loading.show();
        $subjects.on('click', '.special-item', function() {
            var subject_id = $(this).data("id");
            if (!subject_id) return;
            updateSelection(model, subject_id);
            openSubject(subject_id);
        });

        setTimeout(function() {
            if (status === "init") {
                $loading.hide();
                $empty.html("连接异常，请尝试重新连接手机");
                $empty.show();
            }
        }, 10 * 1000);


        $(nativeMessage).on('device.info', function(e, deviceInfo) {
            if (status !== "init") {
                return;
            }

            __log(_.pairs(deviceInfo));
            __log("storage");
            _.each(deviceInfo.storage_infos, function(item) {
                __log(_.pairs(item));
            });

            if (!deviceInfo.is_available) {
                status = "fail";
                $loading.hide();
                return $empty.html("暂时没有专题").show();
            }

            if (!deviceInfo.is_connected ||
                deviceInfo.model === undefined ||
                deviceInfo.storage_infos === undefined ||
                deviceInfo.storage_infos.length === 0) {
                return;
            }

            var internalSDCapacity = 0;
            var externalSDCapacity = 0;
            var systemCapacity = 0;
            _.each(deviceInfo.storage_infos, function(info) {
                if (info.type === 0 && systemCapacity === 0) {
                    systemCapacity = parseInt(info.available_size, 10);
                }

                if (info.type === 1 && internalSDCapacity === 0) {
                    internalSDCapacity = parseInt(info.available_size, 10);
                }

                if (info.type === 2 && externalSDCapacity === 0) {
                    externalSDCapacity = parseInt(info.available_size, 10);
                }
            });

            __log("device info got!");
            status = "ready";
            model = deviceInfo.model;
            deviceid = deviceInfo.device_id;
            size = (systemCapacity + internalSDCapacity + externalSDCapacity) * 1024 * 1024;

            $subjects.empty();
            $loading.show();
            $empty.hide();
            getSubjects(model, size, function(err, data) {
                __log("model: " + model + " size: " + size);
                $loading.hide();
                if (err) {
                    return $empty.html("加载失败，请刷新重试！").show();
                }

                var subjects = data.subjects;
                if (subjects.length === 0) {
                    return $empty.html("暂无应用专题").show();
                }

                if (subjects.length === 1) {
                    __log("result subject: " + _.pairs(subjects[0]));
                    __log("ready to jump!");
                    return openSubject(subjects[0].id);
                }


                var selection = getSelection(model);
                if (selection) {
                    __log("selection got from cookie: " + _.pairs(selection));
                    return openSubject(selection.subject);
                }

                _.each(data.subjects, function(subject) {
                    var html = subject_template({
                        subject: subject
                    });
                    var html = html.replace(/^\s+|\s+$/g, '');
                    $(html).appendTo($subjects);
                });
                $subjects_wrap.show();
            });
        });

        sendMessageToNative('dom.ready', '');
        sendMessageToNative('device.info', '');
    }

    $(ready);
})();
