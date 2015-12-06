% rebase('components/base.tpl')

<div class="row snake-img-container">
  <div onclick="toggleSecret()" class="snake-img" id='snake-img'></div>
</div>

<div style="text-align:center;" class="row">
    <iframe id="snake_game" src="/secret" ></iframe>
</div>

<script>
    document.getElementById('snake_game').hidden = true
</script>

<script>
    function toggleSecret() {
        if ($("#snake_game").is(":visible")){
            $("#snake-img").show();
            $("#snake_game").hide();
        }
        else{
            $("#snake-img").hide();
            $("#snake_game").fadeIn();
        }
    }
</script>

% include('components/search-bar.tpl')

