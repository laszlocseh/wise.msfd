!function(a){function b(){colorPalette={light:["lightgreen","lightblue","lightgoldenrodyellow","lightgrey"],dark:["darkgreen","darkblue","darkmagenta","darkred"]},usernames={light:[],dark:[]},a(".comment-name").each(function(){var b=a(this).attr("group-id"),c=a(this).text();usernames[b].indexOf(c)===-1&&usernames[b].push(c)}),a(".comms").each(function(){var b=a(this).find(".comment-name"),c=b.text(),d=b.attr("group-id"),e=colorPalette[d];indx=usernames[d].indexOf(c),color=e[indx%e.length],$comment=a(this).find(".comment"),$comment.css("background-color",color),"light"===d&&$comment.css("color","black")})}function c(c){var d=c.data("question-id"),e=c.data("thread-id"),f="./@@ast-comments?q="+d+"&thread_id="+e;a.get(f,function(a){c.html(a),b()})}function d(b){b.find(".comms .comm-del").each(function(){var c=a(this);clickEventExists=c.data("click-event-setup"),"true"!==clickEventExists&&(c.data("click-event-setup","true"),c.on("click",function(){var c=a(this),d=a(".comments",c.closest(".right")),e=c.siblings(".comm-crtr").find(".comment-name").text(),f=c.siblings(".comm-crtr").find(".comment-time").text(),g=c.siblings(".comment").text(),h=b.data("question-id"),i=b.data("thread-id");if(confirm("Are you sure you want to delete the comment '"+g+"'?")){var j="./@@del_comment",k={comm_name:e,comm_time:f,text:g,q:h,thread_id:i};a.post(j,k,function(a){d.html(a)})}}))})}function e(){a(window).on("resize scroll",function(){a(".subform .right .comments").each(function(){var b=a(this);"true"!==b.data("comments-loaded")&&b.isInViewport()&&(b.data("comments-loaded","true"),c(b))})})}function f(){a(".subform .right .textline button").on("click",function(){var c=a(this),d=a(".comments",c.closest(".right")),e=a("textarea",c.closest(".textline")),f=d.data("question-id"),g=d.data("thread-id"),h=e.val();if(!h)return!1;var i="./@@add_comment",j={text:h,q:f,thread_id:g};return a.post(i,j,function(a){d.html(a),e.val(""),b()}),!1})}function g(){var b=a(".right.disc-tl"),c=a(".right.disc-ec");b.length,c.length;a(".comm-hide").click(function(){a(this).closest(".right").addClass("inactive")}),a(".right.discussion .comments").click(function(){$thisComm=a(this).closest(".right"),$thisComm.hasClass("inactive")&&$thisComm.toggleClass("inactive")})}function h(){a("#comp-national-descriptor div.subform.disabled div.left").find("textarea").each(function(){a(this).attr("disabled",!0)}),a(".kssattr-formname-edit-assessment-data-2018").submit(function(){a(":disabled").each(function(){a(this).removeAttr("disabled")})})}function i(){a("#comp-national-descriptor div.subform div.left div.assessment-form-input").find("option:contains('No value'), span.select2-chosen:contains('No value')").each(function(){a(this).text("-")})}function j(){var b=!1,c=!1,d=a("#comp-national-descriptor");a("#comp-national-descriptor form").submit(function(){b=!0}),d.on("change","input, textarea, select",function(a){c=!0}),a(window).bind("beforeunload",function(){if(c&&!b)return"You have unsaved changes. Do you want to leave this page?"});var e=d.find(".select2-container"),f=d.find("textarea");e.closest(".fields-container-row").addClass("flex-select"),f.closest(".fields-container-row").addClass("flex-textarea")}function k(){var b=a(".report-nav.sticky"),c=a("#assessment-edit-infobox"),d=a(".form-right-side.fixed-save-btn");d.length?(c.show().css("display","inline-box"),leftPos=d.position().left-c.width(),c.css("left",leftPos+"px")):c.hide(),0===c.children().length?b.removeClass("has-infobox"):b.addClass("has-infobox")}function l(){function b(){var b=[],c=a("<div>"),d=a("div#assessment-edit-infobox"),e="'Not relevant' option selected for the following questions:";return d.empty(),a(".subform .left select option:selected").each(function(){var d=a(this).text(),e=a(this).parent().attr("id").split("_").slice(-2),f=e[0],g=e[1];g.match("[^a-zA-Z]")&&(g=g.split("-").join(".")),"Not relevant"==d&&(c.append("<p>").append(f+": "+g),b.indexOf(g)===-1&&b.push(g))}),b.forEach(function(b,c,e){d.append(a("<span>").attr("class","info-item").append(b))}),d.attr("class","help-popover").attr("data-trigger","hover").attr("data-html","true").attr("data-placement","left").attr("data-content",c.html()).attr("data-original-title",e).popover(),0===b.length?void d.hide():void d.append(a("<span>").attr("class","fa fa-exclamation").css("font-size","20px"))}b(),a("select").change(function(){b(),k()})}a.fn.isInViewport=function(){var b=a(this).offset().top,c=b+a(this).outerHeight(),d=a(window).scrollTop(),e=d+a(window).height();return c>d&&b<e},a(document).ready(function(){e(),f(),g(),h(),i(),j(),l(),a(".subform .right .comments").mouseenter(function(){d(a(this))});var b=a(window),c=a(".subform");c.each(function(){var c=a(this),d=c.find(".right"),e=c.find(".left").innerHeight();d.innerHeight(e);var f;b.resize(function(){clearTimeout(f),f=setTimeout(function(){d=c.find(".right"),e=c.find(".left").innerHeight(),d.innerHeight(e)},100)})});var m,n,o=a(".form-right-side"),p=a(".report-nav"),q=0;o.offset()&&(q=o.offset().top),p.length>0&&(rnOffset=p.offset().top),n=b.height()-2*o.height(),o.find("#form-buttons-save").addClass("btn-success");var r=o.find("#form-buttons-translate");r.addClass("btn-secondary"),window.location.pathname.indexOf("art10")==-1&&r.css("display","none"),b.scroll(function(){m=b.scrollTop();var a=m+n<q&&m>=rnOffset;o.toggleClass("fixed-save-btn",a),k()})})}(jQuery);
//# sourceMappingURL=assessment-edit.js.map