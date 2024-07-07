async function load(i){
    const youtubeLink = document.getElementById('youtubeLink').value;
    //saving link
    document.getElementById('saved-link').innerHTML = youtubeLink;
    const info = [
        {   url: '/generate-blog/',
            loadingId: 'loading-circle-1',
            output: 'blogContent'
        },
        {   url: '/generate-ts/',
            loadingId: 'loading-circle-2',
            output: 'tsContent'
        }
    ] 
    const blogContent = document.getElementById(info[i].output);
    const endpointUrl = info[i].url
    const loadId = info[i].loadingId

    function display(i, outputElement, data){
        
        //timestamps
        if (i==1){
            array = JSON.parse(data.content);
            htmlOutput = '';
            tsUrl=''
            for (const line of array){
                timeStr='';
                
                if ("time" in line && Object.keys(line.time).length==2){
                    timeStr=line.time.min+':'+line.time.sec;
                    tsUrl = line.time.min + 'm' + line.time.sec +'s'
                }
                else if ("time" in line && Object.keys(line.time).length==3){
                    timeStr=line.time.hour+':'+line.time.min+':'+line.time.sec;
                    tsUrl = line.time.hour + 'h' + line.time.min + 'm' + line.time.sec +'s'
                }
                else{
                    continue;
                }
                //modifying link to select specific timestamp
                const link = youtubeLink+"&t="+tsUrl
                htmlOutput+=('<a href="'+link+'" class="text-blue-600 hover:underline">'+timeStr + '</a>' + ' - ' + line.title +'\n');
            }
            outputElement.innerHTML = htmlOutput;
            
        } else {
            //blogpost
            //output the post and make the share button appear
            outputElement.innerHTML = data.content;
            document.getElementById('share-blog').style.display = 'block';
            document.getElementById('save-blog').style.display = 'block';



        }
    }
    
    if((youtubeLink)) {
        document.getElementById('already-saved').style.display = 'none';
        document.getElementById(loadId).style.display = 'block';

        blogContent.innerHTML = ''; // Clear previous content

        
        try {
            const response = await fetch(endpointUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ link: youtubeLink })
            });

            const data = await response.json();
            display(i, blogContent, data);

        } catch (error) {
            console.error("Error occurred:", error);
            alert("Something went wrong. Please try again later.");
            
        }
        document.getElementById(loadId).style.display = 'none';
    } else {
        alert("Please enter a YouTube link.");
    }
}

document.getElementById('generateBlogButton').addEventListener('click', async ()=>load(0)
);
document.getElementById('generateTSButton').addEventListener('click', async ()=>load(1)
);

document.getElementById('share-blog').addEventListener('click',function(event){
    const blogContent = document.getElementById('blogContent');
    const blog = blogContent.innerHTML;
    const youtubeLink = document.getElementById('saved-link').innerHTML;
    const prompt = 'If that sounds like a fit to you, click the following link to watch the full video: '
    sharedData = blog + prompt + youtubeLink;
    event.preventDefault();
    window.open('https://twitter.com/intent/post?text='+sharedData);
});
document.getElementById('save-blog').addEventListener('click', async function(event){
    try {
        const blogContent = document.getElementById('blogContent');
        const blog = blogContent.innerHTML;
        const youtubeLink = document.getElementById('saved-link').innerHTML;
        result = await fetch('/save-blog/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                blog: blog,
                link: youtubeLink
             })
        });
        
        document.getElementById('save-blog').style.display = 'none';
        document.getElementById('already-saved').style.display = 'block';


        

    } catch (error) {
        console.error("Error occurred:", error);
        alert("Can't save blog post. Please try again later.");
        
    }
});

