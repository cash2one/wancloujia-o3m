

var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;

$(function() {
    $('select').select2(select2_tip_options);
});


$(function() {
    var $form = $(".form-filter");
    var form = $form[0];

    var combo_options = {
        dataType: 'json',
        initial_text: '--------',
        first_optval: ''
    };
    var $filter_region = $("#filter_region");
    $filter_region.jCombo("regions", combo_options);
    var $filter_company = $("#filter_company")
    $filter_company.jCombo("companies?r=", $.extend({parent: $filter_region}, combo_options));
    var $filter_store = $("#filter_store");
    $filter_store.jCombo("stores?c=", $.extend({parent: $filter_company}, combo_options));

    var $filter_employee = $("#filter_employee");
    var select2_options = $.extend({}, select2_tip_options, {
        query: function(query) {
            var store = $filter_store.val();
            var company = $filter_company.val();
            var region = $filter_region.val();
            $.get('employee', {
                s: store,
                c: company,
                r: region,
                q: query.term
            }, function(data) {
                query.callback(data);
            }, "json").error(function() {
                query.callback([]);
            });
        }
    });

    $filter_employee.select2(select2_options);

    var $filter_app = $("#filter_app");
    $filter_app.select2($.extend({}, select2_tip_options, {
        query: function(query) {
            $.get('apps', {
                q: query.term,
                p: query.page
            }, function(data) {
                console.log(data);
                query.callback(data);
            }, "json").error(function() {
                query.callback([]);
            });
        }
    }));


    var $filter_from_date = $("#filter_from_date");
    var $filter_to_date = $("#filter_to_date");

    var $table = $(".table").dataTable($.extend({}, suning.dataTables.options, {
        sPaginationType: "bootstrap",
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
            sTitle: '应用名称'
        }, {
            sTitle: '是否推广'
        }, {
            sTitle: '日期'
        }],
        iDisplayStart: 0,
        iDisplayLength: 50,
        fnServerData: function(source, data, callback, settings) {
            console.log("source", source)
            console.log("settings", settings);
            var values = suning.dataTables.map(data, ["sEcho", "iDisplayLength", "iDisplayStart"]);
            console.log("values", values);

            Dajaxice.statistics.get_flow_logs(login_check(error_check(function(data) {
                console.log(data);
                var aaData = [];
                _.each(data.logs, function(item) {
                    var app_popularize;
                    if (item.popularize === true) {
                        app_popularize = '是';
                    } else if (item.popularize == false) {
                        app_popularize = '否';
                    } else {
                        app_popularize = '—';
                    }

                    aaData.push([
                        item.region,
                        item.company,
                        item.store,
                        item.emp,
                        item.brand,
                        item.model,
                        item.device,
                        item.app.name,
                        app_popularize,
                        item.date
                    ]);
                });
                console.log(aaData);
                $(".total").html(data.total);
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

        $table.fnClearTable();
        $table.fnDraw();
    });
});

