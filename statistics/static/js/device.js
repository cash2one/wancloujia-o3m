// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
var get_device_stat = Dajaxice.statistics.get_device_stat;
var app_temp = statistics.app_temp;

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
            $filter_store.jCombo("stores?c=", 
                    $.extend({parent: $filter_company}, combo_options));
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
                    query.callback([]);
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
                var results = _.map(data.brands, function(brand) {
                    return {'id': brand, 'text': brand};
                });
                results.unshift({'id': '', 'text': '--------'});
                query.callback({ results: results, more: data.more });
            }, "json").error(function() {
                query.callback({ results: [], more: false });
            });
        }
    }));

    var $filter_model = $("#filter_model");
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

    var $filter_app = $("#filter_app");
    $filter_app.select2($.extend({}, select2_tip_options, {
        query: function(query) {
            $.get('apps', {
                q: query.term,
                p: query.page
            }, function(data) {
                query.callback(data);
            }, "json").error(function() {
                query.callback([]);
            });
        }
    }));

    statistics.period("#filter_from_date", "#filter_to_date");

    $("#export-summary").click(function(e) {
        e.preventDefault();
        window.location =  'installed_capacity/excel?' + $form.serialize(true);
    });

    var $table = $("#summary .table").dataTable($.extend({}, statistics.table_options, {
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
                $(".total").html(data.capacity);
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
        $table.fnDraw();
    });
});

