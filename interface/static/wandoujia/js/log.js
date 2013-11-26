/*
(function(window) {
    define(['Configuration'], function(CONFIG) {
        console.log('Log - File loaded.');

        var Log = function(data) {
            var logSwitch = true;
            if (logSwitch) {
                data = data || {};

                var url = 'wdj://window/log.json';
                var datas = [];
                var d;
                for (d in data) {
                    if (data.hasOwnProperty(d)) {
                        datas.push(d + '=' + window.encodeURIComponent(data[d]));
                    }
                }
                url += '?' + datas.join('&');

                window.OneRingRequest('get', url, '', function(resp) {
                    resp = JSON.parse(resp);
                    if (resp.state_code === 200) {
                        console.log('Log: ', url);
                    }
                });
            }
        };

        return Log;
    });
}(this));


*/