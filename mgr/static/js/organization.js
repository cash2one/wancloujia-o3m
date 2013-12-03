$(function() {
	$("select").select2(select2_tip_options);
});

$(function() {
	var modal = new FormModal($("#add-edit-company")[0], {
		add_title: "新增公司",
		edit_title: "编辑公司",
		add_success_msg: '新增公司成功',
		edit_success_msg: '公司信息修改成功',
		process: Dajaxice.mgr.add_edit_company,
		clear: function(form) {
			form.id.value = "";
			form.name.value = "";
			form.code.value = "";
			$(form.region).val("").trigger('change');
		},
		bind: function(form, company) {
			form.id.value = company.id;
			form.code.value = company.code;
			form.name.value = company.name;
			$(form.region).val(company.region).trigger('change');
		},
		table: '.companies'
	});
});

$(function() {
	var modal = new FormModal($("#add-edit-store")[0], {
		add_title: "新增门店",
		edit_title: "编辑门店",
		add_success_msg: '新增门店成功',
		edit_success_msg: '门店信息修改成功',
		process: Dajaxice.mgr.add_edit_store,
		clear: function(form) {
			form.id.value = "";
			form.name.value = "";
			form.code.value = "";
			$(form.company).val("").trigger('change');
		},
		bind: function(form, store) {
			form.id.value = store.id;
			form.code.value = store.code;
			form.name.value = store.name;
			$(form.company).val(store.region).trigger('change');
		},
		table: '.stores'
	});
});

$(function() {
	var modal = new ActionModal($("#delete-organization")[0], {
		tip: _.template("确认要删除&nbsp;<strong><%= name %></strong>&nbsp;吗？"),
		msg: '删除成功',
		table: 'table',
		process: Dajaxice.mgr.delete_organization
	});
});

$(function() {
	var modal = new FormModal($("#add-edit-region")[0], {
		add_title: "新增大区",
		edit_title: "编辑大区",
		add_success_msg: '新增大区成功',
		edit_success_msg: '大区信息修改成功',
		process: Dajaxice.mgr.add_edit_region,
		clear: function(form) {
			form.id.value = "";
			form.name.value = "";
		},
		bind: function(form, region) {
			form.id.value = region.id;
			form.name.value = region.name;
		},
		table: '.regions'
	});
});