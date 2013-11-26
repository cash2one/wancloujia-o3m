/*global $, define*/
(function (window, undefined) {
    define(['IO/IO'], function (IO) {

        var Social = {};

        Social.share = function (extensionId, title, content, imgURL) {
            var deferred = $.Deferred();

            IO.requestAsync({
                url : 'wdj://social/doraemon_share',
                data : {
                    extension_id : extensionId,
                    title : title || '',
                    content : content || '',
                    image : imgURL || ''
                },
                success : function (resp) {
                    if (resp.state_code === 200) {
                        deferred.resolve(resp);
                    } else {
                        deferred.reject(resp);
                    }
                }
            });

            return deferred.promise();
        };

        return Social;
    });
}(this));
