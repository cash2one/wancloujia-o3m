(function(window) {
    var options = {
        successClass: '', // nothing
        errorClass: 'has-error',
        validateIfUnchanged: true,
        errors: {
            classHandler: function(el) {
                return el.parents(".form-group");
            }
        }
    };

    window.parsley = window.parsley || {};
    window.parsley.bs_options = options;
    window.parsley.highlightError = function(form, field) {
        var group = $("[name=" + field + "]", form).parents(".form-group");
        group.addClass("has-error");
    };

    window.parsley.clearHighlight = function(form) {
        $(".has-error", form).removeClass("has-error");
    };
})(window);

(function(global) {
    var console = global.console || {}
    console.log = console.log || function() {};
    console.error = console.error || function() {};
    global.console = console;
})(window);

window.NETWORK_ERROR_MSG = '网路异常，请稍后重试';

(function() {
    var RET_OK = 0;
    var RET_NOT_LOGIN = 1001;

    var suning = {
        reload: function(delay) {
            if (!delay) {
                window.location.reload();
                return;
            }

            setTimeout(function() {
                window.location.reload();
            }, delay);
        },

        toastNetworkError: function() {
            toast('error', NETWORK_ERROR_MSG);
        },

        // TODO 在bs-modal之上扩展，而不使用以下的helper function
        modal: {
            setTitle: function($modal, title) {
                $(".modal-title", $modal).html(title);
            },

            lock: function($modal) {
                $modal.modal('lock');
                $(".modal-footer .btn").button('loading');
            },

            unlock: function($modal) {
                $modal.modal('unlock');
                $(".modal-footer .btn").button('reset');
            },

            highlightError: function(form, field) {
                parsley.highlightError(form, field);
            },

            clearHightLight: function(form) {
                parsley.clearHighlight(form);
            }
        },

        decorators: {
            login_check: function(func) {
                return function(data) {
                    console.log(data);
                    if (data.ret_code == RET_NOT_LOGIN) {
                        toast('error', '会话可能已过期，请重新登录');
                        return;
                    }

                    func(data);
                }
            },

            error_check: function(func) {
                return function(data) {
                    console.log("error", data)
                    if (data.ret_code == RET_OK) {
                        func(data);
                        return;
                    }

                    toast('error', data.ret_msg || '服务器端发生异常');
                }
            },

            delay: function(func, millies) {
                return function() {
                    var args = arguments;
                    setTimeout(function() {
                        func.apply(window, args);
                    }, millies);
                }
            }
        }
    };

    window.suning = suning;
})();