$(function() {
    var modal = new modals.ActionModal($("#delete-feedback")[0], {
        tip: _.template("确认删除&nbsp;<strong>反馈<%-id%></strong>&nbsp;吗？"),
        msg: '操作成功',
        process: Dajaxice.feedback.delete_feedback
    });

    $("table").on('click', '.delete', function() {
        modal.show($(this.parentNode).data());
    });
});