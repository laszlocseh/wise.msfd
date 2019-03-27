$(document).ready(function () {

  var $original = $('#transl-original-text');
  var $old = $('#transl-old-translation');

  var setupTranslationsInReportPage = function () {

    /*
     * Triggered by translation edit btn. Sets proper text in modal edit dialog
     */
    function setupEditTranslationDialog () {
      var $cell = $(this).parents('td.translatable');

      var $text_div = $('.tr-text', $cell);
      var old_translation = $('.transl.system', $text_div).text();
      var orig_text = $('.text.system', $text_div).text();

      $original.text(orig_text);
      $old.text(old_translation);

      var $textarea = $('#form-edit-translation #new_transl');
      $textarea.val(old_translation.trim());
    };

    /*
     * Handles clicking on save translation in the edit translation dialog
     */
    function handleTranslationSave (e) {

      // inline editing in report data view page
      e.preventDefault();

      var orig_text = $original.text().trim();
      var $form = $('#form-edit-translation');
      var translation = $("#new_transl", $form).val();
      var url = $('.form-group').attr('portal_url') + '/@@edit-translation';
      var language = $form.children('input').attr('value');

      $.ajax({
        form: $form,
        type: 'POST',
        url: url,
        dataType: 'json',
        data: {
          'original': orig_text,
          'tr-new': translation,
          'language': language,
        },
        success: function (result) {
          location.reload();
        },
        error: function (result) {
          alert('ERROR saving translation!');
        }
      });

      $('.submitTransl')
        .attr('disabled', true)
        .attr('value', 'Please wait...')
      ;
    };

    /*
     * Setup the translations in the report data view screens
     */
    function toggleTranslations () {
      //
      $(this).toggleClass('active');
      $(this).siblings('.btn-translate').toggleClass('active');

      var $cell = $(this).parents('td.translatable');
      $cell
        .toggleClass('blue')
        .toggleClass('green')
      ;

      $('.text', $cell).toggleClass('active');
      $('.transl', $cell).toggleClass('active');

      // fix height of <th> on this row
      var $th = $(this).parents('tr').find('th').each(function(){
        var $th = $(this);
        var $next = $('td', $th.parent());
        var cells_max_height = Math.max($next.height());

        $th.height(cells_max_height);
      });
      // $th.fixTableHeaderHeight();

      // fix height of lang-toolbar on this row
      $(this).parents('tr').find('.lang-toolbar').each(function(){
        var $this = $(this);
        $this.css('height', $this.parent().height());
      });
    };

    function setupUITranslatedCells() {
      $('.lang-toolbar').each(function(){
        var $this = $(this),
          $p = $this.parent(),
          h = $p.height();

        var $c = $this
          .css('height', h)
          .children()
          .hide();
        ;
        console.log();

        function inhover(){
          var p = $p.position();
          $this
            .css({
              width: 'unset',
              position: 'absolute',
              float: 'none',
              top: p.top,
              left: p.left
            })
            .children()
            .show()
          ;
        }
        function outhover() {
          $this
            .css({
              width: '0px',
              float: 'left',
              position: 'initial'
            })
            .children()
            .hide()
          ;
        }

        $this.hover(inhover, outhover);
      });
    }

    function autoTranslation() {
      var $form = $("#form-refresh-translation");
      var $cell = $(this).parents('td.translatable');
      var text = $('.tr-text .text.system', $cell).text();

      $form.find('textarea').val(text);
      $form.submit();
    }

    window.setupTranslateClickHandlers = function () {
      $(".autoTransl").on("click", autoTranslation);
      // todo: toggle clickability of buttons?
      setupUITranslatedCells();

      $('.editTransl').on("click", setupEditTranslationDialog);
      $('.submitTransl').on("click", handleTranslationSave);

      $('.lang-orig').on("click", toggleTranslations);
      $('.lang-transl').on("click", toggleTranslations);
    };

    setupTranslateClickHandlers();

  };

  var setupTranslationsInOverviewPage = function () {
    var $form = $('#form-edit-translation');
    var $modal = $('#edit-translation');

    $modal.on('show.bs.modal', function (event) {
      $form.off('submit');
      // setup the modal to show proper values
      var $btn = $(event.relatedTarget);
      var cells = $btn.parent().parent().children();

      var original = $(cells[0]).text();
      var translated = $(cells[1]).text();

      $('#tr-original').text(original);   // show original text
      $('textarea[name="original"]', $form).val(original);   // form input

      $('#tr-new').val(translated);    // textarea for new translation

      $('#tr-current').text(translated);    // show current translation
      $form.on('submit', function () {
        var url = $form.attr('action');
        var data = {};

        $('textarea,input', $form).each(function () {
          var name = $(this).attr('name');
          if (!name) return;
          data[name] = $(this).val();
        });

        $.ajax({
          form: $form,
          type: 'POST',
          url: url,
          dataType: 'json',
          data: data,
          success: function (result) {
            location.reload(); // reload page from the server, ignoring cache
          },
          error: function (result) {
            alert('ERROR saving translation!');
          }
        });

        return false;
      });
    });
  };

  var onReport = $('.report-page-view ').length;

  if (onReport) {
    setupTranslationsInReportPage();
  } else {
    setupTranslationsInOverviewPage();
  }
});
