$(function(){
    var $form = $(".form");
    $(".form-group input").placeholder();
    $form.submit(function(e) {
        e.preventDefault();

        var self = this;
        var params = {
            username: this.username.value,
            password: this.password.value,
            remember_me: this.remember_me.checked
        };
        var $submit = $("#submit");
        $submit.button('loading');
        Dajaxice.framework.login(function(result) {
            $submit.button('reset')

            if(result.ret_code != 0) {
                toast('error', result.ret_msg);
                return;
            }

            window.location = self.next.value ? self.next.value : window.location;
        }, params, { 
            error_callback: function() {
                $submit.button('reset')
                toast('error', '操作失败，请稍后重试');
            }
        });
    });
});

