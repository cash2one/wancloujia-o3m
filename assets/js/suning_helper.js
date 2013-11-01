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
var suning = {
    reload: function(delay) {
        if (!delay) {
            window.location.reload();
            return;
        }

        setTimeout(function() {
            window.location.reload();
        }, delay);
    }
};

window.suning = suning;
})();

