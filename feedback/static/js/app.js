$(function() {
    var modal = new modals.ActionModal($("#edit-app")[0], {
        tip: _.template("如果应用下线了，将不能被手机助手用户看到，" +
                        "并且会排在应用列表的后面。确认继续吗？"),
        msg: '应用已下线',
        process: Dajaxice.app.drop_app
    });

    $("table").on('click', '.edit', function() {
        modal.show($(this.parentNode).data());
    });
});