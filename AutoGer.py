from transformers import pipeline
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

# Required input
#Id = '8135489781570160332'
Id=input("Enter Your Blogger ID: ")
"""I have set my account for blogger
If you want to use your account get .json file from google developer api and set the file name in 'CLIENT_SECRET' 
variable"""
CLIENT_SECRET = 'client_secret.json'
SCOPE = 'https://www.googleapis.com/auth/blogger'
STORAGE = Storage('credentials.storage')


def generate(topic, count):
    File = open(str(count) + '.txt', 'a+')
    generator = pipeline(task='text-generation', model='gpt2')
    text = generator(topic, max_length=10, num_return_sequences=1)
    for sentence in text:
        para = sentence['generated_text'].split('\n')
        File.write('<p>'+sentence['generated_text']+'</p>')
        File.flush()
    File1 = open(str(count) + '.txt', 'r+')
    read = File1.read()
    print(read)
    return read


# Start the OAuth flow to retrieve credentials
def authorization():
    # Fetch credentials from storage
    credential = STORAGE.get()
    # If the credentials doesn't exist in the storage location then run the flow
    if credential is None or credential.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credential = run_flow(flow, STORAGE, http=http)
    return credential


credentials = authorization()
print(credentials)


def post(blogid):
    credential = authorization()
    http = credential.authorize(httplib2.Http())
    discoveryUrl = 'https://blogger.googleapis.com/$discovery/rest?version=v3'
    service = discovery.build('blogger', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
    users = service.users()
    # Retrieve this user's profile information
    user = users.get(userId='self').execute()
    print('This user\'s display name is: %s' % user['displayName'])
    blogs = service.blogs()

    # Retrieve the list of Blogs this user has write privileges on
    thisusersblogs = blogs.listByUser(userId='self').execute()
    for blog in thisusersblogs['items']:
        print('The blog named \'%s\' is at: %s' % (blog['name'], blog['url']))

    posts = service.posts()
    number = int(input('Enter number of topics: '))
    Titles = []
    for num in range(1, number + 1):
        topic = input('Enter topic %d: ' % num)
        Titles.append(topic)
        print("happy code is name of the file")
        print("Enter file name in number")
    count = int(input('Enter Happy Code: '))
    for item in Titles:
        title = item
        content = generate(title, count)
        payload = {
            "content": "<div dir=\"ltr\" style=\"text-align: left;\" trbidi=\"on\">\n" + content + "</div>\n",
            "title": title,
        }
        respost = posts.insert(blogId=blogid, body=payload, isDraft=True).execute()
        # publishing the new post
        print('post ', title, ' is successfully posted')
        print("The post id:", respost['id'])
        count += 1


post(Id)
