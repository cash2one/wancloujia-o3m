// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;

var app_temp = statistics.app_temp;
var PeriodFilter = statistics.PeriodFilter;
var AppFilter = statistics.AppFilter;
var MgrFilter = statistics.MgrFilter;
var BrandFilter = statistics.BrandFilter;

$(function() {
    var $form = $(".form-filter");

    var mgrFilter = new MgrFilter('#user-filter');
    var brandFilter = new BrandFilter('#filter_brand');
    var appFilter = new AppFilter("#filter_app");
    var periodFilter = new PeriodFilter("#filter_from_date", "#filter_to_date");

    $("#export-data").click(function(e) {
        e.preventDefault();
        //window.OneRingRequest = true;
        if (!window.OneRingRequest) {
            window.location = 'flow/excel?' + $form.serialize(true);
        } else {
            var link = 'flow/excel?' + $form.serialize(true) + "#name=statistics.xls&content-type=file";
            var anchor = $("<a href='" + link + "' download='statistics.xls'></a>");
            anchor[0].click();
        }
    });

    var $table = $(".table").dataTable($.extend({}, statistics.table_options, {
        aoColumns: [{
            sTitle: '大区'
        }, {
            sTitle: '公司'
        }, {
            sTitle: '门店'
        }, {
            sTitle: '员工'
        }, {
            sTitle: '品牌'
        }, {
            sTitle: '机型'
        }, {
            sTitle: '串号'
        }, {
            sTitle: '应用名称',
            mRender: function(data, type, full) {
                if(data.name) {
                    return app_temp(data);
                } else {
                    return '&mdash;'
                }
            },
        }, {
            sTitle: '是否推广'
        }, {
            sTitle: '日期'
        }],
        fnDrawCallback: function() {
            $table.find(".app-name").popover();
        },
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, 
                    ["sEcho", "iDisplayLength", "iDisplayStart"]);
            Dajaxice.statistics.get_flow_logs(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    var app_popularize;
                    if (item.app.popularize === true) {
                        app_popularize = '是';
                    } else if (item.app.popularize === false) {
                        app_popularize = '否';
                    } else {
                        app_popularize = '—';
                    }

                    aaData.push([
                        item.region || '&mdash;',
                        item.company || '&mdash;',
                        item.store || '&mdash;',
                        item.emp || '&mdash;',
                        item.brand || '&mdash;',
                        item.model || '&mdash;',
                        item.device || '&mdash;',
                        item.app,
                        app_popularize,
                        item.date
                    ]);
                });
                console.log(aaData);
                $(".total").html(data.total || 0);
                $(".brands").html(data.brands || 0);
                callback({
                    sEcho: values.sEcho,
                    iTotalRecords: data.total,
                    iTotalDisplayRecords: data.total,
                    aaData: aaData
                });
            })), {
                form: $form.serialize(true),
                offset: values.iDisplayStart,
                length: values.iDisplayLength
            }, { 
                errorCallback: error_check(toastNetworkError)
            });
        }
    }));

    $form.submit(function(e) {
        e.preventDefault();

        //$table.fnClearTable();
        $table.fnDraw();
    });
});

