var gulp = require("gulp");
var less = require("gulp-less");


gulp.task("less", function() {
    return gulp.src("assets/less/{login,app,subject}.less")
        .pipe(less({
            paths: [
                "assets/less",
                "assets/components"
            ]
        }))
        .on('error', console.error)
        .pipe(gulp.dest("assets/css"));
});

gulp.task("watch-less", function() {
    return gulp.watch("assets/less/*.less", ["less"]);
});
