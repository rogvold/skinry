ParseQuery<ParseObject> query = ParseQuery.getQuery("GameScore");
query.whereExists("ClientName");
query.findInBackground(new FindCallback<ParseObject>() {
public void done(List<ParseObject> ClientList, ParseException e) {
if (e == null) {
Log.d("score", "Retrieved " + ClientList.size() + " scores");
} else {
Log.d("score", "Error: " + e.getMessage()); 
} 
}
});