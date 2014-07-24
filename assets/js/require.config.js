require.config({
    baseUrl: "/static/",
    paths: {
        "login": "js/login",
        "app": "js/app",
        "sta_ad": "js/sta_ad",
        "highcharts": "js/highcharts",
        "edit_app": "js/edit_app",
        "dajaxice": "dajaxice/dajaxice.core",
        "download": "js/download",
        "download": "js/sta_ad",
        "statistics": "js/statistics",
        "datef": "js/datef",
        "datetimepicker": "js/bootstrap-datetimepicker.min",
        "locale-datetimepicker": "js/locales/bootstrap-datetimepicker.zh-CN",
        "datatables": "js/jquery.dataTables.min",
        "bootstrap-datatables": "js/bootstrap.datatables",
        "subject": "js/subject",
        "jquery.pnotify": "js/jquery.pnotify.min",
        "toast": "js/toast",
        "suning_helper": "js/suning_helper",

        'jquery.ui.core': 'components/jqueryui/ui/jquery.ui.core',
        'jquery.ui.mouse': 'components/jqueryui/ui/jquery.ui.mouse',
        'jquery.ui.widget': 'components/jqueryui/ui/jquery.ui.widget',
        'jquery.ui.sortable': 'components/jqueryui/ui/jquery.ui.sortable',

        "underscore": "components/underscore/underscore",
        "parse-bytes": "components/parse-bytes/bundle",
        "jquery": "components/jquery/dist/jquery.min",
        "jquery.uploadify": "js/jquery.uploadify",
        "jquery.placeholder": "components/jquery.placeholder/jquery.placeholder.min",
        "select2": "components/select2/select2",
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
        'select2': {
            deps: ['jquery']
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
        },

        'jquery.ui.core': {
            deps: ['jquery']
        },
        'jquery.ui.widget': {
            deps: ['jquery', 'jquery.ui.core']
        },
        'jquery.ui.mouse': {
            deps: ['jquery', 'jquery.ui.widget']
        },
        'jquery.ui.sortable': {
            deps: ['jquery', 'jquery.ui.core', 'jquery.ui.mouse', 'jquery.ui.widget']
        },
        'datatables' : {
            deps: ['jquery']
        },
        'bootstrap-datatables': {
            deps: ['jquery', 'bootstrap']
        },
        'locale-datetimepicker': {
            deps: ['datetimepicker']
        },
        'datetimepicker': {
            deps: ['bootstrap', 'jquery']
        },
        'highcharts': {
            deps: ['jquery']
        }
    }
});
