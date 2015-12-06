<div class="panel panel-default">
      <!-- Default panel contents -->
      <div class="panel-heading">{{!title}}</div>
      <!-- Table -->
      <table id={{table_id}} class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>word</th>
            <th>count</th>
          </tr>
        </thead>
        <tbody>
        % for item in zip([ tuple([id])  for id in range(1,len(wordDict.items())+1)], wordDict.items()):
          <tr>
            <th class="col-md-2" scope="row">{{item[0][0]}}</th>
            <td class="col-md-5">{{item[1][0]}}</td>
            <td class="col-md-5">{{item[1][1]}}</td>
          </tr>
        % end
        </tbody>
      </table>
</div>
