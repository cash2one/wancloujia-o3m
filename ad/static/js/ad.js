$(function() {
    $("select").select2();
    
});

var login_check = suning.decorators.login_check;
var error_check = suning.decorators.error_check;

$(function() {
    var $modal = $("#reorder-ad");
    if($modal.find(".ad").length == 0) return;

    var $saveBtn = $modal.find(".save");

    $("#reorder-ad table").tableDnD({
        onDragClass: "drag"
    });

    function lock_check(func) {
        return function(data) {
            suning.modal.unlock($modal);
            func(data);
        }
    }

    $saveBtn.click(function() {
        var pks = [];
        $modal.find(".ad").each(function() {
            var id = $(this).data("id")
            if (id) pks.push(id); 
        });
        if(pks.length == 0)  return;

        suning.modal.lock($modal);
        Dajaxice.ad.sort_ad(lock_check(login_check(error_check(function(data) {
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

$(function() {
    var $modal = $("#add-edit-ad");
    var $form = $("form", $modal);
    var form = $form[0];
    var $saveBtn = $(".save", $modal);
    var $cancelBtn = $(".cancel", $modal);

    var options = $.extend({}, parsley.bs_options, {
        excluded: '[type=hidden], #id_cover',
    });

    var auw = new AjaxUploadWidget($(form.cover), {
        changeButtonText : "修改图片",
        removeButtonText : "删除图片",
        onError: function(data) {
            toast('error', '图片上传失败，请重试。');
        }
    });

    $("#add_ad").click(function() {
        $modal.modal('show');
    });

    $("table").on("click", ".edit", function() {
        var ad = $(this.parentNode).data(); 
        form.id.value = ad.id;
        form.visible.checked = ad.visible
        form.title.value = ad.title;
        $(form.cover).val(ad.cover).trigger('change');
        form.from_date.value = ad.from_date;
        form.to_date.value = ad.to_date;
        form.desc.value = ad.desc;
        form.position.value = ad.position;
        $modal.modal('show');
    });

    var $from = $("[name=from_date]");
    var $to = $("[name=to_date]");

    function ensureDate(fromDate) {
        $from.datetimepicker('setDate', fromDate);
        var startDate = new Date(fromDate.getTime() + 1000 * 60 * 5);
        $to.datetimepicker("setStartDate", startDate);
        if (!$to.val()) {
            return;
        }

        var toDate = parseDate($to.val());
        if (toDate.getTime() < startDate.getTime()) {
            $to.datetimepicker("setDate", startDate);
        }
    }

    function parseDate(value) {
        var regex = /(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d)/;
        var result = value.match(regex);
        var year = parseInt(result[1], 10);
        var month = parseInt(result[2], 10);
        var date = parseInt(result[3], 10);
        var hours = parseInt(result[4], 10);
        var minutes = parseInt(result[5], 10);
        return new Date(year, month-1, date, hours, minutes);
    }

    $from.change(function() {
        ensureDate(parseDate(this.value));
    });

    $modal.on('shown.bs.modal', function() {
        $form.parsley(options);
        var title = form.id.value == "" ? "新增广告" : "编辑广告";
        $(".modal-title", $modal).html(title);

        if($from.val() != "") {
            ensureDate(parseDate($from.val()));
        } else {
            ensureDate(new Date());
        }
    });

    $modal.on('hidden.bs.modal', function() {
        auw.abort();
        form.id.value = "";
        form.visible.checked = false;
        form.title.value = "";
        $(form.cover).val("").trigger('change');
        form.cover.value = "";
        form.from_date.value = "";
        form.to_date.value = "";
        form.desc.value = "";
        form.position.value = 0;
        $form.parsley('destroy');
    });

    function loading() {
        $saveBtn.button('loading');
        $cancelBtn.button('loading');
    }

    function reset() {
        $saveBtn.button('reset');
        $cancelBtn.button('reset');
    }

    function btn_check(func) {
        return function(data) {
            reset();
            func(data);
        }
    }

    $saveBtn.click(function() {
        $form.submit();
    });

    function field_check(func) {
        return function(data) {
            if (data.ret_code != 0 && data.field) {
                suning.modal.highlightError(form, data.field);
                toast('error', data.error);
                return;
            }

            func(data);
        }
    }

    $form.submit(function(e) {
        e.preventDefault();
        if (!$form.parsley('validate')) {
            return;
        }

        loading(); 
        Dajaxice.ad.add_edit_ad(btn_check
            (login_check
            (field_check
            (error_check
            (function(data) {
                var msg = form.visible.checked ? '保存成功': 
                            '保存成功，因本条广告状态为隐藏，所以排在列表的后面';
                toast('success', msg);
                $modal.modal('hide');
                suning.reload(2000);
        })))), { 
            form: $form.serialize(true),
            visible: form.visible.checked
        }, {
            error_callback: function() {
                reset();
                toast('error', NETWORK_ERROR_MSG);
            }
        });
    });
});

$(function() {
    var $modal = $("#delete-ad");
    var modal = new modals.ActionModal($modal[0], {
        tip: _.template("确认要删除&nbsp;<strong><%- title %></strong>&nbsp;吗?"),
        msg: '删除成功',
        process: Dajaxice.ad.delete_ad
    });

    $("table").on('click', '.delete', function() {
        modal.show($(this.parentNode).data());
    });
});

