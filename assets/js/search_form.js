(function($){
	function SearchForm(form) {
		var that = this;
		this.form = form;
		this.$form = $(form);
		this.$searchBtn = this.$form.find(".search");
		this.$resetBtn = this.$form.find(".reset");
		this.$query = this.$form.find(".query");
		this.$query.removeAttr("readonly");

		if(this.$query.val()) {
			this.$searchBtn.addClass("hide");
			this.$resetBtn.removeClass("hide");
		} else {
			this.$searchBtn.removeClass("hide");
			this.$resetBtn.addClass("hide");
		}

		this.$resetBtn.click(function(e) {
			e.preventDefault();
			window.location.href = window.location.pathname;
		});
	}

	$.fn.search_form = function() {
		return this.each(function(){
			var $this = $(this);
			if($this.data("sf")) return;

			var sf = new SearchForm(this);
			$this.data("sf", sf);
		});
	};

	$(function(){
		$("[data-provide=search-form]").search_form();
	});
})($);