/*global define*/
(function (window, undefined) {
    define([
        'IO/IO',
        'utils/QueryString'
    ], function (
        IO,
        QueryString
    ) {
        var alert = window.alert;

        var Device = Backbone.Model.extend({
            defaults : {
                isConnected : false,
                isMounted : false,
                hasSDCard : false,
                hasEmulatedSD : false,
                isUSB : false,
                isWifi : false,
                isInternet : false,
                SDKVersion : 0,
                productId : '',
                isRoot : false,
                deviceName : '',
                screen : new Backbone.Model(),
                build : new Backbone.Model()
            },
            initialize : function () {
                this.on('change:isConnected', function (Device, isConnected) {
                    if (isConnected) {
                        IO.requestAsync('wdj://device/screen.json').done(function (resp) {
                            if (resp.state_code === 200) {
                                this.get('screen').set({
                                    height : resp.body.height,
                                    width : resp.body.width,
                                    rotation : resp.body.rotation,
                                    pixelFormat : resp.body.pixel_format,
                                    refreshRate : resp.body.refresh_rate
                                });
                            }
                        }.bind(this));

                        IO.requestAsync('wdj://device/build.json').done(function (resp) {
                            if (resp.state_code === 200) {
                                this.get('build').set({
                                    brand : resp.body.brand,
                                    device : resp.body.device,
                                    display : resp.body.display,
                                    manufacturer : resp.body.manufacturer,
                                    model : resp.body.model,
                                    product : resp.body.product,
                                    release : resp.body.release,
                                    sdk : resp.body.sdk
                                });
                            }
                        }.bind(this));

                        IO.requestAsync('wdj://device/features.json').done(function (resp) {
                            if (resp.state_code === 200) {
                                this.set('features', resp.body.value);
                            }
                        }.bind(this));
                    }
                }, this);

                IO.requestAsync('wdj://device/state.json').done(function (resp) {
                    if (resp.state_code === 200) {
                        this.changeHandler(resp.body);
                    }
                }.bind(this));

                IO.onmessage({
                    'data.channel' : 'device.state_changed'
                }, this.changeHandler, this);
            },
            changeHandler : function (data) {
                this.set({
                    isConnected : data.connection_state,
                    isMounted : data.mmount_state === 1 ? true : false,
                    hasSDCard : data.mmount_state === 2 ? false : true,
                    hasEmulatedSD : !data.has_non_emulated_external_storage,
                    isUSB : data.type === 1,
                    isWifi : data.type === 3,
                    isInternet : data.type === 4,
                    SDKVersion : data.sdk_version,
                    productId : data.product_id,
                    isRoot : data.is_root,
                    deviceName : data.device_name
                });
            }
        });

        var device = new Device();

        return device;
    });
}(this));
