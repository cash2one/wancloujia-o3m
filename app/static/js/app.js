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
		form.version_code.value = "";

        form.apk.value = "";
        form.name.value = "";
        form.version.value = "";
        form.version_code.value = "";
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
		form.version_code.value = app.version_code;
        form.size.value = str_size(app.size);
        if (app.desc) form.desc.value = app.desc;

        set_app_icon(app.icon)
        if (app.popularize) set_popularize(app.popularize);
        if (app.category) set_category(app.category);
    }

    function loadApkInfo() {
        form.package.value = app.package;
		form.version_code.value = app.version_code;
        form.apk.value = app.apk;
        form.name.value = app.name;
        form.version.value = app.version;
        form.version_code.value = app.version_code;
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
			version_code: data.versionCode,

            desc: data.desc || "",
            popularize: data.popularize || "",
            category: data.category || "",
            id: data.id || "",
			old_version_code: data.oldVersionCode || "",
			old_version: data.oldVersion || ""
        };
        return result;
    }

    function reload_apk_info(data) {
        console.log(data);
		if (mode == ADD_APP_MODE) {
            if (data.id) {
                mode = EDIT_APP_MODE;
                app = create_app(data);

				var hint_msg = "";
				var confirm_label = "覆盖";
				if (app.old_version_code < app.version_code) {
					hint_msg = "本次上传版本高于已存在版本，是否需要覆盖？";
				} else if (app.old_version_code == app.version_code) {
					hint_msg = "本次上传版本与已存在版本一致，是否需要覆盖？";
				} else {
					hint_msg = "本次上传版本低于已存在版本，是否继续上传？";
					confirm_label = "继续";
				}
				bootbox.dialog({
					title: '提示',
					message: '<p>该应用已存在，信息如下：</p><br /><p>应用名称：' + app.name + '</p><p>版本号：' + app.old_version + '</p><br /><p>' + hint_msg + '</p>',
					closeButton: false,
					className: 'app-dialog',
					buttons: {
						overwrite: {
							label: confirm_label,
							className: 'btn-primary',
							callback: function() {
								bindForm();
							}
						},
						cancel: {
							label: '取消',
							className: 'btn-default',
							callback: function() {
								$('#add-edit-app').modal('hide');
							}
						}
					}
				});
            } else {
                mode = ADD_APP_MODE;
                app = create_app(data);
                loadApkInfo();
            }
        } else {
            if (data.id && app.package == data.packageName) {
                mode = EDIT_APP_MODE;
                app = create_app(data);

				var hint_msg = "";
				var confirm_label = "覆盖";
				if (app.version_code == app.old_version_code) {
					hint_msg = "本次上传版本与已存在版本一致，是否需要覆盖？";
					bootbox.dialog({
						title: '提示',
						message: '<p>该应用已存在，信息如下：</p><br /><p>应用名称：' + app.name + '</p><p>版本号：' + app.old_version + '</p><br /><p>' + hint_msg + '</p>',
						closeButton: false,
						className: 'app-dialog',
						buttons: {
							overwrite: {
								label: confirm_label,
								className: 'btn-primary',
								callback: function() {
									loadApkInfo();
								}
							},
							cancel: {
								label: '取消',
								className: 'btn-default',
								callback: function() {
									$('#add-edit-app').modal('hide');
								}
							}
						}
					});
				} else if (app.version_code < app.old_version_code) {
					hint_msg = "本次上传版本低于已存在版本，是否继续上传？";
					confirm_label = "继续";
					bootbox.dialog({
						title: '提示',
						message: '<p>该应用已存在，信息如下：</p><br /><p>应用名称：' + app.name + '</p><p>版本号：' + app.old_version + '</p><br /><p>' + hint_msg + '</p>',
						closeButton: false,
						className: 'app-dialog',
						buttons: {
							overwrite: {
								label: confirm_label,
								className: 'btn-primary',
								callback: function() {
									loadApkInfo();
								}
							},
							cancel: {
								label: '取消',
								className: 'btn-default',
								callback: function() {
									$('#add-edit-app').modal('hide');
								}
							}
						}
					});
				} else {
					loadApkInfo();
				}
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
        var template = _.template("<option value='<%- pk %>'><%- name %></option>");
        /*
        $(template({
            pk: "",
            name: "-----"
        })).appendTo($category);
        */
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
    var modal = new modals.ActionModal($("#delete-app")[0], {
        tip: _.template("确认要删除&nbsp;<strong><%- name %></strong>&nbsp;吗?"),
        msg: '删除成功',
        process: Dajaxice.app.delete_app
    });

    $("table").on('click', '.delete', function() {
        modal.show($(this.parentNode).data());
    });
});

$(function() {
    var modal = new modals.ActionModal($("#publish-app")[0], {
        tip: _.template("确定要上线应用&nbsp;<strong><%- name %></strong>&nbsp;吗?"),
        msg: '应用已上线',
        process: Dajaxice.app.publish_app
    });

    $("table").on('click', '.publish', function() {
        modal.show($(this.parentNode).data());
    });
});

$(function() {
    var modal = new modals.ActionModal($("#drop-app")[0], {
        tip: _.template("如果应用下线了，将不能被手机助手用户看到，" +
                        "并且会排在应用列表的后面。确认继续吗？"),
        msg: '应用已下线',
        process: Dajaxice.app.drop_app
    });

    $("table").on('click', '.drop', function() {
        modal.show($(this.parentNode).data());
    });
});
