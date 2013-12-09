$(function() {
	$("select").select2(select2_tip_options);
});

$(function() {
	var modal = new modals.FormModal($("#add-edit-company")[0], {
		title: modals.text_generator("新增公司", "编辑公司"),
		msg: modals.text_generator("新增公司成功", "公司信息修改成功"),
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
		}
	});

	$("table.companies").on('click', '.edit', function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var modal = new modals.FormModal($("#add-edit-store")[0], {
		title: modals.text_generator("新增门店", "编辑门店"),
		msg: modals.text_generator('新增门店成功', '门店信息修改成功'),
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
			$(form.company).val(store.company).trigger('change');
		}
	});

	$("table.stores").on('click', '.edit', function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var modal = new modals.ActionModal($("#delete-organization")[0], {
		tip: _.template("确认要删除&nbsp;<strong><%= name %></strong>&nbsp;吗？"),
		msg: '删除成功',
		process: Dajaxice.mgr.delete_organization
	});

	$("table").on('click', '.delete', function() {
		modal.show($(this.parentNode).data());
	});
});

$(function() {
	var modal = new modals.FormModal($("#add-edit-region")[0], {
		title: modals.text_generator("新增大区", "编辑大区"),
		msg: modals.text_generator('新增大区成功', '大区信息修改成功'),
		process: Dajaxice.mgr.add_edit_region,
		clear: function(form) {
			form.id.value = "";
			form.name.value = "";
		},
		bind: function(form, region) {
			form.id.value = region.id;
			form.name.value = region.name;
		}
	});

	$("table.regions").on('click', '.edit', function() {
		modal.show($(this.parentNode).data());
	});
});
