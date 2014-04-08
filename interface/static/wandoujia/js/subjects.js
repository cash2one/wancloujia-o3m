(function() {

    function __log(s) {
        //return;
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
        window.location = "/interface/subjects/" + id;
    }

    function resetEmpty() {
        $empty.html("暂无应用专题");
    }


    function ready() {
        $empty = $("#empty");
        $loading = $("#loading");
        $subjects_wrap = $("#subjects_wrap");
        $subjects = $subjects_wrap.find(".special-content");
        subject_template = _.template($("#subject_template").html());

        $loading.show();
        $subjects.on('click', '.special-item', function() {
            var subject_id = $(this).data("id");
            if (!subject_id) return;
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
            if(status !== "init") {
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

                if (info.type === 2 && extenalSDCapacity === 0) {
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
