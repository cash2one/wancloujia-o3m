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
        window.location = 'organization/' + mode + '_' + level + '/excel?' + $form.serialize(true);
    });

    var $levels = $("#levels");
    var level;

    $levels.on("click", "a", function() {
        var $this = $(this);
        if(level != $this.data('level')) {
            level = $this.data('level'); 
            $levels.find(".active").removeClass("active");
            $(this.parentNode).addClass("active");
            onLevelChange();
        }
    });

    var LEVELS = ['region', 'company', 'store', 'emp','did'];
    
    function to_row(mode, level, item) {
        var items = [];
        var from = _.indexOf(LEVELS, mode);
        var to = _.indexOf(LEVELS, level);
        _.each(LEVELS.slice(from, to + 1), function(level) {
            if(level === 'region') {
                items.push(item.region || "&mdash;");
            } else if(level === 'company') {
                items.push(item.company.code || '&mdash;');
                items.push(item.company.name || '&mdash;');
            } else if(level === 'store') {
                items.push(item.store.code || '&mdash;');
                items.push(item.store.name || '&mdash;');
            } else if(level === 'emp') {
                items.push(item.emp.username || '&mdash;');
                items.push(item.emp.realname || '&mdash;');
            }
        });
        if(item.did)
        {
            items.push(item.did);
        }
        else
        {
            items.push(item.total_device_count);
        }
        items.push(item.total_popularize_count);
        items.push(item.total_app_count);
        return items;
    }

    function titles(mode, level) {
        var result = [];
        var from = _.indexOf(LEVELS, mode);
        var to = _.indexOf(LEVELS, level);
        _.each(LEVELS.slice(from, to + 1), function(level) {
            if(level === 'region') {
                result.push('大区');
            } else if(level === 'company') {
                result.push('公司编码');
                result.push('公司名称');
            } else if(level === 'store') {
                result.push('门店编码');
                result.push('门店名称');
            } else if(level === 'emp') {
                result.push('员工编码');
                result.push('员工姓名');
            }
        });
        if(level==='did')
        {
            result.push('串号');
        }else
        {
            result.push('机器台数');
        }
        result.push('推广数');
        result.push('安装总数');
        return result;
    }

    function available_levels(mode) {
        var pos = _.indexOf(LEVELS, mode);
        return LEVELS.slice(pos);
    }

    var $table = null;

    var mode;
    function reload_data(region, company, store, emp, did) {
        var _mode; 
        if(did)
        {
            _mode = 'did';
        }
        else if(emp){
            _mode = 'did';
        } else if (store) {
            _mode = 'emp';
        } else if (company) {
            _mode = 'store';
        } else if (region) {
            _mode = 'company';
        } else {
            _mode = 'region';
        }

        if (_mode == mode) {
            $table && $table.fnDraw();
            return;
        }
    
        mode = _mode;
        onModeChange();
    }

    function onModeChange() {
        reloadLevels();
    }

    function desc_of_level(level) {
        if(level === 'region') {
            return '按大区';   
        } else if (level === 'company') {
            return '按公司';
        } else if (level === 'store') {
            return '按门店';
        } else if (level === 'emp') { 
            return '按员工';
        } else if(level ==='did')
        {
            return '按手机';
        }
    }

    var level_temp = _.template("<li><a href='#' data-level='<%= name %>'><%= desc %></a></li>");
    function reloadLevels() {
        var levels = available_levels(mode);
        $levels.empty();
        _.each(levels, function(level) {
            var $el = $(level_temp({
                name: level,
                desc: desc_of_level(level)
            })).appendTo($levels);
        });

        $levels.find("li:first-child").addClass("active");
        level = levels[0];
        onLevelChange();
    }

    function reloadTable() {
        $table && $table.dataTable().fnDestroy();
        $table && $table.html('<thead></thead><tbody></tbody>');
        var table_options = $.extend({}, statistics.table_options, {
            bRetrieve: true,
            sPaginationType: "bootstrap",
            iDisplayStart: 0,
            iDisplayLength: 50
        });

        $table = $(".table").dataTable($.extend({}, table_options, {
            aoColumns: _.map(titles(mode, level), function(title) {
                return {sTitle: title};
            }),
            fnServerData: function(source, data, callback, settings) {
                var values = statistics.table_map(data, 
                        ["sEcho", "iDisplayLength", "iDisplayStart"]);

                var filter = Dajaxice.statistics.filter_org_statistics;
                filter(login_check(error_check(function(data) {
                    var aaData = [];
                    _.each(data.logs, function(item) {
                        aaData.push(to_row(mode, level, item));
                    });
                    $(".total").html(data.capacity || 0);
                    $(".brands").html(data.brands || 0);
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
                    mode: mode,
                    level: level
                }, {
                    errorCallback: error_check(toastNetworkError)
                });
            }
        }));
    }

    function onLevelChange() {
        reloadTable();
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

