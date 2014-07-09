define(function(require) {

require("jquery");
require("underscore");
require("bootstrap");
require("select2");
require("django-csrf-support");
require("ajax_upload");
var toast = require("toast");

function editAD(pk, cover, link) {
    return $.post('/ad/edit', {
        pk: pk,
        cover: cover,
        link: link
    }, "json");
}

$(function() {
    var $modal = $("#add-edit-ad");
    var $form = $("form", $modal);
    var form = $form[0];
    var $saveBtn = $(".save", $modal);
    var $cancelBtn = $(".cancel", $modal);

    var auw = new AjaxUploadWidget($(form.cover), {
        changeButtonText : "修改图片",
        removeButtonText : "删除图片",
        onError: function(data) {
            toast('error', '图片上传失败，请重试。');
        }
    });

    $("table").on("click", ".edit", function() {
        var ad = $(this.parentNode).data(); 
        _.each(["id", "link", "title"], function(attr) {
            form[attr].value = ad[attr]
        });
        $(form.cover).val(ad.cover).trigger('change');
        var tip = ad.title === '主广告位' ? '图片尺寸为725px*90px' : '图片尺寸为220px*90px';
        $modal.find(".cover-tip").html(tip);
        $modal.modal('show');
    });
    
    $modal.on('hidden.bs.modal', function() {
        auw.abort();
        _.each(["id", "title", "link"], function(attr) {
            form[attr].value = "";
        });
        $(form.cover).val("").trigger('change');
    });

    function loading() {
        $saveBtn.button('loading');
        $cancelBtn.button('loading');
    }

    function reset() {
        $saveBtn.button('reset');
        $cancelBtn.button('reset');
    }

    $saveBtn.click(function() {
        $form.submit();
    });

    $form.submit(function(e) {
        e.preventDefault();

        if(form.cover.value === "") {
            return toast('error', '图片不能为空');
        }

        if(form.link.value === "") {
            return toast('error', '链接不能为空');
        }

        if(!/^\w+:\/\/([^\s\.]+\.\S{2}|localhost[\:?\d]*)\S*$/.test(form.link.value)) {
            return toast('error', '链接格式不对');
        }

        loading(); 
        editAD(form.id.value, form.cover.value, form.link.value).done(function() {
            toast('success', '保存成功');
            setTimeout(function() {
                window.location.reload();
            }, 500);
        }).fail(function() {
            toast('error', '保存失败');
        }).always(function() {
            reset();
        });
    });
});
});

