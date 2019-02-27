if (!Array.prototype.last){
  Array.prototype.last = function(){
    return this[this.length - 1];
  };
};

(function(window, document, $){

  var selectorFormContainer = ".wise-search-form-container";
  var exceptVal = ["all", "none", "invert", "apply"];
  /*
   * SELECT2 functions
   * */
  // TODO: please explain what this does and why it's needed
  function setupSelects2(selector){
    var forbiddenIDs = [];
    var selectorFormCont = selector || selectorFormContainer;

    $(selectorFormCont + " select").each(function(ind, selectElement) {
      var selectedElementID = $(selectElement).attr("id");
      if(forbiddenIDs.indexOf(selectedElementID) !== -1){
        return false;
      }

      $(selectElement).addClass("js-example-basic-single");
      var lessOptions = $(selectElement).find("option").length < 10;

      var options = {
        placeholder: 'Select an option',
        closeOnSelect: true,
        dropdownAutoWidth : true,
        width: '100%',
        theme: "flat"
      };
      if (lessOptions) options.minimumResultsForSearch = Infinity;

      $(selectElement).select2(options);
    });
  }

  function initStyling(){
    // TODO: is this still needed? I don't think so
    //$("#form-buttons-continue").hide("fast");
    $(".button-field").addClass("btn");

    // mobile hide .toggle-sidebar
    $(".toggle-sidebar").hide();
  }

  $.fn.fixTableHeaderAndCellsHeight = function fixTableHeaderAndCellsHeight() {
    // because the <th> are position: absolute, they don't get the height of
    // the <td> cells, and the other way around.
    this.each(function() {

      $("th", this).each(function() {
        var $th = $(this);
        var $next = $('td', $th.parent());
        var cells_max_height = Math.max($next.height());
        var height = Math.max($th.height(), cells_max_height);

        $th.height(height);

        if ($th.height() > cells_max_height) {
          $next.height($th.height());
        }
      });
    });
  };

  $.fn.fixTableHeaderHeight = function fixTableHeaderHeight() {
    this.each(function() {

      $("th", this).each(function() {
        var $th = $(this);
        var $next = $('td', $th.parent());
        var cells_max_height = Math.max($next.height());

        $th.height(cells_max_height);
      });

    });
  };

  $.fn.simplifyTable = function simplifyTable(){
    var $table = $(this);

    if (!$table.data('original')) {
      $table.data('original', $table.html());
    }

    // stretch all cells to the maximum table columns;
    var max = 0;
    var $tr = $('tr.merge', this);
    $tr.each(function(){
      $tds = $('td', this);
      if ($tds.length > max) {
        max = $tds.length;
      }
    });

    $tr.each(function(){
      $tds = $('td', this);
      if ($tds.length) {
        var td = $tds[$tds.length - 1];
        $(td).attr('colspan', max - $tds.length + 1);
      }
    });

    // join adjacent cells with identical text
    $tr.each(function(){
      var sets = [];
      $('td', this).each(function() {
        if (sets.length == 0) {   // start of processing
          sets.push([this]);
        } else {
          var thisText = $(this).text().trim();
          var lastText = $(sets.last().last()).text().trim();

          if ((thisText.length > 0) && (thisText == lastText)) {
            sets.last().push(this);
          } else {
            sets.push([this]);
          }
        }
      });
      $(sets).each(function(){
        if (this.length > 1) {
          var colspan = this.length;
          $(this[0]).attr('colspan', colspan);
          $(this.slice(1)).each(function(){
            $(this).remove();
          });
        }
      });
    });

    $table.fixTableHeaderHeight();
    $table.data('simplified', $table.html());
  };

  $.fn.toggleTable = function toggleTable(onoff) {
    var original = $(this).data('original');
    var simplified = $(this).data('simplified');
    if (onoff) {
      //$(this).simplifyTable();
      $(this).html(simplified);
    } else {
      $(this).hide();
      $(this).empty().html(original);
      $(this).show();

      console.log("done restoring");
      $(this).fixTableHeaderAndCellsHeight();

      //addTranslateClickHandlers();
    }
    setupReadMoreModal();
    // addTranslateClickHandlers();
  };

  /* Used in report data table create a 'read more' modal if the cell content
   * is too long
   */
  function setupReadMoreModal() {
    var $table = $('.table-report');
    var $td = $table.find('td');
    var $modalContent = $('.modal-content-wrapper');
    var maxchars = 500;
    var seperator = '...';

    $td.each(function() {
      var $this = $(this);
      var $tw = $this.find('.tr');

      $tw.each(function() {
        var $thw = $(this);
        var $text = $thw.find('.text-trans');
        var $si = $('<span class="short-intro"/>');

        if ($text.text().length > (maxchars - seperator.length)) {
          $this.addClass('read-more-wrapper');
          $si.insertBefore($text);

          var $intro = $thw.children('.short-intro');
          if ($thw.find('.short-intro').length > 1) {
            $intro.eq(0).remove();
          }
          $intro.text($text.text().substr(0, maxchars-seperator.length) + seperator);

          $this.find('.read-more-btn').click(function() {
            $this.find('.active').children('.text-trans').clone().appendTo($modalContent);
          });
        } else {
          $this.removeClass('read-more-wrapper');
        }
      });

    });

    $('.btn-close').click(function() { // TODO: make selector more specific
      $modalContent.empty();
    });

    $table.fixTableHeaderAndCellsHeight();
  }

  function setupReportNavigation() {
    // This is a menu that is triggered from a button. When scrolling down, it
    // sticks to the top. Allows navigation between articles/years
    var $reportnav = $('#report-data-navigation');
    $('button', $reportnav).on('click', function() {
      $('.nav-body', $reportnav).toggle();
      $(this).children().toggleClass('fa-bars fa-times');
      return false;
    });
    $('.nav-body', $reportnav).hide();

    // sticky report data navigation
    var $rn = $('.report-nav');
    var $title = $rn.closest('#report-data-navigation').siblings('.report-title');

    if ($rn.length > 0) {
      var stickyOffset = $rn.offset().top;

      $(window).scroll(function() {
        var scroll = $(window).scrollTop();

        if (scroll >= stickyOffset) {
          $rn.addClass('sticky').removeClass('fixed');
          $title.addClass('fixed-title');
        } else {
          $rn.removeClass('sticky').addClass('fixed');
          $title.removeClass('fixed-title');
        }
      });
    }
  }

  function setupTableScrolling() {
    // When dealing with a really wide table, with wide cells, we want to keep
    // the text relatively narrow, but always keep in view that cell content
    var $td = $('.table-report td');

    if (!$td.length) { return; }

    $td.children('div').wrapInner('<span class="td-content"/>');

    // get table header cell right position
    var $th = $('.table-report th');
    var thRight = $th.position().left + $th.outerWidth();

    $td.each(function() {
      var $this = $(this);
      var scrollTimer;

      $('.report-page-view .overflow-table .inner').scroll(function() {
        clearTimeout(scrollTimer);

        if ($this.attr('colspan') > 1) {
          var tdText = $this.find('.td-content');
          var tdLeft = $this.position().left;
          var tdRight = tdLeft + $this.outerWidth(); // get table cell right position
          var tdTextWidth = $this.find('.td-content').width();
          var thAndCellWidth = tdTextWidth + thRight;

          $this.css('height', $this.outerHeight());

          scrollTimer = setTimeout(function() {
            afterScroll()}, 1);

          if (tdLeft < thRight) {
            tdText.addClass('td-scrolled').css('left', thRight + 5);
          } else {
            $this.css('height', '');
            tdText.removeClass('td-scrolled').addClass('td-content-scrolled');
          }

          if (thAndCellWidth >= tdRight) {
            $this.addClass('td-relative');
          } else {
            $this.removeClass('td-relative');
          }
        }

      });

      function afterScroll() {
        $('.btn-translate').on('click', function() {
          var $btn = $(this);
          var transTextHeight = $btn.closest('.td-content').outerHeight();
          var $td = $btn.closest('td.translatable');
          var $th = $td.siblings('th');
          $td.css({
            'height': transTextHeight,
            'padding': '0'
          });
          $btn.closest('.td-content').css('padding', '8px');
          $th.css('height', transTextHeight);
        });
      }
    });
  }

  function setupCustomScroll() {
    // A fixed scrollbar at the bottom of the window for tables
    var $ot = $('.overflow-table');
    var $win = $(window);

    var $cs = $('<div class="scroll-wrapper">' +
      '<i class="fa fa-table"></i>' +
      '<div class="top-scroll">' +
        '<div class="top-scroll-inner"></div>' +
      '</div>' +
    '</div>');

    $cs.insertAfter($('.overflow-table').find('.inner'));

    // check if element is in viewport
    $.fn.isInViewport = function() {
      var elementTop = $(this).offset().top;
      var elementBottom = elementTop + $(this).height();

      var viewportTop = $win.scrollTop();
      var viewportBottom = viewportTop + $win.height();

      return elementBottom > viewportTop && elementTop < viewportBottom;
    };

    $ot.each(function() {
      var $t = $(this);
      var topScroll = $t.find('.top-scroll');
      var topScrollInner = topScroll.find('.top-scroll-inner');
      var tableScroll = $t.find('.inner');
      var tableWidth = $t.find('table').width();
      var tableHeaderWidth = $t.find('th').width();
      var tableAndHeaderWidth = tableWidth + tableHeaderWidth;
      var customScroll = $t.find('.scroll-wrapper');
      var lastTable = $('.overflow-table:last');

      topScrollInner.width(tableWidth);

      topScroll.on('scroll', function() {
        tableScroll.scrollLeft($(this).scrollLeft());
      });

      tableScroll.on('scroll', function() {
        topScroll.scrollLeft($(this).scrollLeft());
      });

      if (tableAndHeaderWidth > $t.width()) {
        $win.on('resize scroll', function() {
          var scroll = $win.scrollTop();

          if ($t.isInViewport()) {
            customScroll.addClass('fixed-scroll');
          } else {
            customScroll.removeClass('fixed-scroll');
          }

          // hide custom scrollbar when it reaches the bottom of the last table
          if (scroll >= lastTable.offset().top + lastTable.outerHeight() - window.innerHeight) {
            customScroll.hide();
          } else {
            customScroll.show();
          }
        });
      }
    });
  }

  function setupFixedTableRows() {
    // WIP
    // Allows report table rows to be fixed while scrolling
    var $ot = $('.overflow-table');
    var $ft = $(
      '<div class="fixed-table-wrapper">' +
        '<table class="table table-bordered table-striped table-report fixed-table">' +
        '</table>' +
      '</div>'
    );

    $ft.insertBefore($('.overflow-table').find('.inner'));
    $ot.each(function() {
      var $t = $(this);
      var tdWidth = $t.find('.inner').find('td').outerWidth();

      var $cb = $('<input type="checkbox" class="row-check"/>');
      $t.find('th').append($cb);

      var checkBox = $t.find('.row-check');
      checkBox.click(function(e) {
        var $this = $(this);

        if ($this.is(':checked')) {
          console.log("true", $this.closest('tr'), fixedTable);
          $this.closest('tr').clone().appendTo(fixedTable);
        }
      });

    });
  }

  function setupResponsiveness() {
    // fire resize event after the browser window resizing it's completed
    var resizeTimer;
    $(window).resize(function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(doneResizing, 500);
    });

    function doneResizing() {
      $('.table-report').fixTableHeaderHeight();
    }

    if (window.matchMedia("(max-width: 768px)").matches) {
      $(".overflow-table h5").width( $(".overflow-table table").width() );
    }
  }

  function setupSimplifiedTables() {
    //$('.simplify-form').next().find('table').simplifyTable();

    $('.simplify-form').next().find('table').each(function(){
      $(this).simplifyTable();
      setupCustomScroll();
    });

    $('.simplify-form button').on('click', function(){
      var onoff = $(this).attr('aria-pressed') == 'true';
      $p = $(this).parent().next();
      $('table', $p).toggleTable(!onoff);
      setupCustomScroll();
    });
  }

  $(document).ready(function($){
    initStyling();
    setupSelects2();
    setupReportNavigation();
    setupTableScrolling();
    setupReadMoreModal();
    setupResponsiveness();
    setupSimplifiedTables();
    // setupFixedTableRows();
  });
}(window, document, $));
