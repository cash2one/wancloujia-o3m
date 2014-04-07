// Send mesage to native c++
var sendMessageToNative = function (cmd, param) {
    var message = {
      'cmd' : cmd,
      'param' : param
    };
    window.external.call($.toJSON(message));
}

var nativeMessage = {};
window.receiveMessageFromNative = function (key, json) {
   $(nativeMessage).trigger(key, json);
}

var sendLog = function (logContent) {
    sendMessageToNative('log.send', logContent);
}
