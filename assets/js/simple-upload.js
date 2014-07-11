define(function(require) {
    require("jquery");
    require("backbone/backbone");
    var _ = require("underscore");
    var multiline = require("multiline");

    var tpl = _.template(multiline(function() {
        /*@preserve
        <div class="simple-upload">
            <input type='hidden' name='<%= name %>'>
            <input accept="image/*" type='file' name='file' id="<%= id %>">
            <div class="preview" style="display: none"></div>
        </div>
        */
        console.log
    }));

    var previewTpl = _.template(multiline(function() {
        /*@preserve
        <a class="thumbnail" href="<%= url %>" target="_blank">
            <img class="img-responsive" src="<%= url %>">
        </a>
        */
        console.log
    }));

    var SimpleUpload = Backbone.View.extend({
        initialize: function(options) {
            options = _.extend({
                name: '',
                id: ''
            }, options || {});
            _.extend(this, _.pick(options, "getUrl", "upload"));
            this.setElement($(tpl(options).trim())[0]);

            this.$file = this.$(':file');
            this.$field = this.$('[type=hidden]');
            this.$preview = this.$('.preview');
        },

        rightNow: function(timestamp, fn) {
            this.timestamp = timestamp;
            return _.bind(function() {
                if (timestamp !== this.timestamp) {
                    return;
                }

                if (_.isFunction(fn)) {
                    fn.apply(null, arguments);
                }
            }, this);
        },

        events: {
            'change :file': 'onFileSelected',
            'change [type=hidden]': 'onFileChanged'
        },

        onFileSelected: function() {
            var timestamp = _.now();
            setTimeout(_.bind(function() {
                this.$file.attr("disabled", "disabled");
            }, this), 0);
            this.upload(this.$file).then(
                this.rightNow(timestamp, _.bind(this.onUploadDone, this)),
                this.rightNow(timestamp, _.bind(this.onUploadFailed, this))
            );
        },

        onFileChanged: function() {
            var key = this.$field.val();
            if (key) {
                this.preview(this.getUrl(key));
            } else {
                this.$file.val('');
                this.$preview.hide().empty();
            }
        },

        onUploadFailed: function() {
            this.setPath(null);
            this.$file.removeAttr("disabled");
            this.trigger('upload-failed');
        },

        onUploadDone: function(key) {
            this.setPath(key || '');
            this.$file.removeAttr("disabled");
            this.trigger('upload-done');
        },

        preview: function(url) {
            this.$preview.hide();
            this.$preview.empty();
            $(previewTpl({
                url: url
            }).trim()).appendTo(this.$preview);
            this.$preview.show();
        },

        setPath: function(key) {
            this.$field.val(key || '').trigger('change');
            this.timestamp = _.now();
        }
    });

    return SimpleUpload;
});