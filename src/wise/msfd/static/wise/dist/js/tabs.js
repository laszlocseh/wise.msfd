function clickFirstTab(){$("#tabs-wrapper ul li:first-child a").trigger("click"),$(".tabs-wrapper ul li:first-child a").trigger("click")}window.setupTabs=function(a){clickFirstTab()},jQuery(document).ready(function(a){"undefined"!=typeof window.setupTabs&&window.setupTabs(),a(window).on("resize",function(){"undefined"!=typeof window.setupTabs&&window.setupTabs()})});
//# sourceMappingURL=tabs.js.map