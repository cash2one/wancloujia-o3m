var toast = function(type, text, callback) {
    var options = { 
        text: text,
        type: type,
        delay: 2000,
        history: false,
        stack: false,
        closer: false,
        sticker: false,
        styling: 'bootstrap',
        before_open: function(pnotify) {
            pnotify.css({
                "top": ($(window).height() / 2) - (pnotify.height() / 2), 
                "left": ($(window).width() / 2) - (pnotify.width() / 2)
            }); 
        }   
    }; 

    if(typeof callback == 'function') {
        options.after_close = callback;
    }   

    $.pnotify(options);
};

