// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
var app_temp = statistics.app_temp;
var PeriodFilter = statistics.PeriodFilter;
var AppFilter = statistics.AppFilter;


$(function() {
    var $form = $(".form-filter");
    var form = $form[0];

    var combo_options = {
        dataType: 'json',
        initial_text: '---------',
        first_optval: ''
    };
    var $filter_region = $("#filter_region");
    $filter_region.select2(select2_tip_options);
    if(!$filter_region.data('readonly')) {
        $filter_region.jCombo("regions", combo_options);
    }

    var $filter_company = $("#filter_company")
    $filter_company.select2(select2_tip_options);
    if(!$filter_company.data('readonly')) {
        if (!$filter_region.data('readonly')) {
            $filter_company.jCombo("companies?r=", 
                $.extend({parent: $filter_region}, combo_options));
        } else {
            $filter_company.jCombo("companies?r=" + $filter_region.val(), combo_options);
        }
    }

    var $filter_store = $("#filter_store");
    $filter_store.select2(select2_tip_options);
    if(!$filter_store.data('readonly')) {
        if(!$filter_company.data("readonly")) {
            $filter_store.jCombo("stores?c=", $.extend({parent: $filter_company}, combo_options));
        } else {
            $filter_store.jCombo("stores?c=" + $filter_company.val(), combo_options);
        }
    }

    var $filter_employee = $("#filter_employee");
    if (!$filter_employee.data('readonly')) {
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
                    query.callback({
                        resutls: [],
                        more: false
                    });
                });
            }
        });
        $filter_employee.select2(select2_options);
    } else {
        $filter_employee.select2(select2_tip_options);
    }
    
    var region = $filter_region.val();
    var company = $filter_company.val();
    var store = $filter_store.val();
    function ensure_emp() {
        var changed = false;
        if($filter_region.val() != region) {
            region = $filter_region.val();
            changed = true;
        }

        if($filter_company.val() != company) {
            company = $filter_company.val();
            changed = true;
        }

        if($filter_store.val() != store) {
            store = $filter_store.val();
            changed = true;
        }

        if (changed) {
            $filter_employee.select2('val', '');
        }
    }

    $filter_region.change(ensure_emp);
    $filter_company.change(ensure_emp);
    $filter_store.change(ensure_emp);

    var $filter_brand = $("#filter_brand");
    $filter_brand.select2($.extend({}, select2_tip_options, {
        query: function(query) {
            $.get('brands', {
                q: query.term,
                p: query.page
            }, function(data) {
                results = _.map(data.brands, function(brand) {
                    return {'id': brand, 'text': brand};
                });
                results.unshift({'id': '', 'text': '--------'});
                query.callback({
                    results: results,
                    more: data.more
                });
            }, "json").error(function() {
                query.callback({
                    results: [],
                    more: false
                });
            });
        }
    }));

    var appFilter = new AppFilter("#filter_app");
    var periodFilter = new PeriodFilter("#filter_from_date", "#filter_to_date");

    $("#export-data").click(function(e) {
        e.preventDefault();
        window.location = 'flow/excel?' + $form.serialize(true);
    });

    var $table = $(".table").dataTable($.extend({}, statistics.table_options, {
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
        iDisplayStart: 0,
        iDisplayLength: 50,
        fnDrawCallback: function() {
            $table.find(".app-name").popover();
        },
        fnServerData: function(source, data, callback, settings) {
            console.log("source", source)
            console.log("settings", settings);
            var values = statistics.table_map(data, ["sEcho", "iDisplayLength", "iDisplayStart"]);
            console.log("values", values);

            Dajaxice.statistics.get_flow_logs(login_check(error_check(function(data) {
                console.log(data);
                var aaData = [];
                _.each(data.logs, function(item) {
                    var app_popularize;
                    if (item.app.popularize === true) {
                        app_popularize = '是';
                    } else if (item.app.popularize == false) {
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

