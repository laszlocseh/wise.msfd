!function(a,b,c){function d(a,b,d){return $d=c("<div>"),$d.append(c("<label>").text(d)),$select=c("<select>"),c(b).each(function(){var a=c("<option>").attr("value",this.u).text(this.t).data("data",this);$select.append(a)}),$d.append($select),a.append($d),$select}function e(a,b){var d=null;return c(a).each(function(){this.i==b&&(d=this)}),d}function f(a){var b=e(a,"national-descriptors-assessments").c,f=c("#compliance-nav");d(f,b,"Countries",function(){}),d(f,b[0].c,"Regions",function(){}),d(f,b[0].c[0].c,"Descriptors",function(){}),d(f,b[0].c[0].c[0].c,"Articles",function(){}),d(f,[{t:"2012",u:""},{t:"2018",u:""}],"Version",function(){})}c(b).ready(function(b){console.log(a.jsonMapURL),b.getJSON(a.jsonMapURL,f)})}(window,document,jQuery);
//# sourceMappingURL=nav.js.map