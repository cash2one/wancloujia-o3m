define(function(require) {
    require("jquery");
    require("underscore");
    require("django-csrf-support");
    require("bootstrap");
    require("jquery.placeholder");

    var toast = require("toast");

    function login(username, password, remember_me) {
        return $.post("/login", {
            usrename: username,
            password: password,
            remember_me: remember_me
        }, "json");
    }

    $(function() {
        var $form = $(".form");
        $(".form-group input").placeholder();
        $form.submit(function(e) {
            e.preventDefault();

            var self = this;
            var $submit = $("#submit");

            function reload() {
                window.location = self.next.value ? self.next.value : window.location;
            }

            var username = this.username.value;
            var password = this.password.value;
            var remember_me = this.remember_me.value;

            $submit.button('loading');
            login(username, password, remember_me).done(function(result) {
                if (result.ret_code !== 0) {
                    return toast('error', result.ret_msg);
                }

                reload();
            }).fail(_.partial(toast, 'error', '网络异常')).always(function() {
                $submit.button('reset');
            });
        });
    });
});