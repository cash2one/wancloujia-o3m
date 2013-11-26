/*global $, define*/
(function (window, undefined) {
    define(['IO/IO'], function (IO) {

        var Doraemon = {};

        Doraemon.openExtensionAsync = function (extensionId, extensionName, targetURL) {
            var deferred = $.Deferred();

            IO.requestAsync({
                url : 'wdj://window/publish.json',
                data : {
                    channel : 'sidebar.preview',
                    value : JSON.stringify({
                        id : extensionId,
                        name : extensionName,
                        targetURL : targetURL
                    })
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

        Doraemon.openGalleryAsync = function () {
            var deferred = $.Deferred();

            IO.requestAsync({
                url : 'wdj://window/publish.json',
                data : {
                    channel : 'sidebar.gallery',
                    value : JSON.stringify({})
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

        Doraemon.downloadAsync = function (type, downloadUrl, title, icon, format) {
            var deferred = $.Deferred();

            var url;

            switch (type) {
            case 'app':
                url = 'wdj://apps/download.json';
                break;
            case 'app-data':
                url = 'wdj://apps_data/download.json';
                break;
            case 'music':
                url = 'wdj://music/download.json';
                break;
            case 'photo':
                url = 'wdj://photo/download.json';
                break;
            case 'video':
                url = 'wdj://video/download.json';
                break;
            case 'book':
                url = 'wdj://book/download.json';
                break;
            default:
                url = 'wdj://apps/download.json';
            }

            IO.requestAsync({
                url : url,
                data : {
                    url : downloadUrl,
                    name : title,
                    icon : icon,
                    source : 'SnapPea SDK',
                    format : format || ''
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

        return Doraemon;
    });
}(this));
