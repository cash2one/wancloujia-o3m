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
                if (errorString == 'Cancelled') return;

                func(file, errorCode, errorMsg, errorString);
            }
        }

        function show_uploading_ui(func) {
            return function() {
                $("#fileupload").uploadify('disable', true);
                $cancelBtn.show();
                $tip.empty();
                func && func.apply(global, arguments);
            }
        }

        function hide_uploading_ui(func) {
            return function() {
                $("#fileupload").uploadify('disable', false);
                $cancelBtn.hide();
                $tip.empty();
                func && func.apply(global, arguments);
            }
        }

        function setButtonText(text) {
            var html = "<span class='glyphicon glyphicon-upload'></span>&nbsp;" + text;
            $("#fileupload .uploadify-button-text").html(html);

        }

        function upload_error_check(func) {
            return function(file, result) {
                var data = $.parseJSON(result);
                if (data.ret_code && data.ret_code != 0) {
                    var msg = "";
                    if (data.ret_msg == "not_login_error") {
                        msg = "会话可能已经过期，请重新登录";
                    } else if (data.ret_msg == "inspect_apk_failed") {
                        msg = "应用文件解析失败，文件可能已经损坏";
                    } else {
                        msg = "权限不足";
                    }
                    $tip.html(msg);
                    setButtonText("重新上传");
                    options.onFailed();
                    return;
                }

                setButtonText("选择文件");
                $tip.html('上传成功');
                func && func.apply(global, [data]);
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
            onUploadError: cancel_check(hide_uploading_ui(function() {
                setButtonText("重新上传");
                $tip.html("上传失败，可能是网络发生异常");
                options.onFailed();
            })),
            onUploadSuccess: hide_uploading_ui(upload_error_check(options.onDone))
        });

        return {
            reset: function() {
                setButtonText("选择文件");
                $tip.empty();
            },

            cancel: function() {
                $("#fileupload").uploadify('cancel');
            }
        };
    }

    global.apk_upload = apk_upload;
})(window);