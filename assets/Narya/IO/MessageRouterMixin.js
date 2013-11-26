/*global Backbone, _, console, define*/
(function (window, undefined) {
    define([
        'underscore',
        'backbone',
        'utils/FilterFunction'
    ], function (
        _,
        Backbone,
        FilterFunction
    ) {
        console.log('MessageRouterMixin - File loaded.');

        var id = 1;

        var MessageRouterMixin = _.extend(function () {}, Backbone.Events);

        var reg = function (route, callback, context) {
            id++;
            this.callbackList.push({
                id : id,
                route : route,
                filter : FilterFunction.generate(route),
                callback : callback,
                context : context || window
            });

            return id;
        };

        var unreg = function (id) {
            var callbackList = this.callbackList;
            var filter = FilterFunction.generate({ id : id });
            var i;
            for (i = callbackList.length; i--; undefined) {
                if (filter(callbackList[i])) {
                    callbackList.splice(i, 1);
                    break;
                }
            }
        };

        var router = function (message) {
            _.each(this.callbackList, function (item) {
                if (item.filter(message)) {
                    item.callback.call(item.context, JSON.parse(message.data.data));
                }
            });
        };

        MessageRouterMixin.mixin = function (that) {
            that.onmessage = reg.bind(that);
            that.offmessage = unreg.bind(that);
            that.on('message', router.bind(that));

            that.callbackList = [];
        };

        return MessageRouterMixin;
    });
}(this));
