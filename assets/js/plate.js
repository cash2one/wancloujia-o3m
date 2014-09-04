define(function(require) {
    require("jquery");
    require("bootstrap");
    require("select2");
    require("jquery.ui.sortable");
    require("django-csrf-support");
    require("ajax_upload");
    var toast = require("toast");

    function editSubject(pk,position,name,cover,apps) {
        return $.post("/app/plate/edit", {
            pk: pk,
            position:position,
            name: name,
            cover: cover,
            apps: apps
        }, "json");
    }

    $(function() {
        var $modal = $("#add-edit-plate");
        var $form = $("form", $modal);
        var form = $form[0];
        var $saveBtn = $(".save", $modal);
        var $apps = $(form.apps);
        var query_id = 0;

        var apps_cache = [];

        function parse_apps_cache(value) {
            var arr = value.split(",");
            var results = [];
            for (var i = 0; i < arr.length; i += 2) {
                results.push(arr[i]);
                apps_cache.push({
                    id: arr[i],
                    text: arr[i + 1] + '(' + arr[i] + ')'
                });
            }
            return results;
        }

        var select2_options = {
            formatSearching: function() {
                return "搜索中...";
            },
            formatNoMatches: function() {
                return "没有搜索结果";
            },
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
        };

        $apps.select2(select2_options);
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
                toast('error', '图片上传失败，请重试。');
            }
        });

        $("table").on("click", ".edit", function() {
            var plate = $(this.parentNode).data();
            form.id.value = plate.id;
            form.name.value = plate.name;
            form.position.value = plate.position;
            $(form.cover).val(plate.cover).trigger('change');
            var apps = parse_apps_cache(plate.apps);
            console.log("set apps: ", apps.join(","));
            $apps.val(apps.join(",")).trigger('change');
            $modal.modal('show');
        });

        $modal.on('hide.bs.modal', function() {
            auw.abort();
            form.id.value = "";
            form.name.value = "";
            form.position.value="";
            $(form.cover).val("").trigger('change');


            $apps.val("").trigger('change');
            $apps.select2('readonly', false);
            apps_cache = [];
            query_id++;
        });

        $modal.on('show.bs.modal', function() {
            $modal.find(".title").html('修改集合页');
        });

        $saveBtn.click(function() {
            $form.submit();
        });

        $form.submit(function(e) {
            e.preventDefault();

            var onSuccess = function(data) {
                var msg = !form.id.value ? '新增应用专题成功' : '应用专题修改成功';
                toast('success', msg);
                $modal.modal("hide");
            };

            console.log("apps: ", form.apps.value);
            $modal.find(".save").button("loading");
            editSubject(form.id.value,form.position.value,form.name.value,form.cover.value,form.apps.value).done(function(data) {
                if(data.ret_code !== 0) {
                    toast('error', '操作失败');
                    return;
                }
                
                toast('success', '操作成功');
                setTimeout(function() {
                    window.location.reload();
                }, 500);
            }).fail(function() {
                toast('error', '操作失败');
            }).always(function() {
                $modal.find(".save").button("reset");
            });
        });
    });

    $(function() {
        /*
        var modal = new modals.ActionModal($("#delete-subject")[0], {
            tip: _.template("确认要删除&nbsp;<strong><%- name %></strong>&nbsp;吗?"),
            msg: '删除成功',
            process: Dajaxice.app.delete_subject
        });

        $("table").on('click', '.delete', function() {
            modal.show($(this.parentNode).data());
        });
        */
    });
});
