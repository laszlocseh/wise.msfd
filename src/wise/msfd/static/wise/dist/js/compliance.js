Array.prototype.last||(Array.prototype.last=function(){return this[this.length-1]}),function(a,b,c){function d(a){var b=[],d=a||k;c(d+" select").each(function(a,d){var e=c(d).attr("id");if(b.indexOf(e)!==-1)return!1;c(d).addClass("js-example-basic-single");var f=c(d).find("option").length<10,g={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"100%",theme:"flat"};f&&(g.minimumResultsForSearch=1/0),c(d).select2(g)})}function e(){c(".button-field").addClass("btn"),c(".toggle-sidebar").hide()}function f(){var a=c(".table-report"),b=a.find("td"),d=c(".modal-content-wrapper"),e=500,f="...";b.each(function(){var a=c(this),b=a.find(".tr");b.each(function(){var b=c(this),g=b.find(".text-trans"),h=c('<span class="short-intro"/>');if(g.text().length>e-f.length){a.addClass("read-more-wrapper"),h.insertBefore(g);var i=b.children(".short-intro");b.find(".short-intro").length>1&&i.eq(0).remove(),i.text(g.text().substr(0,e-f.length)+f),a.find(".read-more-btn").click(function(){a.find(".active").children(".text-trans").clone().appendTo(d)})}else a.removeClass("read-more-wrapper")})}),c(".btn-close").click(function(){d.empty()}),a.fixTableHeaderAndCellsHeight()}function g(){var a=c("#report-data-navigation");c("button",a).on("click",function(){return c(".nav-body",a).toggle(),c(this).children().toggleClass("fa-bars fa-times"),!1}),c(".nav-body",a).hide()}function h(){var a=c(".table-report td");if(a.length){a.children("div").wrapInner('<span class="td-content"/>');var b=c(".table-report th"),d=b.position().left+b.outerWidth();a.each(function(){function a(){c(".btn-translate").on("click",function(){var a=c(this),b=a.closest(".td-content").outerHeight(),d=a.closest("td.translatable"),e=d.siblings("th");d.css({height:b,padding:"0"}),a.closest(".td-content").css("padding","8px"),e.css("height",b)})}var b,e=c(this);c(".report-page-view .overflow-table .inner").scroll(function(){if(clearTimeout(b),e.attr("colspan")>1){var c=e.find(".td-content"),f=e.position().left,g=f+e.outerWidth(),h=e.find(".td-content").width(),i=h+d;e.css("height",e.outerHeight()),b=setTimeout(function(){a()},1),f<d?c.addClass("td-scrolled").css("left",d+5):(e.css("height",""),c.removeClass("td-scrolled").addClass("td-content-scrolled")),i>=g?e.addClass("td-relative"):e.removeClass("td-relative")}})})}}function i(){var b=c(".overflow-table"),d=c(a);c.fn.isInViewport=function(){var a=c(this).offset().top,b=a+c(this).height(),e=d.scrollTop(),f=e+d.height();return b>e&&a<f},b.each(function(){var a=c(this),b=a.find(".top-scroll"),e=b.find(".top-scroll-inner"),f=a.find(".inner"),g=a.find("table").outerWidth(!0),h=a.find("th").outerWidth(!0);e.width(g-h-107),b.on("scroll",function(){f.scrollLeft(c(this).scrollLeft())}),f.on("scroll",function(){b.scrollLeft(c(this).scrollLeft())});var i=a.find(".scroll-wrapper");d.on("resize scroll",function(){a.isInViewport()?i.addClass("table-fixed-scroll"):i.removeClass("table-fixed-scroll"),c(".footer").isInViewport()?i.hide():i.show()})})}function j(){c("#comp-national-descriptor div.subform.disabled").find("select, textarea").each(function(){c(this).attr("disabled",!0)})}var k=".wise-search-form-container";c.fn.fixTableHeaderAndCellsHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height()),e=Math.max(a.height(),d);a.height(e),a.height()>d&&b.height(a.height())})})},c.fn.fixTableHeaderHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height());a.height(d)})})},c.fn.simplifyTable=function(){var a=c(this);a.data("original")||a.data("original",a.html());var b=0,d=c("tr",this);d.each(function(){$tds=c("td",this),$tds.length>b&&(b=$tds.length)}),d.each(function(){if($tds=c("td",this),$tds.length){var a=$tds[$tds.length-1];c(a).attr("colspan",b-$tds.length+1)}}),d.each(function(){var a=[];c("td",this).each(function(){if(0==a.length)a.push([this]);else{var b=c(this).text().trim(),d=c(a.last().last()).text().trim();b.length>0&&b==d?a.last().push(this):a.push([this])}}),c(a).each(function(){if(this.length>1){var a=this.length;c(this[0]).attr("colspan",a),c(this.slice(1)).each(function(){c(this).remove()})}})}),a.fixTableHeaderHeight(),a.data("simplified",a.html())},c.fn.toggleTable=function(a){var b=c(this).data("original"),d=c(this).data("simplified");a?c(this).html(d):(c(this).hide(),c(this).empty().html(b),c(this).show(),console.log("done restoring"),c(this).fixTableHeaderAndCellsHeight()),f()},c(b).ready(function(b){function c(){b(".table-report").fixTableHeaderHeight()}e(),d(),g(),h(),j(),f(),i(),b(".kssattr-formname-edit-assessment-data-2018").submit(function(){b(":disabled").each(function(){b(this).removeAttr("disabled")})}),a.matchMedia("(max-width: 768px)").matches&&b(".overflow-table h5").width(b(".overflow-table table").width()),b(".simplify-form").next().find("table").each(function(){b(this).simplifyTable()});var k;b(a).resize(function(){clearTimeout(k),k=setTimeout(c,500)}),b(".simplify-form button").on("click",function(){var a="true"==b(this).attr("aria-pressed");$p=b(this).parent().next(),b("table",$p).toggleTable(!a)});var l=!1,m=!1,n=b("#comp-national-descriptor");b("#comp-national-descriptor form").submit(function(){l=!0}),n.on("change","input, textarea, select",function(a){m=!0}),b(a).bind("beforeunload",function(){if(m&&!l)return"You have unsaved changes. Do you want to leave this page?"});var o=n.find(".select2-container"),p=n.find("textarea");o.closest(".fields-container-row").addClass("flex-select"),p.closest(".fields-container-row").addClass("flex-textarea");var q=b(".report-nav");if(q.length>0){var r=q.offset().top;b(a).scroll(function(){var c=b(a).scrollTop();c>=r?q.addClass("sticky").removeClass("fixed"):q.removeClass("sticky").addClass("fixed")})}})}(window,document,$);
//# sourceMappingURL=compliance.js.map