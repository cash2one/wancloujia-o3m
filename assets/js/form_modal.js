(function(window) {
	var error_check = suning.decorators.error_check;
	var login_check = suning.decorators.login_check;
	var toastNetworkError = suning.toastNetworkError;

	function _onSubmit(e) {
		e.preventDefault();
		if (!this.$form.parsley('validate')) return;

		var that = this;

		function btn_check(func) {
			return function(data) {
				suning.modal.unlock(that.$el);
				func && func(data);
			};
		}

		function field_check(func) {
			return function(data) {
				if (data.ret_code != 0 && data.field) {
					suning.modal.highlightError(that.form, data.field);
					toast('error', data.error);
					return;
				}

				func && func(data);
			}
		}

		var onSuccess = btn_check(login_check(field_check(error_check(function() {
			toast('success', that.msg());
			that.$el.modal('hide');
			suning.reload(2000);
		}))));
		var onError = btn_check(toastNetworkError);

		suning.modal.lock(this.$el);
		this.options.process(onSuccess, this.params(), {
			error_callback: onError
		});
	}

	function FormModal(el, options) {
		if (!el) return;

		var that = this;
		this.el = el;
		this.$el = $(el);
		this.options = options;
		this.$el.on('show.bs.modal', $.proxy(this.onShow, this));
		this.$el.on('hide.bs.modal', $.proxy(this.onHide, this));

		this.$form = this.$el.find("form");
		this.form = this.$form[0];
		this.$el.find(".save").click(function() {
			that.$form.submit();
		});
		this.$form.submit($.proxy(_onSubmit, this));

		$(options.table).on("click", ".edit", function() {
			options.bind(that.form, $(this.parentNode).data());
			that.$el.modal('show');
		});
	}

	FormModal.prototype.title = function() {
		var options = this.options;
		return this.editing() ? options.edit_title : options.add_title;
	};

	FormModal.prototype.editing = function() {
		return this.form.id.value != "";
	};

	FormModal.prototype.params = function() {
		return {
			form: this.$form.serialize(true)
		};
	};

	FormModal.prototype.onShow = function() {
		this.$form.parsley(this.options.parsley || {});
		suning.modal.setTitle(this.$el, this.title());
	};

	FormModal.prototype.onHide = function() {
		this.options.clear(this.form);
		this.$form.parsley('destroy');
	};

	FormModal.prototype.msg = function() {
		var options = this.options;
		return this.editing() ? options.edit_success_msg : options.add_success_msg;
	};

	window.FormModal = FormModal;

	function ActionModal(el, options) {
		if (!el) return;

		var that = this;
		
		this.el = el;
		this.$el = $(el);
		this.options = options;
		this.$el.on('show.bs.modal', $.proxy(this.onShow, this));
		this.$el.find(".save").click($.proxy(this.process, this));

		$(options.table).on("click", ".delete", function() {
			that.data = $(this.parentNode).data();
			that.$el.modal('show');
		});
	}

	ActionModal.prototype = {
		constructor: ActionModal,

		onShow: function() {
			this.$el.find(".modal-body").html(this.options.tip(this.data));
		},

		process: function() {
			var that = this;

			function btn_check(func) {
				return function(data) {
					suning.modal.unlock(that.$el);
					func && func(data);
				}
			}

			var onSuccess = btn_check(login_check(error_check(function() {
				toast('success', that.msg());
				that.$el.modal('hide');
				suning.reload(2000);
			})));
			var onError = btn_check(toastNetworkError);

			suning.modal.lock(this.$el);
			this.options.process(onSuccess, this.params(), {
				error_callback: onError
			});
		},

		params: function() {
			var params = this.options.params;
			return params ? params(this.data) : {
				id: this.data.id
			};
		},

		msg: function() {
			var msg = this.options.msg;
			return typeof msg == "string" ? msg : msg(this.data);
		}
	};

	window.ActionModal = ActionModal;
})(window);