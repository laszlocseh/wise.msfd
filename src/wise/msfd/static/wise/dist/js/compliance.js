Array.prototype.last||(Array.prototype.last=function(){return this[this.length-1]}),function(a,b,c){function d(a){var b=[],d=a||n;c(d+" select").each(function(a,d){var e=c(d).attr("id");if(b.indexOf(e)!==-1)return!1;c(d).addClass("js-example-basic-single");var f=c(d).find("option").length<10,g={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"100%",theme:"flat"};f&&(g.minimumResultsForSearch=1/0),c(d).select2(g)})}function e(){c(".button-field").addClass("btn"),c(".toggle-sidebar").hide()}function f(a,b){var d=[],e=[],f=c(a).data("level");f=void 0!=f?parseInt(f):-1,c(b.setlimits).each(function(){if(this.level==f)return e=this.limits,!1}),0==e.length&&(e=b.setlimits[b.setlimits.length-1].limits),c("td",a).each(function(a){if(0==d.length||e.includes(a))d.push([this]);else{var b=c(this).text().trim(),f=c(d.last().last()).text().trim();b==f?d.last().push(this):d.push([this])}}),c(d).each(function(){if(this.length>1){var a=this.length;c(this[0]).attr("colspan",a),c(this.slice(1)).each(function(){c(this).remove()})}}),f!=-1&&(e=[],b.curentLevel=f,c(d).each(function(){var a=this.length;e.length&&(a+=e[e.length-1]),e.push(a)}),b.setlimits.push({level:b.curentLevel,limits:e.slice(0)}));var g=0;c("td",a).each(function(a){var d,f,h=b.curentLevel,i=parseInt(c(this).attr("colspan")||"1");if(g+=i,e.includes(g)){if(h>0)for(d=0;d<b.setlimits.length;d++)if(f=b.setlimits[d].limits,f.includes(g)){h=b.setlimits[d].level;break}c(this).addClass("endgroup_"+h)}})}function g(){var b=c("#report-data-navigation");c("button",b).on("click",function(){return c(".nav-body",b).toggle(),c(this).children().toggleClass("fa-bars fa-times"),!1}),c(".nav-body",b).hide();var d=c(".report-nav"),e=c(".report-title");if(d.length>0){var f=d.offset().top;c(a).scroll(function(){var b=c(a).scrollTop(),g=b>=f;d.toggleClass("sticky",g),e.toggleClass("fixed-title",g)})}}function h(){var a=c('<div class="scroll-wrapper"><i class="fa fa-table"></i><div class="top-scroll"><div class="top-scroll-inner"></div></div></div>');a.insertAfter(c(".overflow-table").find(".inner"))}function i(){var b=c(".overflow-table"),d=c(a);b.each(function(){var b=c(this),e=c(".top-scroll",b.parent()),f=e.find(".top-scroll-inner"),g=c(".inner",b.parent()),h=c(".table-report",b.parent()).width(),i=c("th",b.parent()).width(),j=h+i,k=c(".scroll-wrapper",b.parent());f.width(h),e.on("scroll",function(){g.scrollLeft(c(this).scrollLeft())}),g.on("scroll",function(){e.scrollLeft(c(this).scrollLeft())}),j>b.width()&&d.on("resize scroll",function(){var c=d.scrollTop();b.isInViewport()?k.addClass("fixed-scroll"):k.removeClass("fixed-scroll"),c>=b.offset().top+b.outerHeight()-a.innerHeight?k.hide():k.show()})})}function j(){var a=c(".overflow-table"),b=a.find("table"),d=c('<input type="checkbox" class="fix-row"/>'),e=c('<div class="fixed-table-wrapper"><div class="fixed-table-inner"><table class="table table-bordered table-striped fixed-table"></table></div></div>');b.find("th div").append(d),e.insertBefore(a.find(".inner"))}function k(){var b=c(".overflow-table"),d=c(".fixed-table-wrapper");b.each(function(){function a(a){function b(){g.scrollLeft(c(this).scrollLeft())}function d(){h.scrollLeft(c(this).scrollLeft())}a?(h.on("scroll",b),g.on("scroll",d)):(h.off("scroll",b),g.off("scroll",d))}var b=c(this),e=c("th",b.parent()),f=c(".table-report",b.parent()).width(),g=c(".inner",b.parent()),h=c(".fixed-table-inner",b.parent());a(!0),e.each(function(a){var b="cb"+a++,d=c(this).find(".fix-row");d.val(b)});var i=b.find(".fix-row");i.change(function(){var e=c(this),i=e.val(),j=e.closest(".overflow-table").find(".fixed-table"),k=e.closest(".overflow-table").find(".fixed-table-wrapper");if(c(".fixed-table").width(f),e.is(":checked")){k.addClass("sticky-table");var l=e.closest("tr"),m=l.children("td"),n=l.clone();n.children("td").width(function(a,b){return m.eq(a).outerWidth()}),n.appendTo(j).attr("data-row",i),b.find(".table").fixTableHeaderAndCellsHeight()}else d.find('tr[data-row="'+i+'"]').slideUp("fast",function(){c(this).remove()}),1===j.find("tr").length&&k.removeClass("sticky-table");var o=d.find(".fix-row");o.change(function(){var a=c(this),b=a.val();0===a.closest("tr").siblings().length&&a.closest(".fixed-table-wrapper").removeClass("sticky-table"),a.closest("tr").remove(),c('.fix-row[value="'+b+'"]').prop("checked",!1)}),a(!1),h.scrollLeft(g.scrollLeft()),a(!0)})}),c(a).on("resize scroll",function(){c(".report-nav.sticky").length>0?d.css("top","58px"):d.css("top","0")})}function l(){function b(){c(".table-report").fixTableHeaderHeight()}var d;c(a).resize(function(){clearTimeout(d),d=setTimeout(b,500)}),a.matchMedia("(max-width: 768px)").matches&&c(".overflow-table h5").width(c(".overflow-table table").width())}function m(){c(".simplify-form").next().find(".table-report").each(function(){c(this).simplifyTable()}),c(".simplify-form button").on("click",function(){var a="true"==c(this).attr("aria-pressed");$p=c(this).parent().next(),c(".table-report",$p).toggleTable(!a),i(),k()})}var n=".wise-search-form-container";c.fn.fixTableHeaderAndCellsHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height()),e=Math.max(a.height(),d);a.height(e),a.height()>d&&b.height(a.height()),c("div",this).css("margin-top","-4px")})})},c.fn.fixTableHeaderHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height());a.height(d)})})},c.fn.simplifyTable=function(){var a=c(this);a.data("original")||a.data("original",a.html());var b={curentLevel:0,setlimits:[{level:-1,limits:[]}]};c("tr",this).each(function(){f(this,b)}),a.fixTableHeaderHeight(),a.data("simplified",a.html())},c.fn.toggleTable=function(a){var b=c(this).data("original"),d=c(this).data("simplified");a?c(this).html(d):(c(this).hide(),c(this).empty().html(b),c(this).show(),c(this).fixTableHeaderAndCellsHeight(),setupTranslateClickHandlers(),setupReadMoreModal()),setupReadMoreModal(),setupTranslateClickHandlers()},a.setupReadMoreModal=function(){var a=c(".table-report"),b=c("#read-more-modal"),d=c(".modal-content-wrapper"),e=397,f="...",g=a.find(".tr-text");g.each(function(){var a=c(this).text();if(a.length>e){c(this).addClass("short");var g=a.substr(0,.75*e)+f;c(this).text(g),c(this).on("click",function(){d.html(a),b.modal("show")})}}),c(".btn-close-modal").click(function(){d.empty()}),a.fixTableHeaderAndCellsHeight()},c.fn.isInViewport=function(){var b=c(this).offset().top,d=b+c(this).height(),e=c(a).scrollTop(),f=e+c(a).height();return d>e&&b<f},c(b).ready(function(b){setupReadMoreModal(),e(),d(),g(),l(),h(),j(),b(a).on("load",function(){i(),k(),m()})})}(window,document,$);
//# sourceMappingURL=compliance.js.map