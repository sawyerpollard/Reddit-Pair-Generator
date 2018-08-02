# Reddit Pair Generator
#### Python module for generating question-answer Reddit comment pairs using the pushshift.io Reddit dataset format.

# Usage
### Setup
Clone the repository.  
Change current directory to repo folder and run the following commands.

`pip install -r requirements.txt`

`./install_recognizers.sh`

### Create CoreNLP Server
The IP of a server running Stanford's CoreNLP is necessary.  
One can easily create a CoreNLP server by running the following Docker command that provides a community made Docker image.

*Must have Docker installed. Check operating system specific instructions.*

`docker run -p 9000:9000 -it --rm frnkenstien/corenlp`

### Download Reddit Data
Download comment data from  
https://files.pushshift.io/reddit/comments/  
and extract the text files.

### Python Use
Create Python file in the repo directory and use the following code as example.
```
import rpg

rpg = rpg.RPG(storage, corenlp_url)

rpg.perform_all(filepath, subreddits)
```
**Variable meanings:**
* storage = String path, relative to current working directory, to pre-existing directory to store file output.
* corenlp_url = URL string of CoreNLP server including port 9000.  
*Ex. http://8.8.8.8:9000 or http://example.com:9000*
* filepath = String path, relative to current working directory, to downloaded Reddit data or any other similarly formatted data.
* subreddits = Python list containing case-insensitive subreddit names.  
*Ex. ['askreddit', 'buildapc']*
---
**Additional info:** *To change entity recognition type, refer to Microsoft.Recognizers.Text documentation and edit `rpg.py` directly.*