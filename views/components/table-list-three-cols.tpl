

% if len(wordList):
  <div class="panel panel-default">
        <!-- Default panel contents -->
        <div class="panel-heading">{{!title}}</div>
        <!-- Table -->
        <table id={{table_id}} class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>URL</th>
              <th>URL Title</th>
              <th>PageRank Score</th>
            </tr>
          </thead>
          <tbody>
          % for item in zip([id for id in range(1,len(wordList)+1)], wordList):
            <tr>
              <th class="col-md-2" scope="row">{{item[0]}}</th>
              <td class="col-md-3">
                <a href={{item[1][0]}}>
                  {{ (item[1][0][:15] + '...') if (len(item[1][0]) > 15) else item[1][0] }}
                </a>
              </td>
              <td class="col-md-3">
                {{item[1][1] if len(item[1][1]) else None}}
              </td>
              <td class="col-md-3">
                {{ (item[1][2]) if ((item[1][2])!=None) else 0 }}
              </td>
            </tr>
          % end
          </tbody>
        </table>
  </div>
% else:
  <div class="jumbotron">
      <h2>No PageRanked URLs</h2>        
  </div>
