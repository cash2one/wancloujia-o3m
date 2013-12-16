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
    var form = $form[0];

    var mgrFilter = new MgrFilter('#user-filter');
    var brandFilter = new BrandFilter('#filter_brand');
    var appFilter = new AppFilter("#filter_app");
    var periodFilter = new PeriodFilter("#filter_from_date", "#filter_to_date");

    // TABLE
    var table = (function() {

    $("#export-data").click(function(e) {
        e.preventDefault()
        if(!mode)  return;
        window.location = 'organization/' + mode + '/excel?' + $form.serialize(true);
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
                    $(".total").html(data.capacity || 0);
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


    var values = mgrFilter.values();
    table.reload(values.region, values.company, values.store, values.employee);

    $form.submit(function(e) {
        e.preventDefault();
        var values = mgrFilter.values();
        table.reload(values.region, values.company, values.store, values.employee);
    });
});
