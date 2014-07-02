require.config({
    baseUrl: "/static/",
    paths: {
        "login": "js/login",
        "jquery.pnotify": "js/jquery.pnotify.min",
        "toast": "js/toast",

        "underscore": "components/underscore/underscore",
        "jquery": "components/jquery/dist/jquery.min",
        "jquery.placeholder": "components/jquery.placeholder/jquery.placeholder.min",
        "jquery.cookie": "components/jquery.cookie/jquery.cookie",
        "bootstrap": "components/bootstrap/dist/js/bootstrap.min",
        "django-csrf-support": "components/django-csrf-support/index"
    },
    shim: {
        "bootstrap": {
            deps: ["jquery"]
        },
        "jquery.placeholder": {
            deps: ["jquery"]
        },
        "jquery.pnotify": {
            deps: ["jquery"]
        },
        "jquery.cookie": {
            deps: ['jquery']
        }
    }
});