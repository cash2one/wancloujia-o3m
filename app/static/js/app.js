var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;

$(function() {
    var ADD_APP_MODE = "add";
    var EDIT_APP_MODE = "edit";

    var uploading = false;
    var $modal = $("#add-edit-app");
    var $form = $("#app-form", $modal);
    var form = $form[0];
    var $saveBtn = $(".save", $modal);
    var app = null;
    var mode = null;

    $("a[href=#add-edit-app]").click(function() {
        $modal.modal('show');
    });

    var auw = new AjaxUploadWidget($(form.app_icon), {
        changeButtonText: "修改图片",
        removeButtonText: "删除图片",
        onError: function(data) {
            toast('error', '图片上传失败，请重试。');
        }
    });

    function lock_check(func) {
        return function() {
            suning.modal.unlock($modal);
            func && func.apply(window, arguments);
        }
    }

    function str_size(size) {
        var result = "";
        if (size < 1024 * 1024) {
            result = (size / 1024).toFixed(2) + " KB";
        } else {
            result = (size / 1024 / 1024).toFixed(2) + " MB";
        }
        return result;
    }

    function set_category(value) {
        if (!value) {
            $parent.val("1").trigger('change');
            $category.val("").trigger('change');
        } else {
            var parent = categories.getParentPk(parseInt(app.category, 10));
            $parent.val(parent).trigger('change');
            $category.val(app.category).trigger('change');
        }
    }

    function set_popularize(value) {
        for (var i = 0; i < form.popularize.length; i++) {
            form.popularize[i].checked = form.popularize[i].value == value;
        }
    }

    function set_app_icon(value) {
        $(form.app_icon).val(value || "").trigger('change');
    }

    function clearForm() {
        form.id.value = "";
        form.package.value = "";

        form.apk.value = "";
        form.name.value = "";
        form.version.value = "";
        form.size.value = "";
        form.desc.value = "";

        set_app_icon();
        set_category();
        set_popularize("False");
    }

    function bindForm() {
        form.id.value = app.id;
        form.package.value = app.package;

        form.apk.value = app.apk;
        form.name.value = app.name;
        form.version.value = app.version;
        form.size.value = str_size(app.size);
        if (app.desc) form.desc.value = app.desc;

        set_app_icon(app.icon)
        if (app.popularize) set_popularize(app.popularize);
        if (app.category) set_category(app.category);
    }

    function loadApkInfo() {
        form.package.value = app.package;
        form.apk.value = app.apk;
        form.name.value = app.name;
        form.version.value = app.version;
        form.size.value = str_size(app.size);
        set_app_icon(app.icon);
    }

    function create_app(data) {
        var result = {
            apk: data.apk_id,
            apk_name: data.apk_name,
            name: data.name,
            version: data.version,
            size: Number(data.size),
            icon: data.icon,
            package: data.packageName,

            desc: data.desc || "",
            popularize: data.popularize || "",
            category: data.category || "",
            id: data.id || ""
        };
        return result;
    }

    function reload_apk_info(data) {
        if (mode == ADD_APP_MODE) {
            if (data.id) {
                mode = EDIT_APP_MODE;
                app = create_app(data);
                bindForm();
            } else {
                mode = ADD_APP_MODE;
                app = create_app(data);
                loadApkInfo();
            }
        } else {
            if (data.id && app.package == data.packageName) {
                mode = EDIT_APP_MODE;
                app = create_app(data);
                loadApkInfo();
            } else if (data.id && app.package != data.packageName) {
                mode = EDIT_APP_MODE;
                app = create_app(data);
                bindForm();
            } else {
                mode = ADD_APP_MODE;
                app = create_app(data);
                clearForm();
                loadApkInfo();
            }
        }
    }

    var apk_uploader = apk_upload($("#upload-apk"), {
        onCancel: function() {
            uploading = false;
        },
        onFailed: function() {
            uploading = false;
        },
        onDone: function(data) {
            uploading = false;
            reload_apk_info(data);
        },
        onStart: function() {
            uploading = true;
        }
    });

    $("table").on("click", ".edit", function() {
        app = $(this.parentNode).data();
        bindForm();
        $modal.modal('show');
    });

    var $category = $(form.category);
    var $parent = $(form.parent).change(function() {
        $category.select2('destroy');
        $category.html("");
        var options = categories.getOptionsByParentPk(this.value);
        var template = _.template("<option value='<%= pk %>'><%= name %></option>");
        $(template({
            pk: "",
            name: "-----"
        })).appendTo($category);
        _.each(options, function(option) {
            $(template(option)).appendTo($category);
        });
        $category.val('').trigger('change');
        $category.select2(select2_tip_options);
    });
    $category.select2(select2_tip_options);
    $parent.select2(select2_tip_options);
    set_category();

    $modal.on('show.bs.modal', function() {
        $form.parsley(parsley.bs_options);
        mode = form.id.value == "" ? ADD_APP_MODE : EDIT_APP_MODE;
        var title = mode == ADD_APP_MODE ? "新增应用" : "编辑应用";
        suning.modal.setTitle($modal, title);
    });

    $modal.on('hide.bs.modal', function() {
        auw.abort();
        clearForm();
        if (uploading) apk_uploader.cancel();
        apk_uploader.reset();
        $form.parsley('destroy');
    });

    $saveBtn.click(function() {
        $form.submit();
    });

    function field_check(func) {
        return function(data) {
            if (data.ret_code != 0 && data.field) {
                parsley.highlightError(form, data.field);
                toast('error', data.error);
                return;
            }

            func(data);
        }
    }

    $form.submit(function(e) {
        e.preventDefault();

        if (mode == ADD_APP_MODE && !app) {
            toast('error', uploading ? '正在上传应用，请稍等' : '请先上传应用文件');
            return;
        }

        if (!$form.parsley('validate')) return;

        var onSuccess = lock_check(login_check(field_check(error_check(function(data) {
            var msg = mode == ADD_APP_MODE ? '新增应用成功' : '应用信息修改成功';
            toast('success', msg);
            $modal.modal("hide");
            suning.reload(2000);
        }))));
        var onError = lock_check(suning.toastNetworkError);

        suning.modal.lock($modal);
        Dajaxice.app.add_edit_app(onSuccess, {
            form: $form.serialize(true)
        }, {
            error_callback: onError
        });
    });
});

$(function() {
    var app = null;
    var $modal = $("#delete-app");
    var $saveBtn = $(".save", $modal);

    $("table").on('click', '.delete', function() {
        app = $(this.parentNode).data();
        $('.model-name', $modal).html(app.name);
        $modal.modal('show');
    });

    function lock_check(func) {
        return function(data) {
            suning.modal.unlock($modal);
            func(data);
        }
    }

    $saveBtn.click(function() {
        suning.modal.lock($modal);
        Dajaxice.app.delete_app(lock_check(login_check(error_check(function(data) {
            $modal.modal('hide');
            toast('success', '删除成功');
            suning.reload(2000);
        }))), {
            id: app.id
        }, {
            error_callback: lock_check(suning.toastNetworkError)
        });
    });
});

$(function() {
    var mode = null;
    var PUBLISH_APP = "publish_app";
    var DROP_APP = "drop_app";
    var app = null;
    var $modal = $("#prompt");
    var $saveBtn = $modal.find(".save");

    $("table").on("click", ".publish", function() {
        mode = PUBLISH_APP;
        app = $(this.parentNode).data();
        $modal.modal('show');
    });

    $("table").on("click", ".drop", function() {
        mode = DROP_APP;
        app = $(this.parentNode).data();
        $modal.modal('show');
    });

    function lock_check(func) {
        return function(data) {
            suning.modal.unlock($modal);
            func(data);
        }
    }

    $modal.on('show.bs.modal', function() {
        var action = mode == PUBLISH_APP ? "上线应用" : "下线应用";
        $modal.find(".modal-title").html(action);
        if (mode == PUBLISH_APP) {
            var template = _.template("确定要上线应用&nbsp;<strong><%= name %></strong>&nbsp;吗?");
            $modal.find(".modal-body").html(template({
                name: app.name
            }));
        } else {
            $modal.find(".modal-body").html("如果应用下线了，将不能被手机助手用户看到，并且会排在应用列表的后面。确认继续吗？");
        }
    });

    $saveBtn.click(function() {
        var func = Dajaxice.app[mode];
        suning.modal.lock($modal);
        func(lock_check(login_check(error_check(function(data) {
            toast('success', mode == PUBLISH_APP ? '应用已上线' : '应用已下线');
            $modal.modal('hide');
            suning.reload(2000);
        }))), {
            id: app.id
        }, {
            error_callback: lock_check(suning.toastNetworkError)
        });
    });
});