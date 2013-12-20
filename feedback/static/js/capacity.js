// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
var get_installed_capacity = Dajaxice.statistics.get_installed_capacity;

var app_temp = statistics.app_temp;
var PeriodFilter = statistics.PeriodFilter;
var AppFilter = statistics.AppFilter;
var MgrFilter = statistics.MgrFilter;

$(function() {
    var $form = $(".form-filter");
    var form = $form[0];

    var mgrFilter = new MgrFilter("#user-filter"); 
    var appFilter = new AppFilter("#filter_app");
    var periodFilter = new PeriodFilter("#filter_from_date", "#filter_to_date");

    $("#export-data").click(function(e) {
        e.preventDefault();
        window.location =  'capacity/excel?' + $form.serialize(true);
    });

    var $table = $(".table").dataTable($.extend({}, statistics.table_options, {
        aoColumns: [{
            sTitle: '应用名称',
            mRender: function(data) {
                if(data.name) {
                    return app_temp(data);
                } else {
                    return '&mdash;'
                }
            }
        }, {
            sTitle: '是否推广',
            mRender: function(data) {
                if(data === null) {
                    return '&mdash;';
                } else {
                    return data ? '是' : '否';
                }
            }
        }, {
            sTitle: '安装总数'
        }],
        fnDrawCallback: function() {
            $table.find(".app-name").popover();
        },
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, ["sEcho", "iDisplayLength", "iDisplayStart"]);
            get_installed_capacity(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    aaData.push([
                        item.app,
                        item.app.popularize,
                        item.count
                    ]);
                });
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
        $table.fnDraw();
    });
});

