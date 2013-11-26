/*global define*/
(function (window, undefined) {
    'use strict';

    define([
        'backbone',
        'underscore',
        'IO/IO',
        'Device/Device'
    ], function (
        Backbone,
        _,
        IO,
        Device
    ) {

        var AppsCollection = Backbone.Collection.extend({
            url : 'wdj://apps/show.json',
            data : {
                upgrade_info : 1
            },
            parse : function (resp) {
                if (resp.state_code === 202 && Device.get('isConnected')) {
                    this.syncing = true;
                    this.trigger('syncStart');
                }

                this.loadingUpdateInfo = (resp.state_code === 251 || resp.state_code === 202);

                var result = _.map(resp.body.app, function (app) {
                    return {
                        id : app.base_info.package_name,
                        packageName : app.base_info.package_name,
                        versionCode : app.base_info.version_code
                    };
                });

                return result;
            },
            initialize : function () {
                var loading = false;
                var loadingUpdateInfo = false;
                var syncing = false;
                Object.defineProperties(this, {
                    loading : {
                        set : function (value) {
                            loading = value;
                        },
                        get : function () {
                            return loading;
                        }
                    },
                    loadingUpdateInfo : {
                        set : function (value) {
                            loadingUpdateInfo = value;
                        },
                        get : function () {
                            return loadingUpdateInfo;
                        }
                    },
                    syncing : {
                        set : function (value) {
                            syncing = value;
                        },
                        get : function () {
                            return syncing;
                        }
                    }
                });

                this.on('update', function () {
                    if (!loading) {
                        loading = true;
                        this.fetch({
                            success : function (collection) {
                                loading = false;
                                collection.trigger('refresh', collection);
                            }
                        });
                    }
                }, this);

                IO.Backend.onmessage({
                    'data.channel' : 'apps.updated'
                }, function (data) {
                    if (syncing) {
                        syncing = false;
                        this.trigger('syncEnd');
                    }

                    if (!!data) {
                        this.trigger('update');
                    } else {
                        loading = false;
                    }
                }, this);
            }
        });

        var appsCollection;

        var factory = _.extend({
            getInstance : function () {
                if (!appsCollection) {
                    appsCollection = new AppsCollection();
                    appsCollection.trigger('update');
                }
                return appsCollection;
            }
        });

        return factory;
    });
}(this));
