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
        bFilter: false,
        bServerSide: true,
        bRetrieve: true,
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

    function Period(from, to) {
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
        var first_day = new Date(today.getYear() + 1900, today.getMonth(), 1);
        this.$from.val(datef('YYYY-MM-dd', first_day))
        this.$to.val(datef('YYYY-MM-dd', today))
    }

    var app_temp = _.template("<span class='app-name' " +
                                "data-html='true' " +
                                "data-placement='bottom' " +
                                "data-content='包名:&nbsp;<%- package %><br>序号:&nbsp;<%- id %>'" +
                                "data-trigger='hover' >" + 
                                "<%- name %></span>");

    window.statistics = {
        app_temp: app_temp,
        parseDate: parseDate,
        table_map: table_map,
        table_options: table_options,
        period: Period
    };
})(window);
