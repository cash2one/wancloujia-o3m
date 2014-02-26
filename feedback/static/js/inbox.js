$(function() {
    var modal = new modals.ActionModal($("#handle-feedback")[0], {
        tip: _.template("确认处理掉&nbsp;<strong>反馈<%-id%></strong>&nbsp;吗？"),
        msg: '操作成功',
        process: Dajaxice.feedback.handle_feedback
    });

    $("table").on('click', '.handle', function() {
        modal.show($(this.parentNode).data());
    });

    $("feedb").tab('show')
});