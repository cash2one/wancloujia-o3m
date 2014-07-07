require.config({
    baseUrl: "/static/",
    paths: {
        "login": "js/login",
        "app": "js/app",
        "edit_app": "js/edit_app",
        "jquery.pnotify": "js/jquery.pnotify.min",
        "toast": "js/toast",

        "underscore": "components/underscore/underscore",
        "parse-bytes": "components/parse-bytes/bundle",
        "jquery": "components/jquery/dist/jquery.min",
        "jquery.uploadify": "js/jquery.uploadify",
        "jquery.placeholder": "components/jquery.placeholder/jquery.placeholder.min",
        "jquery.cookie": "components/jquery.cookie/jquery.cookie",
        "jquery.iframe-transport": "components/jquery.iframe-transport/jquery.iframe-transport",
        'jquery.serializeObject': 'components/jQuery.serializeObject/dist/jquery.serializeObject.min',
        "ajax_upload": "ajax_upload/js/ajax-upload-widget",
        "bootstrap": "components/bootstrap/dist/js/bootstrap.min",
        "apk_upload": "js/apk_upload",
        "django-csrf-support": "components/django-csrf-support/index"
    },
    shim: {
        "bootstrap": {
            deps: ["jquery"]
        },
        "jquery.uploadify": {
            deps: ["jquery"]
        },
        "jquery.iframe-transport": {
            deps: ["jquery"]
        },
        'jquery.serializeObject': {
            deps: ["jquery"]
        },
        "ajax_upload": {
            deps: ["jquery.iframe-transport"]
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