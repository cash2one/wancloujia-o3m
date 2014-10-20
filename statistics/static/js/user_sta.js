// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;
var PeriodFilter = statistics.PeriodFilter;
var MgrFilter = statistics.MgrFilter;

$(function() {
    var $form = $(".form-filter");

    var mgrFilter = new MgrFilter('#user-filter');
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
            sTitle: '真实姓名'
        }, {
            sTitle: '当前在线'
        }, {
            sTitle: '在线时长'
        }],
        fnDrawCallback: function() {
            $table.find(".app-name").popover();
        },
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, 
                    ["sEcho", "iDisplayLength", "iDisplayStart"]);
            Dajaxice.statistics.filter_users(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    var app_popularize;

                    aaData.push([
                        item.region || '&mdash;',
                        item.company || '&mdash;',
                        item.store || '&mdash;',
                        item.emp || '&mdash;',
                        item.realname || '&mdash;',
                        item.isonline || '&mdash;',
                        item.duration || '&mdash;',
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

