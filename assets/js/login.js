$(function() {
    var $form = $(".form");
    $(".form-group input").placeholder();
    $form.submit(function(e) {
        e.preventDefault();

        var self = this;
        var $submit = $("#submit");

        var params = {
            username: this.username.value,
            password: this.password.value,
        };
        if (!this.wandoujia.value) {
            params.remember_me = this.remember_me.checked;
    } else {
            params.csrfmiddlewaretoken = this.csrfmiddlewaretoken.value;
        }

        function lock_check(func) {
            return function() {
                $submit.button('reset');
                func && func.apply(this, arguments);
            }
        }

        function toastNetworkError() {
            toast('error', '网路异常');
        }

        function reload() {
            window.location = self.next.value ? self.next.value : window.location;
        }

        function error_check(func) {
            return function(data) {
                if (data.ret_code != 0) {
                    toast('error', data.ret_msg);
                    return;
                }

                func && func.apply(this, arguments);
            }
        }

        var onResult = lock_check(error_check(reload));
        var onError = lock_check(toastNetworkError);

        $submit.button('loading');
        if (this.wandoujia.value) {
            $.post("/interface/login", params, onResult, "json").error(onError);
        } else {
            Dajaxice.framework.login(onResult, params, {error_callback: onError});
        }
    });
});