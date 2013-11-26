(function(window, undefined) {
    define([], function() {
        if (window.setImmediate === undefined) {
            window.setImmediate = function(callback) {
                return setTimeout(callback, 0);
            };
        }

        if (window.clearImmediate === undefined) {
            window.clearImmediate = window.clearTimeout;
        }
    });
})(this);
