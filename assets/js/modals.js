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
	}

	FormModal.prototype = {
		constructor: FormModal,

		onShow: function() {
			var parsley_options = this.options.parsley || {};
			this.$form.parsley($.extend({}, parsley.bs_options, parsley_options));
			suning.modal.setTitle(this.$el, this.title());
		},

		onHide: function() {
			this.options.clear(this.form);
			parsley.clearHighlight(this.form);
			this.$form.parsley('destroy');
		},

		show: function(data) {
			this.options.bind(this.form, data);
			this.$el.modal('show');

		},

		params: function() {
			return {
				form: this.$form.serialize(true)
			};
		},

		msg: function() {
			var msg = this.options.msg;
			return typeof msg == 'string' ? msg : msg(this.form);
		},

		title: function() {
			var title = this.options.title;
			return typeof title == 'string' ? title : title(this.form);
		}
	};

	function ActionModal(el, options) {
		if (!el) return;

		this.el = el;
		this.$el = $(el);
		this.options = options;
		this.$el.on('show.bs.modal', $.proxy(this.onShow, this));
		this.$el.find(".save").click($.proxy(this.process, this));
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
		},

		show: function(data) {
			this.data = data;
			this.$el.modal('show');
		}
	};

	function text_generator(add_text, edit_text) {
		return function(form) {
			return form.id.value ? edit_text : add_text;
		}
	}

	window.modals = {
		FormModal: FormModal,
		ActionModal: ActionModal,
		text_generator: text_generator
	};
})(window);