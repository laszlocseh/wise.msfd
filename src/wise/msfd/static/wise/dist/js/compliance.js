Array.prototype.last||(Array.prototype.last=function(){return this[this.length-1]}),function(a,b,c){function d(a){var b=[],d=a||r;c(d+" select").each(function(a,d){var e=c(d).attr("id");if(b.indexOf(e)!==-1)return!1;c(d).addClass("js-example-basic-single");var f=c(d).find("option").length<10,g={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"100%",theme:"flat"};f&&(g.minimumResultsForSearch=1/0),c(d).select2(g)})}function e(){c(".button-field").addClass("btn"),c(".toggle-sidebar").hide()}function f(){var a='<span class="controls" style="display: inline-block;background-color: #ddd;padding-top: 2px;padding-bottom: 2px;padding-left: 0;position: relative;  "><span style="font-size: 0.8em; margin-left: 5px;">Select :</span><a class="" data-value="all"><label><span class="label">All</span></label></a>',b='<a class="" data-value="none" ><label><span class="label">Clear all</span></label></a>',c='<a class="" data-value="invert"><label><span class="label">Invert selection</span></label></a><div class="btn btn-default apply-filters" data-value="apply"><span class="" >Apply filters</span></div><span class="ui-autocomplete"><span class=" search-icon" ></span><span style="position: relative;padding-top:1px;padding-bottom:1px;background: white;" class="search-span"><input class="ui-autocomplete-input" type="text" style="width: 80%;" /><span class="clear-btn"><a class="fa fa-times"></a></span></span></span>';return a+b+c}function g(a,b){a.each(function(a,b){var d=c(b),e=d.find(".option"),g=e.find("input[type='checkbox']"),h=g.length>0;if(h){var j=d.attr("id"),k=f();d.find("> label.horizontal").after(k),e.each(function(a){var b=c(e[a]).text();c(e[a]).attr("title",b.trim())}),e.length<4?(d.find(".controls a").hide(),d.find(".controls").html("").css("height","1px").css("padding",0)):(i(d,j,e),d.find(".search-icon").on("click",function(a){c(a.target).parent().find("input").trigger("focus")})),l(d)}})}function h(a){return a.filter(function(a,b){return s.indexOf(c(b).val())===-1})}function i(b,d,e){b.addClass("panel-group");var f=b.find("> span:not(.controls)");f.css("border-radius",0),f.addClass(d+"-collapse").addClass("collapse").addClass("panel").addClass("panel-default");var g=b.find(".horizontal"),h="<a data-toggle='collapse' class='accordion-toggle' >"+g.text()+"</a>";if(g.html(h),g.addClass("panel-heading").addClass("panel-title"),g.attr("data-toggle","collapse"),g.attr("data-target","."+d+"-collapse"),f.collapse({toggle:!0}),f.collapse({toggle:!0}),b.find(".accordion-toggle").addClass("accordion-after"),f.on("hidden.bs.collapse",function(){f.fadeOut("fast"),b.find(".controls").slideUp("fast"),b.css({"border-bottom":"1px solid #ccc;"})}),f.on("show.bs.collapse",function(){f.fadeIn("fast"),b.find(".controls").slideDown("fast"),b.find("> span").css({display:"block"}),b.find(".accordion-toggle").addClass("accordion-after")}),f.on("hide.bs.collapse",function(){a.setTimeout(function(){b.find(".accordion-toggle").removeClass("accordion-after")},600)}),e.length<6)b.find(".controls .ui-autocomplete").hide();else{f.append("<span class='noresults hidden'>No results found</span>"),f.data("checked_items",[]);var i=f.data("checked_items");c.each(b.find("input:checked"),function(a,b){i.push(b.id)}),j(b)}}function j(a){a.find(".ui-autocomplete-input").autocomplete({minLength:0,source:[],search:function(b){k(b.target,a)},create:function(){var a=this,b=c(this).parentsUntil(".ui-autocomplete").find(".clear-btn ");b.on("click",null,a,function(a){c(this).parentsUntil(".controls").find("input").val(""),c(this).parentsUntil(".controls").find("input").trigger("change"),c(a.data).autocomplete("search","undefined")})}})}function k(a,b){var d=b.find(".option .label:not(.horizontal) "),e=d.parentsUntil(".option").parent(),f=e.find("input"),g=e.parent(),h=g.find(".noresults");if(""===c(a).val()){h.addClass("hidden"),e.removeClass("hidden");var i=b.find(".panel").data("checked_items");return i&&c.each(f,function(a,b){b.checked=i.indexOf(b.id)!==-1}),!0}b.find(".apply-filters").show(),e.removeClass("hidden");var j=c(a).val().toLowerCase().replace(/\s/g,"_"),k=new RegExp(c.ui.autocomplete.escapeRegex(j),"i"),l={},m=(b.find(".option .label:not(.horizontal) ").map(function(a,b){return l[c(b).text().toLowerCase()]=c(b).text().toLowerCase().replace(/\s/g,"_"),c(b).text().toLowerCase().replace(/\s/g,"_")}),[]);c.each(l,function(a,b){k.test(b)||m.push(a)});var n=d.filter(function(a,b){return m.indexOf(c(b).text().toLowerCase())!==-1}),o=d.filter(function(a,b){return m.indexOf(c(b).text().toLowerCase())===-1});c.each(o,function(a,b){c(b).parentsUntil(".option").parent().find("[type='checkbox']").prop("checked",!0)}),c.each(n,function(a,b){c(b).parentsUntil(".option").parent().find("[type='checkbox']").prop("checked",!1),c(b).parentsUntil(".option").parent().find("input[type='checkbox']").prop("checked",!1),c(b).parentsUntil(".option").parent().find("input[type='checkbox']").removeAttr("checked"),c(b).parentsUntil(".option").parent().addClass("hidden")}),n.length===d.length?h.removeClass("hidden"):h.addClass("hidden")}function l(b){if(void 0===a.WISE||void 0===a.WISE.blocks||a.WISE.blocks.indexOf(b.attr("id"))===-1){var d=[];c.each(b.find(".option input[type='checkbox']:not(:checked)"),function(a,b){d.push(c(b).parent())});var e=b.find(".option input[type='checkbox']:checked"),f=[];e.length>0&&c.each(e,function(a,b){f.push(c(b).parent())});var g=f.concat(d);c.each(g,function(a,c){b.find(".panel").append(c)})}}function m(a){a.preventDefault();var b=c(this).parent().parent();b.find(".apply-filters").show();var d=h(c(b).find("[type='checkbox']"));c.each(d,function(a){"all"!==c(d[a]).val()&&"none"!==c(d[a]).val()&&c(d[a]).prop("checked",!0)})}function n(a){a.preventDefault(),c(this).prop("checked",!1);var b=c(this).parent().parent();b.find(".apply-filters").show();var d=h(c(b).find("[type='checkbox']"));c.each(d,function(a){c(d[a]).prop("checked",!1)})}function o(a){a.preventDefault(),c(this).prop("checked",!1);var b=c(this).parent().parent();b.find(".apply-filters").show();var d=h(c(b).find("[type='checkbox']")),e=d.filter(function(a,b){return c(b).is(":checked")}),f=d.filter(function(a,b){return!c(b).is(":checked")});c.each(e,function(a){c(e[a]).prop("checked",!1)}),c.each(f,function(a){c(f[a]).prop("checked",!0)})}function p(){var a=c(".controls");a.on("click","a[data-value='all']",m),a.on("click","a[data-value='none']",n),a.on("click","a[data-value='invert']",o),a.one("click",".apply-filters",function(){c(r+" [name='form.widgets.page']").val(0),c(r+" .formControls #form-buttons-continue").trigger("click",{button:this})})}function q(){var b=c("#comp-national-descriptor").find("[data-fieldname]");b.on("click",".option",function(b){c("#ajax-spinner2").hide();c(this).find("input[type='checkbox']").val();a.WISE.blocks.indexOf(c(this).parentsUntil(".field").parent().attr("id"))!==-1})}var r=".wise-search-form-container",s=["all","none","invert","apply"];c.fn.fixTableHeaderHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height()),e=Math.max(a.height(),d);a.height(e-1),b.height(e)})})},c.fn.simplifyTable=function(){var a=c(this);a.data("original")||a.data("original",a.html());var b=0,d=c("tr",this);d.each(function(){$tds=c("td",this),$tds.length>b&&(b=$tds.length)}),d.each(function(){if($tds=c("td",this),$tds.length){var a=$tds[$tds.length-1];c(a).attr("colspan",b-$tds.length+1)}}),d.each(function(){var a=[];c("td",this).each(function(){if(0==a.length)a.push([this]);else{var b=c(this).text().trim(),d=c(a.last().last()).text().trim();b.length>0&&b==d?a.last().push(this):a.push([this])}}),c(a).each(function(){if(this.length>1){var a=this.length;c(this[0]).attr("colspan",a),c(this.slice(1)).each(function(){c(this).remove()})}})}),a.fixTableHeaderHeight()},c.fn.toggleTable=function(a){var b=c(this).data("original");a?c(this).simplifyTable():(c(this).html(b),c(this).fixTableHeaderHeight()),addTranslateClickHandlers()},c(b).ready(function(b){e();var c=b("[data-fieldname]");c.length>0&&g(c,c.length),p(b("#comp-national-descriptor")),q(),d(),a.matchMedia("(max-width: 768px)").matches&&b(".overflow-table h5").width(b(".overflow-table table").width()),b(".simplify-form").next().find("table").simplifyTable(),b(".simplify-form button").on("click",function(){var a="true"==b(this).attr("aria-pressed");$p=b(this).parent().next(),b("table",$p).toggleTable(!a)})})}(window,document,$);
//# sourceMappingURL=compliance.js.map