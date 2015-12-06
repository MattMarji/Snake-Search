<div class="panel panel-default">
      <!-- Default panel contents -->
      <div class="panel-heading">{{!title}}</div>
      <!-- Table -->
      <table id={{table_id}} class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>word</th>
          </tr>
        </thead>
        <tbody>
        % for item in zip([id for id in range(1,len(wordList)+1)], wordList):
          <tr>
            <th class="col-md-2" scope="row">{{item[0]}}</th>
            <td class="col-md-10">{{item[1]}}</td>
          </tr>
        % end
        </tbody>
      </table>
</div>
