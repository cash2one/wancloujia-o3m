// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
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
    var emp = '';
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

    $filter_employee.change(function() {
        emp = $filter_employee.val();
    });

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
                query.callback({
                    results: [],
                    more: false
                });
            });
        }
    }));

    statistics.period("#filter_from_date", "#filter_to_date");

    // TABLE
    var table = (function() {

    $("#export-data").click(function(e) {
        e.preventDefault()
        if(!mode)  return;
        window.location = 'organization/' + mode + '/excel';
    });

    var $table = null;
    var options = {
        region: {
            to_row: function(item) {
                return [item.region || '&mdash;', item.total_device_count, 
                        item.total_popularize_count, item.total_app_count] 
            },
            titles: ['大区', '机器台数', '推广数', '安装总数']
        },
        company: {
            to_row: function(item) {
                return [item.company.code || '&mdash;', item.company.name || '&mdash;', 
                        item.total_device_count, item.total_popularize_count, 
                        item.total_app_count] 
            },
            titles: ['公司编码', '公司名称', '机器台数', '推广数', '安装总数']
        },
        store: {
            to_row: function(item) {
                return [item.store.code || '&mdash;', item.store.name || '&mdash;', 
                        item.total_device_count, item.total_popularize_count,
                        item.total_app_count] 
            },
            titles: ['门店编码', '门店名称', '机器台数', '推广数', '安装总数']
        },
        emp: {
            to_row: function(item) {
                return [item.emp.username || '&mdash;' , item.emp.realname || '&mdash;', 
                        item.total_device_count, item.total_popularize_count,
                        item.total_app_count] 
            },
            titles: ['员工编码', '员工姓名', '机器台数', '推广数', '安装总数']
        },
        emp_only: {
            to_row: function(item) {
                return [item.emp.username || '&mdash;' , item.emp.realname || '&mdash;', 
                        item.total_device_count, item.total_popularize_count,
                        item.total_app_count] 
            },
            titles: ['员工编码', '员工姓名', '机器台数', '推广数', '安装总数']
        }
    };

    var sub_options; 
    var mode;
    function reload_data(region, company, store, emp) {
        var _sub_options; 
        if (emp) {
            mode = 'emp_only';
            _sub_options = options.emp_only;
        } else if (store) {
            mode = 'emp';
            _sub_options = options.emp;
        } else if (company) {
            mode = 'store';
            _sub_options = options.store;
        } else if (region) {
            mode = 'company';
            _sub_options = options.company;
        } else {
            mode = 'region';
            _sub_options = options.region;
        }

        if (_sub_options == sub_options) {
            $table && $table.fnDraw();
            return;
        }
    
        $table && $table.dataTable().fnDestroy();
        $table && $table.html('<thead></thead><tbody></tbody>');
        sub_options = _sub_options;
        var table_options = $.extend({}, statistics.table_options, {
            bRetrieve: true,
            sPaginationType: "bootstrap",
            iDisplayStart: 0,
            iDisplayLength: 50
        });

        $table = $(".table").dataTable($.extend({}, table_options, {
            aoColumns: _.map(sub_options.titles, function(title) {
                return {sTitle: title};
            }),
            fnServerData: function(source, data, callback, settings) {
                var values = statistics.table_map(data, 
                        ["sEcho", "iDisplayLength", "iDisplayStart"]);

                var filter = Dajaxice.statistics.filter_org_statistics;
                filter(login_check(error_check(function(data) {
                    var aaData = [];
                    _.each(data.logs, function(item) {
                        aaData.push(sub_options.to_row(item));
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
                    length: values.iDisplayLength,
                    mode: mode
                }, {
                    errorCallback: error_check(toastNetworkError)
                });
            }
        }));
    }

    return { reload: reload_data };

    })();


    table.reload($filter_region.val(), $filter_company.val(), 
                 $filter_store.val(), $filter_employee.val());

    $form.submit(function(e) {
        e.preventDefault();
        table.reload($filter_region.val(), $filter_company.val(), 
                     $filter_store.val(), $filter_employee.val());
    });
});

