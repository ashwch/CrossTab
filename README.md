# CrossTab

This app allows you to cross-tabulate a csv file on two columns.

**Explanation:**

- Both email and Facebook based login/signup are supported(I've not added any sort to Js validation, 
  email verification etc, let's assume we are all consenting adults here ;-).

- For a new user or an old user who has not uploaded any files at all will see a message that they should upload a CSV
  file to get up and running.
  
- For an old returning user with already uploaded their latest uploaded file will be displayed to them on login or 
  page refresh.

- When user uploads a file the file is sent to the server(using JSON POST) where I check its content-type first and then an entry is
  saved in [`UserFiles`](https://github.com/ashwch/CrossTab/blob/master/app/models.py#L92) model with the file's actual name,
  uploader's id, and the new autogenerated name. After this the file is saved in 'media/files/'. Next step is to pass the already in-memory present file to `pandas.read_csv` after
  moving the file pointer to the start of the file, if an error occurs while parsing the file its entry from database is removed
  and an error is displayed to user otherwise the dataframe is converted to a records dictionary using `to_dict()` method
  of dataframe and then this and some other meta-data is sent to the user.
  
- On user end I've used the [Bootstrap Table](http://bootstrap-table.wenzhixin.net.cn/) library to create a table from
  the records list sent from the server, my earlier atttemp was to use dataframe's `to_html()` method everywhere to get the content
  in HTML form itself from the server, but I ended up dropping that approach because I faced a lot of CSS issues.
  After populating the table with the data I also update the two select boxes with the headers received from the
  uploaded file, they select boxes will only allow you to choose unique columns. (After displaying the result I also
  add an entry of the file in "Load an older file" select box.)
  
- Now once we have a main table we can use the `Cross Tabulate ` button to perform cross-tabulation on our data, this
  is done using a JSON POST request where the two headers from the select boxes and the current file's name is sent to
  the server. On server using the filename I searrch for its entry in database if found I read the corresponding file 
  from the '/media/files' directory and then perform cross-tabulation on it based on the columns passed. After this I
  convert the dataframe to html using `to_html()` method of dataframe and then some processing is done on the HTML using 
  [`BeautifulSoup`](http://www.crummy.com/software/BeautifulSoup/) to remove from unwanted rows and add a class to the table. Lastly the HTML is returned to the user where
  I simply use it to fill a `div` and display the results to user.
  
- Apart from these another feature is that the user can use the "Load an older file" dropdown the load one of their older
  files, here only the filename is sent to the server with the JSON POST request and then I look for a related entry
  in database, if found I process the file using the and return the records dictionary else an error is raised.
  On user end after receiving the recors array the main table is re-populated using the new data as well the two select
  boxes and if any older cross-tabulation table is present it is removed.

---
  
**Languages and libraries used:**

- Python
- Django
- JavaScript
- Pandas
- jQuery
- Twitter Bootstrap
- BeautifulSoup
- Bootstrap Table

---
  
The app is currrently hosted at http://ashwch.pythonanywhere.com