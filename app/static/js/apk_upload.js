(function(global) {
    function apk_upload($form, options) {
        var form = $form[0];
        var $upload = $(form.file);
        var $tip = $form.find(".tip");

        var $cancelBtn = $form.find(".cancel");
        $cancelBtn.click(function(e) {
            e.preventDefault();
            $("#fileupload").uploadify('cancel');
        });

        function onProgress(progress) {
            if (progress == 100) {
                $tip.html('正在解析应用信息...');
            } else {
                $tip.html('已上传' + progress + '%，请稍候...');
            }
        }

        function cancel_check(func) {
            return function(file, errorCode, errorMsg, errorString) {
                if (errorString == 'Cancel') return;

                func(file, errorCode, errorMsg, errorString);
            }
        }

        function show_uploading_ui(func) {
            return function() {
                $("#fileupload").uploadify('disable', true);
                $cancelBtn.show();
                $tip.empty().show();
                func && func.apply(global, arguments);
            }
        }

        function hide_uploading_ui(func) {
            return function() {
                $("#fileupload").uploadify('disable', false);
                $cancelBtn.hide();
                $tip.empty().hide();
                func && func.apply(global, arguments);
            }
        }

        $upload.uploadify({
            swf: '/static/uploadify.swf',
            uploader: 'upload',
            buttonText: "<span class='glyphicon glyphicon-upload'></span>&nbsp;选择文件",
            fileObjName: 'file',
            fileTypeExts: "*.apk",
            width: 100,
            height: 34,
            multi: false,
            formData: {
                csrfmiddlewaretoken: form.csrfmiddlewaretoken.value
            },
            onDisable: function() {
                $("#fileupload").css("top", '10000px');
            },
            onEnable: function() {
                $("#fileupload").css("top", '0px');
            },
            onSelectError: function() {
                toast('error', '文件出错，可能是文件类型不符合要求');
            },
            onUploadProgress: function(file, upload, total) {
                onProgress(parseInt(upload / total * 100, 10));
            },
            onUploadStart: show_uploading_ui(options.onStart),
            onCancel: hide_uploading_ui(options.onCancel),
            onUploadError: cancel_check(hide_uploading_ui(options.onFailed)),
            onUploadSuccess: hide_uploading_ui(options.onDone)
        });
    }

    global.apk_upload = apk_upload;
})(window);