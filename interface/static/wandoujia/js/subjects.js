require(["Narya"], function() {
    $(function() {
        var subject_template = _.template($("#subject_template").html());
        var $subjects_wrap = $("#subjects_wrap");
        var $subjects = $subjects_wrap.find(".special-content");
        $subjects.on('click', '.special-item', function() {
            var subject_id = $(this).data("id");
            if (!subject_id) return;

            window.location = "/interface/subjects/" + subject_id;

        });
        var $empty = $("#empty");
        var $loading = $("#loading");

        var count = 0;

        function sequence(callback, current) {
            return function() {
                console.log("current", current, "count", count);
                if (count != current) {
                    return;
                }

                callback.apply(null, arguments);
            }
        }

        function getDeviceInfo(cb) {
            var size = parseInt(Narya.Device.get("internalSDFreeCapacity")) +
                parseInt(Narya.Device.get("externalSDFreeCapacity"));

            function alter(value, default) {
                return value || default;
            }

            var build = Narya.Device.get("build");
            var model = build ? (build.get("model") || "") : "";

            return {
                model: model,
                size: size
            };
        }

        function refreshSubjects() {
            var device = getDeviceInfo();
            $loading.show();
            $subjects_wrap.hide();
            count++;
            getSubjects(device.model, device.size, sequence(function(err, data) {
                $loading.hide();

                if (err) {
                    return $empty.html("加载失败，请刷新重试！").show();
                }

                if (data.subjects.length === 0) {
                    return $empty.html("暂无应用专题").show();
                }

                $subjects.empty();
                _.each(data.subjects, function(subject) {
                    var html = subject_template({
                        subject: subject
                    }).trim();
                    $(html).appendTo($subjects);
                });
                $subjects_wrap.show();
            }, count));
        }

        Narya.Device.on('change:build', function() {
            console.log("info changed");
            refreshSubjects();
        });

        Narya.Device.on('change:internalSDFreeCapacity', function() {
            console.log("info changed");
            refreshSubjects();
        });

        Narya.Device.on('change:externalSDFreeCapacity', function() {
            console.log("info changed");
            refreshSubjects();
        });

        refreshSubjects();
    });
});