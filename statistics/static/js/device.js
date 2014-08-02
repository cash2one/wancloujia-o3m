// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
var get_device_stat = Dajaxice.statistics.get_device_stat;
var get_device_stat_detail = Dajaxice.statistics.get_device_stat_detail;

var app_temp = statistics.app_temp;
var PeriodFilter = statistics.PeriodFilter;
var AppFilter = statistics.AppFilter;
var MgrFilter = statistics.MgrFilter;
var BrandFilter = statistics.BrandFilter;

$(function() {
    var $form = $(".form-filter");
    var form = $form[0];

    var mgrFilter = new MgrFilter('#user-filter');
    var brandFilter = new BrandFilter('#filter_brand');
    
    var $filter_model = $("#filter_model");
    var $filter_brand = $("#filter_brand");
    $filter_brand.change(function() {
        $filter_model.select2('readonly', !$filter_brand.val());
        $filter_model.select2('val', '');
    });

    $filter_model.select2($.extend({}, select2_tip_options, {
        allowClear: true,
        query: function(query) {
            $.get('models', {
                b: $filter_brand.val(),
                q: query.term,
                p: query.page
            }, function(data) {
                var results = _.map(data.models, function(model) {
                    return {'id': model, 'text': model};
                });
                results.unshift({'id': '', 'text': '--------'});
                query.callback({ results: results, more: data.more });
            }, "json").error(function() {
                query.callback({ results: [], more: false });
            });
        }
    }));
    $filter_model.select2('readonly', true);

    var appFilter = new AppFilter("#filter_app");
    var periodFilter = new PeriodFilter("#filter_from_date", "#filter_to_date");

    $(".export-data").click(function(e) {
        e.preventDefault();
        window.location =  'device/excel?' + $form.serialize(true);
    });

    var $summaryTable = $("#summary .table").dataTable($.extend({}, statistics.table_options, {
        sPaginationType: "bootstrap",
        aoColumns: [{
            sTitle: '机型'
        }, {
            sTitle: '机器数'
        }, {
            sTitle: '推广数'
        }, {
            sTitle: '安装总数'
        }],
        iDisplayStart: 0,
        iDisplayLength: 50,
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, ["sEcho", "iDisplayLength", "iDisplayStart"]);
            get_device_stat(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    aaData.push([
                        item.model,
                        item.total_device_count,
                        item.total_popularize_count,
                        item.total_app_count
                    ]);
                });
                $(".total").html(data.capacity || 0);
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

    var $detailTable = $("#detail .table").dataTable($.extend({}, statistics.table_options, {
        sPaginationType: "bootstrap",
        aoColumns: [{
            sTitle: '员工'
        }, {
            sTitle: '品牌'
        }, {
            sTitle: '机型'
        }, {
            sTitle: '串号'
        }, {
            sTitle: '推广数'
        }, {
            sTitle: '安装总数'
        }],
        iDisplayStart: 0,
        iDisplayLength: 50,
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, ["sEcho", "iDisplayLength", "iDisplayStart"]);
            get_device_stat_detail(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    aaData.push([
                        item.emp || '&mdash;',
                        item.brand,
                        item.model,
                        item.device,
                        item.total_popularize_count,
                        item.total_app_count
                    ]);
                });
                $(".detail_total").html(data.capacity || 0);
                $(".detail_brands").html(data.brands || 0);
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

        $summaryTable.fnDraw();
        $detailTable.fnDraw();
    });
});

