async function load(i){
    const youtubeLink = document.getElementById('youtubeLink').value;
    
    const info = [
        {   url: '/generate-blog/',
            loadingId: 'loading-circle-1',
            output: 'blogContent'
        },
        {   url: '/generate-ts/',
            loadingId: 'loading-circle-2',
            output: 'tsContent'
        },
        {   url: '/generate-blog/',
            loadingId: 'loading-circle-3',
            output: 'blogContent'
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
            
            //outputElement.innerHTML = array[0].time.min+array[0].time.sec+data.content+array[0].title;
        } else {
            //blogpost
            outputElement.innerHTML = data.content;

        }
    }
    
    if((i<=1 && youtubeLink) || (i==2 && youtubeLink)) {
        document.getElementById(loadId).style.display = 'block';
        
        blogContent.innerHTML = ''; // Clear previous content

        //const endpointUrl = '/generate-blog/';
        
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
document.getElementById('findClipButton').addEventListener('click', async ()=>load(2)
);