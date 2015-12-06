<!doctype html>
<html>
	<head>
		<!-- Latest compiled and minified CSS -->
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css" integrity="sha512-dTfge/zgoMYpP7QbHy4gWMEGsbsdZeCXz7irItjcC3sPUFtf0kuFbDz/ixG7ArTxmDjLXDmezHubeNikyKGVyQ==" crossorigin="anonymous">
		<link rel="stylesheet" href="/static/style.css">

		<link rel="stylesheet" href="https://cdn.datatables.net/s/bs-3.3.5/dt-1.10.10/datatables.min.css">
		<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
		<script src="//code.jquery.com/jquery-2.1.4.min.js"></script>
		<script src="https://cdn.datatables.net/s/bs-3.3.5/dt-1.10.10/datatables.min.js"></script>
		<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
		<script src="/static/typeahead.js"></script>

		<title> snake search | for all your word counting needs </title>
		<script> 

			$(document).on('click','#feeling-lucky',function(s){
				var query = $("#query").val();
				if (query.trim().length){
					location.href="/lucky?keywords=" + encodeURIComponent(query)
				}
				return false;
			})

			$(document).ready(function(){
				// Clear out modified action variable
				$('form').each(function() { this.reset() });				
				// DataTable Initialization
				$('#pageranked_urls').DataTable({
					pageLength: 5,
					searching: false,
					lengthChange: false
				})
				// Autocomplete engine
				var suggestionEngine = new Bloodhound({
				  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('description'),
				  queryTokenizer: Bloodhound.tokenizers.whitespace,
				  remote: {
				    url: '/api/?keywords=%QUERY',
				    wildcard: '%QUERY',
					  filter: function(response){
						return $.map(response.data, function (item) {
							if (item.description.length){
				                return {
				                    desc: item.description,
				                    url: item.link
				                };								
							}
			            });
					  }				    
				  }
				});
				// Initialize DOM autosuggest element
				$('#query').typeahead(null, {
				  display: 'desc',
				  source: suggestionEngine
				}).on('typeahead:selected', function(e, datum) {
					$("#query-btn").trigger('click');
        		});
			})
		</script>
	</head>
	<body>
		 <div class="container">
		      <div class="header clearfix">
		        <nav>
		          <ul class="nav nav-pills pull-right">
					% if logged_in:
						<li role="presentation"><a class="unclickable">{{user_email}}</a></li>
					% else:
						<li role="presentation"><a href="/signin">Sign In</a></li>
					% end

					% if logged_in:
						<li role="presentation"><a href="/signout">Sign Out</a></li>
					% end
		          </ul>
		        </nav>
		        <h3 class="text-muted">snake search</h3>
		      </div>

		      {{!base}}

		 </div> <!-- /container -->
	</body>
</html>


