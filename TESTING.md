# Testing
As the webpage was being built Chrome developer tools were used regularly to ensure that the code was working smoothly. Each section was then tested again every time a new feature was added. Python functions were regularly tested using the print function to ensure the code worked smoothly. Lighthouse in developer tools was also used to check the applications performance.

At the end of the development process, W3C CSS and Html validator were used to check the code.

The CSS validator came back with no errors

The HTML threw up some errors that were due to the use of flask 

**continued testing**


## Bugs

**Unresolved issues**
* I have not yet set up the functionality for a the user to update their profile image/avatar.


## Functional testing

The final tests done on the app to ensure it was fully funtional and ready to deploy. For each page I tested every possible funtion from top to bottom. 

**Home Page**

Test #1 (Navbar - Loggedin)
Action: Click on each to be redirected to ypur chosen template.
Before: Nav button clicked on home page(No state change of the button)
After: Redirected to chosen template.
Result: Pass

Test #2 (Navbar - Loggedout)
Action: Click on each to be redirected to ypur chosen template.
Before: Nav button clicked on home page(No state change of the button)
After: Redirected to chosen template.
Result: Pass

Test #3a (Search-box input)
Action: Type any book title into search box.
Before: Search box is inactve with plain white background.
After: Text fills the search box and shows previously searched words.
Result: Pass

Test #3b (Search-box input)
Action: Type an other book title into search box to confirm result.
Before: Search box is inactve with plain white background.
After: Text fills the search box and shows previously searched words.
Result: Pass

Test #4a (Search-Box button)
Action: Enter any title into the search box and clik the search button to the right.
Before: Text filss the search box and shows previous searches. 
After: Rdeirected to the search_results template where books of the searched title are displayed.
Result: Pass

Test #4b (Search-Box button)
Action: Enter an other title into the search box and clik the search button to the right to confirm result.
Before: Text filss the search box and shows previous searches. 
After: Rdeirected to the search_results template where books of the searched title are displayed.
Result: Pass

Test #5a (Library button - logged out)
Action: Click on the "Library" button.
Before: Hover over button changes state from orange to light orange.
After: Page is redirrected to Key Error message saying that I am missing the 'email' variable.
Result: fail

Test #5b (Library button - logged out)
Action: Click on the "Library" button.
Before: Hover over button changes state from orange to light orange.
After: 
Result: fail

Test #6
Action:
Before:
After:

Test #7
Action:
Before:
After:

Test #8
Action:
Before:
After:

Test #9
Action:
Before:
After:

Test #10
Action:
Before:
After:

Test #11
Action:
Before:
After:
