define(function(require) {
    require("jquery");
    require("select2");
    require("suning_helper");
    require("statistics");
    require("datetimepicker");
    require("locale-datetimepicker");
    require("datatables");
    require("bootstrap-datatables");
    require("dajaxice");
    var error_check = suning.decorators.error_check;
    var login_check = suning.decorators.login_check;
    var toastNetworkError = suning.toastNetworkError;
    var EMPTY_SELECTION = {'id': '', 'text': '---------'};
    $(function() {
        var periodFilter = new statistics.PeriodFilter("#filter_from_date", "#filter_to_date");
        var $form = $(".form-filter");
        var $table = $(".table").dataTable($.extend({}, statistics.table_options, {
            aoColumns: [{
                sTitle: '集合页位置'
            }, {
                sTitle: '点击数'
            }],
            fnServerData: function(source, data, callback, settings) {
                var values = statistics.table_map(data,
                    ["sEcho", "iDisplayLength", "iDisplayStart"]);
                Dajaxice.statistics.get_plates_sta(login_check(error_check(function(data) {
                    var aaData = [];
                    _.each(data.logs, function(item) {
                        aaData.push([
                        item.position || '&mdash;',
                        item.num || '&mdash;']);
                    });
                    console.log(aaData);
                    callback({
                        sEcho: values.sEcho,
                        iTotalRecords: data.total,
                        iTotalDisplayRecords: data.total,
                        aaData: aaData
                    });
                    $(".view_num").html(data.view_num || 0);
                    $(".click_num").html(data.click_num || 0);
                })), {
                    form: $form.serialize(true),
                }, {
                    errorCallback: error_check(toastNetworkError)
                });
            }
        }));
                

        $form.submit(function(e) {
            e.preventDefault();
        });
    })
})
