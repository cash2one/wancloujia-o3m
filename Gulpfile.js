var gulp = require("gulp");
var exec = require("child_process").exec;

gulp.task('deploy-static', function(cb) {
    exec("./manage.py collectstatic --noinput", {
        env: process.env
    }, function(err, stdout, stderr) {
        console.log(stdout);
        console.error(stderr);
        cb(err);
    });
});

gulp.task('watch-static', function() {
    gulp.watch(["assets/**/*", "*/static/**/*"], ['deploy-static']);
});
