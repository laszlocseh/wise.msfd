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

  $.fn.fixTableHeaderHeight = function fixTableHeaderHeight() {
    // because the <th> are position: absolute, they don't get the height of
    // the <td> cells, and the other way around.
    this.each(function() {

      $("th", this).each(function() {
        var $th = $(this);
        var $next = $('td', $th.parent());
        var cells_max_height = Math.max($next.height());
        var height = Math.max($th.height(), cells_max_height);

        // console.log("TH", $th, thh, mh)

        $th.height(height);
        $next.first().height(height);
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
    var $tr = $('tr', this);
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
      $(this).fixTableHeaderHeight();
      //
      //addTranslateClickHandlers();
    }
    addTranslateClickHandlers();
  };

  function setupReportNavigation() {
    var $reportnav = $('#report-data-navigation');
    $('button', $reportnav).on('click', function() {
      $('.nav-body', $reportnav).toggle();
      return false;
    });
    $('.nav-body', $reportnav).hide();
  }

  function setupTableScrolling() {
    var $td = $('.table-report td');

    if (!$td.length) { return; }

    $td.children('div').wrapInner('<span class="td-text"/>');

    // get table header cell right position
    var $th = $('.table-report th');
    var thRight = $th.position().left + $th.outerWidth();

    $('.report-page-view .overflow-table .inner').scroll(function() {
      $td.each(function() {
        var $this = $(this);

        if ($this.attr('colspan') > 1) {
          var tdText = $this.find('.td-text');
          var tdHeight = $this.height();
          var tdLeft = $this.position().left;
          var tdRight = tdLeft + $this.outerWidth(); // get table data cell right position

          var tdTextWidth = $this.find('.td-text').width();
          var thAndCellWidth = tdTextWidth + thRight;

          if (tdLeft < thRight) {
            $this.height(tdHeight);
            tdText.addClass('table-scrolled');
            tdText.css('left', thRight + 5);
          } else {
            tdText.removeClass('table-scrolled');
            tdText.css('left', 'auto');
          }

          if (thAndCellWidth >= tdRight) {
            $this.css('position', 'relative');
            tdText.css({
              'left': 'auto',
              'right':'15px',
            });
          } else {
            $this.css('position', 'unset');
            tdText.css('right','auto');
          }
        }

      });
    });
  }

  $(document).ready(function($){
    initStyling();
    setupSelects2();
    setupReportNavigation();
    setupTableScrolling();

    if (window.matchMedia("(max-width: 768px)").matches) {
      $(".overflow-table h5").width( $(".overflow-table table").width() );
    }

    //$('.simplify-form').next().find('table').simplifyTable();

    // tibi
    $('.simplify-form').next().find('table').each(function(){
      $(this).simplifyTable();
    });

    $('.simplify-form button').on('click', function(){
      var onoff = $(this).attr('aria-pressed') == 'true';
      $p = $(this).parent().next();
      $('table', $p).toggleTable(!onoff);
    });

    // Warn user before leaving the page with unsaved changes
    var submitted = false;
    var modified = false;

    $('#comp-national-descriptor form').submit(function() {
      submitted = true;
    });

    $('#comp-national-descriptor').on('change', 'input, textarea, select', function(e) {
      modified = true;
    });

    $(window).bind('beforeunload', function() {
      if (modified && !submitted) {
        // most browsers ignores custom messages,
        // in that case the browser default message will be used
        return "You have unsaved changes. Do you want to leave this page?";
      }
    });


  });
}(window, document, $));
