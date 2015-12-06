% rebase('components/base.tpl')

% include('components/search-bar.tpl')

% include('components/table-list-three-cols.tpl', table_id="pageranked_urls", title= "PageRanked URLS for <b>"+ query_str +"</b>", wordList = pagerankedList)

% include('components/table-dict.tpl', table_id="results", title= "Search results for <b>"+ query_str +"</b>", wordDict = resDict)

% if historyDict:
	% include('components/table-dict.tpl', table_id="history", title= "Top 20 Queried Words", wordDict = historyDict)
% end
	
% if recentList: 
	% include('components/table-list-two-cols.tpl', table_id="last_ten", title= "Last 10 Queried Words", wordList = recentList)
% end