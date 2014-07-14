define(function(require) {
    require("jquery");
    require("underscore");
    require("ajax_upload");
    require("select2");
    var csrf_token = require("django-csrf-support");


    var parseBytes = require("parse-bytes");
    var ApkUploader = require("apk_upload");

    function apkSize(size) {
        size = parseBytes(size, 'decimal');
        var results = [];
        if (size.mb > 0) {
            return (size.mb + size.kb / Math.pow(10, 3)).toFixed(1) + ' MB';
        }

        if (size.kb > 0) {
            return size.kb + ' KB';
        }

        return '';
    }

    $(function() {
        var $form = $("#app-form");
        var form = $form[0];
        AjaxUploadWidget.autoDiscover({
            changeButtonText: '修改',
            removeButtonText: '删除'
        });

        form.hsize.value = apkSize(form.size.value);
        $(form.size).change(function() {
            form.hsize.value = apkSize(this.value);
        });

        var uploader = ApkUploader($("#upload-apk"), {
            onStart: function() {},
            onDone: function(app) {
                console.log(app);
                _.each(["version", "name", "apk", "size", "sdk_version", "permissions"], function(field) {
                    $(form[field]).val(app[field]).trigger('change');
                });

                form.apk.value = app.apk_id;
                form.package.value = app.packageName;
                form.version_code.value = app.versionCode;

                $(form.app_icon).val(app.icon).trigger('change');
            },
            onCancel: function() {},
            onFailed: function() {}
        });
        var tag_str = $("#id_tags").val();
        $("#id_select_tags").on("change", function(e) {
            var temp_attr = $("#id_select_tags").val().split(",");
            $("#id_tags").val(temp_attr.join(","));
        });
        $("#id_select_tags").select2({tags: []});
        $("#id_select_tags").select2('val', tag_str.split(","));
    });
});
