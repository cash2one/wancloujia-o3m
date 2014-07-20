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
    function queryApps(query, page, callback) {
        $.get("apps", { q: query, p: page }, function(data) {
            callback(null, data);
        }, "json").error(function() {
            callback("error");
        });
    }
    $(function() {
        $("#filter_app").select2($.extend({}, select2_tip_options, {
            query: function(query) {
                queryApps(query.term, query.page, function(err, data) {
                    if (err) {
                        result = {results:[EMPTY_SELECTION], more:false};
                    } else {
                        if (query.page == 1) data.results.unshift(EMPTY_SELECTION);
                        result = data;
                    }
                    alert(result);
                    query.callback(result);
                });
            }}));
        $("#filter_model").select2($.extend({}, select2_tip_options, {
            data: [{"id": "1", "text":"排行榜"}, {"id":"2", "text":"编辑推荐"}]
        }));
        var periodFilter = new statistics.PeriodFilter("#filter_from_date", "#filter_to_date");
        var $form = $(".form-filter");
        var $table = $(".table").dataTable($.extend({}, statistics.table_options, {
            aoColumns: [{
                sTitle: '应用名称'
            }, {
                sTitle: '包名'
            }, {
                sTitle: '列表页下载次数'
            }, {
                sTitle: '总下载次数'
            }],
            fnDrawCallback: function() {
                $table.find(".app-name").popover();
            },
            fnServerData: function(source, data, callback, settings) {
                var values = statistics.table_map(data,
                    ["sEcho", "iDisplayLength", "iDisplayStart"]);
                Dajaxice.statistics.get_download_logs(login_check(error_check(function(data) {
                    var aaData = [];
                    _.each(data.logs, function(item) {
                        aaData.push([
                        item.appName || '&mdash;',
                        item.appPkg || '&mdash;',
                        item.listDownloadNum || '&mdash;',
                        item.detailDownloadNum || '&mdash;',
                        item.allDownloadNum || '&mdash;']);
                    });
                    console.log(aaData);
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
    })
})
