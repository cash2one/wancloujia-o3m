define(function(require) {
    require("jquery");
    require("bootstrap");

    $(function() {
        var $modal = $("#delete-app");

        $("table").on('click', '.delete', function() {
            var app = $(this).parent().data();
            $modal.find(".save").attr("href", "/app/delete?id=" + app.id);
            $modal.find(".model-name").html(app.name);
            $modal.modal('show');
        });
    });
});