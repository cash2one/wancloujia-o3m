define(function(require) {
    require("jquery");
    require("jquery.pnotify");
    require("underscore");

    var options = {
        delay: 2000,
        history: false,
        stack: false,
        closer: false,
        sticker: false,
        styling: 'bootstrap',
        before_open: function(pnotify) {
            pnotify.css({
                "position": "absolute",
                "top": ($(window).height() / 2) - (pnotify.height() / 2) + 'px',
                "left": ($(window).width() / 2) - (pnotify.width() / 2) + 'px'
            });
        }
    };

    return function(type, text) {
        $.pnotify(_.extend({}, options, {
            text: text,
            type: type
        }));
    }
});