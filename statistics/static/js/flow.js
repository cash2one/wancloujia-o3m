// deps
var error_check = suning.decorators.error_check;
var login_check = suning.decorators.login_check;
var toastNetworkError = suning.toastNetworkError;

var PeriodFilter = statistics.PeriodFilter;
var SubjectFilter = statistics.SubjectFilter;
var UserFilter = statistics.UserFilter;
var ModelFilter = statistics.ModelFilter;
var DeviceFilter = statistics.DeviceFilter;

$(function() {
    var $form = $(".form-filter");

	var userFilter = new UserFilter('#filter_user');
	var modelFilter = new ModelFilter('#filter_model');
    var deviceFilter = new DeviceFilter('#filter_device');
    var subjectFilter = new SubjectFilter("#filter_subject");
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
            sTitle: '日期'
        }, {
            sTitle: '机型'
        }, {
            sTitle: 'IMEI'
        }, {
            sTitle: '应用专题',
            mRender: function(data, type, full) {
                if(data.name) {
                    return data.name;
                } else {
                    return '&mdash;'
                }
            },
        }, {
            sTitle: '批次号'
        }, {
            sTitle: '账号'
        }, {
            sTitle: '客户端版本'
        }, {
            sTitle: '是否加工成功'
        }],
        fnDrawCallback: function() {
        },
        fnServerData: function(source, data, callback, settings) {
            var values = statistics.table_map(data, 
                    ["sEcho", "iDisplayLength", "iDisplayStart"]);
            Dajaxice.statistics.get_flow_logs(login_check(error_check(function(data) {
                var aaData = [];
                _.each(data.logs, function(item) {
                    var installed;
                    if (item.installed === true) {
                        installed = '是';
                    } else if (item.installed === false) {
                        installed = '否';
                    } else {
                        installed = '—';
                    }

                    aaData.push([
                        item.date || '&mdash;',
                        item.model || '&mdash;',
                        item.device || '&mdash;',
                        item.subject,
                        item.pici || '&mdash;',
						item.user,
                        item.client_version || '&mdash;',
                        installed || '&mdash;',
                    ]);
                });
                console.log(aaData);
                $(".total").html(data.total || 0);
                $(".devices").html(data.devices || 0);
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

