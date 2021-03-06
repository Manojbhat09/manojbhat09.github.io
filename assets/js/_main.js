/* ==========================================================================
   jQuery plugin settings and other scripts
   ========================================================================== */

$(document).ready(function(){
   // Sticky footer
  var bumpIt = function() {
      $("body").css("margin-bottom", $(".page__footer").outerHeight(true));
    },
    didResize = false;

  bumpIt();

  $(window).resize(function() {
    didResize = true;
  });
  setInterval(function() {
    if (didResize) {
      didResize = false;
      bumpIt();
    }
  }, 250);
  // FitVids init
  $("#main").fitVids();

  // init sticky sidebar
  $(".sticky").Stickyfill();

  var stickySideBar = function(){
    var show = $(".author__urls-wrapper button").length === 0 ? $(window).width() > 1024 : !$(".author__urls-wrapper button").is(":visible");
    // console.log("has button: " + $(".author__urls-wrapper button").length === 0);
    // console.log("Window Width: " + windowWidth);
    // console.log("show: " + show);
    //old code was if($(window).width() > 1024)
    if (show) {
      // fix
      Stickyfill.rebuild();
      Stickyfill.init();
       $(".sticky").append("
//             <!-- Badge Code - Do Not Change The Code -->
//             <a class="hitCounter" href="https://visitorshitcounter.com/" target="_blank" title="Hit counter" data-name="7e31594ceddc8b0317147f983999c83b|5|ip|1|#31c95c|#ffffff|small|s-hit">Hit Counter</a><script>document.write("<script type='text/javascript' src='https://visitorshitcounter.com/js/hitCounter.js?v="+Date.now()+"'><\/script>");</script>
//             <!-- Badge Code End Here -->
               // <!-- Badge Code - Do Not Change The Code --><div class="col-xs-12 mt20" id="bg"><div style="margin:0px auto;width:133px;background:rgb(0, 170, 16);text-align:left;display:flex;border-radius:5px"><span style="padding:7px;display:inline-block;border-right:1px solid #746dba"><a href="http://visitorshitcounter.com" rel="nofollow noopener"  target="_blank" title="https://visitorshitcounter.com/"><img src="https://visitorshitcounter.com/img/s-logo.svg" alt="https://visitorshitcounter.com/" style="width:100%;border:none;float:left"></a></span><span class="text" id="dupli_hit_counter"   style="padding:10px 0 0 0;display:inline-block;color:#ffffff;width:100%;text-align:center;"></span></span><input type="hidden" id="site_val"   value="https://visitorshitcounter.com/counterDisplay?code=7e31594ceddc8b0317147f983999c83b&style=0017&pad=5&type=ip&initCount=1"></div></div><script src="https://visitorshitcounter.com/js/badgess.js?v=1588160522"></script><!-- Badge Code End Here -->
               <script type="text/javascript" src="//counter.websiteout.net/js/20/6/0/0"></script>
       ");
      $(".author__urls").show();
    } else {
      // unfix
      Stickyfill.stop();
      $(".author__urls").hide();
    }
  };

  stickySideBar();

  $(window).resize(function(){
    stickySideBar();
  });

  // Follow menu drop down

  $(".author__urls-wrapper button").on("click", function() {
    $(".author__urls").fadeToggle("fast", function() {});
    $(".author__urls-wrapper button").toggleClass("open");
  });

  // init smooth scroll
  $("a").smoothScroll({offset: -20});

  // add lightbox class to all image links
  $("a[href$='.jpg'],a[href$='.jpeg'],a[href$='.JPG'],a[href$='.png'],a[href$='.gif']").addClass("image-popup");

  // Magnific-Popup options
  $(".image-popup").magnificPopup({
    // disableOn: function() {
    //   if( $(window).width() < 500 ) {
    //     return false;
    //   }
    //   return true;
    // },
    type: 'image',
    tLoading: 'Loading image #%curr%...',
    gallery: {
      enabled: true,
      navigateByImgClick: true,
      preload: [0,1] // Will preload 0 - before current, and 1 after the current image
    },
    image: {
      tError: '<a href="%url%">Image #%curr%</a> could not be loaded.',
    },
    removalDelay: 500, // Delay in milliseconds before popup is removed
    // Class that is added to body when popup is open.
    // make it unique to apply your CSS animations just to this exact popup
    mainClass: 'mfp-zoom-in',
    callbacks: {
      beforeOpen: function() {
        // just a hack that adds mfp-anim class to markup
        this.st.image.markup = this.st.image.markup.replace('mfp-figure', 'mfp-figure mfp-with-anim');
      }
    },
    closeOnContentClick: true,
    midClick: true // allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source.
  });

});
