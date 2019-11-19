# ImageSearchUsingDescriptor

This project is about a search engine using elasticsearch. This search engine is based on image descriptor. Normally, the input of the search should be an image, then you would calculate its descriptor and use it to search the database, then finally show the images that have close descriptors, based or a particular distance.
In this project, we have a database of already calculated descriptors, and some thummbnails or the respective pictures, just to check results. We'll be using those descriptors for the search engine. And instead of calculating descriptors, we'll use the same for testing. That way in the search results, the first picture must be the one we entered, and the other pictures should be the closest ones in the database.
The database is huge, so the challenge is to make the search the fastest possible.The solution is to make a clustering to make the search easier, which in my case took several steps:
  
  - A first clustering of the whole database into 20 cluster
  - A second clustering of 10 cluster for each of those cluster
  
Honestly at first I thought the first clustering should be enough, then I got surprised with a search that took 4 to 5 seconds. So I added the second clustering, which made the search take less then one second.

You can find the thumbnails and the dataset in the link below:
https://drive.google.com/drive/folders/19cU70RDVKU7OuwpHslTjrsJJY_1kc-hS?usp=sharing
