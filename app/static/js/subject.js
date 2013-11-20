var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;

$(function() {
    var $modal = $("#add-edit-subject");
    var $form = $("form", $modal);
    var form = $form[0];
    var $saveBtn = $(".save", $modal);
    var $apps = $(form.apps);
    var query_id = 0;

    var apps_cache = [];
    function parse_apps_cache(value) {
        var arr = value.split(",");
        var results = [];
        for(var i = 0; i < arr.length; i+=2) {
            results.push(arr[i]);
            apps_cache.push({
                id: arr[i],
                text: arr[i+1]
            });
        }
        return results;
    } 

    $apps.select2({
        tags: [],
        ajax: {
            url: '/app/search_apps/',
            dataType: 'json',
            data: function(term, page) {
                return {
                    q: term,
                    page_limit: 10,
                    p: page
                }
            },
            results: function(data, page) {
                if (data.ret_code != 0) return {
                    results: [],
                    more: false
                };
                var more = (page * 10) < data.total;
                return {
                    results: data.results,
                    more: more
                };
            }
        },
        initSelection: function(element, callback) {
            var value = $(element).val();
            if (form.id.value == "" || value == '') {
                callback([]);
                return;
            }

            callback(apps_cache);
        }
    });

    $apps.select2("container").find("ul.select2-choices").sortable({
        containment: 'parent',
        start: function() {
            $apps.select2("onSortStart");
        },
        update: function() {
            $apps.select2("onSortEnd");
        }
    });

    var auw = new AjaxUploadWidget($(form.cover), {
        changeButtonText: "修改图片",
        removeButtonText: "删除图片",
        onError: function(data) {
            suning.modal.unlock($modal);
            toast('error', '图片上传失败，请重试。');
        },
        onUpload: function() {
            suning.modal.lock($modal);
        },
        onComplete: function() {
            suning.modal.unlock($modal);
        }
    });

    function lock_check(func) {
        return function() {
            suning.modal.unlock($modal);
            func && func.apply(window, arguments);
        }
    }

    $("table").on("click", ".edit", function() {
        var subject = $(this.parentNode).data();
        form.id.value = subject.id;
        form.name.value = subject.name;
        form.desc.value = subject.desc;
        $(form.cover).val(subject.cover).trigger('change');
        var apps = parse_apps_cache(subject.apps);
        console.log("set apps: ", apps.join(","));
        $apps.val(apps.join(",")).trigger('change');
        $modal.modal('show');
    });

    $modal.on('hide.bs.modal', function() {
        form.id.value = "";
        form.name.value = "";
        form.desc.value = "";
        $(form.cover).val("").trigger('change');

        $apps.val("").trigger('change');
        $apps.select2('readonly', false);
        apps_cache = [];
        query_id++;
        $form.parsley('destroy');
    });

    $modal.on('show.bs.modal', function() {
        $form.parsley(parsley.bs_options);
        var title = !form.id.value ? '新增应用专题' : '修改应用专题';
        suning.modal.setTitle($modal, title);
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
        if (!$form.parsley('validate')) return;

        var onSuccess = lock_check(login_check(field_check(error_check(function(data) {
            var msg = !form.id.value ? '新增应用专题成功' : '应用专题修改成功';
            toast('success', msg);
            $modal.modal("hide");
            suning.reload(2000);
        }))));
        var onError = lock_check(suning.toastNetworkError);

        suning.modal.lock($modal);
        console.log("apps: ", form.apps.value);
        Dajaxice.app.add_edit_subject(onSuccess, {
            form: $form.serialize(true)
        }, {
            error_callback: onError
        });
    });
});

$(function() {
    var subject = null;
    var $modal = $("#delete-subject");
    var $saveBtn = $(".save", $modal);

    $("table").on('click', '.delete', function() {
        subject = $(this.parentNode).data();
        $('.model-name', $modal).html(subject.name);
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
        Dajaxice.app.delete_subject(lock_check(login_check(error_check(function(data) {
            $modal.modal('hide');
            toast('success', '删除成功');
            suning.reload(2000);
        }))), {
            id: subject.id
        }, {
            error_callback: lock_check(suning.toastNetworkError)
        });
    });
});

$(function() {
    var mode = null;
    var PUBLISH_SUBJECT = "publish_subject";
    var DROP_SUBJECT = "drop_subject";
    var subject = null;
    var $modal = $("#prompt");
    var $saveBtn = $modal.find(".save");

    $("table").on("click", ".publish", function() {
        mode = PUBLISH_SUBJECT;
        subject = $(this.parentNode).data();
        $modal.modal('show');
    });

    $("table").on("click", ".drop", function() {
        mode = DROP_SUBJECT;
        subject = $(this.parentNode).data();
        $modal.modal('show');
    });

    function lock_check(func) {
        return function(data) {
            suning.modal.unlock($modal);
            func(data);
        }
    }

    $modal.on('show.bs.modal', function() {
        var action = mode == PUBLISH_SUBJECT ? "上线应用专题" : "下线应用专题";
        $modal.find(".modal-title").html(action);
        if (mode == PUBLISH_SUBJECT) {
            var template = _.template("确定要上线应用专题&nbsp;<strong><%= name %></strong>&nbsp;吗?");
            $modal.find(".modal-body").html(template({
                name: subject.name
            }));
        } else {
            $modal.find(".modal-body").html("如果应用专题下线了，将不能被手机助手用户看到，并且会排在应用专题列表的后面。确认继续吗？");
        }
    });

    $saveBtn.click(function() {
        var func = Dajaxice.app[mode];
        suning.modal.lock($modal);
        func(lock_check(login_check(error_check(function(data) {
            toast('success', mode == PUBLISH_SUBJECT ? '应用专题已上线' : '应用专题已下线');
            $modal.modal('hide');
            suning.reload(2000);
        }))), {
            id: subject.id
        }, {
            error_callback: lock_check(suning.toastNetworkError)
        });
    });
});

$(function() {
    var $modal = $("#sort-subjects");
    $modal.find("table").tableDnD({
        onDragClass: "drag"
    })
    var $saveBtn = $modal.find(".save");

    function lock_check(func) {
        return function(data) {
            suning.modal.unlock($modal);
            func(data);
        }
    }

    $saveBtn.click(function() {
        var pks = [];
        $modal.find(".subject").each(function() {
            var id = $(this).data("id")
            if (id) pks.push(id);
        });
        if (pks.length == 0) return;

        suning.modal.lock($modal);
        Dajaxice.app.sort_subjects(lock_check(login_check(error_check(function(data) {
            toast('success', '操做成功！');
            $modal.modal('hide');
            suning.reload(2000);
        }))), {
            pks: pks.join(",")
        }, {
            error_callback: lock_check(suning.toastNetworkError)
        });
    });
});