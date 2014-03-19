var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;

function _reload(millies) {
    setTimeout(function() {
        window.location = "/app/subject/map";
    }, millies);
}

$(function() {
    var $modelModal = $("#add-edit-subjectmap-model");
    var $modelForm = $("form", $modelModal);
    var modelForm = $modelForm[0];
    var $saveBtn = $(".save", $modelModal);
    var $model = $('#id_model', $modelModal);
    var $subject = $('#id_subject', $modelModal);

    function lock_check(func) {
        return function() {
            suning.modal.unlock($modelModal);
            func && func.apply(window, arguments);
        }
    }

    $modelModal.on('hide.bs.modal', function() {
        modelForm.id.value = "";
        modelForm.type.value = "";

        $model.val("").trigger('change');
        $subject.val("").trigger('change');

        $modelForm.parsley('destroy');
    });

    $(".subjectmap-type-1").on("click", ".edit", function() {
        var subjectmap = $(this.parentNode).data();
        modelForm.id.value = subjectmap.id;
        modelForm.type.value = subjectmap.type;
        $model.val(subjectmap.model).trigger('change');
        $subject.val(subjectmap.subject).trigger('change');

        $modelModal.modal('show');
    });

    $modelModal.on('show.bs.modal', function() {
        $modelForm.parsley(parsley.bs_options);
        var title = !modelForm.id.value ? '新增机型适配' : '修改机型适配';
        suning.modal.setTitle($modelModal, title);
    });

    $saveBtn.click(function() {
        $modelForm.submit();
    });

    function field_check(func) {
        return function(data) {
            if (data.ret_code != 0 && data.field) {
                parsley.highlightError(modelForm, data.field);
                toast('error', data.error);
                return;
            }

            func(data);
        }
    }

    $modelForm.submit(function(e) {
        e.preventDefault();
        if (!$modelForm.parsley('validate')) return;

        var onSuccess = lock_check(login_check(field_check(error_check(function(data) {
            var msg = !modelForm.id.value ? '新增机型适配成功' : '机型适配修改成功';
            toast('success', msg);
            $modelModal.modal("hide");
            _reload(2000);
        }))));
        var onError = lock_check(suning.toastNetworkError);

        suning.modal.lock($modelModal);
        Dajaxice.app.add_edit_subjectmap_model(onSuccess, {
            form: $modelForm.serialize(true)
        }, {
            error_callback: onError
        });
    });
});

$(function() {
    var $memModal = $("#add-edit-subjectmap-memsize");
    var $memForm = $("form", $memModal);
    var memForm = $memForm[0];
    var $saveBtn = $(".save", $memModal);
    var $memsize = $('#id_mem_size', $memModal);
    var $subject = $('#id_subject2', $memModal);

    function lock_check(func) {
        return function() {
            suning.modal.unlock($memModal);
            func && func.apply(window, arguments);
        }
    }

    $memModal.on('hide.bs.modal', function() {
        memForm.id.value = "";
        $memsize.val("").trigger('change');
        $subject.val("").trigger('change');

        $memForm.parsley('destroy');
    });

    $(".subjectmap-type-2").on("click", ".edit", function() {
        var subjectmap = $(this.parentNode).data();
        memForm.id.value = subjectmap.id;
        memForm.type.value = subjectmap.type;
        $memsize.val(subjectmap.memsize).trigger('change');
        $subject.val(subjectmap.subject).trigger('change');

        $memModal.modal('show');
    });

    $memModal.on('show.bs.modal', function() {
        $memForm.parsley(parsley.bs_options);
        var title = !memForm.id.value ? '新增存储空间适配' : '修改存储空间适配';
        suning.modal.setTitle($memModal, title);
    });

    $saveBtn.click(function() {
        $memForm.submit();
    });

    function field_check(func) {
        return function(data) {
            if (data.ret_code != 0 && data.field) {
                parsley.highlightError(memForm, data.field);
                toast('error', data.error);
                return;
            }

            func(data);
        }
    }

    $memForm.submit(function(e) {
        e.preventDefault();
        if (!$memForm.parsley('validate')) return;

        var onSuccess = lock_check(login_check(field_check(error_check(function(data) {
            var msg = !memForm.id.value ? '新增存储空间适配成功' : '存储空间适配修改成功';
            toast('success', msg);
            $memModal.modal("hide");
            _reload(2000);
        }))));
        var onError = lock_check(suning.toastNetworkError);

        suning.modal.lock($memModal);
        Dajaxice.app.add_edit_subjectmap_memsize(onSuccess, {
            form: $memForm.serialize(true)
        }, {
            error_callback: onError
        });
    });
});

$(function() {
    var modal = new modals.ActionModal($("#delete-subjectmap")[0], {
        tip: _.template("确认要删除&nbsp;<strong><%- name %></strong>&nbsp;吗?"),
        msg: '删除成功',
        process: Dajaxice.app.delete_subjectmap
    });

    $("table").on('click', '.delete', function() {
        modal.show($(this.parentNode).data());
    });
});

$(function() {
    var $form = $(".form-filter");
    var form = $form[0];
    var EMPTY_SELECTION = {
        'id': '',
        'text': '---------'
    };

    $(form.mem_size).select2();

    $(form.model).select2($.extend({}, select2_tip_options, {
        query: function(query) {
            $.get("/model/query", {
                q: query.term
            }).done(function(data) {
                query.callback(data);
            }).error(function() {
                result = {
                    results: [EMPTY_SELECTION],
                    more: false
                };
                query.callback(result);
            });
        },
        initSelection: function(el, callback) {
            function get_model(id) {
                return $.get("/model/" + id).then(function(data) {
                    if (data.ret_code !== 0) {
                        throw new Error("Server Error");
                    }

                    return {
                        text: data.name,
                        id: data.id
                    };
                });
            }

            var id = $(el).val();
            if (!id) {
                return setTimeout(function() {
                    callback(EMPTY_SELECTION);
                }, 0);
            }

            get_model(id).then(function(model) {
                callback(model);
            }, function() {
                callback(EMPTY_SELECTION);
            });
        }
    }));

    $(form.updator).select2($.extend({}, select2_tip_options, {
        query: function(query) {
            $.get("/app/updators", {
                query: query.term
            }).done(function(data) {
                query.callback(data);
            }).error(function() {
                result = {
                    results: [EMPTY_SELECTION],
                    more: false
                };
                query.callback(result);
            });
        },
        initSelection: function(el, callback) {
            var $el = $(el);
            var id = $el.val();
            if (id) {
                $.get("/app/updators", {
                    id: id
                }).done(function(data) {
                    callback(data);
                }).error(function() {
                    callback(EMPTY_SELECTION);
                });
            } else {
                callback(EMPTY_SELECTION);
            }
        }
    }));
});