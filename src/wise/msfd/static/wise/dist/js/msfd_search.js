!function(a,b,c){function d(){var a=c("#ajax-spinner");c("body").append(a.clone(!0).attr("id","ajax-spinner2")),a.remove(),c(".button-field").addClass("btn"),c(U+" #s2id_form-widgets-marine_unit_id").parentsUntil(".field").parent().hide(),c("#form-buttons-continue").hide("fast");var b=c("#form-buttons-download");if(b.length>0){var d=b.prop("outerHTML").replace("input","button")+' <span style="margin-left:0.4rem;">Download as spreadsheet</span>',e=b.parent();b.remove(),e.append(c(d)),c("#form-buttons-download").val("&#xf019; Download as spreadsheet").addClass("fa").addClass("fa-download")}}function e(){var a='<span class="controls"><span>Select :</span><a data-value="all"><label><span class="label">All</span></label></a>',b='<a data-value="none"><label><span class="label">Clear all</span></label></a>',c='<a data-value="invert"><label><span class="label">Invert selection</span></label></a><div class="btn btn-default apply-filters" data-value="apply"><span>Apply filters</span></div><span class="ui-autocomplete"><span class=" search-icon" ></span><span class="search-span"><input class="ui-autocomplete-input" type="text" /><span class="clear-btn"></span></span></span>';return a+b+c}function f(a,b){var d=b.find(".option .label:not(.horizontal) "),e=d.parentsUntil(".option").parent(),f=e.find("input"),g=e.parent(),h=g.find(".noresults");if(""===c(a).val()){h.addClass("hidden"),e.removeClass("hidden");var i=b.find(".panel").data("checked_items");return i&&c.each(f,function(a,b){b.checked=i.indexOf(b.id)!==-1}),!0}b.find(".apply-filters").show(),e.removeClass("hidden");var j=c(a).val().toLowerCase().replace(/\s/g,"_"),k=new RegExp(c.ui.autocomplete.escapeRegex(j),"i"),l={},m=(b.find(".option .label:not(.horizontal) ").map(function(a,b){return l[c(b).text().toLowerCase()]=c(b).text().toLowerCase().replace(/\s/g,"_"),c(b).text().toLowerCase().replace(/\s/g,"_")}),[]);c.each(l,function(a,b){k.test(b)||m.push(a)});var n=d.filter(function(a,b){return m.indexOf(c(b).text().toLowerCase())!==-1}),o=d.filter(function(a,b){return m.indexOf(c(b).text().toLowerCase())===-1});c.each(o,function(a,b){c(b).parentsUntil(".option").parent().find("[type='checkbox']").prop("checked",!0)}),c.each(n,function(a,b){c(b).parentsUntil(".option").parent().find("[type='checkbox']").prop("checked",!1),c(b).parentsUntil(".option").parent().find("input[type='checkbox']").prop("checked",!1),c(b).parentsUntil(".option").parent().find("input[type='checkbox']").removeAttr("checked"),c(b).parentsUntil(".option").parent().addClass("hidden")}),n.length===d.length?h.removeClass("hidden"):h.addClass("hidden")}function g(a){a.find(".ui-autocomplete-input").autocomplete({minLength:0,source:[],search:function(b){f(b.target,a)},create:function(){var a=this,b=c(this).parentsUntil(".ui-autocomplete").find(".clear-btn ");b.on("click",null,a,function(a){c(this).parentsUntil(".controls").find("input").val(""),c(this).parentsUntil(".controls").find("input").trigger("change"),c(a.data).autocomplete("search","undefined")})}})}function h(b,d,e){b.addClass("panel-group");var f=b.find("> span:not(.controls)");f.addClass(d+"-collapse").addClass("collapse").addClass("panel").addClass("panel-default");var h=b.find(".horizontal"),i="<a data-toggle='collapse' class='accordion-toggle' >"+h.text()+"</a>";if(h.html(i),h.addClass("panel-heading").addClass("panel-title"),h.attr("data-toggle","collapse"),h.attr("data-target","."+d+"-collapse"),f.collapse({toggle:!0}),f.collapse({toggle:!0}),b.find(".accordion-toggle").addClass("accordion-after"),f.on("hidden.bs.collapse",function(){f.fadeOut("fast"),b.find(".controls").slideUp("fast"),b.css({"border-bottom":"1px solid #ccc;"})}),f.on("show.bs.collapse",function(){f.fadeIn("fast"),b.find(".controls").slideDown("fast"),b.find("> span").css({display:"block"}),b.find(".accordion-toggle").addClass("accordion-after")}),f.on("hide.bs.collapse",function(){a.setTimeout(function(){b.find(".accordion-toggle").removeClass("accordion-after")},600)}),e.length<6)b.find(".controls .ui-autocomplete").hide();else{f.append("<span class='noresults hidden'>No results found</span>"),f.data("checked_items",[]);var j=f.data("checked_items");c.each(b.find("input:checked"),function(a,b){j.push(b.id)}),g(b)}}function i(b){if(void 0===a.WISE||void 0===a.WISE.blocks||a.WISE.blocks.indexOf(b.attr("id"))===-1){var d=[];c.each(b.find(".option input[type='checkbox']:not(:checked)"),function(a,b){d.push(c(b).parent())});var e=b.find(".option input[type='checkbox']:checked"),f=[];e.length>0&&c.each(e,function(a,b){f.push(c(b).parent())});var g=f.concat(d);c.each(g,function(a,c){b.find(".panel").append(c)})}}function j(b,d){c("#"+b).on("click",".option",function(){var b=this;c("#ajax-spinner2").hide(),a.WISE.blocks.indexOf(c(this).parentsUntil(".field").parent().attr("id"))!==-1?i(d):a.setTimeout(function(){c(U+" .formControls #form-buttons-continue").trigger("click",{button:b})},300)})}function k(a,b){var d=b;a.each(function(a,b){var f=c(b),g=f.find(".option"),k=g.find("input[type='checkbox']"),l=k.length>0;if(l){var m=f.attr("id");j(m,f);var n=e();f.find("> label.horizontal").after(n),g.each(function(a){var b=c(g[a]).text();c(g[a]).attr("title",b.trim())}),g.length<4?(f.find(".controls a").hide(),f.find(".controls").html("").css("height","1px").css("padding",0)):(h(f,m,g),f.find(".search-icon").on("click",function(a){c(a.target).parent().find("input").trigger("focus")})),i(f)}--d||c(U+","+V).animate({opacity:1},1e3)})}function l(b){b.preventDefault();var d=c(this).parent().parent();a.WISE.blocks.push(c(this).parentsUntil(".field").parent().attr("id")),d.find(".apply-filters").show();var e=p(c(d).find("[type='checkbox']"));c.each(e,function(a){"all"!==c(e[a]).val()&&"none"!==c(e[a]).val()&&c(e[a]).prop("checked",!0)})}function m(b){b.preventDefault(),c(this).prop("checked",!1);var d=c(this).parent().parent();d.find(".apply-filters").show();var e=p(c(d).find("[type='checkbox']"));a.WISE.blocks.push(c(this).parentsUntil(".field").parent().attr("id")),c.each(e,function(a){c(e[a]).prop("checked",!1)})}function n(b){b.preventDefault(),c(this).prop("checked",!1);var d=c(this).parent().parent();d.find(".apply-filters").show(),a.WISE.blocks.push(c(this).parentsUntil(".field").parent().attr("id"));var e=p(c(d).find("[type='checkbox']")),f=e.filter(function(a,b){return c(b).is(":checked")}),g=e.filter(function(a,b){return!c(b).is(":checked")});c.each(f,function(a){c(f[a]).prop("checked",!1)}),c.each(g,function(a){c(g[a]).prop("checked",!0)})}function o(){var a=c(".controls");a.on("click","a[data-value='all']",l),a.on("click","a[data-value='none']",m),a.on("click","a[data-value='invert']",n),a.one("click",".apply-filters",function(){c(U+" [name='form.widgets.page']").val(0),c(U+" .formControls #form-buttons-continue").trigger("click",{button:this})})}function p(a){return a.filter(function(a,b){return T.indexOf(c(b).val())===-1})}function q(){var b=c(U+", "+V).find("[data-fieldname]"),d=function(a,b){c(U+" [name='form.widgets.page']").val(0),T.indexOf(a)===-1&&c(b.target).find("input[type='checkbox']").trigger("click")};b.on("click",".option",function(b){c("#ajax-spinner2").hide();var e=c(this).find("input[type='checkbox']").val();a.WISE.blocks.indexOf(c(this).parentsUntil(".field").parent().attr("id"))!==-1||d(e,b)})}function r(b){var d=["form-widgets-member_states-from","form-widgets-member_states-to"],e=b||U;c(e+" select").each(function(b,f){var g=c(f).attr("id");if(d.indexOf(g)!==-1)return!1;c(f).addClass("js-example-basic-single");var h=c(f).find("option").length<10,i=c(e),j={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"100%",theme:"flat"};h&&(j.minimumResultsForSearch=1/0),c(f).select2(j),c(e+" #s2id_form-widgets-marine_unit_id").hide();var k=function(){i.find("[name='form.buttons.prev']").remove(),i.find("[name='form.buttons.next']").remove(),i.find("[name='form.widgets.page']").remove()};c(f).on("select2-selecting",function(b){"form-widgets-article"===c(this).attr("id"),k();var d=this;a.setTimeout(function(){c(e+" .formControls #form-buttons-continue").trigger("click",{select:d})},300)})})}function s(a){var b=c(a.element[0]),d=b.attr("data-subtitle");return'<span style="font-weight: bold;">'+b.attr("data-maintitle")+": </span><span>"+d+"</span>"}function t(){var a=c("#mobile-select-article"),d={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!0,width:"auto",theme:"flat",minimumResultsForSearch:20,formatSelection:s,formatResult:s,containerCssClass:"mobile-select-article"};void 0!==c.fn.select2&&(a.select2(d),a.one("select2-selecting",function(a){b.location.href=a.choice.id}))}function u(){var a="#marine-unit-trigger";return!c(V+" select:not(.notselect)").hasClass("js-example-basic-single")&&void c(V+" select:not(.notselect)").addClass("js-example-basic-single").each(function(b,d){var e={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:!1,width:"auto",theme:"flat",minimumResultsForSearch:20,allowClear:!0,dropdownParent:"#marine-unit-trigger",dropdownAdapter:"AttachContainer",containerCssClass:"select2-top-override",dropdownCssClass:"select2-top-override-dropdown",debug:!0};if(c(d).select2(e),c(d).parentsUntil(".field").parent().prepend("<h4>Marine Unit ID: </h4>"),c(d).on("select2-open",function(){var b=c(a).offset().top;c(a+" .arrow").hide(),c(".select2-top-override-dropdown").css({top:b+c(a).height()-c(a+" .arrow").height()+"px","margin-top":"12px !important"})}),c(d).on("select2-selecting",function(a){c(U+" [name='form.widgets.page']").val(0),c(U+" #form-widgets-marine_unit_id").select2().val(a.val).trigger("change"),c(U+" .formControls #form-buttons-continue").trigger("click",{select:a.target,from_marine_widget:!0})}),c(d).on("select2-close",function(){c(a).css("background","transparent"),c(a+" a").css("background","transparent"),c(a+" .arrow").show()}),c(V+" select").hasClass("js-example-basic-single")){var f=c(V+' select [value="'+jQuery(V+" .select-article select").val()+'"]').text();c(V+" select:not(.notselect)").parentsUntil(".field").before('<div id="marine-unit-trigger"><div class="text-trigger">'+f+"</div></div>"),c(a).on("click",function(){if(X)return!1;c(a).css("background","rgb(238, 238, 238)"),c(a+" a").css("background","rgb(238, 238, 238)"),c(V+" select:not(.notselect)").select2("open");var b=c(a+" a").height();c(".select2-top-override-dropdown").css("margin-top",b/2+"px")})}})}function v(){r(),u(),t();var b="auto",d=!0;a.matchMedia("(max-width: 967px)").matches&&(b=!1,d=!1);var e={placeholder:"Select an option",closeOnSelect:!0,dropdownAutoWidth:d,width:b,theme:"flat",minimumResultsForSearch:20,containerCssClass:"extra-details-select"};c.each(c(V+" .extra-details-select"),function(a,b){c(b).find("option").length>1?c(b).select2(e):c(b).hide()}),c(V+" .extra-details .tab-panel").fadeOut("slow",function(){c.each(c(V+" .extra-details .extra-details-section"),function(a,b){c(c(b).find(".tab-panel")[0]).show()})}),c(V+" .extra-details-select").on("select2-selecting",function(a){var b=c(a.target).parentsUntil(".extra-details-section").parent();c.each(c(b).find(".tab-panel"),function(b,d){c(d).attr("id")!==a.choice.id?c(d).hide():c(d).fadeIn()})})}function w(a){var b=a.data.direction,d=c(U+" #s2id_form-widgets-marine_unit_id"),e=d.select2("data"),f=c(e.element[0]).next(),g=c(e.element[0]).prev();if("next"===b)var h=f.val();else if("prev"===b)var h=g.val();c(U+" [name='form.widgets.page']").remove(),c(U+" #form-widgets-marine_unit_id").select2().val(h).trigger("change",{from_marine_widget:!0}),c(U+" #s2id_form-widgets-marine_unit_id").hide(),c(U+" .formControls #form-buttons-continue").trigger("click")}function x(){var a=c(".msfd-search-wrapper [name='form.buttons.prev']"),b=c(".msfd-search-wrapper [name='form.buttons.next']"),d=".formControls #form-buttons-continue";a.one("click",function(){return!X&&(c(U).find("form").append("<input type='hidden' name='form.buttons.prev' value='Prev'>"),void c(U).find(d).trigger("click"))}),b.one("click",function(){return!X&&(c(U).find("form").append("<input type='hidden' name='form.buttons.next' value='Next'>"),void c(U).find(d).trigger("click"))});var e=(c(V+" select:not(.notselect)").val(),c(V+" select:not(.notselect) option")),f="#form-buttons-prev-top",g="#form-buttons-next-top",h="#marine-unit-trigger";if(c("#marine-unit-nav").hide(),c(V+" select:not(.notselect)").val()!==c(e[1]).val()){var i='<button type="submit" id="form-buttons-prev-top" name="marine.buttons.prev" class="submit-widget button-field btn btn-default pagination-prev" value="" button="">          </button>';c(f).append(i),c(f).on("click",null,{direction:"prev"},w),c(f).hide(),c(h+" .arrow-left-container").one("click",function(){c(f).trigger("click")})}else c(h+" .arrow-left-container").hide(),c(".text-trigger").css("margin-left",0);if(c(V+" select:not(.notselect)").val()!==c(e[e.length-1]).val()){var j='<button type="submit" id="form-buttons-next-top" name="marine.buttons.next" class="submit-widget button-field btn btn-default pagination-next" value="">            </button>';c(g).append(j),c(g).on("click",null,{direction:"next"},w),c(g).hide(),c(h+" .arrow-right-container").one("click",function(){c("#form-buttons-next-top").trigger("click")})}else c(h+" .arrow-right-container").hide()}function y(){return!(parseInt(c(c(".pagination-text > span:nth-child(2)")[0]).text())<3)&&(c(Y).addClass("pagination-result"),0===c(Y).parent().find("input").length&&(c(Y).after('<input type="text" class="pagination-input" />'),c(".pagination-text .pagination-input").hide(),z()),c(".msfd-search-wrapper").on("click",Y,function(a){c(a.target).parent().find("input").show(300).focus().css("display","inline-block"),c(a.target).hide()}),void c(".msfd-search-wrapper").on("click",function(a){c(a.target).is(Y)||c(a.target).is(".pagination-text .pagination-input")||(c(Y).parent().find("input").hide(),c(Y).show())}))}function z(){var a=c(".pagination-text .pagination-input");a.bind("focusout",function(a){var b=c(a.target).val(),d=parseInt(c(c(a.target).parent().find("> span")[1]).text());if(X)return!1;var e=(c(this),function(a,b){if(isNaN(parseInt(a)))return!1;a=parseInt(a);var d=c(c(Y)[0]).text();return a!==parseInt(d)&&(a>b?b-1:!(a<=0)&&(1===a?0:a-1))}),f=e(b,d);f!==!1?(c(U+" [name='form.widgets.page']").val(f),c(Y).text(b),c(Y).show(),c(Y).parent().find("input").hide(),c(U+" .formControls #form-buttons-continue").trigger("click")):(c(a.target).val(""),c(Y).parent().find("input").hide(),c(Y).show())})}function A(){var b=c(".prev-next-row").eq(0);b.length&&c("#marine-widget-top").detach().insertBefore(b),d();var e=c(U+", "+V).find("[data-fieldname]");e.length>0&&k(e,e.length),c(U+","+V).animate({opacity:1},1e3),o(c(U)),q(),v(),"undefined"!=typeof a.setupTabs&&null!==a.setupTabs&&a.setupTabs(),"undefined"!=typeof clickFirstTab&&null!==clickFirstTab&&clickFirstTab(),x(),y()}function B(b,d){a.WISE.blocks=[],c(V+" .no-results").remove();var e="<div id='wise-search-form-container-preloader'/>",f=c("#ajax-spinner2").attr("id","ajax-spinner-form").show();if(c(U).append(e),c("#wise-search-form-container-preloader").append(f),c("#form-widgets-marine_unit_id").prop("disabled",!0),c("[name='form.buttons.prev']").prop("disabled",!0),c("[name='form.buttons.next']").prop("disabled",!0),c("[name='marine.buttons.prev']").prop("disabled",!0),c("[name='marine.buttons.next']").prop("disabled",!0),c("#marine-widget-top").length>0){var g=c("#marine-widget-top").next();g.css("position","relative")}else g=c(".left-side-form");g.prepend("<div id='wise-search-form-preloader'/>"),c("#wise-search-form-preloader").append("<span style='position: absolute; display: block; left: 50%;top: 10%;'></span>"),c("#wise-search-form-preloader > span").append(c("#ajax-spinner2").clone().attr("id","ajax-spinner-center").show()),c("#ajax-spinner-center").css({position:"fixed"}),c("#wise-search-form-top").find(".alert").remove(),X=!0}function C(b,d,e){c(V+" #wise-search-form-top").siblings().html(""),c(V+" #wise-search-form-top").siblings().fadeOut("fast"),c(V+" .topnav").next().remove();var f=c(b);a.WISE.formData=c(b).find(U).clone(!0);var g=f.find(U),h=g.html(),i=f.find(V+" #wise-search-form-top").siblings();c(U).html(h),f.find(V+" .topnav").next().length>0&&c(V+" .topnav").after(f.find(V+" .topnav").next()),c(V+" #wise-search-form-top").siblings().remove(),c(V+" #wise-search-form-top").after(i),A(),Q(),R(),c("[name='form.buttons.prev']").prop("disabled",!1),c("[name='form.buttons.next']").prop("disabled",!1),c("[name='marine.buttons.prev']").prop("disabled",!1),c("[name='marine.buttons.next']").prop("disabled",!1),c("#wise-search-form-top").find(".alert").remove()}function D(a){var b,c;return b=new RegExp("sortabledata-([^ ]*)","g"),c=b.exec(a.attr("class")),c?c[1]:null}function E(a){var b=D(a);return null===b&&(b=a.text()),"-"===b.charAt(4)||"-"===b.charAt(7)||isNaN(parseFloat(b))?b.toLowerCase():parseFloat(b)}function F(){var a,b,d,e,f,g,h,i,j;a=c(this).closest("th"),b=c("th",c(this).closest("thead")).index(a),d=c(this).parents("table:first"),e=d.find("tbody:first"),j=parseInt(d.attr("sorted")||"-1",10),f=j===b,c(this).parent().find("th:not(.nosort) .sortdirection").html("&#x2003;"),c(this).children(".sortdirection").html(f?"&#x25b2;":"&#x25bc;"),g=c(this).parent().children("th").index(this),h=[],i=!0,e.find("tr").each(function(){var a,b;a=c(this).children("td"),b=E(a.slice(g,g+1)),isNaN(b)&&(i=!1),h.push([b,E(a.slice(1,2)),E(a.slice(0,1)),this])}),h.length&&(i?h.sort(function(a,b){return a[0]-b[0]}):h.sort(),f&&h.reverse(),d.attr("sorted",f?"":b),e.append(c.map(h,function(a){return a[3]})),e.each(G))}function G(){var a=c(this);a.find("tr").removeClass("odd").removeClass("even").filter(":odd").addClass("even").end().filter(":even").addClass("odd")}function H(a,b){"success"===b&&c(U).fadeIn("fast",function(){c(V+" #wise-search-form-top").siblings().fadeIn("fast")}),c(U).find("[name='form.buttons.prev']").remove(),c(U).find("[name='form.buttons.next']").remove(),c(V+" #loader-placeholder").remove(),c("#form-widgets-marine_unit_id").prop("disabled",!1),c(V+" select").hasClass("js-example-basic-single")&&(c(V+" .select2-choice").width()/2<=c(V+" #select2-chosen-3").width()?c(V+" .select2-choice").css("width","50%"):2*(c(V+" .select2-choice").width()/3)<=c(V+" #select2-chosen-3").width()&&c(V+" .select2-choice").css("width","70%")),0===c("#wise-search-form-top").next().length&&c(V+" #wise-search-form-top").after("<span class='no-results'>No results found.</span>"),X=!1;var d=c("<span>&#x2003;</span>").addClass("sortdirection");c("table.listing:not(.nosort) thead th:not(.nosort)").append(d.clone()).css("cursor","pointer").click(F),c("table.listing:not(.nosort) tbody").each(G),"undefined"!=typeof scanforlinks&&jQuery(scanforlinks),S()}function I(a,b,d){c("#wise-search-form-top").find(".alert").remove(),c("#wise-search-form-top").append('<div class="alert alert-danger alert-dismissible show" style="margin-top: 2rem;" role="alert">  <strong>There was a error from the server.</strong> You should check in on some of those fields from the form.  <button type="button" class="close" data-dismiss="alert" aria-label="Close">    <span aria-hidden="true">&times;</span>  </button></div>'),c(U).find("[name='form.buttons.prev']").remove(),c(U).find("[name='form.buttons.next']").remove(),c("#form-widgets-marine_unit_id").prop("disabled",!1),c("#wise-search-form-container-preloader").remove(),c("#wise-search-form-preloader").remove(),c("#ajax-spinner-form").hide(),c("[name='form.buttons.prev']").prop("disabled",!0),c("[name='form.buttons.next']").prop("disabled",!0),c("[name='marine.buttons.prev']").prop("disabled",!0),c("[name='marine.buttons.next']").prop("disabled",!0),"undefined"!=typeof Storage&&W.removeItem("form"),X=!1}function J(a){c.each(c("#"+a).find(".option"),function(a,b){c(b).find("[type='checkbox']").prop("checked",!0)})}function K(a,b,d,e){var f,g;(!a||b||d)&&(f=function(a){var b,d,e;b=c(a).closest(".panel-group"),d=b.closest(".subform"),e=d.find(".subform"),b.nextAll(".panel-group").find(".panel").empty(),e.length?(e.hasClass("subform")&&e.empty(),e.find(".panel").empty(),e.find(".subform").empty()):c(a).parent().parent().next().empty()},g=function(b){var d,e,f,g=c(b).parent().next().attr("id");return d=c(b).closest(".panel-group"),e=d.closest(".subform"),f=c(b).parent().parent().next(),void 0!==a.from_marine_widget||a.from_marine_widget===!0||(J("formfield-form-widgets-member_states"===g?g:"memberstatesform"),d.nextAll(".panel-group").find(".panel").empty(),void(f.length&&f.find(".subform").empty()))},b?f(b):d?g(d):c(".ui-autocomplete-input").each(function(a,b){if(b.value)return f(b),!1}))}function L(a){function b(){try{var b="__some_random_key_you_are_not_going_to_use__";return a.setItem(b,b),a.removeItem(b),!0}catch(c){return!1}}function c(){b()?a.clear():h={}}function d(c){return b()?a.getItem(c):h.hasOwnProperty(c)?h[c]:null}function e(c){return b()?a.key(c):Object.keys(h)[c]||null}function f(c){b()?a.removeItem(c):delete h[c]}function g(c,d){b()?a.setItem(c,d):h[c]=String(d)}var h={},i=0;return{getItem:d,setItem:g,removeItem:f,clear:c,key:e,length:i}}function M(a){var b=a.data||null,c=a.boundary||null,d=a.formData||null;if("undefined"!=typeof LZString){var e=LZString.compressToEncodedURIComponent(b),f=LZString.compress(JSON.stringify(d));"undefined"!=typeof Storage&&(W.setItem("form-"+Z,e),W.setItem("boundary",c),W.setItem(Z,f))}}function N(a,b,d,e){c.ajax({type:"POST",contentType:"multipart/form-data; boundary="+a,cache:!1,data:b,dataType:"html",url:d,beforeSend:B,success:function(c,d,f){M({boundary:a,data:b,formData:e}),C(c,d,f)},complete:H,error:I})}function O(){if(null===W.getItem("form-"+Z))return!1;if("undefined"==typeof LZString)return console.error("LZString not found"),!1;try{var a=LZString.decompressFromEncodedURIComponent(W.getItem("form-"+Z)),b=c(U).find("form"),d=c.getMultipartData("#"+b.attr("id")),e=function(a,b){var d=!1;try{var e=JSON.parse(a);c.each(Object.keys(e),function(a,c){var f=e[c],g="undefined"!=typeof b[c]?b[c].filter(function(a){return f.indexOf(a)===-1}):[];if(g.length>0)return d=!0,!1})}catch(f){return!1}return!!d},f=W.getItem(Z);c.getMultipartData("#"+b.attr("id"),W.getItem("boundary"));if(e(LZString.decompress(f),d[2])){var g=b.attr("action"),h=W.getItem("boundary");N(h,a,g)}else console.log("same data")}catch(i){console.log(i)}}function P(b){var d=c(this).attr("href").indexOf("@@"),e=c(this).attr("href");if(d>0){b.preventDefault();var f=c(this).attr("href").substr(d,e.length-1);W.removeItem(f),W.removeItem("form"),a.location.href=e}}function Q(){var a=c(".select-widget");a.find("option:contains('No value')").each(function(){c(this).remove()})}function R(){var a=c(".table-report");a.fixTableHeaderAndCellsHeight()}function S(){var a='<div class="cloned-scroll-top" style="overflow-x: auto;"><div style="height: 1px;"></div></div>';c(".double-scroll").each(function(){var b=c(this),d=b.find("table").outerWidth(includeMargin=!0);if(null!=d){b.parent().before(a);var e=b.parent().siblings(".cloned-scroll-top").first();e.on("scroll",function(){b.scrollLeft(e.scrollLeft())}),b.scroll(function(){e.scrollLeft(b.scrollLeft())}),e.children().width(d)}})}var T=["all","none","invert","apply"],U=".wise-search-form-container",V="#wise-search-form",W=L(sessionStorage);c.randomString=function(){for(var a="0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz",b=8,c="",d=0;d<b;d++){var e=Math.floor(Math.random()*a.length);c+=a.substring(e,e+1)}return c},c.getMultipartData=function(a,b){var d=b||c.randomString(),e="--"+d,f="",g="\r\n",h=(c(a).attr("id"),c(a).serializeArray());if(0===h.length)return!1;var i=[],j={};return c.each(h,function(a,b){f+=e+g+'Content-Disposition: form-data; name="'+b.name+'"'+g+g+b.value+g,i.push(b.name),j[b.name]||(j[b.name]=[]),j[b.name].push(b.value)}),f+=e+"--"+g,[d,f,j]};var X=!1,Y=".pagination-text > span:first-child",Z=a.location.pathname.substr(a.location.pathname.indexOf("@@"),a.location.pathname.length-1)||"defaultForm";c.fn.fixTableHeaderAndCellsHeight=function(){this.each(function(){c("th",this).each(function(){var a=c(this),b=c("td",a.parent()),d=Math.max(b.height()),e=Math.max(a.height(),d);a.height(e),a.height()>d&&b.height(a.height()),c("div",this).css("margin-top","-4px")})})},jQuery(b).ready(function(b){a.setTimeout(function(){A()},100);var c=!0;a.WISE={},a.WISE.formData=b(U).clone(!0),a.WISE.blocks=[],b(U).unbind("click").on("click",".formControls #form-buttons-continue",function(a){if(!c)return!0;a.preventDefault();var d=arguments[1],e=d&&d.button,f=d&&d.select,g=!0;g&&K(d,e,f,arguments);var h=b(U).find("form"),i=h.attr("action"),j=b.getMultipartData("#"+h.attr("id"));N(j[0],j[1],i,j[2])}),O(),b(".topnav a").on("click",P),Q(),R(),S()})}(window,document,jQuery);
//# sourceMappingURL=msfd_search.js.map