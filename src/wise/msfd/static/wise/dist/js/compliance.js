Array.prototype.last||(Array.prototype.last=function(){return this[this.length-1]}),function(a,b,c){function d(a){var b=[],d=a||m;c(d+" select").each(function(a,d){var e=c(d).attr("id");if(b.indexOf(e)!==-1)return!1;c(d).addClass("js-example-basic-single");var f=c(d).find("option").length<10,g={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"100%",theme:"flat"};f&&(g.minimumResultsForSearch=1/0),c(d).select2(g)})}function e(){c(".button-field").addClass("btn"),c(".toggle-sidebar").hide()}function f(){var a=c(".table-report"),b=a.find("td"),d=c(".modal-content-wrapper"),e=500,f="...";b.each(function(){var a=c(this),b=a.find(".tr");b.each(function(){var b=c(this),g=b.find(".text-trans"),h=c('<span class="short-intro"/>');if(g.text().length>e-f.length){a.addClass("read-more-wrapper"),h.insertBefore(g);var i=b.children(".short-intro");b.find(".short-intro").length>1&&i.eq(0).remove(),i.text(g.text().substr(0,e-f.length)+f),a.find(".read-more-btn").click(function(){a.find(".active").children(".text-trans").clone().appendTo(d)})}else a.removeClass("read-more-wrapper")})}),c(".btn-close-modal").click(function(){d.empty()}),a.fixTableHeaderAndCellsHeight()}function g(){var b=c("#report-data-navigation");c("button",b).on("click",function(){return c(".nav-body",b).toggle(),c(this).children().toggleClass("fa-bars fa-times"),!1}),c(".nav-body",b).hide();var d=c(".report-nav"),e=d.closest("#report-data-navigation").siblings(".report-title");if(d.length>0){var f=d.offset().top;c(a).scroll(function(){var b=c(a).scrollTop();b>=f?(d.addClass("sticky").removeClass("fixed"),e.addClass("fixed-title")):(d.removeClass("sticky").addClass("fixed"),e.removeClass("fixed-title"))})}}function h(){var a=c(".table-report td");if(a.length){a.children("div").wrapInner('<span class="td-content"/>');var b=c(".table-report th"),d=b.position().left+b.outerWidth();a.each(function(){function a(){c(".btn-translate").on("click",function(){var a=c(this),b=a.closest(".td-content").outerHeight(),d=a.closest("td.translatable"),e=d.siblings("th");d.css({height:b,padding:"0"}),a.closest(".td-content").css("padding","8px"),e.css("height",b)})}var b,e=c(this);c(".report-page-view .overflow-table .inner").scroll(function(){if(clearTimeout(b),e.attr("colspan")>1){var c=e.find(".td-content"),f=e.position().left,g=f+e.outerWidth(),h=e.find(".td-content").width(),i=h+d;e.css("height",e.outerHeight()),b=setTimeout(function(){a()},1),f<d?c.addClass("td-scrolled").css("left",d+5):(e.css("height",""),c.removeClass("td-scrolled").addClass("td-content-scrolled")),i>=g?e.addClass("td-relative"):e.removeClass("td-relative")}})})}}function i(){var b=c(".overflow-table"),d=c(a),e=c('<div class="scroll-wrapper"><i class="fa fa-table"></i><div class="top-scroll"><div class="top-scroll-inner"></div></div></div>');e.insertAfter(c(".overflow-table").find(".inner")),b.each(function(){var b=c(this),e=c(".top-scroll",b.parent()),f=e.find(".top-scroll-inner"),g=c(".inner",b.parent()),h=c("table",b.parent()).width(),i=c("th",b.parent()).width(),j=h+i,k=c(".scroll-wrapper",b.parent()),l=c(".overflow-table:last");f.width(h),e.on("scroll",function(){g.scrollLeft(c(this).scrollLeft())}),g.on("scroll",function(){e.scrollLeft(c(this).scrollLeft())}),j>b.width()&&d.on("resize scroll",function(){var c=d.scrollTop();b.isInViewport()?k.addClass("fixed-scroll"):k.removeClass("fixed-scroll"),c>=l.offset().top+l.outerHeight()-a.innerHeight?k.hide():k.show()})})}function j(){var b=c(".overflow-table"),d=c('<div class="fixed-table-wrapper"><div class="fixed-table-inner"><table class="table table-bordered table-striped table-report fixed-table"></table></div></div>');d.insertBefore(b.find(".inner"));var e=c(".fixed-table-wrapper");b.each(function(){var a=c(this),b=c("th",a.parent()),d=c(".inner",a.parent()),f=c(".fixed-table-inner",a.parent());f.on("scroll",function(){d.scrollLeft(c(this).scrollLeft())}),d.on("scroll",function(){f.scrollLeft(c(this).scrollLeft())});var g=c('<input type="checkbox" class="fix-row"/>');a.find("th").append(g),b.each(function(a){var b="cb"+a++,d=c(this).find(".fix-row");d.val(b)});var h=a.find(".fix-row");h.change(function(){var b=c(this),d=b.val(),f=b.closest(".overflow-table").find(".fixed-table");b.is(":checked")?(b.closest("tr").clone().appendTo(f).attr("data-row",d),a.find(".table").fixTableHeaderAndCellsHeight()):e.find('tr[data-row="'+d+'"]').slideUp("fast",function(){c(this).remove()});var g=e.find(".fix-row");g.change(function(){var a=c(this),b=a.val();a.closest("tr").remove(),c('.fix-row[value="'+b+'"]').prop("checked",!1)})})}),c(a).on("resize scroll",function(){c(".report-nav.sticky").length>0?e.css("top","58px"):e.css("top","0")})}function k(){function b(){c(".table-report").fixTableHeaderHeight()}var d;c(a).resize(function(){clearTimeout(d),d=setTimeout(b,500)}),a.matchMedia("(max-width: 768px)").matches&&c(".overflow-table h5").width(c(".overflow-table table").width())}function l(){c(".simplify-form").next().find("table").each(function(){c(this).simplifyTable(),i()}),c(".simplify-form button").on("click",function(){var a="true"==c(this).attr("aria-pressed");$p=c(this).parent().next(),c("table",$p).toggleTable(!a),i()})}var m=".wise-search-form-container";c.fn.fixTableHeaderAndCellsHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height()),e=Math.max(a.height(),d);a.height(e),a.height()>d&&b.height(a.height())})})},c.fn.fixTableHeaderHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height());a.height(d)})})},c.fn.simplifyTable=function(){var a=c(this);a.data("original")||a.data("original",a.html());var b=0,d=c("tr.merge",this);d.each(function(){$tds=c("td",this),$tds.length>b&&(b=$tds.length)}),d.each(function(){if($tds=c("td",this),$tds.length){var a=$tds[$tds.length-1];c(a).attr("colspan",b-$tds.length+1)}}),d.each(function(){var a=[];c("td",this).each(function(){if(0==a.length)a.push([this]);else{var b=c(this).text().trim(),d=c(a.last().last()).text().trim();b.length>0&&b==d?a.last().push(this):a.push([this])}}),c(a).each(function(){if(this.length>1){var a=this.length;c(this[0]).attr("colspan",a),c(this.slice(1)).each(function(){c(this).remove()})}})}),a.fixTableHeaderHeight(),a.data("simplified",a.html())},c.fn.toggleTable=function(a){var b=c(this).data("original"),d=c(this).data("simplified");a?c(this).html(d):(c(this).hide(),c(this).empty().html(b),c(this).show(),console.log("done restoring"),c(this).fixTableHeaderAndCellsHeight()),f()},c.fn.isInViewport=function(){var b=c(this).offset().top,d=b+c(this).height(),e=c(a).scrollTop(),f=e+c(a).height();return d>e&&b<f},c(b).ready(function(a){e(),d(),g(),h(),f(),k(),l(),j()})}(window,document,$);
//# sourceMappingURL=compliance.js.map