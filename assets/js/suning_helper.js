(function(window) {
var options = {
    successClass: 'has-success',
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
    
    decorators: {
        login_check: function(func) {
            return function(data) {
               if(data.ret_code == RET_NOT_LOGIN) {
                   toast('error', '会话可能已过期，请重新登录');
                   return;
               }

               func(data);
            }
        },

        error_check: function(func) {
            return function(data) {
                if(data.ret_code != RET_OK) {
                    toast('error', data.ret_msg);
                    return;
                }

                func(data);
            }
        }
    }
};

window.suning = suning;
})();


