!function(a){function b(){var a="s--Plone"+window.location.pathname.split("/").slice(0,-1).join("-");document.cookie=a+"="+Date.now()+";path=/"}function c(){colorPalette={light:["lightgreen","lightblue","lightgoldenrodyellow","lightgrey"],dark:["darkgreen","darkblue","darkmagenta","darkred"]},usernames={light:[],dark:[]},a(".comment-name").each(function(){var b=a(this).attr("group-id"),c=a(this).text();usernames[b].indexOf(c)===-1&&usernames[b].push(c)}),a(".comms").each(function(){var b=a(this).find(".comment-name"),c=b.text(),d=b.attr("group-id"),e=colorPalette[d];indx=usernames[d].indexOf(c),color=e[indx%e.length],$comment=a(this).find(".comment"),$comment.css("background-color",color),"light"===d&&$comment.css("color","black")})}function d(b){var c,d=b.find(".accordion");for(c=0;c<d.length;c++)d[c].addEventListener("click",function(){this.classList.toggle("active");var b=a(this).nextUntil("li.accordion");b.each(function(){this.classList.toggle("active")})})}function e(b){var e=b.data("question-id"),f=b.data("thread-id"),g="./@@ast-comments?q="+e+"&thread_id="+f;a.get(g,function(a){b.html(a),c(),d(b)})}function f(d){d.find(".comms .comm-del").each(function(){var e=a(this);clickEventExists=e.data("click-event-setup"),"true"!==clickEventExists&&(e.data("click-event-setup","true"),e.on("click",function(){var e=a(this),f=a(".comments",e.closest(".right")),g=e.siblings(".comm-crtr").find(".comment-name").text(),h=e.siblings(".comm-crtr").find(".comment-time").text(),i=e.siblings(".comment").text(),j=d.data("question-id"),k=d.data("thread-id");if(confirm("Are you sure you want to delete the comment '"+i+"'?")){var l="./@@del_comment",m={comm_name:g,comm_time:h,text:i,q:j,thread_id:k};a.post(l,m,function(a){b(),f.html(a),c()})}}))})}function g(){a(window).on("resize scroll",function(){a(".subform .right .comments").each(function(){var b=a(this);"true"!==b.data("comments-loaded")&&b.isInViewport()&&(b.data("comments-loaded","true"),e(b))})})}function h(){a(".subform .right .textline button").on("click",function(){var d=a(this),e=a(".comments",d.closest(".right")),f=a("textarea",d.closest(".textline")),g=e.data("question-id"),h=e.data("thread-id"),i=f.val();if(!i)return!1;var j="./@@add_comment",k={text:i,q:g,thread_id:h};return a.post(j,k,function(a){b(),e.html(a),f.val(""),c()}),!1})}function i(){var b=a(".right.disc-tl"),c=a(".right.disc-ec");b.length,c.length;a(".comm-hide").click(function(){a(this).closest(".right").addClass("inactive")}),a(".right.discussion .comments").click(function(){$thisComm=a(this).closest(".right"),$thisComm.hasClass("inactive")&&$thisComm.toggleClass("inactive")})}function j(){a("#comp-national-descriptor div.subform.disabled div.left").find("textarea").each(function(){a(this).attr("disabled",!0)}),a(".kssattr-formname-edit-assessment-data-2018").submit(function(){a(":disabled").each(function(){a(this).removeAttr("disabled")})})}function k(){a("#comp-national-descriptor div.subform div.left div.assessment-form-input").find("option:contains('No value'), span.select2-chosen:contains('No value')").each(function(){a(this).text("-")})}function l(){var b=!1,c=!1,d=a(".fields-container");a("#comp-national-descriptor form").submit(function(){b=!0}),d.on("change","input, textarea, select",function(a){c=!0}),a(window).bind("beforeunload",function(){if(c&&!b)return"You have unsaved changes. Do you want to leave this page?"});var e=d.find(".select2-container"),f=d.find("textarea");e.closest(".fields-container-row").addClass("flex-select"),f.closest(".fields-container-row").addClass("flex-textarea")}function m(){var b=a("#report-nav-toggle"),c=a(".report-nav.sticky"),d=a("#assessment-edit-infobox"),e=d.children().length,f=a(".form-right-side.fixed-save-btn");if(e>0&&c.length){c.addClass("has-infobox"),d.show().css("display","inline-block");var g=b.position().left-16;f.length&&(g=f.position().left),g-=d.width(),d.css("left",g+"px")}else c.removeClass("has-infobox"),d.hide()}function n(){function b(){var b=[],c=a("<div>"),d=a("div#assessment-edit-infobox"),e="'Not relevant' option selected for the following questions:";return d.empty(),a(".subform .left select option:selected").each(function(){var d=a(this).text(),e=a(this).parent().attr("id").split("_").slice(-2),f=e[0],g=e[1];g.match("[^a-zA-Z]")&&(g=g.split("-").join(".")),"Not relevant"==d&&(c.append(a("<span>").addClass("infobox-popover").append(f+": "+g)),b.indexOf(g)===-1&&b.push(g))}),b.forEach(function(b,c,e){d.append(a("<span>").attr("class","info-item").append(b))}),d.attr("class","help-popover").attr("data-trigger","hover").attr("data-html","true").attr("data-placement","bottom").attr("data-content",c.html()).attr("data-original-title",e).popover(),0===b.length?void d.hide():void d.append(a("<span>").attr("class","fa fa-exclamation").css({"font-size":"26px","float":"right",display:"block"}))}b(),a("select").change(function(){b(),m()})}a.fn.isInViewport=function(){var b=a(this).offset().top,c=b+a(this).outerHeight(),d=a(window).scrollTop(),e=d+a(window).height();return c>d&&b<e},a(document).ready(function(){b(),g(),h(),i(),j(),k(),l(),n(),a(".subform .right .comments").mouseenter(function(){f(a(this))});var c=a(window),d=a(".subform");d.each(function(){var b=a(this),d=b.find(".right"),e=b.find(".left").innerHeight();d.innerHeight(e);var f;c.resize(function(){clearTimeout(f),f=setTimeout(function(){d=b.find(".right"),e=b.find(".left").innerHeight(),d.innerHeight(e)},100)})});var e,o,p=a(".form-right-side"),q=a(".report-nav"),r=0;p.offset()&&(r=p.offset().top),q.length>0&&(rnOffset=q.offset().top),o=c.height()-2*p.height(),p.find("#form-buttons-save").addClass("btn-success");var s=p.find("#form-buttons-translate");s.addClass("btn-secondary"),window.location.pathname.indexOf("art10")==-1&&s.css("display","none"),c.scroll(function(){e=c.scrollTop();var a=e+o<r&&e>=rnOffset;p.toggleClass("fixed-save-btn",a),m()})})}(jQuery);
//# sourceMappingURL=assessment-edit.js.map