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
        $("#main_click").html(data.main_click || 0);
        $("#main_view").html(data.main_view || 0);
        $("#side_view").html(data.side_view || 0);
        $("#side_click").html(data.side_click || 0);
        var keys = Object.keys(data['logs']['main']['view']).sort();
        var interval = Math.floor(keys.length / 10) + 1;
        var view_vals = [];
        var click_vals = [];
        for (var k in keys) {
            //view_vals.push(data['logs']['main']['view'][keys[k]]);
            view_vals.push([]);
            view_vals[k].push(keys[k]);
            view_vals[k].push(data['logs']['main']['view'][keys[k]]);
            click_vals.push([]);
            click_vals[k].push(keys[k]);
            click_vals[k].push(data['logs']['main']['click'][keys[k]]);
        }
        console.log(view_vals);
        $("#main_ad_chart").highcharts({
            title: {
                text: '主广告位',
                x: -20 //center
            },
            xAxis: {
                categories: keys,
                tickInterval: interval
            },
            yAxis: {
                title: {
                    text: '次数'
                },
                plotLines: [{
                    value: 0,
                     width: 1,
                     color: '#808080'
                     }],
                     min: 0,
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                name: '展示量',
                data: view_vals}, {
                name: '点击量',
                data: click_vals}]});
    var keys = Object.keys(data['logs']['side']['view']).sort();
        var interval = Math.floor(keys.length / 10) + 1;
        var view_vals = [];
        var click_vals = [];
        for (var k in keys) {
            view_vals.push([]);
            view_vals[k].push(keys[k]);
            view_vals[k].push(data['logs']['side']['view'][keys[k]]);
            click_vals.push([]);
            click_vals[k].push(keys[k]);
            click_vals[k].push(data['logs']['side']['click'][keys[k]]);
        }
    $("#side_ad_chart").highcharts({
            title: {
                text: '副广告位',
                x: -20 //center
            },
            xAxis: {
                categories: keys,
                tickInterval: interval
            },
            yAxis: {
                title: {
                    text: '次数'
                },
                plotLines: [{
                    value: 0,
                     width: 1,
                     color: '#808080'
                     }],
                     min: 0
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: [{
                name: '展示量',
                data: view_vals}, {
                name: '点击量',
                data: click_vals}]});
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
        queryAd($form.serialize(true), function(err, data) {
            if (!err) {
                console.log(data);
                fill_chart(data);
            }
        });

    });

});
    
