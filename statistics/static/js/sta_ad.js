define(function(require) {
    require("bootstrap");
    require("jquery");
    require("datetimepicker");
    require("locale-datetimepicker");
    require("statistics");
    require("highcharts");

    function queryAd(form, callback) {
        $.get("ad_log", {f: form }, function(data) {
            callback(null, data);
        }, "json").error(function() {
            callback("error");
        });
    }
    function fill_chart(data) {
        $("#main_ad_chart").highcharts({
            title: {
                text: '主广告位',
                x: -20 //center
            },
            xAxis: {
                categories: Object.keys(data['logs']['main']['view'])
            },
            yAxis: {
                title: {
                    text: '次数'
                },
                plotLines: [{
                    value: 0,
                     width: 1,
                     color: '#808080'
                     }]
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                name: '展示量',
                data: $.map(data['logs']['main']['view'], function(v) { return v; })}, {
                name: '点击量',
                data: $.map(data['logs']['main']['click'], function(v) { return v; })}]});
    $("#side_ad_chart").highcharts({
            title: {
                text: '副广告位',
                x: -20 //center
            },
            xAxis: {
                categories: Object.keys(data['logs']['side']['view'])
            },
            yAxis: {
                title: {
                    text: '次数'
                },
                plotLines: [{
                    value: 0,
                     width: 1,
                     color: '#808080'
                     }]
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                name: '展示量',
                data: $.map(data['logs']['side']['view'], function(v) { return v; })}, {
                name: '点击量',
                data: $.map(data['logs']['side']['click'], function(v) { return v; })}]});

    }
    $(function() {
        var $form = $(".form-filter");
        var periodFilter = new statistics.PeriodFilter("#filter_from_date", "#filter_to_date");

        $form.submit(function(e) {
            e.preventDefault();
            queryAd($form.serialize(true), function(err, data) {
                if (!err) {
                    console.log(data);
                    fill_chart(data);
                }
            });
        });
    });

});
    
