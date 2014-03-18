var FormModal = modals.FormModal;
var ActionModal = modals.ActionModal;
var text_generator = modals.text_generator;

$(function() {
    var modal = new FormModal($("#add-edit-model")[0], {
        title: text_generator("新增机型", "编辑机型"),
        msg: text_generator("新增机型成功", "机型息修改成功"),
        process: Dajaxice.modelmgr.add_edit_model,
        clear: function(form) {
            form.id.value = "";
            form.name.value = "";
            form.ua.value = "";
        },
        bind: function(form, model) {
            form.id.value = model.id;
            form.name.value = model.name;
            form.ua.value = model.ua;
        }
    });

    $("table").on('click', '.edit', function() {
        modal.show($(this.parentNode).data());
    });
});

$(function() {
    var modal = new ActionModal($("#delete-model")[0], {
        tip: _.template("确认要删除&nbsp;<strong><%- name %></strong>&nbsp;吗？"),
        msg: '删除成功',
        process: Dajaxice.modelmgr.delete_model
    });

    $("table").on('click', '.delete', function() {
        modal.show($(this.parentNode).data());
    });
});
