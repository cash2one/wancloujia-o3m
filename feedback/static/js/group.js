$(function() {
	$("select").select2(select2_tip_options);
});

var FormModal = modals.FormModal;
var ActionModal = modals.ActionModal;
var text_generator = modals.text_generator;

$(function() {
	var modal = new FormModal($("#add-edit-group")[0], {
		title: text_generator("新增用户组", "编辑用户组"),
		msg: text_generator("新增用户组成功", "用户组信息修改成功"),
		process: Dajaxice.mgr.add_edit_group,
		clear: function(form) {
			form.id.value = "";
			form.name.value = "";
			$(form.permissions).val("").trigger('change');
			$(form.region).val("").trigger('change');
		},
		bind: function(form, group) {
			form.id.value = group.id;
			form.name.value = group.name;
			$(form.permissions).val(group.permissions.toString().split(",")).trigger('change')
		}
	});

	$("table").on('click', '.edit', function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var modal = new ActionModal($("#delete-group")[0], {
		tip: _.template("确认要删除&nbsp;<strong><%- name %></strong>&nbsp;吗？"),
		msg: '删除成功',
		process: Dajaxice.mgr.delete_group
	});

	$("table").on('click', '.delete', function() {
		modal.show($(this.parentNode).data());
	});
});
