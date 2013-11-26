var Log = function(data) {
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

    var req = window.OneRingRequest;
    if (req) {
        req('get', url, '', function(resp) {
            resp = JSON.parse(resp);
            if (resp.state_code != 200) {
                console.error("log failed");
            }
        });
    }
}