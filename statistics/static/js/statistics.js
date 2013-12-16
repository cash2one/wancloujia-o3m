(function(window) {
    function parseDate(value) {
        var regex = /(\d{4})-(\d\d)-(\d\d)/;
        var result = value.match(regex);
        var year = parseInt(result[1], 10);
        var month = parseInt(result[2], 10);
        var date = parseInt(result[3], 10);
        return new Date(year, month-1, date, 0);
    }

    function table_map(data, names) {
        var result = {};
        _.each(data, function(item) {
            if(~_.indexOf(names, item.name)) {
                result[item.name] = item.value; 
            }
        });

        return result;
    }

    var table_options = {
        bProcessing: true,
        bLengthChange: false,
        bSort: false,
        sPaginationType: "bootstrap",
        bFilter: false,
        bServerSide: true,
        bRetrieve: true,
        iDisplayStart: 0,
        iDisplayLength: 50,
        oLanguage: {
            oPaginate: {
                sFirst: '第一页',
                sLast: '最后一页',
                sNext: '&raquo;',
                sPrevious: '&laquo;'
            },
            sEmptyTable: '暂无记录',
            sInfo: '共 _TOTAL_ 次安装',
            sInfoEmpty: '暂无记录',
            sProcessing: '正在查询，请稍等...',
            sZeroRecords: '暂无记录'
        }
    };

    var EMPTY_SELECTION = {'id': '', 'text': '---------'};

    function queryApps(query, page, callback) {
        $.get('apps', { q: query, p: page }, function(data) {
            callback(null, data);
        }, "json").error(function() {
            callback("error");
        });
    }

    function AppFilter(selector) {
        this.$el = $(selector);
        this.$el.select2($.extend({}, select2_tip_options, {
            query: function(query) {
                queryApps(query.term, query.page, function(err, data) {
                    var result;
                    if(err) {
                        result = {results: [EMPTY_SELECTION], more: false};
                    } else {
                        data.results.unshift(EMPTY_SELECTION);
                        result = data;
                    }
                    query.callback(result);
                });
            }
        }));
    }

    function PeriodFilter(from, to) {
        var that = this;
        this.$from = $(from);
        this.$to = $(to);
        this.$from.change(function() {
            var from_date = parseDate(that.$from.val());
            if(!from_date) return;

            that.$to.datetimepicker('setStartDate', from_date);

            if (!that.$to.val()) return;

            var to_date = parseDate(that.$to.val());
            if(to_date.getTime() < from_date.getTime()) {
                that.$to.datetimepicker('setDate', from_date);
            }
        });

        var today = new Date();
        var first_day = new Date();
        first_day.setFullYear(today.getFullYear());
        first_day.setMonth(today.getMonth(), 1);
        first_day.setHours(0);
        first_day.setMinutes(0);
        first_day.setSeconds(0);
        first_day.setMilliseconds(0);
        this.$from.val(datef('YYYY-MM-dd', first_day))
        this.$to.val(datef('YYYY-MM-dd', today))
    }

    var popover_temp = "'包名:&nbsp;<%- package %><br>序号:&nbsp;<%- id %>'";
    var app_temp = _.template("<span class='app-name' " +
                                "data-html='true' data-placement='right' " +
                                "data-content=" + popover_temp + 
                                "data-trigger='hover'>" + 
                                "<%- name %></span>");

    function query_brands(query, page, callback) {
        $.get('brands', { q: query, p: page }, function(data) {
            callback(null, data);
        }, "json").error(function() {
            callback('error');
        });
    }

    function BrandFilter(filter) {
        this.$filter = $(filter);
        this.$filter.select2($.extend({}, select2_tip_options, {
            query: function(query) {
                query_brands(query.term, query.page, function(err, data) {
                    var result;
                    if(err) {
                        result = {results: [EMPTY_SELECTION], more: false};
                    } else {
                        var brands = _.map(data.brands, function(brand) {
                            return {'id': brand, 'text': brand};
                        });
                        brands.unshift(EMPTY_SELECTION);
                        result = {results: brands, more: data.more};
                    }
                    query.callback(result);
                });
            }
        }));
    }

    var COMBO_OPTIONS = {
        dataType: 'json',
        initial_text: '---------',
        first_optval: ''
    };

    function query_employee(params, callback) {
        $.get('employee', params, function(data) {
            callback(null, data);
        }, "json").error(function() {
            callback('error');
        });
    }

    function MgrFilter(group) {
        var that = this;
        this.$group = $(group);
        
        var $region = this.$group.find("#filter_region");
        $region.select2(select2_tip_options);
        $region.data('readonly') || $region.jCombo('regions', COMBO_OPTIONS);
        this.$region = $region;

        var $company = this.$group.find("#filter_company");
        this.$company = $company;
        $company.select2(select2_tip_options);
        if(!$company.data('readonly')) {
            if (!$region.data('readonly')) {
                $company.jCombo("companies?r=", 
                    $.extend({parent: $region}, COMBO_OPTIONS));
            } else {
                $company.jCombo("companies?r=" + $region.val(), COMBO_OPTIONS);
            }
        }

        var $store = $("#filter_store");
        this.$store = $store;
        $store.select2(select2_tip_options);
        if(!$store.data('readonly')) {
            if(!$company.data("readonly")) {
                $store.jCombo("stores?c=", $.extend({parent: $company}, COMBO_OPTIONS));
            } else {
                $store.jCombo("stores?c=" + $company.val(), COMBO_OPTIONS);
            }
        }

        var $employee = $("#filter_employee");
        this.$employee = $employee;
        if (!$employee.data('readonly')) {
            var select2_options = $.extend({}, select2_tip_options, {
                query: function(query) {
                    query_employee($.extend({}, that.values(), {
                        p: query.page,
                        q: query.term
                    }), function(err, data) {
                        var result;
                        if(err) {
                            result = {'results': [EMPTY_SELECTION], 'more': false};
                        } else {
                            data.results.unshift(EMPTY_SELECTION);
                            result = data;
                        }
                        query.callback(result);
                    });
                }
            });
            $employee.select2(select2_options);
        } else {
            $employee.select2(select2_tip_options);
        }
    
        $region.change($.proxy(this._ensure_emp, this));
        $company.change($.proxy(this._ensure_emp, this));
        $store.change($.proxy(this._emsure_emp, this));
    }

    MgrFilter.prototype = {
        consturctor: MgrFilter,

        _ensure_emp: function() {
            this.$employee.select2('val', '');
        },

        values: function() {
            return {
                region: this.$region.val(),
                company: this.$company.val(),
                store: this.$store.val(),
                employee: this.$employee.val()
            };
        }
    };

    window.statistics = {
        app_temp: app_temp,
        parseDate: parseDate,
        table_map: table_map,
        table_options: table_options,
        MgrFilter: MgrFilter,
        BrandFilter: BrandFilter,
        AppFilter: AppFilter, 
        PeriodFilter: PeriodFilter
    };
})(window);
