$(function() {
	$("select").select2(select2_tip_options);
});

var FormModal = modals.FormModal;
var ActionModal = modals.ActionModal;
var text_generator = modals.text_generator;

var parsley_options = {
	validators: {
		phone: function() {
			return {
				validate: function(val) {
					return /^\d{11}$/.test(val);
				},
				priority: 2
			};
		}
	},
	messages: {
		phone: '请输入正确的手机号码'
	}
};

$(function() {
	var modal = new ActionModal($("#delete-user")[0], {
		tip: _.template("确认要删除&nbsp;<strong><%- username %></strong>&nbsp;吗？"),
		msg: '删除成功',
		process: Dajaxice.mgr.delete_user
	});

	$('table').on('click', '.delete', function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var modal = new FormModal($("#reset-password")[0], {
		title: "重置密码",
		msg: '修改密码成功',
		process: Dajaxice.mgr.reset_password,
		clear: function(form) {
			form.id.value = "";
			form.password.value = "";
			form.confirm.value = "";
		},
		bind: function(form, data) {
			form.id.value = data.id;
		},
		parsley: {
			validators: {
				equal: function() {
					return {
						validate: function(val) {
							return $("#reset-password form")[0].password.value == val;
						},
						priority: 2
					}
				}
			},
			messages: {
				equal: '两次输入的密码不相同'
			}
		}
	});

	$("table").on("click", ".pwd", function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var adminModal = new FormModal($("#add-edit-admin")[0], {
		title: text_generator("新增管理员", "编辑管理员信息"),
		msg: text_generator('新增管理员成功', '管理员信息修改成功'),
		process: Dajaxice.mgr.add_edit_admin,
		clear: function(form) {
			form.id.value = "";
			form.username.value = "";
			form.realname.value = "";
			form.phone.value = "";
			form.email.value = "";
			form.introduce.value = "";
			form.tel.value = "";
		},
		bind: function(form, user) {
			form.id.value = user.id;
			form.username.value = user.username;
			form.realname.value = user.realname;
			form.phone.value = user.phone;
			form.email.value = user.email;
			form.tel.value = user.tel;
			form.introduce.value = user.introduce;
		},
		parsley: parsley_options
	});

	var empModal = new FormModal($("#add-edit-employee")[0], {
		title: text_generator("新增普通用户", "编辑普通用户"),
		msg: text_generator('新增普通用户成功', '普通用户修改成功'),
		process: Dajaxice.mgr.add_edit_employee,
		clear: function(form) {
			form.id.value = "";
			form.username.value = "";
			form.realname.value = "";
			form.phone.value = "";
			form.email.value = "";
			form.introduce.value = "";
			form.tel.value = "";
			$("[name=organization]").val("").trigger('change');
			$("[name=groups]").val("").trigger('change');
			$("[name=user_permissions]").val("").trigger('change');
		},
		bind: function(form, user) {
			form.id.value = user.id;
			form.username.value = user.username;
			form.realname.value = user.realname;
			form.phone.value = user.phone;
			form.email.value = user.email;
			form.tel.value = user.tel;
			form.introduce.value = user.introduce;
			$("[name=organization]").val(user.organization).trigger('change');
			$("[name=groups]").val(user.groups.toString().split(",")).trigger('change');
			$("[name=user_permissions]").val(user.permissions.toString().split(",")).trigger('change');
		},
		parsley: parsley_options
	});

	empModal.params = function() {
		var permissions = !this.form.user_permissions ? "" : 
							($(this.form.user_permissions).val() || []).join(",");
		return {
			form: this.$form.serialize(true),
			permissions: permissions
		};
	};

	$("table").on("click", ".edit", function() {
		var user = $(this.parentNode).data();
		user.type == "admin" ? adminModal.show(user) : empModal.show(user);
	});
});
